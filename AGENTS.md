# Multitool Workflow

A reusable spec-driven methodology and POSIX/Python runner for Codex and Claude Code.
Canonical skills live in workflow/skills. Target-project artifacts live in context/;
this toolkit repository does not contain an application roadmap.

- Keep runner state, validation and publication independent of engine output formats.
- Never introduce permission-bypass defaults, embedded credentials or attribution trailers.
- Preserve existing application instructions during installation.
- Keep README.md in Polish and document limits honestly.
- Verify changes with `python3 -m unittest discover -s tests -v`.
- Tests use fake CLIs and temporary Git repositories; never start paid sessions in tests.
