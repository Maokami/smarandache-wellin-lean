"""연구 제안의 권한 경계, 중복·stale·잘린 조회·구조화 출력 계약 시험."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("research_planner", ROOT / "scripts/research_planner.py")
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)
BASE = "a" * 40
REPO = "Maokami/smarandache-wellin-lean"


def issue(number=1, label="lemma-hunt", author="Maokami", body="고정 과제", state="OPEN"):
    return {"number": number, "title": f"기존 과제 {number}", "body": body, "state": state,
            "labels": [{"name": label}], "author": {"login": author}}


def proposal():
    return {"notes": "일반 Q1은 IOR-all 조건부이며 소수성 연결은 미해결이다.",
            "sources": [{"url": "https://github.com/Maokami/example/blob/main/README.md", "checked": "정리의 가정"}],
            "candidates": [{"title": "다음 과제", "kind": "formalization", "statement": "정확한 진술",
                            "assumptions": ["IntervalOneRunsAll"], "dependencies": ["SW.W"],
                            "bottleneck": "미해결 연결", "done_when": "CI 통과와 독립 검토",
                            "stop_when": "가정 부족이면 중단, 새 전략이 있을 때 재시도"}]}


class FixtureGH:
    repo = REPO

    def __init__(self):
        self.sha, self.records, self.pulls, self.notes, self.writes = BASE, [issue()], [], [], []

    def main_sha(self):
        return self.sha

    def issues(self):
        return copy.deepcopy(self.records)

    def prs(self):
        return copy.deepcopy(self.pulls)

    def comments(self, number):
        return copy.deepcopy(self.notes)

    def write_report(self, number, body):
        self.writes.append((number, body))
        return "published"


class Collection(unittest.TestCase):
    def test_multiline_contracts_and_failures_remain_readable_to_the_model(self):
        gh = FixtureGH()
        body = "목표\n```lean\n정확한 계약\n```\n가정과 범위"
        gh.records[0]["body"] = body
        gh.notes = [{"user": {"login": "claude[bot]"}, "body": "실패 원인\n다음 전략"}]
        gh.pulls = [{"number": 4, "headRefName": "claude/hunt-x", "state": "CLOSED", "body": body}]
        snapshot = P.collect(gh, BASE)
        self.assertEqual(snapshot["issues"][0]["body_lines"], body.splitlines())
        self.assertEqual(snapshot["issues"][0]["comments"][0]["body_lines"], ["실패 원인", "다음 전략"])
        self.assertEqual(snapshot["prs"][0]["body_lines"], body.splitlines())

    def test_only_research_inputs_and_changes_trigger_ai(self):
        gh = FixtureGH()
        first = P.collect(gh, BASE)
        self.assertTrue(first["should_plan"])
        gh.records += [issue(9, P.LABEL, "github-actions", P.MARKER + "\n" +
                             f"<!-- research-plan-input: {first['digest']} -->"), issue(10, "unrelated")]
        second = P.collect(gh, BASE)
        self.assertEqual(first["digest"], second["digest"])
        self.assertFalse(second["should_plan"])
        gh.notes.append({"user": {"login": "claude[bot]"}, "body": "시도 실패 [sw-done:1.1]"})
        self.assertTrue(P.collect(gh, BASE)["should_plan"])

    def test_context_cap_counts_the_readable_serialization(self):
        gh = FixtureGH()
        gh.records[0]["body"] = "\n" * 15000
        with self.assertRaises(P.PlannerError):
            P.collect(gh, BASE)

    def test_untrusted_or_duplicate_report_is_never_overwritten(self):
        for records in ([issue(9, P.LABEL, "outsider", P.MARKER)],
                        [issue(9, P.LABEL, "github-actions", "표식 없음")],
                        [issue(9, P.LABEL, "github-actions", P.MARKER),
                         issue(10, P.LABEL, "github-actions", P.MARKER)]):
            with self.subTest(records=records):
                gh = FixtureGH()
                gh.records = records
                with self.assertRaises(P.PlannerError):
                    P.collect(gh, BASE)
                self.assertEqual(gh.writes, [])

    def test_truncated_lists_fail_closed(self):
        for name, value in (("records", [issue()] * 101), ("pulls", [{}] * 201),
                            ("notes", [{}] * 100)):
            with self.subTest(name=name):
                gh = FixtureGH()
                setattr(gh, name, value)
                with self.assertRaises(P.PlannerError):
                    P.collect(gh, BASE)

    def test_review_backlog_stops_new_ai_work(self):
        gh = FixtureGH()
        gh.pulls = [{"number": n, "headRefName": "claude/hunt-x", "state": "OPEN"} for n in (4, 5)]
        self.assertFalse(P.collect(gh, BASE)["should_plan"])
        gh.pulls[1]["headRefName"] = "dependabot/x"
        self.assertTrue(P.collect(gh, BASE)["should_plan"])

    def test_main_change_and_api_failure_do_not_publish(self):
        gh = FixtureGH()
        gh.sha = "b" * 40
        with self.assertRaises(P.Stale):
            P.collect(gh, BASE)
        with patch.object(gh, "main_sha", side_effect=P.PlannerError("API 실패")):
            with self.assertRaises(P.PlannerError):
                P.collect(gh, BASE)


class Validation(unittest.TestCase):
    def setUp(self):
        self.snapshot = P.collect(FixtureGH(), BASE)

    def test_empty_candidate_list_is_an_honest_valid_result(self):
        ai = proposal()
        ai["candidates"] = []
        P.validate(ai, self.snapshot)

    def test_malformed_or_duplicate_candidates_are_rejected(self):
        cases = [None, {}, dict(proposal(), extra=True)]
        for field, bad in (("kind", "approved"), ("assumptions", "묵시적 가정"),
                           ("statement", "  "), ("title", "기존 과제 1"), ("done_when", "x" * 1501)):
            ai = proposal()
            ai["candidates"][0][field] = bad
            cases.append(ai)
        ai = proposal()
        ai["candidates"] *= 4
        cases.append(ai)
        ai = proposal()
        ai["candidates"] *= 2
        cases.append(ai)
        for ai in cases:
            with self.subTest(ai=ai):
                with self.assertRaises(P.PlannerError):
                    P.validate(ai, self.snapshot)

    def test_non_primary_or_injected_source_urls_are_rejected(self):
        for url in ("https://example.com/paper", "http://arxiv.org/abs/1", "https://user@github.com/x",
                    "https://github.com/x> @all", "https://github.com.evil.example/x"):
            ai = proposal()
            ai["sources"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(P.PlannerError):
                P.validate(ai, self.snapshot)


class Publishing(unittest.TestCase):
    def test_combined_and_escaped_body_limit_is_checked_before_any_write(self):
        gh = FixtureGH()
        snapshot = P.collect(gh, BASE)
        ai = proposal()
        ai["notes"] = "가" * 6000
        ai["sources"] = [{"url": f"https://arxiv.org/abs/{n}", "checked": "가" * 1200} for n in range(8)]
        ai["candidates"] = []
        for n in range(3):
            candidate = proposal()["candidates"][0]
            candidate["title"] = f"새 과제 {n}"
            candidate["statement"] = "가" * 3000
            ai["candidates"].append(candidate)
        P.validate(ai, snapshot)  # 필드별 상한은 만족해도 전체 게시 본문은 넘을 수 있다.
        with self.assertRaises(P.PlannerError):
            P.publish(gh, snapshot, ai, "https://github.com/run", "오늘")
        self.assertEqual(gh.writes, [])

    def test_changes_after_ai_and_target_race_are_stale_without_writes(self):
        for change in ("main", "issue", "report"):
            gh = FixtureGH()
            snapshot = P.collect(gh, BASE)
            if change == "main":
                gh.sha = "b" * 40
            elif change == "issue":
                gh.records[0]["body"] = "수정된 과제"
            else:
                gh.records.append(issue(9, P.LABEL, "github-actions", P.MARKER))
            with self.subTest(change=change), self.assertRaises(P.Stale):
                P.publish(gh, snapshot, proposal(), "https://github.com/run", "오늘")
            self.assertEqual(gh.writes, [])

    def test_success_is_a_report_only_and_unchanged_result_is_no_op(self):
        gh = FixtureGH()
        snapshot = P.collect(gh, BASE)
        ai = proposal()
        ai["notes"] += " @all <script> [명령](https://evil.example)"
        self.assertEqual(P.publish(gh, snapshot, ai, "https://github.com/run", "오늘"), "published")
        number, body = gh.writes[0]
        self.assertIsNone(number)
        self.assertIn(P.MARKER, body)
        self.assertNotIn("@all", body)
        self.assertNotIn("<script>", body)
        self.assertIn("검토 전 제안", body)
        gh.records.append(issue(9, P.LABEL, "github-actions", body))
        self.assertEqual(P.publish(gh, P.collect(gh, BASE), ai, "https://github.com/run", "내일"),
                         "unchanged-or-backlog")
        self.assertEqual(len(gh.writes), 1)

    def test_transport_keeps_model_text_out_of_commands(self):
        gh = P.GH(REPO)
        payload = {"body": "$(touch /tmp/never-run) `id`\n다음 줄"}
        with patch.object(P.subprocess, "run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = "{}"
            gh.call(["api", "-X", "PATCH", "repos/example/issues/9", "--input", "-"], payload)
            args, kwargs = run.call_args
            self.assertNotIn(payload["body"], args[0])
            self.assertEqual(json.loads(kwargs["input"]), payload)
            self.assertNotIn("shell", kwargs)


class WorkflowBoundary(unittest.TestCase):
    def test_read_only_model_and_separate_non_ai_publisher(self):
        workflow = (ROOT / ".github/workflows/claude-research-planner.yml").read_text(encoding="utf-8")
        propose, publish = workflow.split("\n  publish:\n")
        self.assertIn("\npermissions: {}\n", propose)
        self.assertNotIn("issues: write", propose)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("issues: write", publish)
        self.assertNotIn("claude-code-action", publish)
        self.assertNotIn("CLAUDE_CODE_OAUTH_TOKEN", publish)
        self.assertIn("additional_permissions: |\n            contents: read\n            pull_requests: read\n            issues: read", propose)
        self.assertIn("--disallowedTools \"Bash,Edit,MultiEdit,Write", propose)
        self.assertIn("steps.collect.outputs.should_plan == 'true'", propose)
        self.assertIn("--max-turns 15", propose)
        self.assertIn('cron: "7 0 * * *"', propose)
        for ref in re.findall(r"uses: \S+@(\S+)", workflow):
            self.assertRegex(ref, r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
