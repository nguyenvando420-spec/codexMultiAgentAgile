import contextlib
import importlib.util
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agy_worker.py"
SPEC = importlib.util.spec_from_file_location("agy_worker", SCRIPT)
WORKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORKER)


class AgyWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-worker-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".codex/agents").mkdir(parents=True)
        (self.root / "AGENTS.md").write_text(
            "Keep the documented API contract.\n", encoding="utf-8"
        )
        (self.root / ".codex/agents/developer.toml").write_text(
            'name = "developer"\ndeveloper_instructions = """Implement the task."""\n',
            encoding="utf-8",
        )
        self.task = {
            "schema_version": 1,
            "id": "TASK-001",
            "title": "Implement bounded task",
            "role": "developer",
            "objective": "Read the existing implementation",
            "inputs": ["docs/api.md"],
            "allowed_paths": ["src/**"],
            "acceptance_criteria": ["Existing API behavior is preserved"],
            "dependencies": [],
            "status": "todo",
        }
        self.task_path = self.root / "task.json"
        self.save_task()
        self.result = {
            "task_id": self.task["id"],
            "status": "completed",
            "summary": "Analysis prepared",
            "changed_files": [],
            "checks": [],
            "blockers": [],
        }
        self.fake = self.root / "fake agy"
        self.write_fake("print(" + repr(json.dumps(self.result)) + ")\n")

    def save_task(self):
        self.task_path.write_text(json.dumps(self.task), encoding="utf-8")

    def write_fake(self, body):
        self.fake.write_text("#!" + sys.executable + "\n" + body, encoding="utf-8")
        self.fake.chmod(0o700)

    def call(self, *options):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = WORKER.main(
                [
                    "run",
                    "--project-root",
                    str(self.root),
                    "--task",
                    "task.json",
                    "--agy",
                    str(self.fake),
                    *options,
                ]
            )
        return code, json.loads(stdout.getvalue())

    def test_valid_worker_report_is_not_independent_acceptance(self):
        code, result = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["acceptance_verified"])
        self.assertEqual(json.loads(self.task_path.read_text()), self.task)
        run_dir = Path(result["run_dir"])
        for name in ("prompt.txt", "metadata.json", "stdout.txt", "stderr.txt", "task-result.json"):
            self.assertTrue((run_dir / name).is_file())
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE((run_dir / name).stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(run_dir.stat().st_mode), 0o700)

    def test_dry_run_builds_literal_argv_and_creates_no_run(self):
        self.task["objective"] = "Keep literal $(touch PWNED) and `touch ALSO-PWNED`"
        self.save_task()
        code, result = self.call("--dry-run", "--conversation", "literal;not-a-command")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "dry_run")
        argv = result["argv"]
        self.assertEqual(argv[0], str(self.fake.resolve()))
        self.assertEqual(argv[argv.index("--mode") + 1], "plan")
        self.assertEqual(argv[argv.index("--conversation") + 1], "literal;not-a-command")
        prompt = argv[argv.index("--print") + 1]
        self.assertIn(self.task["objective"], prompt)
        self.assertIn("Keep the documented API contract", prompt)
        self.assertIn("Implement the task", prompt)
        self.assertIn("PLAN ONLY", prompt)
        self.assertIn("--sandbox", argv)
        self.assertFalse(any("skip-permissions" in item for item in argv))
        self.assertFalse((self.root / ".team/runs").exists())
        self.assertFalse((self.root / "PWNED").exists())

    def test_actual_process_receives_literal_argument_without_shell(self):
        self.task["objective"] = "literal $(touch PWNED) `touch ALSO-PWNED`"
        self.save_task()
        self.write_fake(
            "import json, sys\nfrom pathlib import Path\n"
            "Path('argv.json').write_text(json.dumps(sys.argv[1:]))\n"
            "print(" + repr(json.dumps(self.result)) + ")\n"
        )
        code, result = self.call()
        self.assertEqual(code, 0)
        argv = json.loads((self.root / "argv.json").read_text())
        self.assertIn(self.task["objective"], argv[argv.index("--print") + 1])
        self.assertFalse((self.root / "PWNED").exists())
        self.assertFalse((self.root / "ALSO-PWNED").exists())

    def test_unknown_output_is_unverified(self):
        self.write_fake("print('{\"success\": true}')\n")
        code, result = self.call()
        self.assertEqual(code, 3)
        self.assertEqual(result["status"], "unverified")
        self.assertFalse((Path(result["run_dir"]) / "task-result.json").exists())

    def test_known_result_envelope_is_supported(self):
        self.write_fake("print(" + repr(json.dumps({"result": json.dumps(self.result)})) + ")\n")
        code, result = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(result["result"]["task_id"], "TASK-001")

    def test_wrong_task_result_is_unverified(self):
        self.result["task_id"] = "SOME-OTHER-TASK"
        self.write_fake("print(" + repr(json.dumps(self.result)) + ")\n")
        code, result = self.call()
        self.assertEqual(code, 3)
        self.assertIn("task_id", result["reason"])

    def test_worker_failure_and_permission_block_are_distinct(self):
        self.write_fake("import sys\nprint('unexpected failure', file=sys.stderr)\nsys.exit(2)\n")
        self.assertEqual(self.call()[1]["status"], "failed")
        self.write_fake(
            "import sys\nprint('bind: operation not permitted', file=sys.stderr)\nsys.exit(1)\n"
        )
        code, result = self.call()
        self.assertEqual(code, 4)
        self.assertEqual(result["status"], "blocked")

    def test_timeout_is_bounded(self):
        self.write_fake("import time\ntime.sleep(30)\n")
        started = time.monotonic()
        code, result = self.call("--timeout", "0.05")
        self.assertEqual(code, 124)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - started, 5)

    @unittest.skipUnless(os.name == "posix", "Process groups require POSIX")
    def test_timeout_terminates_descendant(self):
        self.write_fake(
            "import subprocess, sys, time\n"
            "child = subprocess.Popen([sys.executable, '-c', "
            '"import time; from pathlib import Path; time.sleep(1); '
            "Path('orphan-result').write_text('orphan')\"])\n"
            "time.sleep(30)\n"
        )
        code, result = self.call("--timeout", "0.2")
        self.assertEqual(code, 124)
        time.sleep(1.1)
        self.assertFalse((self.root / "orphan-result").exists())

    @unittest.skipUnless(os.name == "posix", "Process groups require POSIX")
    def test_timeout_kills_term_ignoring_child_with_closed_pipes_only_in_worker_group(self):
        sentinel = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
        )
        self.addCleanup(lambda: sentinel.wait(timeout=5))
        self.addCleanup(sentinel.kill)
        child_code = (
            "import signal,time\nfrom pathlib import Path\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "Path('child-ready').write_text('ready')\n"
            "while not Path('check-orphan').exists(): time.sleep(0.01)\n"
            "Path('orphan-result').write_text('orphan')\n"
        )
        self.write_fake(
            "import subprocess, sys, time\nfrom pathlib import Path\n"
            "child = subprocess.Popen([sys.executable, '-c', " + repr(child_code) + "], "
            "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            "while not Path('child-ready').exists(): time.sleep(0.01)\n"
            "time.sleep(30)\n"
        )
        code, result = self.call("--timeout", "2")
        self.assertEqual(code, 124)
        self.assertTrue((self.root / "child-ready").exists())
        (self.root / "check-orphan").write_text("check")
        time.sleep(0.5)
        self.assertFalse((self.root / "orphan-result").exists())
        self.assertIsNone(sentinel.poll())

    def test_scope_and_role_restrictions(self):
        self.task["allowed_paths"] = ["../outside"]
        self.save_task()
        code, result = self.call()
        self.assertEqual(code, 4)
        self.assertIn("scoped", result["reason"])
        self.task["allowed_paths"] = ["src/**"]
        self.task["role"] = "critical_reviewer"
        self.save_task()
        code, result = self.call("--mode", "accept-edits")
        self.assertEqual(code, 4)
        self.assertIn("limited", result["reason"])

    def test_plan_cannot_claim_changes_and_edit_reports_must_stay_in_scope(self):
        self.result["changed_files"] = ["src/module.py"]
        self.write_fake("print(" + repr(json.dumps(self.result)) + ")\n")
        self.assertEqual(self.call()[1]["status"], "unverified")
        self.assertEqual(self.call("--mode", "accept-edits")[1]["status"], "completed")
        self.result["changed_files"] = [".team/gates/release.json"]
        self.write_fake("print(" + repr(json.dumps(self.result)) + ")\n")
        self.assertEqual(self.call("--mode", "accept-edits")[1]["status"], "unverified")

    def test_failed_check_cannot_be_completed(self):
        self.result["checks"] = [{"name": "unit tests", "status": "failed", "evidence": "test.log"}]
        self.write_fake("print(" + repr(json.dumps(self.result)) + ")\n")
        self.assertEqual(self.call()[1]["status"], "unverified")

    def test_task_file_outside_project_is_rejected(self):
        outside = self.root.parent / (self.root.name + "-outside-task.json")
        outside.write_text(json.dumps(self.task))
        self.addCleanup(outside.unlink)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = WORKER.main(
                [
                    "run",
                    "--project-root",
                    str(self.root),
                    "--task",
                    str(outside),
                    "--agy",
                    str(self.fake),
                ]
            )
        self.assertEqual(code, 4)
        self.assertIn("within project-root", json.loads(stdout.getvalue())["reason"])

    def test_nonfinite_timeout_is_rejected(self):
        self.assertEqual(self.call("--timeout", "nan")[0], 4)
        self.assertEqual(self.call("--timeout", "inf")[0], 4)

    def test_task_id_matches_team_contract(self):
        self.task["id"] = "TASK.001-v2_subtask"
        self.save_task()
        self.assertEqual(self.call("--dry-run")[0], 0)
        for value in (".hidden", "a" * 101, "bad/id"):
            self.task["id"] = value
            self.save_task()
            self.assertEqual(self.call("--dry-run")[0], 4)

    def test_doctor_help_does_not_claim_live_startup(self):
        self.write_fake("print('Usage: agy --print --output-format')\n")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = WORKER.main(["doctor", "--agy", str(self.fake)])
        result = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(result["help_ok"])
        self.assertFalse(result["live_worker_verified"])

    def probe(self, body):
        self.write_fake(body)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = WORKER.main(["doctor", "--agy", str(self.fake), "--probe"])
        return code, json.loads(stdout.getvalue())

    def test_probe_exit_zero_with_authentication_failure_is_blocked(self):
        code, result = self.probe("print('not authenticated but exit zero')\n")
        self.assertEqual(code, 4)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["live_worker_verified"])

    def test_probe_exit_zero_with_unknown_output_is_unverified(self):
        for output in ("starting", '{"probe":"wrong"}', '{"probe":"ok","extra":true}'):
            code, result = self.probe("print(" + repr(output) + ")\n")
            self.assertEqual(code, 3)
            self.assertEqual(result["status"], "unverified")
            self.assertFalse(result["live_worker_verified"])

    def test_probe_verifies_exact_json_in_recognized_envelope(self):
        for payload in ({"probe": "ok"}, {"result": '{"probe":"ok"}'}):
            code, result = self.probe("print(" + repr(json.dumps(payload)) + ")\n")
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "ready")
            self.assertTrue(result["live_worker_verified"])

    def test_probe_auth_failure_overrides_expected_json(self):
        code, result = self.probe(
            "import sys\nprint('{\"probe\":\"ok\"}')\nprint('permission denied', file=sys.stderr)\n"
        )
        self.assertEqual(code, 4)
        self.assertFalse(result["live_worker_verified"])


if __name__ == "__main__":
    unittest.main()
