---
name: mw-ship
description: Run a planned roadmap item through the shared workflow using Codex or Claude, or apply authorized PR comments.
---

# Run a change

Read AGENTS.md and .workflow-kit/config.toml. Confirm the roadmap item exists and the tree
is clean. Choose one engine for the entire change, defaulting to Codex when unspecified.
All planning, implementation, mutation and review sessions use that engine. Resume and PR
follow-ups must use the recorded engine; a different roadmap item may choose the other tool.

```bash
python3 .workflow-kit/run.py ship S-01 --engine codex
python3 .workflow-kit/run.py resume S-01 --engine codex
```

These commands prepare local commits and a PR description. Add `--publish` only when the
user authorized pushing the branch and opening/updating a PR. Never merge the PR.
With authorization to apply comments and reply:

```bash
python3 .workflow-kit/run.py address-pr 42 --engine codex --publish
```

Only the authenticated user's comments are trusted by default. An explicitly authorized
additional reviewer can be specified with `--reviewer LOGIN`. Use the current tool's actual
process/session mechanism for long-running commands; do not assume background parameter
names or automatic exit notifications. Report the result and the URL or local artifact.
After failure, inspect preserved changes before resuming; never reset or discard them.
