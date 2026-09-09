# Interaction evidence

Use when selected UX questions require evidence about input, focus, asynchronous state, or recovery. Identify the user's task and which states are actually available.

| Evidence available | Can support | Cannot establish alone |
|---|---|---|
| Screenshot | Visible labels, hierarchy, displayed status, visible control affordances | Keyboard operation, accessible names, focus order, unseen errors |
| Markup/source | Declared roles and names, event wiring, static control semantics | Actual assistive-technology output or successful completion of the running flow |
| Host-supplied isolated interaction results | The inputs, states, and outcomes actually exercised | Other devices, users, states, or full standards compliance |

Trace task start, progress, completion, error, and recovery where relevant. For a failed payment, distinguish an actual charge result from what the UI reports; one missing idempotency boundary can cause several visible symptoms. For controls, inspect whether the intended input method can reach and operate them, whether names convey the action, and whether focus remains usable after a transition. Do not infer runtime success from markup alone.

Use the required accessibility standard/version only when the task establishes it; consult authoritative criteria before assigning a standards violation. A heuristic concern is not a compliance verdict. A screenshot-only request remains bounded to visible evidence even if broader interaction checks would be valuable.

Interaction can mutate session or external state. The reviewer requests isolated execution through the host and consumes the resulting evidence; it does not submit a purchase or alter a live account.

Provenance: original task-specific questions informed by [Nielsen Norman Group's usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), inspected 2026-09-08 in the design phase. The source is live and heuristic, not a pinned accessibility standard.
