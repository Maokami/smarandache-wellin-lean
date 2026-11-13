#!/usr/bin/env python3
"""일일 연구 과제 제안의 수집·검증·게시. 후보는 실행 권한을 얻지 않는다.

AI는 읽기만 한다. publish는 입력을 다시 모아 낡은 결과를 거부하고, 봇 소유의
research-plan/report 이슈 하나만 갱신한다. 수학 과제 생성·승인·병합은 하지 않는다.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

LABEL = "research-plan/report"
TITLE = "연구 과제 제안 (자동)"
MARKER = "<!-- research-plan-report:v1 -->"
DIGEST = re.compile(r"<!-- research-plan-input: ([0-9a-f]{64}) -->")
RESEARCH_LABELS = {"lemma-hunt", "research-audit", "lit-watch"}
BOTS = {"github-actions[bot]", "github-actions", "app/github-actions"}
SOURCE_HOSTS = {"github.com", "raw.githubusercontent.com", "arxiv.org", "export.arxiv.org",
                "doi.org", "oeis.org", "zbmath.org", "leanprover-community.github.io",
                "primegaps.axiommath.ai"}
ISSUE_LIMIT, PR_LIMIT, COMMENT_LIMIT = 100, 200, 100


class PlannerError(ValueError):
    pass


class Stale(PlannerError):
    pass


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def text(value, name, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise PlannerError(f"{name}: 비어 있거나 길이가 상한 {limit}을 넘는다")
    return value.strip()


class GH:
    def __init__(self, repo, dry_run=False):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise PlannerError("저장소는 owner/name 형식이어야 한다")
        self.repo, self.dry_run = repo, dry_run

    def call(self, args, payload=None):
        result = subprocess.run(["gh"] + args, capture_output=True, text=True,
                                input=json.dumps(payload, ensure_ascii=False) if payload is not None else None)
        if result.returncode:
            raise PlannerError(f"GitHub 조회/게시 실패: {result.stderr.strip()[:200]}")
        return json.loads(result.stdout)

    def main_sha(self):
        return self.call(["api", f"repos/{self.repo}/git/ref/heads/main"])["object"]["sha"]

    def issues(self):
        return self.call(["issue", "list", "-R", self.repo, "--state", "all", "--limit", str(ISSUE_LIMIT + 1),
                          "--json", "number,title,body,state,labels,author"])

    def prs(self):
        return self.call(["pr", "list", "-R", self.repo, "--state", "all", "--limit", str(PR_LIMIT + 1),
                          "--json", "number,title,body,state,headRefName,headRefOid,isDraft"])

    def comments(self, number):
        # 상한과 같아도 다음 페이지가 없다고 단정하지 않는다.
        return self.call(["api", f"repos/{self.repo}/issues/{number}/comments?per_page={COMMENT_LIMIT}"])

    def write_report(self, number, body):
        if self.dry_run:
            return "dry-run"
        endpoint = f"repos/{self.repo}/issues"
        if number is not None:
            self.call(["api", "-X", "PATCH", f"{endpoint}/{number}", "--input", "-"], {"body": body})
            return f"updated #{number}"
        # 전용 라벨만 만들며 이미 존재하는 라벨의 속성은 덮어쓰지 않는다.
        labels = self.call(["api", f"repos/{self.repo}/labels?per_page=100"])
        if len(labels) >= 100:
            raise PlannerError("라벨 목록이 잘렸을 수 있어 게시하지 않는다")
        if not any(item["name"] == LABEL for item in labels):
            self.call(["api", "-X", "POST", f"repos/{self.repo}/labels", "--input", "-"],
                      {"name": LABEL, "color": "0052cc", "description": "검토 전 연구 후보 보고서 (실행 큐 아님)"})
        result = self.call(["api", "-X", "POST", endpoint, "--input", "-"],
                           {"title": TITLE, "body": body, "labels": [LABEL]})
        return f"created #{result['number']}"


def collect(gh, base):
    if not re.fullmatch(r"[0-9a-f]{40}", base) or gh.main_sha() != base:
        raise Stale("실행 기준이 현재 main과 다르다")
    issues, prs = gh.issues(), gh.prs()
    if len(issues) > ISSUE_LIMIT or len(prs) > PR_LIMIT:
        raise PlannerError("이슈/PR 조회 상한을 넘어 전체 상태를 확인하지 못했다")
    reports, research = [], []
    for issue in sorted(issues, key=lambda item: item["number"]):
        labels = sorted(item["name"] for item in issue["labels"])
        if LABEL in labels and issue["state"].upper() == "OPEN":
            if issue["author"]["login"] not in BOTS or MARKER not in (issue["body"] or ""):
                raise PlannerError("연구 보고서 라벨이 봇 소유 보고서가 아닌 이슈에 있다")
            reports.append(issue)
        if not RESEARCH_LABELS.intersection(labels):
            continue
        comments = gh.comments(issue["number"])
        if len(comments) >= COMMENT_LIMIT:
            raise PlannerError(f"#{issue['number']} 댓글 목록이 잘렸을 수 있다")
        research.append({"number": issue["number"], "title": issue["title"], "body": issue["body"],
                         "state": issue["state"], "labels": labels, "author": issue["author"]["login"],
                         "comments": [{"author": c["user"]["login"], "body": c["body"]} for c in comments]})
    if len(reports) > 1:
        raise PlannerError("봇 소유 연구 보고서가 여러 개다")
    report = reports[0] if reports else None
    research_prs = sorted((p for p in prs if p["headRefName"].startswith("claude/hunt-")),
                          key=lambda item: item["number"])
    facts = {"version": 1, "repo": gh.repo, "base_sha": base, "issues": research, "prs": research_prs}
    if len(json.dumps(facts, ensure_ascii=False).encode("utf-8")) > 120000:
        raise PlannerError("연구 입력이 120 KB를 넘는다. 기록을 정리해야 한다")
    previous = DIGEST.search(report["body"]) if report else None
    snapshot = dict(facts, digest=digest(facts), report_number=report["number"] if report else None,
                    previous_digest=previous.group(1) if previous else None)
    backlog = sum(p["state"].upper() == "OPEN" for p in research_prs)
    snapshot["should_plan"] = backlog < 2 and snapshot["digest"] != snapshot["previous_digest"]
    return snapshot


def validate(ai, snapshot):
    if not isinstance(ai, dict) or set(ai) != {"notes", "sources", "candidates"}:
        raise PlannerError("제안 출력의 필드가 notes/sources/candidates와 다르다")
    text(ai["notes"], "notes", 6000)
    if not isinstance(ai["sources"], list) or not 1 <= len(ai["sources"]) <= 8:
        raise PlannerError("확인한 출처가 1~8개여야 한다")
    for source in ai["sources"]:
        if not isinstance(source, dict) or set(source) != {"url", "checked"}:
            raise PlannerError("출처 필드가 url/checked와 다르다")
        raw_url = text(source["url"], "url", 1000)
        url = urlparse(raw_url)
        if url.scheme != "https" or url.hostname not in SOURCE_HOSTS or url.username or url.password:
            raise PlannerError("허용된 1차 출처 HTTPS 주소가 아니다")
        if any(c.isspace() for c in raw_url) or re.search(r"[<>`\\]", raw_url):
            raise PlannerError("출처 주소에 공백/제어 표기가 있다")
        text(source["checked"], "checked", 1200)
    candidates = ai["candidates"]
    if not isinstance(candidates, list) or len(candidates) > 3:
        raise PlannerError("후보는 0~3개여야 한다")
    titles = {item["title"].strip() for item in snapshot["issues"]}
    fields = {"title", "kind", "statement", "assumptions", "dependencies", "bottleneck", "done_when", "stop_when"}
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != fields:
            raise PlannerError("후보 필드가 계약과 다르다")
        title = text(candidate["title"], "title", 160)
        if title in titles:
            raise PlannerError("이미 있는 과제 또는 같은 출력의 중복 제목이다")
        titles.add(title)
        if candidate["kind"] not in ("formalization", "literature", "obstruction"):
            raise PlannerError("알 수 없는 후보 유형이다")
        for name, limit in (("statement", 3000), ("bottleneck", 1200), ("done_when", 1500), ("stop_when", 1500)):
            text(candidate[name], name, limit)
        for name in ("assumptions", "dependencies"):
            values = candidate[name]
            if not isinstance(values, list) or len(values) > 8:
                raise PlannerError(f"{name}는 0~8개 목록이어야 한다")
            for value in values:
                text(value, name, 500)
    return ai


def safe(value):
    # 자료 속 멘션/HTML/Markdown을 게시 명령이나 알림으로 해석하지 않는다.
    escaped = html.escape(str(value)).replace("@", "＠")
    return re.sub(r"([\\`*_{}\[\]()#!|])", r"\\\1", escaped)


def render(snapshot, ai, run_url, now):
    lines = ["> *This was generated by AI during triage.*", "", MARKER,
             f"<!-- research-plan-input: {snapshot['digest']} -->",
             f"기준 main `{snapshot['base_sha']}` · {now} · [실행]({run_url})", "",
             "후보는 검토 전 제안이다. 이 보고서는 증명 상태를 올리거나 실행 과제·PR을 만들지 않는다.",
             "소유자가 진술과 가정을 검토해 작성한 `lemma-hunt` 이슈만 기존 사냥꾼이 실행한다.", "",
             "## 연구 검토", "", safe(ai["notes"]), "", "## 확인한 자료", ""]
    for source in ai["sources"]:
        lines.append(f"- <{source['url']}> — {safe(source['checked'])}")
    lines += ["", f"## 다음 후보 ({len(ai['candidates'])}개)", ""]
    for index, candidate in enumerate(ai["candidates"], 1):
        lines += [f"### {index}. {safe(candidate['title'])}", "", f"유형: {candidate['kind']}", ""]
        for name, label in (("statement", "목표 진술"), ("assumptions", "허용 가정"),
                            ("dependencies", "의존성"), ("bottleneck", "줄일 미해결 고리"),
                            ("done_when", "완료 기준"), ("stop_when", "중단·재시도 기준")):
            value = candidate[name]
            value = "; ".join(value) if isinstance(value, list) else value
            lines += [f"**{label}:** {safe(value or '없음')}", ""]
    body = "\n".join(lines)
    if len(body.encode("utf-8")) > 60000:
        raise PlannerError("이스케이프한 보고서가 60 KB를 넘어 게시하지 않는다")
    return body


def publish(gh, snapshot, ai, run_url, now):
    if snapshot.get("repo") != gh.repo:
        raise PlannerError("스냅샷의 저장소가 다르다")
    current = collect(gh, snapshot["base_sha"])
    if current["digest"] != snapshot["digest"] or current["report_number"] != snapshot["report_number"]:
        raise Stale("수집 이후 main/연구 입력/보고서 대상이 바뀌어 게시하지 않는다")
    if not current["should_plan"]:
        return "unchanged-or-backlog"
    validate(ai, current)
    return gh.write_report(current["report_number"], render(current, ai, run_url, now))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("collect", "validate", "publish"))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--ai")
    parser.add_argument("--github-output")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        gh = GH(args.repo, args.dry_run)
        if args.command == "collect":
            snapshot = collect(gh, args.base or "")
            Path(args.snapshot).write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            if args.github_output:
                with open(args.github_output, "a", encoding="utf-8") as out:
                    out.write(f"should_plan={str(snapshot['should_plan']).lower()}\n")
            print(f"연구 입력 {snapshot['digest'][:12]}, AI 실행 {snapshot['should_plan']}")
        else:
            snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
            ai = json.loads(Path(args.ai).read_text(encoding="utf-8")) if args.ai else None
            if args.command == "validate":
                validate(ai, snapshot)
                print("연구 후보 구조 검사 통과 (수학적 검증 아님)")
            else:
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                print(publish(gh, snapshot, ai, args.run_url, now))
    except Stale as error:
        print(f"::warning::{error}")
        return 3
    except (PlannerError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(f"::error::{error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
