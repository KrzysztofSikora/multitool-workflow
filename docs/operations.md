# Operations and limitations

## Updating an installation

The toolkit is vendored into `.workflow-kit`; VERSION records the source commit. Updates are
not automatic. Review the new toolkit diff, preserve application-specific config.toml, and
replace the selected files deliberately on a clean tree. The installer refuses to overwrite
an existing installation. There is no automated update or artifact migration command.

This revision removes per-step routing. Existing changes with a single recorded engine can
continue with that engine. Legacy receipts containing multiple engines are rejected. Preserve
those artifacts for inspection and start a separately planned change rather than rewriting
the audit trail to pretend the previous run used only one tool.

## Moving an existing application

Finish active runs before installing another runner. Review AGENTS.md, CLAUDE.md, skill
collisions, and old hooks. Select one owner for commits and publication. The `mw-` prefix
avoids built-in skill collisions but does not disable hooks from another installation.
Handle retirement of old tooling as a separate reviewed change.

Application restrictions are not copied from MeshCore Guardian. For Android projects, define
physical-device and AVD rules in AGENTS.md and a fail-closed preflight check. An `emulator-`
serial alone does not establish the AVD name; gate scripts must validate their target too.

## Recovering from a session or gate failure

1. Read the reported local log; review it before sharing.
2. Inspect branch, `git status`, and diff. Incomplete edits are preserved.
3. Fix the cause and commit only deliberate changes. Do not bypass a denied tool operation.
4. Resume with the originally selected engine. If `.workflow/stuck` exists, remove that local
   marker deliberately after resolving the reported problem.
5. Divergent history during address-pr stops at `--ff-only` for manual resolution.

An attempt to use the other engine is rejected, including after losing local runtime state
when the committed engine record is available. Different roadmap items can select different
engines. A new clone can rebuild verification receipts using the recorded tool.

There are no unbounded retries or automatic CLI retries. Limits cover review corrections,
phase sessions, and timeouts. Timeout stops the process group and shell children. Aggregate
provider billing is not computed; monitor your account's usage and spending limits.

## Trust and access

Gate and preflight commands execute as the local runner user, outside the model sandbox.
Review project configuration before running it, particularly when reading an untrusted PR.
CLI hook trust and project permissions remain engine-specific; the runner neither approves
nor rewrites them. Configure required access before launching the complete run.

Post-session checks cannot prevent every operation during a session. Keep secrets outside
the accessible workspace and use a suitable execution environment. Instructions forbidding
secret access are not a replacement for isolation. Runtime logs are private local artifacts,
not scanned or published automatically.

Comments are identified by stable IDs. To revise an already handled decision, add a new
comment rather than editing the old one. A changed snapshot while replies are pending stops
the run for state inspection; reply markers help recover from uncertain publication responses.

## Current scope

- Shared runner and 14 canonical skills; Codex or Claude for a complete change.
- One active runner per repository, including its worktrees.
- Local commits by default; GitHub publication and replies only with `--publish`.
- No per-step engine selection, automatic failover, or engine changes on resume.
- No GitLab, fork PR support, automatic merge, scheduler, or background monitor.
- No automatic issue creation, migration of an old toolkit, or installation updates.
- Fake-CLI tests verify orchestration, not model quality or actual provider authentication.
- Active CI requires enabling the supplied template with appropriate GitHub permissions.

Pilot each engine separately on a small change in a disposable application repository before
relying on unattended runs. Pin working CLI/toolkit versions and repeat the pilot after
adapter or permission changes.
