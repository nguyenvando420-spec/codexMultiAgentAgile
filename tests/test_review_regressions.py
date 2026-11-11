"""Independent reviewer probes for stale source reviews and misleading startup."""

import argparse
import importlib.util
import os
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


team = load_module("review_team", "team.py")
agy = load_module("review_agy", "agy_worker.py")


class IndependentReviewRegressions(unittest.TestCase):
    def test_source_symlink_target_change_is_detected_or_refused(self):
        with tempfile.TemporaryDirectory(prefix="agile-review-") as folder:
            project = Path(folder)
            (project / ".team").mkdir()
            (project / "src").mkdir()
            target = project / ".team" / "module.py"
            target.write_text("value = 1\n", encoding="utf-8")
            (project / "src" / "main.py").symlink_to("../.team/module.py")
            try:
                before = team.source_digest(project)
                target.write_text("value = 2\n", encoding="utf-8")
                after = team.source_digest(project)
            except team.TeamError:
                return
            self.assertNotEqual(before, after)

    def test_probe_requires_expected_response_not_just_exit_zero(self):
        with tempfile.TemporaryDirectory(prefix="agile-review-") as folder:
            executable = Path(folder) / "fake-agy"
            executable.write_text(
                "#!/bin/sh\nprintf 'not authenticated but exit zero'\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            result = agy.doctor(argparse.Namespace(agy=str(executable), probe=True))
            self.assertFalse(result["live_worker_verified"])
            self.assertNotEqual(result["status"], "ready")

    @unittest.skipUnless(os.name == "posix", "Process groups require POSIX")
    def test_timeout_kills_descendant_even_when_its_pipes_are_closed(self):
        with tempfile.TemporaryDirectory(prefix="agile-review-") as folder:
            project = Path(folder)
            worker = project / "worker.py"
            pidfile = project / "child.pid"
            child = (
                "import os,pathlib,signal,sys,time; "
                "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                "pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); "
                "[(pathlib.Path(sys.argv[1] + '.heartbeat').write_text(str(time.monotonic())), "
                "time.sleep(0.03)) for _ in range(1000)]"
            )
            worker.write_text(
                "import subprocess,sys,time\n"
                f"subprocess.Popen([sys.executable, '-c', {child!r}, sys.argv[1]], "
                "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
                "time.sleep(30)\n",
                encoding="utf-8",
            )
            child_pid = None
            try:
                _, _, _, timed_out = agy.invoke(
                    [sys.executable, str(worker), str(pidfile)], project, 1
                )
                self.assertTrue(timed_out)
                child_pid = int(pidfile.read_text(encoding="utf-8"))
                time.sleep(0.1)
                heartbeat = Path(str(pidfile) + ".heartbeat")
                before = heartbeat.read_text(encoding="utf-8")
                time.sleep(0.15)
                self.assertEqual(before, heartbeat.read_text(encoding="utf-8"))
            finally:
                if child_pid is None and pidfile.exists():
                    child_pid = int(pidfile.read_text(encoding="utf-8"))
                if child_pid is not None:
                    try:
                        os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass


if __name__ == "__main__":
    unittest.main()
