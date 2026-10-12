---
name: mw-fix-review
description: Triage the findings of /review autonomously - fix, defer, reject or turn into a proposed lesson - then prepare the verified fixes. Every choice is recorded on the finding so the PR reviewer can overrule it.
---

# Act on review findings

This step runs without a person (`.workflow-kit/autonomy.md`). In the interactive workflow
the user triaged each finding; here you do it, and the PR shows what you chose.

## Input

- `context/changes/<change-id>/review.md`: every finding with `- Decision: open`.
- `context/changes/<change-id>/plan.md`, `AGENTS.md` (*Gates*), `context/lessons.md`.

## Triage

Re-verify each open finding in the code first. Then decide:

| Finding | Decision |
|---------|----------|
| `blocker` | **fix**. If you cannot fix it within the change's scope, follow `autonomy.md` section 5. |
| `major`, effort small or medium, inside the change's files | **fix** |
| `major`, effort large or outside the change's scope | **defer**: add a `[FOLLOW-UP]` deviation to `plan.md` |
| `minor`, small and local | **fix** |
| `minor`, otherwise | **defer** |
| Re-verification shows the finding is wrong | **reject**, with the evidence in one line |

A fix that would change a `costly` decision (`D-<n>` with reversal `costly`) is not yours to
make silently: implement the reviewer's suggestion only if it keeps the decision's contract,
otherwise defer it and add a `[REVIEW]` deviation naming the D-ID.

## Fix

- Fix findings one at a time, smallest diff that resolves the problem, with a test where the
  finding is about behaviour.
- After all fixes run the gates from the `AGENTS.md` *Gates* table. Never weaken a test.
- Leave the changes for the runner to commit after validation.

## Lessons

For each finding with a lesson candidate that you judge recurring (it would apply to other
changes, not just this diff), append it to `context/lessons.md` in the format below, marked as
proposed. Proposed rules are not binding until accepted by the user. The runner includes
them in the step commit; rejecting a proposal removes that rule, without reverting code fixes.

```markdown
## <rule, as an imperative sentence>
- Why: <the failure it prevents>
- Seen in: <change-id>, R<n>
- Scope: <paths or layers it applies to>
- Status: proposed in the PR for <change-id>
```

## Record

Update each finding's `Decision:` line in `review.md`:

- `- Decision: fixed (pending runner commit)`
- `- Decision: deferred (<why>; FOLLOW-UP in plan.md)`
- `- Decision: rejected (<evidence>)`
- add `+ lesson proposed` to any of the above when you appended a lesson.

Update review.md and plan.md. No finding may remain Decision: open. Leave the diff for
the runner; do not commit or change the review verdict yourself.

## Runner contract

When invoked by `.workflow-kit/run.py`, do not stage or commit: the runner owns commits,
branch changes and publication. Finish the requested edits and artifacts; leave the diff
for the runner to validate and commit by explicit path. A clean tree is required at entry,
not at exit. Never push, publish, merge, or post replies yourself.
