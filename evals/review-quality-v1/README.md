# Review quality controls, version 1

Eight fictional packets test the quality of corrections and evidence claims.
The skill stays unchanged for the first baseline. Inputs, expectations and the
separate matcher oracle are frozen before running. No private project text is
included.

| Pair | Cases | Controlled change | Expected distinction |
| --- | --- | --- | --- |
| Correction recall | 39, 40 | Proposed regex gains optional plural suffix | Reject a fix that loses required plurals; accept the valid replacement |
| Negative evidence | 41, 42 | Complete corpus count changes from 0/4 to 3/4 | Preserve a possible bug while accepting only supported frequency claims |
| Citation support | 43, 44 | One fictional protocol clause changes | An exact quote can resolve without supporting a claim; a different clause can supply support |
| Contract discrepancy | 45, 46 | Retry policies change from conflicting to aligned | Identify disagreement before prescribing behavior; preserve the required eventual abort |

The matcher oracle contains twelve concrete inputs and expected booleans. It is
withheld from the reviewer but author-written, not independent ground truth.
The tests execute the two fixture patches and prove that the invalid one loses
three plural examples. They also recalculate the corpus observations and check
retry behavior before and after budget exhaustion.

## Run and assess

Requires an authenticated Claude Code CLI and authorization to consume usage.
Use a fresh output directory. From the repository root:

```sh
python3 evals/run_claude.py --case-dir evals/review-quality-v1/cases --cases 39 40 41 42 43 44 45 46 --output .scratch/review-quality-01 --budget-per-case 1 --timeout 240
python3 evals/check_results.py .scratch/review-quality-01/records.json --expectations evals/review-quality-v1/expectations.json
python3 evals/check_citations.py evals/review-quality-v1/cases/43.json .scratch/review-quality-01/43/record.json --require-quotes
python3 evals/check_citations.py evals/review-quality-v1/cases/44.json .scratch/review-quality-01/44/record.json --require-quotes
```

Each isolated session receives one packet, the frozen skill and host provenance.
Expectations, rubric, oracle and other responses are withheld. Preserve raw
attempts privately, including failures. Do not repair or rerun failed answers
inside the first baseline.

Cases 39 and 40 request a `proposed_replacement` field. Inspect any proposed
module before executing it against [matcher-oracle.json](matcher-oracle.json)
in a separate, bounded host check. Do not automatically execute model output.
Record an unperformed check if inspection cannot establish that execution is
appropriate. The review session itself has no execution or editing permission.

Cases 43 and 44 request exact `quote` annotations in evidence items.
[check_citations.py](../check_citations.py) checks only those annotations against
the supplied packet's source identity, revision and line range. It reads no
external source paths. Missing annotations are counted as unchecked, or rejected
with `--require-quotes`; no checked citations means failure. A successful receipt
explicitly leaves semantic support unverified. Freeform citations elsewhere in
a record are outside this check.

Assess every condition in [rubric.json](rubric.json) as pass, fail or inconclusive,
with response fields and source locations. All conditions in both responses
must pass for a pair to pass. Record assessor identity, prior exposure, candidate
identity, check results and limits. Severity is diagnostic only. The record
checker verifies structure, lens routing and count bounds, not semantic quality.

These development controls arose from a user-supplied assessment by Claude of
a review produced through Antigravity CLI. The underlying Antigravity model was
not recorded. A new Claude baseline is a separate run, not a reproduction of
that review or an independent adjudication of this suite.
