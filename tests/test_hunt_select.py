"""scripts/hunt_select.py 의 fixture 시험. 실행: python3 -I -B -m unittest discover -s tests -v

fixture 는 2026-11-06 상태를 줄인 것이다: 이슈 #1 (소유자 작성, lemma-hunt) 과 그것을 Refs 로 가리키는 열린 연구 PR #4.
"""
import importlib.util
import json
import pathlib
import unittest
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("hunt_select", ROOT / "scripts" / "hunt_select.py")
assert spec is not None and spec.loader is not None
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)

OWNER = "Maokami"
BASE = "6f2607946ec60e25f30614f2febd8b9fa049e4ec"
OTHER_BASE = "4b9bcaf" + "0" * 33


def issue(number, body="과제 본문", author=OWNER, editor=None, state="OPEN", labels=("lemma-hunt",), comments=()):
    return {"number": number, "body": body, "state": state, "author": {"login": author},
            "editor": {"login": editor} if editor else None,
            "labels": {"totalCount": len(labels), "nodes": [{"name": l} for l in labels]},
            "comments": {"totalCount": len(comments), "nodes": list(comments)}}


def comment(author, body):
    return {"author": {"login": author}, "body": body}


def pr(number, head, state="OPEN", body="", draft=True):
    return {"number": number, "headRefName": head, "state": state, "isDraft": draft, "body": body}


def bot_attempt(body_text, base=BASE, outcome="failure", run="42.1"):
    return comment("github-actions", "기록\n" + H.attempt_marker(H.task_hash(body_text), base, outcome, run))


DEPENDABOT = [pr(2, "dependabot/github_actions/actions/checkout-7.0.1", draft=False),
              pr(3, "dependabot/github_actions/jlumbroso/free-disk-space-2.0.0", draft=False)]
HUNT_4 = pr(4, "claude/hunt-q1-two-it-all", body="Refs #1\n\n형식화 …\n[sw-done:42192527645.1]", draft=False)


class CurrentState(unittest.TestCase):
    def test_issue_1_is_skipped_because_of_open_pr_4(self):
        r = H.select([issue(1, comments=[comment("Maokami", "@claude …"), comment("claude", "답")])],
                     DEPENDABOT + [HUNT_4], OWNER, BASE)
        self.assertIsNone(r["issue"])
        self.assertIn("#1 건너뜀: 연결된 연구 PR #4 (open)", r["reasons"])

    def test_explicit_dispatch_keeps_the_duplicate_rule(self):
        r = H.select([issue(1)], DEPENDABOT + [HUNT_4], OWNER, BASE, explicit=1)
        self.assertIsNone(r["issue"])


class Linking(unittest.TestCase):
    def test_merged_pr_blocks_and_closed_unmerged_does_not(self):
        merged = pr(4, "claude/hunt-x", state="MERGED", body="Refs #1")
        closed = pr(4, "claude/hunt-x", state="CLOSED", body="Refs #1")
        self.assertIsNone(H.select([issue(1)], [merged], OWNER, BASE)["issue"])
        self.assertEqual(H.select([issue(1)], [closed], OWNER, BASE)["issue"], 1)

    def test_number_boundaries_and_keywords(self):
        self.assertFalse(H.links_issue("Refs #10", 1))
        self.assertFalse(H.links_issue("Refs ##1", 1))
        self.assertTrue(H.links_issue("Refs #1.", 1))
        self.assertTrue(H.links_issue("closes #1", 1))
        self.assertFalse(H.links_issue("see #1", 1))

    def test_only_research_branches_count(self):
        owner_pr = pr(9, "feature/x", body="Refs #1")
        self.assertEqual(H.select([issue(1)], [owner_pr], OWNER, BASE)["issue"], 1)


class Backlog(unittest.TestCase):
    def test_two_open_research_prs_stop_new_work(self):
        prs = [pr(4, "claude/hunt-a", body="Refs #7"), pr(5, "claude/hunt-b", draft=False, body="Refs #8")]
        for explicit in (None, 1):
            r = H.select([issue(1)], prs, OWNER, BASE, explicit=explicit)
            self.assertIsNone(r["issue"], explicit)
            self.assertIn("열린 연구 PR 이 2 개", r["reasons"][0])

    def test_one_open_research_pr_still_allows_other_issue(self):
        r = H.select([issue(1), issue(2)], [HUNT_4], OWNER, BASE)
        self.assertEqual(r["issue"], 2)


class Attempts(unittest.TestCase):
    def test_same_task_and_base_is_not_repeated_by_schedule(self):
        i = issue(1, body="과제", comments=[bot_attempt("과제")])
        self.assertIsNone(H.select([i], [], OWNER, BASE)["issue"])

    def test_started_record_blocks_even_without_outcome(self):
        # 시간 초과·취소로 결과 기록 없이 끝나도 시작 기록만으로 같은 조건의 예약 재선택을 막는다.
        i = issue(1, body="과제", comments=[bot_attempt("과제", outcome="started")])
        self.assertIsNone(H.select([i], [], OWNER, BASE)["issue"])
        self.assertEqual(H.select([i], [], OWNER, BASE, explicit=1)["issue"], 1)

    def test_any_outcome_blocks_including_closed_pr(self):
        i = issue(1, body="과제", comments=[bot_attempt("과제", outcome="pr")])
        self.assertIsNone(H.select([i], [pr(4, "claude/hunt-x", state="CLOSED", body="Refs #1")], OWNER, BASE)["issue"])

    def test_explicit_dispatch_retries(self):
        i = issue(1, body="과제", comments=[bot_attempt("과제")])
        r = H.select([i], [], OWNER, BASE, explicit=1)
        self.assertEqual(r["issue"], 1)
        self.assertTrue(any("명시적 수동 실행" in x for x in r["reasons"]))

    def test_new_base_alone_does_not_retry_but_owner_strategy_edit_does(self):
        self.assertIsNone(H.select([issue(1, body="과제", comments=[bot_attempt("과제", base=OTHER_BASE)])],
                                   [], OWNER, BASE)["issue"])
        self.assertEqual(H.select([issue(1, body="고친 과제", comments=[bot_attempt("과제")])],
                                  [], OWNER, BASE)["issue"], 1)

    def test_markers_from_others_are_ignored(self):
        forged = [comment("someone", "x " + H.attempt_marker(H.task_hash("과제"), BASE, "failure", "1.1")),
                  comment("claude", H.attempt_marker(H.task_hash("과제"), BASE, "failure", "2.1"))]
        self.assertEqual(H.select([issue(1, body="과제", comments=forged)], [], OWNER, BASE)["issue"], 1)

    def test_marker_round_trip_and_validation(self):
        i = issue(1, comments=[bot_attempt("과제", outcome="error", run="77.2")])
        self.assertEqual(H.attempts(i), [{"task": H.task_hash("과제"), "base": BASE, "outcome": "error", "run": "77.2"}])
        for bad in [("x" * 64, BASE, "failure", "1.1"), (H.task_hash("a"), "abc", "failure", "1.1"),
                    (H.task_hash("a"), BASE, "maybe", "1.1"), (H.task_hash("a"), BASE, "failure", "1")]:
            with self.assertRaises(ValueError):
                H.attempt_marker(*bad)


class Trust(unittest.TestCase):
    def test_untrusted_issues_are_skipped(self):
        cases = {"작성자": issue(1, author="someone"), "편집자": issue(1, editor="someone"),
                 "닫힘": issue(1, state="CLOSED"), "라벨": issue(1, labels=("other",))}
        for name, i in cases.items():
            self.assertIsNone(H.select([i], [], OWNER, BASE)["issue"], name)
        self.assertEqual(H.select([issue(1, editor=OWNER)], [], OWNER, BASE)["issue"], 1)

    def test_lowest_eligible_number_wins(self):
        r = H.select([issue(5), issue(3, author="someone"), issue(4)], [], OWNER, BASE)
        self.assertEqual(r["issue"], 4)


class Incomplete(unittest.TestCase):
    def test_truncated_comments_stop_selection(self):
        i = issue(1, comments=[comment("x", "y")])
        i["comments"]["totalCount"] = 150
        with self.assertRaises(H.SelectError):
            H.select([i], [], OWNER, BASE)

    def test_explicit_issue_not_found(self):
        with self.assertRaises(H.SelectError):
            H.select([], [], OWNER, BASE, explicit=1)

    def test_bad_base_sha(self):
        with self.assertRaises(H.SelectError):
            H.select([issue(1)], [], OWNER, "main")

    def fetch_with(self, issues_total: int, n_nodes: int, n_prs: int, explicit: Optional[int] = None):
        def run(args):
            if args[:2] == ["api", "graphql"]:
                nodes = [issue(k) for k in range(1, n_nodes + 1)]
                if explicit is not None:
                    return json.dumps({"data": {"repository": {"issue": nodes[0] if nodes else None}}})
                return json.dumps({"data": {"repository": {"issues": {"totalCount": issues_total, "nodes": nodes}}}})
            if args[:2] == ["pr", "list"]:
                self.assertIn(str(H.PR_LIMIT + 1), args)
                return json.dumps([pr(k, "x") for k in range(n_prs)])
            raise AssertionError(args)
        return H.fetch("o/r", explicit, run)

    def test_fetch_limits(self):
        issues, prs = self.fetch_with(2, 2, 3)
        self.assertEqual((len(issues), len(prs)), (2, 3))
        with self.assertRaises(H.SelectError):
            self.fetch_with(H.ISSUE_LIMIT + 1, H.ISSUE_LIMIT + 1, 0)
        with self.assertRaises(H.SelectError):
            self.fetch_with(3, 2, 0)  # totalCount 와 실제 노드 수가 다름
        with self.assertRaises(H.SelectError):
            self.fetch_with(1, 1, H.PR_LIMIT + 1)


if __name__ == "__main__":
    unittest.main()
