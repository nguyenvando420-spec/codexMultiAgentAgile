---
name: agile-delivery
description: Coordinate a project from idea through research, technical decisions, implementation, independent critique and production delivery using a team of subagents. Use for the installed Agile team workflow; keep ordinary small fixes proportional.
---

# Agile delivery

Use the project-local `AGENTS.md`, `.team/project.json` and existing decisions as the source of continuity. If the project is not initialized, use the toolkit's `scripts/team.py init` before starting project work. Do not invent a product or select a stack when the user has not supplied an idea or constraints.

Read [workflow](../../../docs/workflow.md) for stage contracts and [roles](../../../docs/roles.md) when choosing a role. These links resolve inside the installed project/toolkit, not the user's global Codex directory.

The main agent coordinates. Explicitly use native subagents for bounded independent tasks and an independent `critical_reviewer` at every stage. Use project custom role definitions under `.codex/agents/`; if the client has not reloaded them, read the relevant TOML instructions and pass those instructions to a normally spawned subagent. Do not claim a role was loaded just because its file exists.

Use at most three active children, or fewer when the environment's actual limit is lower. Reuse/rotate roles as stages progress. Give every delegated task its inputs, role, owned paths, dependencies, acceptance criteria and required evidence. Separate author and reviewer sessions; separate worktrees or non-overlapping ownership for parallel writers. Return concise evidence summaries rather than raw logs to the coordinator.

Research must cite primary sources and distinguish facts, inference and unknowns. The Architect owns technology/ADRs; the Tech Lead owns shared format and coding rules, including actual stack-appropriate formatter/linter/CI enforcement after stack choice. Independent review checks these decisions before implementation proceeds.

Use `scripts/team.py` for status, evidence hashes, source snapshots and stage validation. A pending gate, stale evidence, unexecuted check or unresolved material finding is not a pass. Record real author/reviewer identities and raw evidence. The scripts check recorded consistency, not the truth of a human/agent assertion; the coordinator must inspect evidence and the actual subagent identity before accepting it.

`agy` is an external worker, not a native Codex child. Use the provided `scripts/agy_worker.py` adapter according to its CLI help. Preserve host permissions, use explicit task contracts, and report startup/auth/network/sandbox errors as blocked. Do not use permission-bypass flags or claim a successful run from a successful `--help` probe. Native subagents can continue independent work when `agy` cannot start.

Complete authorized preparation and checks without asking for repetitive approval. Actual publishing/deployment must remain within the user's stated target and authorization. Record observed deployment receipts and post-release checks. The workflow state `complete` alone never means a live production deployment occurred.
