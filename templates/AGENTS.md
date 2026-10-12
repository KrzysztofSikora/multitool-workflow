# Application project

Describe the application, architecture and constraints here. Read `context/` as the source
of truth. Shared instructions are in `.workflow-kit/skills` and `.workflow-kit/autonomy.md`.

Project setup is interactive: shape → prd → tech-stack → roadmap → test-plan.
Approve each artifact before proceeding. For each change, use the runner; do not implement
roadmap items outside the loop. The runner owns Git commits, branch changes and publication.

## Rules

- No secrets in code, commits, artifacts, logs or answers. Never read `.env` into transcripts.
- Keep changes scoped to the plan. Record decisions and deviations.
- Never weaken tests to get green, bypass denied tool calls or merge PRs automatically.
- Human checks remain open until a person confirms them.
- No attribution trailers or generated-with lines in commits or PRs.
- Add project-specific boundaries here (layers, devices, data, network, privacy).

## Gates

Configure actual commands in `.workflow-kit/config.toml` and keep this table synchronized.
The TOML command arrays are the executable source of truth.

| Gate | Command | Runs |
|------|---------|------|
| typecheck | configure for this project | fast + final |
| lint | configure for this project | fast + final |
| tests | configure for this project | fast + final |
| e2e | configure for this project | final |

Keep roadmap Overview columns exactly `ID`, `Issue`, `change-id`, `Status`.
