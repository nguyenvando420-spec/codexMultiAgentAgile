#!/usr/bin/env python3
"""Local bootstrap and evidence gates for Codex-led delivery. Python 3.11+."""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath

if sys.version_info < (3, 11):
    raise SystemExit(
        "Python 3.11+ required; use the agile-team launcher or a compatible interpreter."
    )

import tomllib

ROOT = Path(__file__).resolve().parents[1]
STAGES = ("discovery", "architecture", "planning", "implementation", "verification", "release")
ROLES = (
    "product_analyst",
    "research_engineer",
    "solution_architect",
    "tech_lead",
    "developer",
    "qa_engineer",
    "critical_reviewer",
    "sre_engineer",
    "security_reviewer",
)
DOCUMENTS = {
    "discovery": ("docs/product-brief.md", "docs/research.md"),
    "architecture": ("docs/architecture.md", "docs/adr/0001-stack.md", "docs/coding-standards.md"),
    "planning": ("docs/backlog.md",),
    "implementation": ("docs/implementation.md",),
    "verification": ("docs/verification.md",),
    "release": ("docs/production-readiness.md", "docs/runbook.md"),
}
REQUIRED_CHECKS = {
    "verification": {"format", "lint", "test", "build", "security"},
    "release": {
        "ci",
        "security",
        "migration",
        "backup_restore",
        "rollback",
        "observability",
        "performance",
    },
}
SOURCE_EXCLUDES = {
    ".git",
    ".team",
    ".codex",
    ".agents",
    "docs",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    "target",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
}
SHA = re.compile(r"^[a-f0-9]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")


class TeamError(ValueError):
    """A user-visible invalid project or evidence record."""


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise TeamError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TeamError(f"Expected JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".team-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def inside(project: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise TeamError(f"Invalid relative path: {relative!r}")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or parts == PurePosixPath("."):
        raise TeamError(f"Path must stay inside project: {relative!r}")
    result = project / relative
    if not result.resolve().is_relative_to(project.resolve()):
        raise TeamError(f"Path escapes project through symlink: {relative}")
    return result


def digest(path: Path) -> str:
    if not path.is_file():
        raise TeamError(f"Evidence file does not exist: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(project: Path) -> str:
    """Hash source/config contents and paths; docs and generated outputs excluded.

    Source symlinks are rejected rather than following targets outside the snapshot.
    It identifies the reviewed local tree, not remote CI or deployment state.
    """
    result = hashlib.sha256()
    for folder, dirs, files in os.walk(project, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SOURCE_EXCLUDES)
        base = Path(folder)
        links = [d for d in dirs if (base / d).is_symlink()]
        if links:
            raise TeamError(f"Source symlinks are unsupported: {base / links[0]}")
        for name in sorted(files):
            path = base / name
            if name in SOURCE_EXCLUDES or name.endswith((".pyc", ".pyo")):
                continue
            relative = path.relative_to(project).as_posix()
            if path.is_symlink():
                raise TeamError(f"Source symlinks are unsupported: {relative}")
            payload = path.read_bytes()
            result.update(relative.encode() + b"\0" + hashlib.sha256(payload).digest())
    return result.hexdigest()


def project_state(project: Path) -> dict:
    state = load_json(inside(project, ".team/project.json"))
    if state.get("schema_version") != 1 or state.get("stage") not in (*STAGES, "complete"):
        raise TeamError("Invalid project schema_version or stage")
    for key in ("name", "idea"):
        if not isinstance(state.get(key), str) or not state[key].strip():
            raise TeamError(f"Project needs a nonempty {key}")
    return state


def text_list(value, label: str, allow_empty: bool = False) -> list:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise TeamError(
            f"{label} must be a {'possibly empty ' if allow_empty else 'nonempty '}list"
        )
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise TeamError(f"{label} entries must be nonempty strings")
    return value


def task_records(project: Path) -> dict:
    records = {}
    task_dir = inside(project, ".team/tasks")
    for path in sorted(task_dir.glob("*.json")):
        task = load_json(inside(project, path.relative_to(project).as_posix()))
        task_id = task.get("id")
        if not isinstance(task_id, str) or not ID.fullmatch(task_id) or task_id in records:
            raise TeamError(f"Invalid or duplicate task ID in {path.name}")
        if task.get("schema_version") != 1 or task.get("role") not in ROLES:
            raise TeamError(f"Invalid schema_version or role in {path.name}")
        if task.get("status") not in {"todo", "in_progress", "review", "done", "blocked"}:
            raise TeamError(f"Invalid status in {path.name}")
        if task.get("stage", "implementation") not in STAGES:
            raise TeamError(f"Invalid stage in {path.name}")
        for key in ("title", "objective"):
            if not isinstance(task.get(key), str) or not task[key].strip():
                raise TeamError(f"Missing {key} in task {task_id}")
        text_list(task.get("inputs"), "inputs", True)
        text_list(task.get("acceptance_criteria"), "acceptance_criteria")
        for relative in text_list(task.get("allowed_paths"), "allowed_paths", True):
            inside(project, relative)
        text_list(task.get("dependencies"), "dependencies", True)
        records[task_id] = task
    visiting, visited = set(), set()

    def visit(task_id):
        if task_id in visiting:
            raise TeamError(f"Dependency cycle at task {task_id}")
        if task_id in visited:
            return
        if task_id not in records:
            raise TeamError(f"Unknown task dependency {task_id}")
        visiting.add(task_id)
        for dependency in records[task_id]["dependencies"]:
            visit(dependency)
            if (
                records[task_id]["status"] in {"in_progress", "review", "done"}
                and records[dependency]["status"] != "done"
            ):
                raise TeamError(f"Task {task_id} started before dependency {dependency} was done")
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in records:
        visit(task_id)
    return records


def task_contract_digest(project: Path) -> str:
    """Bind reviewed scope while allowing task status and results to evolve."""
    contracts = []
    for task_id, task in sorted(task_records(project).items()):
        contract = {
            key: task.get(key)
            for key in (
                "id",
                "title",
                "objective",
                "role",
                "stage",
                "inputs",
                "allowed_paths",
                "acceptance_criteria",
                "dependencies",
                "deliverables",
            )
        }
        contracts.append(contract)
    serialized = json.dumps(contracts, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def validate_config(project: Path) -> dict:
    agents = {}
    config_path = inside(project, ".codex/config.toml")
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    policy = config.get("agents", {})
    if policy.get("enabled") is not True or policy.get("max_concurrent_threads_per_session") != 3:
        raise TeamError("Expected enabled agents and concurrency 3 (host may impose a lower cap)")
    for role in ROLES:
        path = inside(project, f".codex/agents/{role.replace('_', '-')}.toml")
        item = tomllib.loads(path.read_text(encoding="utf-8"))
        if item.get("name") != role:
            raise TeamError(f"Agent name mismatch in {path}")
        for key in ("description", "developer_instructions"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise TeamError(f"Missing {key} in {path}")
        agents[role] = item
    skill = inside(project, ".agents/skills/agile-delivery/SKILL.md")
    if not skill.is_file() or not inside(project, "AGENTS.md").is_file():
        raise TeamError("Missing entrypoint skill or AGENTS.md")
    return agents


def validate_gate(project: Path, stage: str) -> dict:
    gate = load_json(inside(project, f".team/gates/{stage}.json"))
    if gate.get("schema_version") != 1 or gate.get("stage") != stage:
        raise TeamError(f"Gate schema/stage mismatch: {stage}")
    author, reviewer = gate.get("author_session"), gate.get("reviewer_session")
    if not all(isinstance(v, str) and v.strip() for v in (author, reviewer)) or author == reviewer:
        raise TeamError(f"{stage}: distinct real author/reviewer session IDs required")
    if gate.get("reviewer_role") != "critical_reviewer" or gate.get("verdict") != "pass":
        raise TeamError(f"{stage}: independent critical reviewer must return pass")
    evidence = gate.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise TeamError(f"{stage}: evidence list required")
    evidence_paths = set()
    for record in evidence:
        if not isinstance(record, dict):
            raise TeamError(f"{stage}: evidence must be objects with path and sha256")
        relative, expected = record.get("path"), record.get("sha256")
        path = inside(project, relative)
        if (
            relative in evidence_paths
            or not isinstance(expected, str)
            or not SHA.fullmatch(expected)
        ):
            raise TeamError(f"{stage}: duplicate evidence or invalid sha256")
        if not path.stat().st_size or digest(path) != expected:
            raise TeamError(f"{stage}: stale or empty evidence: {relative}")
        evidence_paths.add(relative)
    missing = set(DOCUMENTS[stage]) - evidence_paths
    if missing:
        raise TeamError(f"{stage}: missing required evidence {sorted(missing)}")
    findings = gate.get("findings")
    if not isinstance(findings, list):
        raise TeamError(f"{stage}: findings must be a list (empty when none)")
    finding_ids = set()
    for finding in findings:
        if not isinstance(finding, dict):
            raise TeamError(f"{stage}: invalid finding")
        fid = finding.get("id")
        if not isinstance(fid, str) or not ID.fullmatch(fid) or fid in finding_ids:
            raise TeamError(f"{stage}: invalid/duplicate finding ID")
        finding_ids.add(fid)
        severity, status = finding.get("severity"), finding.get("status")
        if severity not in {"blocking", "major", "minor"} or status not in {"open", "resolved"}:
            raise TeamError(f"{stage}: invalid finding severity/status")
        for key in ("reason", "evidence"):
            if not isinstance(finding.get(key), str) or not finding[key].strip():
                raise TeamError(f"{stage}: finding needs {key}")
        if status == "open" and severity in {"blocking", "major"}:
            raise TeamError(f"{stage}: unresolved {severity} finding {fid}")
        if status == "resolved" and not str(finding.get("resolution", "")).strip():
            raise TeamError(f"{stage}: resolved finding {fid} needs resolution")
    checks = gate.get("checks")
    if not isinstance(checks, list):
        raise TeamError(f"{stage}: checks must be a list")
    names = set()
    for check in checks:
        if (
            not isinstance(check, dict)
            or not isinstance(check.get("name"), str)
            or not check["name"].strip()
        ):
            raise TeamError(f"{stage}: invalid check")
        name, status = check["name"], check.get("status")
        if name in names or status not in {"passed", "not_applicable"}:
            raise TeamError(f"{stage}: duplicate or unsuccessful check {name}")
        names.add(name)
        references = text_list(
            check.get("evidence"), f"{name}.evidence", status == "not_applicable"
        )
        if any(ref not in evidence_paths for ref in references):
            raise TeamError(f"{stage}: check {name} needs hashed evidence references")
        if status == "not_applicable":
            if name in {"format", "lint", "test"} or len(str(check.get("reason", "")).strip()) < 20:
                raise TeamError(
                    f"{stage}: check {name} cannot be waived without a substantive applicable reason"
                )
    missing_checks = REQUIRED_CHECKS.get(stage, set()) - names
    if missing_checks:
        raise TeamError(f"{stage}: missing checks {sorted(missing_checks)}")
    if stage in {"implementation", "verification", "release"}:
        if gate.get("source_digest") != source_digest(project):
            raise TeamError(
                f"{stage}: source changed or source_digest missing; re-review current source"
            )
    if stage in {"planning", "implementation", "verification", "release"}:
        tasks = task_records(project)
        if not tasks:
            raise TeamError(f"{stage}: at least one real task is required")
        if gate.get("task_contract_digest") != task_contract_digest(project):
            raise TeamError(f"{stage}: task contracts changed or digest missing; re-review scope")
        scoped_tasks = [
            t
            for t in tasks.values()
            if STAGES.index(t.get("stage", "implementation")) <= STAGES.index(stage)
        ]
        if stage in {"implementation", "verification", "release"} and any(
            t["status"] != "done" for t in scoped_tasks
        ):
            raise TeamError(f"{stage}: all scoped tasks must be done before phase exit")
    return gate


def initialize(destination: Path, name: str, idea: str) -> dict:
    destination = destination.absolute()
    if not name.strip() or not idea.strip():
        raise TeamError("Project name and idea cannot be empty")
    if destination.exists() or destination.is_symlink():
        raise TeamError("Destination already exists; init never overwrites an existing project")
    validate_config(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".agile-init-", dir=destination.parent))
    try:
        for folder in (".codex", ".agents", "scripts", "templates"):
            shutil.copytree(
                ROOT / folder,
                staging / folder,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        for filename in ("AGENTS.md", ".editorconfig", ".gitignore", "agile-team"):
            shutil.copy2(ROOT / filename, staging / filename)
        for filename in ("workflow.md", "roles.md"):
            path = staging / "docs" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "docs" / filename, path)
        for paths in DOCUMENTS.values():
            for relative in paths:
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / "templates" / target.name, target)
        (staging / ".team/tasks").mkdir(parents=True)
        (staging / ".team/gates").mkdir()
        atomic_json(
            staging / ".team/project.json",
            {
                "schema_version": 1,
                "name": name.strip(),
                "idea": idea.strip(),
                "stage": "discovery",
                "tasks": [],
                "deployment_status": "not_deployed",
            },
        )
        # The generated brief records the user's literal idea, never a shell fragment.
        with (staging / "docs/product-brief.md").open("a", encoding="utf-8") as stream:
            stream.write(f"\n## Ý tưởng ban đầu\n\n{idea.strip()}\n")
        # Reserve the destination exclusively: rename alone can replace an empty
        # directory created by another initializer between preflight and publish.
        destination.mkdir()
        for child in staging.iterdir():
            os.rename(child, destination / child.name)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {"project": str(destination), "stage": "discovery", "deployment_status": "not_deployed"}


def report(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser(
        "init", help="Create a new project; never overwrite an existing directory"
    )
    init.add_argument("project", type=Path)
    init.add_argument("--name", required=True)
    init.add_argument("--idea", required=True)
    for command in ("status", "check", "advance", "snapshot"):
        cmd = sub.add_parser(command)
        cmd.add_argument("project", type=Path)
    gate = sub.add_parser("gate", help="Validate one independent stage review; does not run checks")
    gate.add_argument("project", type=Path)
    gate.add_argument("stage", choices=STAGES)
    evidence = sub.add_parser("evidence", help="Hash local evidence files after real work/review")
    evidence.add_argument("project", type=Path)
    evidence.add_argument("files", nargs="+")
    sub.add_parser("doctor", help="Inspect installed tools without starting external agents")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            report(initialize(args.project, args.name, args.idea))
        elif args.command == "doctor":
            report(
                {
                    "python": sys.version.split()[0],
                    "codex": shutil.which("codex"),
                    "agy": shutil.which("agy"),
                    "native_subagents": "Provided by the active Codex host, not this script",
                    "agy_live_status": "not_probed; use agy_worker.py doctor --probe for bounded startup check",
                }
            )
        else:
            project = args.project.resolve()
            if args.command == "evidence":
                report(
                    {
                        "evidence": [
                            {"path": relative, "sha256": digest(inside(project, relative))}
                            for relative in args.files
                        ]
                    }
                )
            elif args.command == "snapshot":
                report(
                    {
                        "source_digest": source_digest(project),
                        "task_contract_digest": task_contract_digest(project),
                        "excludes": sorted(SOURCE_EXCLUDES),
                    }
                )
            elif args.command == "check":
                agents = validate_config(project)
                state_path = inside(project, ".team/project.json")
                tasks = task_records(project) if state_path.exists() else {}
                if state_path.exists():
                    project_state(project)
                report(
                    {
                        "status": "valid",
                        "roles": sorted(agents),
                        "tasks": len(tasks),
                        "meaning": "Configuration structure only; no production certification or model execution",
                    }
                )
            elif args.command == "gate":
                validate_gate(project, args.stage)
                report(
                    {
                        "stage": args.stage,
                        "status": "pass",
                        "meaning": "Review attestation validated; checks were not executed by this command",
                    }
                )
            elif args.command == "status":
                state = project_state(project)
                tasks = task_records(project)
                report(
                    {
                        **state,
                        "task_summary": {
                            status: sum(t["status"] == status for t in tasks.values())
                            for status in ("todo", "in_progress", "review", "done", "blocked")
                        },
                        "deployment_note": "Readiness gates do not establish that a live deployment exists",
                    }
                )
            elif args.command == "advance":
                state = project_state(project)
                if state["stage"] == "complete":
                    raise TeamError(
                        "Workflow already complete; validate gates again after any material change"
                    )
                index = STAGES.index(state["stage"])
                for stage in STAGES[: index + 1]:
                    validate_gate(project, stage)
                state["stage"] = STAGES[index + 1] if index + 1 < len(STAGES) else "complete"
                atomic_json(inside(project, ".team/project.json"), state)
                report(
                    {
                        "stage": state["stage"],
                        "deployment_status": state.get("deployment_status", "not_deployed"),
                    }
                )
        return 0
    except (TeamError, OSError, tomllib.TOMLDecodeError) as exc:
        report({"status": "blocked", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
