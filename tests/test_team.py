"""Exercise real project bootstrap, dependency and review gate invariants."""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("team", ROOT / "scripts/team.py")
team = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(team)
AGY_SPEC = importlib.util.spec_from_file_location("agy_contract", ROOT / "scripts/agy_worker.py")
agy = importlib.util.module_from_spec(AGY_SPEC)
AGY_SPEC.loader.exec_module(agy)


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        team.initialize(self.project, "Inventory", "Manage inventory for a small business")

    def write(self, relative, value):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, dict):
            team.atomic_json(path, value)
        else:
            path.write_text(value, encoding="utf-8")
        return path

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return team.main(list(args))

    def task(self, task_id="TASK-1", dependencies=None, status="todo"):
        value = {
            "schema_version": 1,
            "id": task_id,
            "title": "Implement inventory",
            "role": "developer",
            "objective": "Record inventory movements",
            "inputs": ["docs/architecture.md"],
            "allowed_paths": ["src/**"],
            "acceptance_criteria": ["Movement preserves stock balance"],
            "dependencies": dependencies or [],
            "status": status,
        }
        self.write(f".team/tasks/{task_id}.json", value)
        return value

    def gate(self, stage):
        evidence = []
        for relative in team.DOCUMENTS[stage]:
            path = self.write(relative, "Reviewed decision with project-specific evidence.\n")
            evidence.append({"path": relative, "sha256": team.digest(path)})
        check_file = self.write(
            f".team/evidence/{stage}.txt", "Actual check output for this synthetic test fixture.\n"
        )
        check_relative = check_file.relative_to(self.project).as_posix()
        evidence.append({"path": check_relative, "sha256": team.digest(check_file)})
        gate = {
            "schema_version": 1,
            "stage": stage,
            "author_session": "author-session-1",
            "reviewer_session": "reviewer-session-2",
            "reviewer_role": "critical_reviewer",
            "verdict": "pass",
            "evidence": evidence,
            "findings": [],
            "checks": [
                {"name": name, "status": "passed", "evidence": [check_relative], "reason": ""}
                for name in sorted(team.REQUIRED_CHECKS.get(stage, set()))
            ],
            "source_digest": team.source_digest(self.project),
            "task_contract_digest": team.task_contract_digest(self.project),
        }
        self.save_gate(gate)
        return gate

    def save_gate(self, gate):
        self.write(f".team/gates/{gate['stage']}.json", gate)

    def test_initialization_creates_discovery_without_fake_completion(self):
        state = team.project_state(self.project)
        self.assertEqual(state["stage"], "discovery")
        self.assertEqual(state["deployment_status"], "not_deployed")
        self.assertEqual(set(team.validate_config(self.project)), set(team.ROLES))
        self.assertEqual(list((self.project / ".team/gates").iterdir()), [])

    def test_filled_task_template_works_with_both_validators(self):
        template = team.load_json(ROOT / "templates/task.json")
        template.update(
            objective="Trace stock changes",
            title="Stock movement task",
            role="developer",
            stage="implementation",
            allowed_paths=["src/**"],
            acceptance_criteria=["Stock is consistent after each movement"],
        )
        self.write(".team/tasks/TASK-001.json", template)
        self.assertIn("TASK-001", team.task_records(self.project))
        self.assertEqual(
            agy.load_task(self.project.resolve(), ".team/tasks/TASK-001.json", "plan")["id"],
            "TASK-001",
        )

    def test_init_never_overwrites_existing_destination(self):
        sentinel = self.write("existing.txt", "keep me")
        with self.assertRaisesRegex(team.TeamError, "already exists"):
            team.initialize(self.project, "Another", "Different idea")
        self.assertEqual(sentinel.read_text(), "keep me")

    def test_init_does_not_execute_literal_idea(self):
        path = Path(self.temp.name) / "literal"
        idea = "`touch PWNED` $(touch PWNED)\nA legitimate idea"
        team.initialize(path, "Example", idea)
        self.assertIn(idea, (path / "docs/product-brief.md").read_text())
        self.assertFalse((path / "PWNED").exists())

    def test_path_escape_and_external_symlink_evidence_rejected(self):
        for relative in ("../outside", "/tmp/outside", "..", "a\\b"):
            with self.assertRaises(team.TeamError):
                team.inside(self.project, relative)
        (self.project / "external").symlink_to(Path(self.temp.name))
        with self.assertRaises(team.TeamError):
            team.inside(self.project, "external/anything")

    def test_dependency_cycle_and_missing_dependency_rejected(self):
        self.task("A", ["B"])
        self.task("B", ["A"])
        with self.assertRaisesRegex(team.TeamError, "cycle"):
            team.task_records(self.project)
        (self.project / ".team/tasks/B.json").unlink()
        with self.assertRaisesRegex(team.TeamError, "Unknown task"):
            team.task_records(self.project)

    def test_dependent_task_cannot_start_early(self):
        self.task("A")
        self.task("B", ["A"], "in_progress")
        with self.assertRaisesRegex(team.TeamError, "before dependency"):
            team.task_records(self.project)

    def test_gate_rejects_self_review(self):
        gate = self.gate("discovery")
        gate["reviewer_session"] = gate["author_session"]
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "distinct real"):
            team.validate_gate(self.project, "discovery")

    def test_gate_rejects_stale_artifact(self):
        self.gate("discovery")
        self.write("docs/research.md", "Changed conclusion after review")
        with self.assertRaisesRegex(team.TeamError, "stale"):
            team.validate_gate(self.project, "discovery")

    def test_gate_rejects_missing_document(self):
        gate = self.gate("discovery")
        gate["evidence"] = gate["evidence"][1:]
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "missing required"):
            team.validate_gate(self.project, "discovery")

    def test_open_major_blocks_but_documented_resolution_unblocks(self):
        gate = self.gate("discovery")
        gate["findings"] = [
            {
                "id": "F-1",
                "severity": "major",
                "status": "open",
                "reason": "Missing target user",
                "evidence": "docs/product-brief.md",
                "resolution": "",
            }
        ]
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "unresolved major"):
            team.validate_gate(self.project, "discovery")
        gate["findings"][0].update(
            status="resolved", resolution="Added users and interview evidence"
        )
        self.save_gate(gate)
        team.validate_gate(self.project, "discovery")

    def test_verification_requires_all_checks_and_current_source(self):
        self.task(status="done")
        self.write("src/app.py", "print('inventory')\n")
        gate = self.gate("verification")
        team.validate_gate(self.project, "verification")
        self.write("src/app.py", "print('changed')\n")
        with self.assertRaisesRegex(team.TeamError, "source changed"):
            team.validate_gate(self.project, "verification")
        gate["source_digest"] = team.source_digest(self.project)
        gate["checks"] = [check for check in gate["checks"] if check["name"] != "test"]
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "missing checks"):
            team.validate_gate(self.project, "verification")

    def test_format_lint_test_cannot_be_waived(self):
        self.task(status="done")
        gate = self.gate("verification")
        check = next(check for check in gate["checks"] if check["name"] == "test")
        check.update(
            status="not_applicable", reason="We prefer to skip automated tests for this app"
        )
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "cannot be waived"):
            team.validate_gate(self.project, "verification")

    def test_claimed_check_requires_hashed_evidence(self):
        self.task(status="done")
        gate = self.gate("verification")
        gate["checks"][0]["evidence"] = ["unhashed-output.txt"]
        self.save_gate(gate)
        with self.assertRaisesRegex(team.TeamError, "hashed evidence"):
            team.validate_gate(self.project, "verification")

    def test_unfinished_task_blocks_implementation_exit(self):
        self.task(status="review")
        self.gate("implementation")
        with self.assertRaisesRegex(team.TeamError, "tasks must be done"):
            team.validate_gate(self.project, "implementation")

    def test_logs_do_not_change_source_digest(self):
        before = team.source_digest(self.project)
        self.write(".team/runs/test/stdout.txt", "A worker log")
        self.assertEqual(before, team.source_digest(self.project))

    def test_scope_change_invalidates_planning_but_status_change_does_not(self):
        task = self.task()
        self.gate("planning")
        task["status"] = "in_progress"
        self.write(".team/tasks/TASK-1.json", task)
        team.validate_gate(self.project, "planning")
        task["acceptance_criteria"].append("New unreviewed requirement")
        self.write(".team/tasks/TASK-1.json", task)
        with self.assertRaisesRegex(team.TeamError, "task contracts changed"):
            team.validate_gate(self.project, "planning")

    def test_future_phase_tasks_do_not_block_current_implementation(self):
        self.task(status="done")
        task = self.task("RELEASE-1")
        task["stage"] = "release"
        self.write(".team/tasks/RELEASE-1.json", task)
        self.gate("implementation")
        team.validate_gate(self.project, "implementation")

    def test_advance_validates_prior_gates(self):
        self.gate("discovery")
        self.assertEqual(self.cli("advance", str(self.project)), 0)
        self.gate("architecture")
        self.write("docs/research.md", "Updated research")
        self.assertEqual(self.cli("advance", str(self.project)), 1)
        self.assertEqual(team.project_state(self.project)["stage"], "architecture")

    def test_failed_advance_never_mutates_stage(self):
        self.assertEqual(self.cli("advance", str(self.project)), 1)
        self.assertEqual(team.project_state(self.project)["stage"], "discovery")

    def test_complete_workflow_does_not_claim_deployment(self):
        self.task(status="done")
        for stage in team.STAGES:
            self.assertEqual(team.project_state(self.project)["stage"], stage)
            self.gate(stage)
            self.assertEqual(self.cli("advance", str(self.project)), 0)
        state = team.project_state(self.project)
        self.assertEqual(state["stage"], "complete")
        self.assertEqual(state["deployment_status"], "not_deployed")


if __name__ == "__main__":
    unittest.main()
