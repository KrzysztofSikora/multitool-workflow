# Assessment: one methodology, either Codex or Claude

## Verdict

**This design makes sense for repeated application development when you want provider choice
without changing your development process.** Keep one engine for the complete change workflow,
and keep provider-specific code in a small adapter. The current implementation is a testable
starting point, not yet a production-proven unattended system.

This is an engineering assessment of the repository and its contracts. It is not a benchmark
of model quality or cost. No paid model runs or real application pilots were performed for
this assessment.

## Why the design is feasible

Both tools support programmatic execution: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
and [Claude programmatic usage](https://code.claude.com/docs/en/headless). That establishes an
invocation boundary, not equal execution behavior. The runner can supply the same instructions
and artifact paths while each adapter translates invocation and permission settings.

Keeping process state in artifacts and Git allows a fresh session to resume the selected
tool's work without requiring the previous conversation. The committed engine record and
local receipts enforce one engine per change. Another change can choose the alternative tool.

## Benefits and trade-offs

| Area | Benefit | Cost or limitation |
|------|---------|--------------------|
| Methodology | One set of requirements, plan, review, and PR contracts | Both tools must follow and produce the same formats |
| Provider choice | Choose Codex or Claude before a complete run | No mid-run failover; the original tool remains required |
| Operation | Only one authenticated CLI is needed for the chosen run | Two adapters still require maintenance and separate pilots |
| Review | Fresh sessions avoid inheriting the author's conversation | The same tool can repeat the author's assumptions |
| Verification | Runner-owned gates and receipts reduce reliance on prose claims | Gate quality determines which defects are actually detected |
| Auditability | Decisions and evidence live in reviewable files | More artifacts and commits than a casual coding session |
| Portability | Domain process is shared rather than duplicated | Sandbox, hooks, permission rules, and billing remain different |
| Scope control | PR makes agent choices visible before merge | Human review and acceptance checks remain necessary |

Choosing one engine removes cross-provider coordination, per-step selection rules, and the
need to decide which tool owns corrections. It also makes logs and failure recovery easier
to explain. This simplification fits the intended use better than provider orchestration.

## When it is worth using

Use it when you expect multiple roadmap items, want traceable decisions, and already have
meaningful tests or can establish them during scaffolding. It is especially useful when the
same process should survive a later provider preference change across new runs or projects.

For a one-off script or a small cosmetic edit, the complete artifact/review/mutation sequence
may cost more time than it saves. Keeping two provider adapters is unnecessary if you expect
to use only one provider indefinitely. Shared interfaces preserve the option without requiring
both CLIs to be installed on every machine.

## Material risks in the current implementation

1. **Provider permissions are not equivalent.** A workflow that passes with one CLI may stop
   under the other tool's access policy. Validate each adapter in its own actual environment;
   shared instructions cannot grant permissions.
2. **Fresh-session review is not independent model judgment.** The reviewer shares the selected
   provider's tendencies. Human review, real acceptance checks, and strong tests remain essential.
3. **Fake CLIs do not prove real-agent reliability.** Tests cover sequencing and contract failures,
   but cannot establish instruction-following, authentication, billing, or actual CLI behavior.
4. **Execution state has limits.** Artifacts are tracked and engine choice persists, but detailed
   receipts/logs are local. A clone without receipts must rebuild verification with the same tool.
5. **The runner is not a security boundary.** It validates Git and outputs after execution. Local
   gate commands run with user permissions; a restrictive environment is still needed when relevant.
6. **Strict artifact contracts add friction.** Formatting mistakes can fail a step. Keep schemas
   small, provide templates, and refine only failures demonstrated by real use.
7. **Migration is manual.** Vendored installations do not update automatically. Pinning improves
   reproducibility but requires deliberate updates and review of existing application settings.

## Recommendation and validation plan

Retain the shared methodology and two alternative adapters. Avoid per-step routing, automatic
failover, provider-specific copies of skills, and additional orchestration until real use
justifies them. Keep the current rule: select once, execute the entire change with that engine,
and resume with the same engine.

Before calling this ready for unattended application work:

1. Run a complete small roadmap item with Codex in a test application, including a meaningful
   gate failure, repair, review correction, and draft/ready PR publication.
2. Run a separate comparable item with Claude through the same methodology and gate strategy.
3. Verify installation, permissions, selected-engine persistence after a clone, comment filtering,
   timeout behavior, and recovery without discarding local work.
4. Record supported CLI versions, time spent on repairs, session usage, missed defects, and
   whether the artifacts helped human review. Compare process reliability before model preference.
5. Fix demonstrated adapter/contract problems, then expand to larger application changes.

**Acceptance criterion:** each tool can complete the same class of workflow independently,
with current verification evidence and no manual workaround to route a step through the other.
The methodology is portable when the process and contracts hold, not when the generated code
or model decisions happen to match.
