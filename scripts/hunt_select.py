#!/usr/bin/env python3
"""보조정리 사냥꾼의 작업 선택과 시도 기록 (.github/workflows/claude-lemma-hunter.yml). 결정적이며 AI 를 쓰지 않는다.

선택 규칙 (예약 실행):
  1. 열린 연구 PR (head 가 claude/hunt-*, Draft·Ready 모두) 이 2 개 이상이면 새 작업을 시작하지 않는다.
  2. 후보는 열린 lemma-hunt 이슈 가운데 소유자가 쓰고, 본문을 소유자 말고는 고친 적 없는 것.
  3. 열린 또는 병합된 연구 PR 이 본문에서 그 이슈를 가리키면 (Refs/Closes/Fixes/Resolves #N) 고르지 않는다.
  4. 같은 본문 (task 해시) 과 같은 기준 main SHA 로 시작한 기록이 있으면 고르지 않는다 (결과와 무관).
     기록은 작업 선택 직후, 비싼 Lean 준비와 AI 실행 전에 github-actions 봇이 남기는 댓글의 고정 표식이다
     (outcome=started). 그래서 시간 초과나 취소로 끝나도 기록이 남는다. AI 가 쓴 문장은 보지 않는다.
  5. 남은 것 가운데 번호가 가장 작은 이슈 하나.
명시적 수동 실행 (--issue N) 은 사용자가 재시도를 지정한 것으로 보고 4 를 건너뛴다. 1·2·3 은 그대로 적용한다.
조회 상한을 넘거나 목록이 잘려 판정할 수 없으면 작업을 시작하지 않는다 (종료 코드 1).

하위 명령:
  select       작업 하나를 고른다. --dry-run 은 이유만 출력한다 (어차피 읽기 전용이다).
  record-body  시도 기록 댓글 본문 (고정 표식 포함) 을 출력한다.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

LABEL = "lemma-hunt"
RESEARCH_PREFIX = "claude/hunt-"
MAX_OPEN_RESEARCH_PRS = 2
ISSUE_LIMIT = 50
PR_LIMIT = 200
COMMENT_LIMIT = 100
LABEL_LIMIT = 20
BOT_LOGINS = {"github-actions", "github-actions[bot]", "app/github-actions"}
OUTCOMES = ("started", "pr", "failure", "error")
ATTEMPT_RE = re.compile(
    r"<!-- lemma-hunt-attempt: v1 task=([0-9a-f]{64}) base=([0-9a-f]{40}) "
    r"outcome=(started|pr|failure|error) run=(\d+)\.(\d+) -->")


class SelectError(Exception):
    """판정할 수 없다 (상한 초과, 목록 잘림, 이슈 없음). 작업을 시작하지 않는다."""


def task_hash(body: Optional[str]) -> str:
    return hashlib.sha256((body or "").strip().encode("utf-8")).hexdigest()


def attempt_marker(task: str, base: str, outcome: str, run: str) -> str:
    if outcome not in OUTCOMES or not re.fullmatch(r"[0-9a-f]{64}", task) or not re.fullmatch(r"[0-9a-f]{40}", base) \
            or not re.fullmatch(r"\d+\.\d+", run):
        raise ValueError("시도 기록 값이 형식에 맞지 않는다")
    return f"<!-- lemma-hunt-attempt: v1 task={task} base={base} outcome={outcome} run={run} -->"


def links_issue(body: Optional[str], number: int) -> bool:
    return re.search(rf"(?<![\w#])(?:Refs|Closes|Fixes|Resolves) #{number}(?!\d)", body or "", re.IGNORECASE) is not None


def _login(node: Optional[dict]) -> str:
    return ((node or {}).get("login") or "")


def trusted(issue: dict, owner: str) -> Tuple[bool, str]:
    labels = issue.get("labels") or {}
    names = {l.get("name") for l in labels.get("nodes") or []}
    if (labels.get("totalCount") or 0) > LABEL_LIMIT and LABEL not in names:
        raise SelectError(f"#{issue['number']} 의 라벨이 {LABEL_LIMIT} 개를 넘어 확인할 수 없다")
    if (issue.get("state") or "").upper() != "OPEN":
        return False, "열린 이슈가 아님"
    if LABEL not in names:
        return False, f"{LABEL} 라벨 없음"
    if _login(issue.get("author")) != owner:
        return False, "소유자가 쓴 이슈가 아님"
    editor = issue.get("editor")
    if editor is not None and _login(editor) != owner:
        return False, f"본문을 소유자가 아닌 {_login(editor) or '?'} 가 고침"
    return True, ""


def attempts(issue: dict) -> List[Dict[str, str]]:
    """github-actions 봇 댓글의 고정 표식에서 시도 기록을 읽는다. 댓글이 잘렸으면 SelectError."""
    comments = issue.get("comments") or {}
    nodes = comments.get("nodes") or []
    total = comments.get("totalCount")
    if total is None or total > COMMENT_LIMIT or len(nodes) != total:
        raise SelectError(f"#{issue['number']} 의 댓글 {total} 개를 모두 읽지 못해 시도 기록을 판정할 수 없다")
    out = []
    for c in nodes:
        if _login(c.get("author")) not in BOT_LOGINS:
            continue
        for m in ATTEMPT_RE.finditer(c.get("body") or ""):
            out.append({"task": m.group(1), "base": m.group(2), "outcome": m.group(3),
                        "run": f"{m.group(4)}.{m.group(5)}"})
    return out


def linked_research_prs(number: int, prs: List[dict]) -> List[dict]:
    return [p for p in prs
            if (p.get("headRefName") or "").startswith(RESEARCH_PREFIX)
            and (p.get("state") or "").upper() in ("OPEN", "MERGED")
            and links_issue(p.get("body"), number)]


def select(issues: List[dict], prs: List[dict], owner: str, base: str,
           explicit: Optional[int] = None) -> Dict[str, Any]:
    """결정적 선택. 반환: {"issue": 번호 또는 None, "task_hash", "body", "reasons": [문장]}."""
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        raise SelectError("기준 main SHA 가 40 자리 16 진수가 아니다")
    reasons: List[str] = []
    open_research = sorted(p["number"] for p in prs
                           if (p.get("headRefName") or "").startswith(RESEARCH_PREFIX)
                           and (p.get("state") or "").upper() == "OPEN")
    if len(open_research) >= MAX_OPEN_RESEARCH_PRS:
        reasons.append(f"열린 연구 PR 이 {len(open_research)} 개 ({open_research}) 라 새 작업을 시작하지 않음")
        return {"issue": None, "reasons": reasons}
    candidates = sorted(issues, key=lambda i: i["number"])
    if explicit is not None:
        candidates = [i for i in candidates if i["number"] == explicit]
        if not candidates:
            raise SelectError(f"#{explicit} 를 찾지 못했다")
    for issue in candidates:
        n = issue["number"]
        ok, why = trusted(issue, owner)
        if not ok:
            reasons.append(f"#{n} 건너뜀: {why}")
            continue
        linked = linked_research_prs(n, prs)
        if linked:
            desc = ", ".join(f"#{p['number']} ({(p.get('state') or '').lower()})" for p in linked)
            reasons.append(f"#{n} 건너뜀: 연결된 연구 PR {desc}")
            continue
        h = task_hash(issue.get("body"))
        same = [a for a in attempts(issue) if a["task"] == h and a["base"] == base]
        if same and explicit is None:
            reasons.append(f"#{n} 건너뜀: 같은 본문·기준 main 으로 이미 시작함 (run {same[-1]['run']}, {same[-1]['outcome']})")
            continue
        if same:
            reasons.append(f"#{n}: 같은 조건의 이전 시도가 있지만 명시적 수동 실행이라 다시 시도")
        reasons.append(f"#{n} 선택")
        return {"issue": n, "task_hash": h, "body": issue.get("body") or "", "reasons": reasons}
    reasons.append("고를 작업 없음")
    return {"issue": None, "reasons": reasons}


# ---------------------------------------------------------------- GitHub 읽기 (gh CLI)

ISSUE_FIELDS = ("number body state author{login} editor{login} "
                f"labels(first:{LABEL_LIMIT}){{totalCount nodes{{name}}}} "
                f"comments(first:{COMMENT_LIMIT}){{totalCount nodes{{author{{login}} body}}}}")

Runner = Callable[[List[str]], str]


def _gh(args: List[str]) -> str:
    res = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if res.returncode != 0:
        raise SelectError(f"gh {' '.join(args[:2])} 실패: {res.stderr.strip()[:300]}")
    return res.stdout


def fetch(repo: str, explicit: Optional[int], run: Runner = _gh) -> Tuple[List[dict], List[dict]]:
    owner, name = repo.split("/", 1)
    if explicit is None:
        query = ("query($o:String!,$r:String!){repository(owner:$o,name:$r){"
                 f"issues(first:{ISSUE_LIMIT + 1},states:OPEN,labels:[\"{LABEL}\"],"
                 f"orderBy:{{field:CREATED_AT,direction:ASC}}){{totalCount nodes{{{ISSUE_FIELDS}}}}}}}}}")
        data = json.loads(run(["api", "graphql", "-F", f"o={owner}", "-F", f"r={name}", "-f", f"query={query}"]))
        conn = data["data"]["repository"]["issues"]
        if conn["totalCount"] > ISSUE_LIMIT or len(conn["nodes"]) != conn["totalCount"]:
            raise SelectError(f"열린 {LABEL} 이슈 {conn['totalCount']} 개를 모두 읽지 못했다 (상한 {ISSUE_LIMIT})")
        issues = conn["nodes"]
    else:
        query = ("query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){"
                 f"issue(number:$n){{{ISSUE_FIELDS}}}}}}}")
        data = json.loads(run(["api", "graphql", "-F", f"o={owner}", "-F", f"r={name}", "-F", f"n={explicit}",
                               "-f", f"query={query}"]))
        issue = data["data"]["repository"]["issue"]
        issues = [issue] if issue else []
    prs = json.loads(run(["pr", "list", "-R", repo, "--state", "all", "--limit", str(PR_LIMIT + 1),
                          "--json", "number,headRefName,state,isDraft,body"]))
    if len(prs) > PR_LIMIT:
        raise SelectError(f"PR 이 {PR_LIMIT} 개를 넘어 연결 여부를 모두 판정할 수 없다")
    return issues, prs


# ---------------------------------------------------------------- CLI

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--repo", required=True)
    s.add_argument("--owner", required=True)
    s.add_argument("--base", required=True, help="기준 main 커밋 SHA (40 자리)")
    s.add_argument("--issue", default="", help="명시적 수동 실행의 이슈 번호 (비우면 예약 규칙)")
    s.add_argument("--task-out")
    s.add_argument("--github-output")
    s.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("record-body")
    r.add_argument("--task", required=True)
    r.add_argument("--base", required=True)
    r.add_argument("--outcome", required=True)
    r.add_argument("--run", required=True, help="run_id.run_attempt")
    r.add_argument("--run-url", default="")
    args = ap.parse_args(argv)

    if args.cmd == "record-body":
        marker = attempt_marker(args.task, args.base, args.outcome, args.run)
        print(f"자동 사냥 시작 기록 ({args.outcome}): 기준 main {args.base[:7]}, [실행]({args.run_url}).\n"
              f"결과는 같은 실행의 PR 이나 실패 보고로 확인한다. 같은 본문·같은 기준으로는 예약 실행이 다시 고르지 않는다\n"
              f"(이슈 본문을 고치거나 main 이 바뀌면 다시 고를 수 있고, 수동 실행은 언제든 가능하다).\n\n{marker}")
        return 0

    explicit: Optional[int] = None
    if args.issue.strip():
        if not args.issue.strip().isdigit():
            print("::error::이슈 번호가 숫자가 아니다")
            return 1
        explicit = int(args.issue.strip())
    try:
        issues, prs = fetch(args.repo, explicit)
        result = select(issues, prs, args.owner, args.base, explicit)
    except SelectError as e:
        print(f"::error::작업을 시작하지 않음: {e}")
        return 1
    for line in result["reasons"]:
        print(f"  {line}")
    if args.dry_run:
        return 0
    if result["issue"] is None:
        if explicit is not None:
            print(f"::error::#{explicit} 를 작업으로 고를 수 없다")
            return 1
        return 0
    if args.task_out:
        with open(args.task_out, "w", encoding="utf-8") as f:
            json.dump({"number": result["issue"], "body": result["body"]}, f, ensure_ascii=False)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as f:
            f.write(f"issue={result['issue']}\ntask_hash={result['task_hash']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
