#!/usr/bin/env python3
"""PR 현황 보고서와 분류 라벨 (.github/workflows/claude-pr-triage.yml 이 쓴다).

라벨과 상태는 GitHub 의 사실에서 결정적으로 정한다. Claude 는 같은 사실로 우선순위와 다음 조치 문장만 제안하고,
이 스크립트가 그 제안을 검증한 뒤에만 보고서에 넣는다. PR 을 병합·종료하거나 브랜치를 고치지 않는다.

하위 명령:
  collect   열린 PR 의 사실을 모아 스냅샷을 만든다. 보고서 이슈의 digest 와 비교해 바뀐 것이 있는지 알려 준다.
  validate  Claude 의 구조화 출력을 스냅샷에 대해 검증한다.
  publish   다시 수집해 스냅샷이 낡지 않았는지 확인하고, 관리 라벨 (pr-triage/*) 과 보고서 이슈 하나를 갱신한다.
            --dry-run 이면 아무것도 바꾸지 않고 계획만 출력한다.

사용 예 (읽기 전용):
  python3 -I scripts/pr_triage.py collect --repo OWNER/REPO --out /tmp/snap.json
  python3 -I scripts/pr_triage.py publish --repo OWNER/REPO --snapshot /tmp/snap.json --ai /tmp/ai.json --dry-run
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Set, Tuple

DIGEST_VERSION = 1
PREFIX = "pr-triage/"
REPORT_LABEL = "pr-triage/report"
REPORT_TITLE = "PR 현황 보고서 (자동)"
REPORT_MARKER = "<!-- pr-triage-report:v1 -->"  # 봇 소유 보고서의 고정 표식
PR_LIMIT = 100      # 한 번에 다루는 열린 PR 상한. 상한 + 1 로 조회해 넘치면 멈춘다
REPORT_LIMIT = 20
BOT_LOGINS = {"app/github-actions", "github-actions[bot]", "github-actions"}
REQUIRED_CHECKS = ("Lean build and audits",)  # ruleset protect-main 의 필수 검사

LABELS: Dict[str, Tuple[str, str]] = {
    "pr-triage/ready": ("0e8a16", "Draft 아님, 충돌 없음, CI 통과, 리뷰 승인, 병합 가능 모두 확인됨"),
    "pr-triage/needs-review": ("fbca04", "리뷰 승인 대기"),
    "pr-triage/changes-requested": ("d93f0b", "리뷰가 변경을 요청함"),
    "pr-triage/ci-failing": ("b60205", "실패한 검사가 있음"),
    "pr-triage/ci-pending": ("c5def5", "진행 중인 검사가 있음"),
    "pr-triage/conflict": ("b60205", "base 와 충돌"),
    "pr-triage/blocked": ("e99695", "나머지 확인은 통과했지만 병합 상태가 BLOCKED·BEHIND 등으로 미해결"),
    "pr-triage/draft": ("cfd3d7", "Draft PR"),
    "pr-triage/unknown": ("ededed", "상태 일부를 확인하지 못함 (누락·UNKNOWN)"),
    REPORT_LABEL: ("5319e7", "PR 현황 보고서 이슈 (자동 갱신)"),
}
PR_LABELS = {name for name in LABELS if name != REPORT_LABEL}
PRIORITIES = ("높음", "보통", "낮음")
DIGEST_RE = re.compile(r"<!-- pr-triage-digest: ([0-9a-f]{64}) -->")

PASS_CONCLUSIONS = {"SUCCESS", "SKIPPED", "NEUTRAL"}
FAIL_CONCLUSIONS = {"FAILURE", "TIMED_OUT", "STARTUP_FAILURE", "ACTION_REQUIRED"}
PENDING_STATUSES = {"QUEUED", "IN_PROGRESS", "PENDING", "WAITING", "REQUESTED"}


class Stale(Exception):
    """게시 직전 다시 모은 사실이 스냅샷과 다르다."""


class TriageError(Exception):
    """수집 결과를 전체라고 믿을 수 없다 (상한 초과, 보고서 이슈 여러 개 등)."""


# ---------------------------------------------------------------- 사실 정규화와 분류 (결정적)

def check_state(check: dict) -> str:
    """검사 하나를 pass / fail / pending / unknown 으로. CANCELLED, STALE, 값 없음은 unknown."""
    if check.get("__typename") == "StatusContext":
        state = (check.get("state") or "").upper()
        return {"SUCCESS": "pass", "FAILURE": "fail", "ERROR": "fail",
                "PENDING": "pending", "EXPECTED": "pending"}.get(state, "unknown")
    status = (check.get("status") or "").upper()
    if status != "COMPLETED":
        return "pending" if status in PENDING_STATUSES else "unknown"
    conclusion = (check.get("conclusion") or "").upper()
    if conclusion in PASS_CONCLUSIONS:
        return "pass"
    if conclusion in FAIL_CONCLUSIONS:
        return "fail"
    return "unknown"


def ci_state(checks: List[dict]) -> str:
    """실패가 하나라도 있으면 fail, 진행 중이면 pending. 필수 검사는 실제 SUCCESS 여야 한다 (SKIPPED·NEUTRAL 이나
    없음은 unknown). 비필수 검사는 SKIPPED·NEUTRAL 도 통과로 본다 (예: PR 에서 건너뛰는 배포 job)."""
    states = [c["state"] for c in checks]
    if "fail" in states:
        return "fail"
    if "pending" in states:
        return "pending"
    if "unknown" in states:
        return "unknown"
    for name in REQUIRED_CHECKS:
        required = [c for c in checks if c["name"] == name]
        if not required or any(c["conclusion"] != "SUCCESS" for c in required):
            return "unknown"
    return "pass"


def _opt_str(value) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def normalize_pr(raw: dict) -> dict:
    checks = sorted(
        ({"name": c.get("name") or c.get("context") or "?",
          "workflow": c.get("workflowName") or "",
          "conclusion": ((c.get("conclusion") if c.get("__typename") != "StatusContext" else c.get("state")) or "").upper(),
          "state": check_state(c)}
         for c in (raw.get("statusCheckRollup") or [])),
        key=lambda c: (c["workflow"], c["name"]))
    labels = sorted(l.get("name", "") for l in (raw.get("labels") or []))
    author = raw.get("author") or {}
    is_draft = raw.get("isDraft")
    return {
        "number": raw["number"],
        "title": raw.get("title") or "",
        "url": raw.get("url") or "",
        "head_sha": _opt_str(raw.get("headRefOid")),
        "author": author.get("login") or "",
        "is_draft": is_draft if isinstance(is_draft, bool) else None,
        "mergeable": _opt_str(raw.get("mergeable")),
        "merge_state": _opt_str(raw.get("mergeStateStatus")),
        "review_decision": _opt_str(raw.get("reviewDecision")),
        "checks": checks,
        "ci": ci_state(checks),
        "labels": labels,
    }


def classify(pr: dict) -> Set[str]:
    """관리 라벨 집합. CI 가 녹색이어도 리뷰 승인이 없으면 ready 가 아니다. 누락·UNKNOWN 은 unknown."""
    out: Set[str] = set()
    unknown = False
    if pr["is_draft"] is None:
        unknown = True
    elif pr["is_draft"]:
        out.add("pr-triage/draft")
    if pr["mergeable"] == "CONFLICTING":
        out.add("pr-triage/conflict")
    elif pr["mergeable"] != "MERGEABLE":
        unknown = True
    if pr["ci"] == "fail":
        out.add("pr-triage/ci-failing")
    elif pr["ci"] == "pending":
        out.add("pr-triage/ci-pending")
    elif pr["ci"] == "unknown":
        unknown = True
    review = pr["review_decision"]
    if review == "REVIEW_REQUIRED":
        out.add("pr-triage/needs-review")
    elif review == "CHANGES_REQUESTED":
        out.add("pr-triage/changes-requested")
    elif review != "APPROVED":
        unknown = True
    if pr["head_sha"] is None:
        unknown = True
    if (not unknown and pr["is_draft"] is False and pr["mergeable"] == "MERGEABLE"
            and pr["ci"] == "pass" and review == "APPROVED"):
        if pr["merge_state"] in ("CLEAN", "HAS_HOOKS"):
            out.add("pr-triage/ready")
        elif pr["merge_state"] in (None, "UNKNOWN"):
            unknown = True
        else:
            out.add("pr-triage/blocked")  # BLOCKED, BEHIND, UNSTABLE, DIRTY 등
    if unknown or not out:
        out.add("pr-triage/unknown")  # 분류가 빈 집합으로 사라지지 않게 한다
    return out


def managed(labels: List[str]) -> Set[str]:
    return {l for l in labels if l in PR_LABELS}


def plan_labels(pr: dict) -> Tuple[List[str], List[str]]:
    """(추가, 제거). 관리 라벨만 다루고 다른 라벨은 건드리지 않는다."""
    desired = classify(pr)
    current = managed(pr["labels"])
    return sorted(desired - current), sorted(current - desired)


def facts_digest(prs: List[dict]) -> str:
    """사실 (현재 관리 라벨은 제외) 의 digest. 시각·URL 은 넣지 않는다."""
    facts = [{k: p[k] for k in ("number", "title", "head_sha", "author", "is_draft", "mergeable",
                                "merge_state", "review_decision", "checks", "ci")}
             for p in sorted(prs, key=lambda p: p["number"])]
    blob = json.dumps({"v": DIGEST_VERSION, "prs": facts}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def find_report_issue(issues: List[dict]) -> Optional[dict]:
    """봇이 만들고, 보고서 라벨·제목·고정 표식을 모두 가진 열린 이슈 하나. 사람이 만든 이슈는 무시한다.
    그런 이슈가 여럿이면 임의로 고르지 않고 TriageError 를 낸다."""
    owned = [i for i in issues
             if (i.get("author") or {}).get("login") in BOT_LOGINS
             and any(l.get("name") == REPORT_LABEL for l in (i.get("labels") or []))
             and (i.get("state") or "OPEN").upper() == "OPEN"
             and i.get("title") == REPORT_TITLE
             and REPORT_MARKER in (i.get("body") or "")]
    if len(owned) > 1:
        raise TriageError(f"봇 소유 보고서 이슈가 여럿이다: {sorted(i['number'] for i in owned)}. 하나만 남기고 닫아야 한다.")
    return owned[0] if owned else None


def parse_digest(body: Optional[str]) -> Optional[str]:
    m = DIGEST_RE.search(body or "")
    return m.group(1) if m else None


# ---------------------------------------------------------------- Claude 출력 검증과 보고서

def _clean(text: str, limit: int) -> str:
    """한 줄로 만들고, 표·HTML·멘션·digest 표식을 무력화한다."""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("<!--", "").replace("-->", "").replace("<", "‹").replace(">", "›")
    text = text.replace("|", "\\|").replace("@", "@​").replace("`", "'")
    return text[:limit].rstrip()


def validate_ai(ai: object, snapshot: dict) -> Dict[int, dict]:
    """digest 일치, PR 번호 집합 일치 (각 1 회), 우선순위 열거값, 비지 않은 다음 조치. 아니면 ValueError."""
    if not isinstance(ai, dict):
        raise ValueError("구조화 출력이 객체가 아니다")
    if ai.get("digest") != snapshot["digest"]:
        raise ValueError("digest 가 스냅샷과 다르다")
    items = ai.get("items")
    if not isinstance(items, list):
        raise ValueError("items 가 배열이 아니다")
    expected = {p["number"] for p in snapshot["prs"]}
    out: Dict[int, dict] = {}
    for it in items:
        if not isinstance(it, dict) or not isinstance(it.get("number"), int):
            raise ValueError("항목 형식이 틀렸다")
        n = it["number"]
        if n in out:
            raise ValueError(f"PR #{n} 가 두 번 나온다")
        if n not in expected:
            raise ValueError(f"스냅샷에 없는 PR #{n}")
        if it.get("priority") not in PRIORITIES:
            raise ValueError(f"PR #{n} 의 우선순위가 허용값이 아니다")
        action = it.get("next_action")
        if not isinstance(action, str) or not action.strip():
            raise ValueError(f"PR #{n} 의 다음 조치가 비었다")
        out[n] = {"priority": it["priority"], "next_action": _clean(action, 160)}
    if set(out) != expected:
        raise ValueError(f"빠진 PR: {sorted(expected - set(out))}")
    return out


DRAFT_TEXT = {True: "예", False: "아니오", None: "미확인"}
MERGE_TEXT = {"MERGEABLE": "없음", "CONFLICTING": "있음"}
CI_TEXT = {"pass": "통과", "fail": "실패", "pending": "진행 중", "unknown": "미확인"}
REVIEW_TEXT = {"APPROVED": "승인", "REVIEW_REQUIRED": "승인 대기", "CHANGES_REQUESTED": "변경 요청"}


def render(snapshot: dict, items: Dict[int, dict], run_url: str, now: str) -> str:
    lines = [
        "## PR 현황 보고서",
        "",
        REPORT_MARKER,
        f"<!-- pr-triage-digest: {snapshot['digest']} -->",
        f"마지막 갱신 {now} · [실행]({run_url})",
        "",
        "라벨과 상태 열은 GitHub 의 사실에서 결정적으로 정했다. 우선순위와 다음 조치는 Claude 가 같은 사실로 쓴 제안이며,",
        "이 보고서는 PR 을 병합·종료하지 않는다. 사실이 바뀌지 않으면 갱신하지 않는다.",
        "",
    ]
    if not snapshot["prs"]:
        lines.append("열린 PR 이 없다.")
        return "\n".join(lines) + "\n"
    lines += ["| PR | head | Draft | 충돌 | CI | 리뷰 | 라벨 | 우선순위 | 다음 조치 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    order = {p: i for i, p in enumerate(PRIORITIES)}
    def rank(p: dict) -> Tuple[int, int]:
        return order.get(str(items.get(p["number"], {}).get("priority", "")), 9), p["number"]
    prs = sorted(snapshot["prs"], key=rank)
    for p in prs:
        it = items.get(p["number"], {"priority": "-", "next_action": "-"})
        labels = ", ".join(l.replace(PREFIX, "") for l in sorted(classify(p))) or "-"
        lines.append(
            f"| #{p['number']} {_clean(p['title'], 80)} | {(p['head_sha'] or '미확인')[:7]} "
            f"| {DRAFT_TEXT[p['is_draft']]} | {MERGE_TEXT.get(p['mergeable'] or '', '미확인')} "
            f"| {CI_TEXT[p['ci']]} | {REVIEW_TEXT.get(p['review_decision'] or '', '미확인')} "
            f"| {labels} | {it['priority']} | {it['next_action']} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- GitHub 입출력

def _subprocess_runner(args: List[str], stdin: Optional[str]) -> Tuple[int, str, str]:
    res = subprocess.run(["gh"] + args, input=stdin, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def label_path(name: str) -> str:
    """라벨 이름을 REST 경로 한 조각으로. pr-triage/foo 의 '/' 가 경로 구분자가 되지 않게 인코딩한다."""
    return urllib.parse.quote(name, safe="")


class GH:
    """gh CLI 얇은 래퍼. dry_run 이면 GET 외의 호출을 실행하지 않고 출력만 한다. runner 는 시험용으로 바꿀 수 있다."""

    def __init__(self, repo: str, dry_run: bool = False,
                 runner: Callable[[List[str], Optional[str]], Tuple[int, str, str]] = _subprocess_runner):
        self.repo = repo
        self.dry_run = dry_run
        self.runner = runner
        self.mutations: List[str] = []

    def _run(self, args: List[str], stdin: Optional[str] = None) -> str:
        rc, out, err = self.runner(args, stdin)
        if rc != 0:
            raise RuntimeError(f"gh {' '.join(args[:3])} 실패: {err.strip()[:300]}")
        return out

    def list_prs(self) -> List[dict]:
        return json.loads(self._run([
            "pr", "list", "-R", self.repo, "--state", "open", "--limit", str(PR_LIMIT + 1), "--json",
            "number,title,url,headRefOid,isDraft,mergeable,mergeStateStatus,reviewDecision,author,labels,statusCheckRollup"]))

    def list_report_issues(self) -> List[dict]:
        return json.loads(self._run([
            "issue", "list", "-R", self.repo, "--state", "open", "--label", REPORT_LABEL,
            "--limit", str(REPORT_LIMIT + 1), "--json", "number,title,author,labels,body,state"]))

    def label_exists(self, name: str) -> bool:
        rc, _, _ = self.runner(["api", f"repos/{self.repo}/labels/{label_path(name)}"], None)
        return rc == 0

    def mutate(self, desc: str, args: List[str], stdin: Optional[str] = None) -> None:
        self.mutations.append(desc)
        if self.dry_run:
            print(f"[dry-run] {desc}")
            return
        self._run(args, stdin)

    def create_label(self, name: str) -> None:
        color, description = LABELS[name]
        self.mutate(f"라벨 생성 {name}", ["api", "-X", "POST", f"repos/{self.repo}/labels",
                                        "-f", f"name={name}", "-f", f"color={color}", "-f", f"description={description}"])

    def add_labels(self, number: int, names: List[str]) -> None:
        args = ["api", "-X", "POST", f"repos/{self.repo}/issues/{number}/labels"]
        for n in names:
            args += ["-f", f"labels[]={n}"]
        self.mutate(f"#{number} 라벨 추가 {names}", args)

    def remove_label(self, number: int, name: str) -> None:
        self.mutate(f"#{number} 라벨 제거 {name}",
                    ["api", "-X", "DELETE", f"repos/{self.repo}/issues/{number}/labels/{label_path(name)}"])

    def update_issue(self, number: int, body: str) -> None:
        self.mutate(f"보고서 이슈 #{number} 본문 갱신", ["api", "-X", "PATCH", f"repos/{self.repo}/issues/{number}",
                                                    "-F", "body=@-"], stdin=body)

    def create_issue(self, body: str) -> None:
        self.mutate("보고서 이슈 생성", ["issue", "create", "-R", self.repo, "--title", REPORT_TITLE,
                                    "--label", REPORT_LABEL, "--body-file", "-"], stdin=body)


def collect(gh) -> dict:
    raw_prs = gh.list_prs()
    if len(raw_prs) > PR_LIMIT:
        raise TriageError(f"열린 PR 이 {PR_LIMIT} 개를 넘는다. 잘린 목록을 전체라고 게시하지 않는다.")
    prs = [normalize_pr(raw) for raw in raw_prs]
    prs.sort(key=lambda p: p["number"])
    issues = gh.list_report_issues()
    if len(issues) > REPORT_LIMIT:
        raise TriageError(f"보고서 라벨 이슈가 {REPORT_LIMIT} 개를 넘는다. 정리가 필요하다.")
    report = find_report_issue(issues)
    digest = facts_digest(prs)
    report_digest = parse_digest(report.get("body")) if report else None
    return {
        "version": DIGEST_VERSION,
        "repo": gh.repo,
        "digest": digest,
        "prs": prs,
        "report_issue": {"number": report["number"], "digest": report_digest} if report else None,
        "facts_changed": report_digest != digest,
        "label_drift": any(plan_labels(p) != ([], []) for p in prs),
    }


def publish(gh, snapshot: dict, ai: Optional[object], run_url: str, now: str) -> str:
    """게시. 반환값: published / labels-only / already-published. 낡은 스냅샷이면 Stale."""
    fresh = collect(gh)
    if fresh["digest"] != snapshot["digest"]:
        raise Stale("게시 직전 다시 모은 사실이 스냅샷과 다르다 (head·CI·리뷰 등이 바뀜). 낡은 상태로 쓰지 않는다.")
    report = fresh["report_issue"]
    need_body = not (report and report["digest"] == snapshot["digest"])
    items: Dict[int, dict] = {}
    if need_body:
        if fresh["prs"]:
            if ai is None:
                raise ValueError("사실이 바뀌었는데 검증할 Claude 출력이 없다")
            items = validate_ai(ai, snapshot)
    plans = [(p, plan_labels(p)) for p in fresh["prs"]]
    if not need_body and all(plan == ([], []) for _, plan in plans):
        return "already-published"
    needed = {l for _, (add, _) in plans for l in add} | ({REPORT_LABEL} if need_body and not report else set())
    for name in sorted(needed):
        if not gh.label_exists(name):
            gh.create_label(name)
    for p, (add, remove) in plans:
        if add:
            gh.add_labels(p["number"], add)
        for name in remove:
            gh.remove_label(p["number"], name)
    if not need_body:
        return "labels-only"
    body = render(snapshot, items, run_url, now)
    if report:
        gh.update_issue(report["number"], body)
    else:
        gh.create_issue(body)
    return "published"


# ---------------------------------------------------------------- CLI

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--repo", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--github-output")
    v = sub.add_parser("validate")
    v.add_argument("--snapshot", required=True)
    v.add_argument("--ai", required=True)
    p = sub.add_parser("publish")
    p.add_argument("--repo", required=True)
    p.add_argument("--snapshot", required=True)
    p.add_argument("--ai")
    p.add_argument("--run-url", default="")
    p.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if args.cmd == "collect":
        try:
            snap = collect(GH(args.repo))
        except TriageError as e:
            print(f"::error::{e}")
            return 1
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)
        print(f"PR {len(snap['prs'])} 개, digest {snap['digest'][:12]}, "
              f"사실 변화 {snap['facts_changed']}, 라벨 어긋남 {snap['label_drift']}")
        for pr in snap["prs"]:
            add, remove = plan_labels(pr)
            print(f"  #{pr['number']} head={(pr['head_sha'] or '?')[:7]} ci={pr['ci']} review={pr['review_decision']} "
                  f"mergeable={pr['mergeable']} -> {sorted(classify(pr))} (+{add} -{remove})")
        if args.github_output:
            with open(args.github_output, "a", encoding="utf-8") as f:
                f.write(f"facts_changed={'true' if snap['facts_changed'] else 'false'}\n")
                f.write(f"label_drift={'true' if snap['label_drift'] else 'false'}\n")
                f.write(f"pr_count={len(snap['prs'])}\n")
                f.write(f"digest={snap['digest']}\n")
        return 0

    with open(args.snapshot, encoding="utf-8") as f:
        snapshot = json.load(f)
    if args.cmd == "validate":
        with open(args.ai, encoding="utf-8") as f:
            raw = f.read()
        try:
            items = validate_ai(json.loads(raw) if raw.strip() else None, snapshot)
        except ValueError as e:
            print(f"::error::Claude 출력 검증 실패: {e}")
            return 1
        for n, it in sorted(items.items()):
            print(f"  #{n} [{it['priority']}] {it['next_action']}")
        return 0

    ai = None
    if args.ai:
        with open(args.ai, encoding="utf-8") as f:
            raw = f.read()
        ai = json.loads(raw) if raw.strip() else None
    gh = GH(args.repo, dry_run=args.dry_run)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        result = publish(gh, snapshot, ai, args.run_url, now)
    except Stale as e:
        print(f"::warning::{e}")
        return 3
    except (ValueError, TriageError) as e:
        print(f"::error::{e}")
        return 1
    print(f"결과: {result}, 변경 {len(gh.mutations)} 건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
