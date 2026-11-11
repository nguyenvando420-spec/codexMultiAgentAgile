# Agile multi-agent delivery

Use `.agents/skills/agile-delivery/SKILL.md` for project delivery requests.
The primary agent coordinates; delegate bounded independent tasks to specialized
subagents. Use at most three concurrently active children, or the host's lower
limit. Run dependent phases in order. Share contracts before parallel code edits.
If named custom agents are unavailable in this active session, read the matching
`.codex/agents/*.toml` and pass its instructions to a native subagent. Do not claim
that changing local files hot-reloads the current session's agent registry.

Use distinct real session IDs for proposal authors and critical reviewers.
Record review evidence against the exact artifacts and source digest. Re-review
after material changes. Follow `docs/workflow.md` for stages and gate formats.
Keep research sources, ADRs, coding standards, backlog, and production evidence
in the project. Do not select an application stack before analyzing its needs.

`scripts/team.py` is the local project/bootstrap and gate helper. It does not
invoke an LLM, run a background daemon, or enforce an OS sandbox. Native Codex
subagents supply orchestration. `scripts/agy_worker.py` is an optional external
worker adapter; report blocked startup honestly and use native subagents when
available. Never bypass host permission restrictions to make a worker run.

For this toolkit, use Python 3.11+ stdlib only, four-space indentation, LF, type
annotations for public helpers where useful, and no shell interpolation of input.
Run `python3 scripts/team.py check .` with a compatible interpreter. When maintaining
the original toolkit, also run its Ruff checks and `python3 -m unittest discover -s
tests -v`. Application projects must select and configure their actual
formatter/linter/test/CI tools through their Tech Lead after choosing a stack.
