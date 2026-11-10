"""PR triage caller 의 고정·권한·설정·스케줄 시험. 네트워크 호출은 하지 않는다.

실행 로직은 continuous-ai-kit 의 재사용 워크플로 .github/workflows/pr-triage.yml 로 옮겼다.
예전 이 파일이 하던 shell 회귀 시험 (publish 단계의 bash -e 에서 stale 종료 코드 3 을 성공으로 처리) 은
kit 의 tests/test_triage_shell.py 로 이관됐다. 여기서는 이 저장소에 남은 caller 가 고정 SHA·최소 권한·
기존 설정·스케줄·concurrency 를 지키는지만 본다. 롤백용 scripts/pr_triage.py 와 tests/test_pr_triage.py 는 그대로 둔다.
"""
import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CALLER = (ROOT / ".github" / "workflows" / "claude-pr-triage.yml").read_text(encoding="utf-8")
CONFIG_PATH = ".github/continuous-ai/pr-triage.json"
KIT_WORKFLOW = "Maokami/continuous-ai-kit/.github/workflows/pr-triage.yml"


def job_permissions(text):
    lines = text.split("\n    permissions:\n", 1)[1].splitlines()
    out = {}
    for line in lines:
        if not line.startswith("      ") or line.startswith("       ") or ": " not in line:
            break
        key, value = line.strip().split(": ", 1)
        out[key] = value
    return out


class CallerWorkflow(unittest.TestCase):
    def test_kit_is_pinned_by_full_commit_sha(self):
        uses = re.findall(r"(?m)^\s*(?:- )?uses: (\S+)", CALLER)
        self.assertEqual(len(uses), 1, uses)
        target, _, ref = uses[0].partition("@")
        self.assertEqual(target, KIT_WORKFLOW)
        self.assertRegex(ref, r"^[0-9a-f]{40}$",
                         "d17b8cf395a9bc6fc48799850f4d80c72386e767 를 검토한 kit 커밋의 전체 SHA 로 바꿔야 한다")

    def test_least_privilege_and_named_secret(self):
        self.assertIn("\npermissions: {}\n", CALLER)
        self.assertEqual(job_permissions(CALLER), {
            "contents": "read", "pull-requests": "write", "issues": "write",
            "checks": "read", "statuses": "read"})
        self.assertNotIn("id-token", CALLER)
        self.assertNotIn("secrets: inherit", CALLER)
        self.assertRegex(CALLER, r"\n    secrets:\n      claude_oauth_token: \$\{\{ secrets\.CLAUDE_CODE_OAUTH_TOKEN \}\}\n")
        self.assertNotIn("run:", CALLER)  # 실행 단계는 kit 에만 있다

    def test_schedule_dispatch_and_concurrency_are_unchanged(self):
        self.assertIn('    - cron: "17 */2 * * *"', CALLER)
        self.assertRegex(CALLER, r"\n  workflow_dispatch:\n")
        self.assertIn("\nconcurrency:\n  group: claude-pr-triage\n  cancel-in-progress: false\n", CALLER)
        self.assertIn("\n      default_branch: main\n", CALLER)


class TriageConfig(unittest.TestCase):
    def setUp(self):
        self.assertIn(f"\n      config: {CONFIG_PATH}\n", CALLER)
        self.config = json.loads((ROOT / CONFIG_PATH).read_text(encoding="utf-8"))

    def test_config_is_the_previous_default(self):
        self.assertEqual(set(self.config),
                         {"version", "label_namespace", "report_title", "required_checks", "marker_id"})
        self.assertEqual(self.config["version"], 1)
        # 롤백용 원본 스크립트의 상수와 같아야 기존 라벨·보고서 이슈·digest 표식을 그대로 이어 쓴다.
        spec = importlib.util.spec_from_file_location("pr_triage", ROOT / "scripts" / "pr_triage.py")
        assert spec is not None and spec.loader is not None
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        self.assertEqual(self.config["label_namespace"], legacy.PREFIX)
        self.assertEqual(self.config["report_title"], legacy.REPORT_TITLE)
        self.assertEqual(tuple(self.config["required_checks"]), legacy.REQUIRED_CHECKS)
        self.assertEqual(f"<!-- {self.config['marker_id']}-report:v1 -->", legacy.REPORT_MARKER)

    def test_required_check_is_the_ci_job_name(self):
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        names = re.findall(r"(?m)^    name: (.+)$", ci)
        for check in self.config["required_checks"]:
            self.assertIn(check, names, "필수 검사 이름이 CI job 이름과 달라지면 모든 PR 이 unknown 이 된다")


if __name__ == "__main__":
    unittest.main()
