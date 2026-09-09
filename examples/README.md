# Example: cancellation plan review

This is a fictional, author-written example showing the report format. It is
not a captured model response or a review of a real project.

**Request:** Review this upload-status plan for correctness and UX. Keep the
review limited to how terminal outcomes are shown.

**Artifacts:** [contract.md](contract.md) and [plan.md](plan.md).

## Illustrative review

Scope: the two supplied documents, with correctness and UX selected. Static
comparison only; no implementation or user testing was available.

**Major: canceled uploads remain labeled "Uploading".**
[plan.md:5](plan.md#status-table) maps every outcome other than success or error
to the active state. The contract explicitly includes cancellation as a terminal
outcome. After a user cancels, the proposed view would therefore show ongoing
work and offer Cancel again.

Add a canceled row with an Upload again action. This is one root cause affecting
both correctness and UX, so it produces one finding.

**What holds up:** the plan distinguishes successful and failed uploads and
provides Retry after a failure.

**Limits:** no implementation was inspected. Keyboard operation, actual timing,
and user comprehension remain untested. This finding concerns the supplied
state mapping, not every aspect of the upload feature.

A matching [structured record](review.json) passes the version 2 validator.
That validates the record's structure, not the truth of an actual model review.
