"""실제 publish step을 GitHub runner와 같은 bash -e로 실행한다. 네트워크 호출은 하지 않는다."""
import base64
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


class PublishShellTests(unittest.TestCase):
    def test_publish_exit_codes_under_runner_errexit(self):
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/claude-pr-triage.yml"
        script = textwrap.dedent(workflow.read_text().rsplit("        run: |\n", 1)[1])
        for child_exit, expected in ((0, 0), (3, 0), (7, 7)):
            with self.subTest(child_exit=child_exit), tempfile.TemporaryDirectory() as tmp:
                fake_python = Path(tmp) / "python3"
                fake_python.write_text(f"#!/bin/sh\nexit {child_exit}\n")
                fake_python.chmod(0o755)
                env = dict(os.environ, PATH=tmp + os.pathsep + os.environ["PATH"],
                           RUNNER_TEMP=tmp, SNAPSHOT=base64.b64encode(b"{}").decode(),
                           AI="{}", GITHUB_REPOSITORY="owner/repo", RUN_URL="test-run")
                result = subprocess.run(["bash", "-e", "-c", script], env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                if child_exit == 3:
                    self.assertIn("낡은 스냅샷이라 게시하지 않았다", result.stdout)


if __name__ == "__main__":
    unittest.main()
