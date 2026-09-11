# First claim-evidence candidate run

2026-09-11. Candidate skill 1.2.0, report version 3, cases and rubric were frozen
at `311944c` before six isolated Claude sessions. One attempt per case, no retries
or response repair. Host-reported identity: Claude Code 2.1.268,
`claude-opus-5[1m]`, with auxiliary Haiku usage. Summed execution time was about
416 seconds; CLI-estimated usage was $1.76.

All six responses passed extraction and version 3 structural checks, including
per-claim support links. Two frozen routing checks failed: cases 51 and 52 used
intent and evidence instead of the expected feasibility lens. The checker exited
3. The rubric's three evidence distinctions pass in the builder's assessment;
this is not a clean pass of the full suite.

| Case | Findings | Observed response |
| --- | --- | --- |
| 47 | 1 | Withholds signing readiness for missing authority verification; does not allege a bypass |
| 48 | 0 | Accepts the recorded prerequisites for the exact candidate and operation |
| 49 | 0 | Notes the handoff omission as clarification; leaves unseen consumer and signer behavior unknown |
| 50 | 1 | Marks consumer failure demonstrated, acceptance behavior inspected, and correction conditional |
| 51 | 1 | Withholds readiness for absent current preflight without declaring the tool broken |
| 52 | 0 | Accepts the current S2 preflight despite the historical S1 failure |

## The claim distinction in practice

In case 50 the supplied probe shows a modified candidate being accepted. The
review attributes that executed result to its provider. It derives unconditional
acceptance from the source, but does not extrapolate to signing harm. Its proposed
correction requires confirming digest details and exercising modified and
unmodified candidates. No correction was implemented or executed in this batch.

Case 49 contains the same contract and handoff without consumer implementation
or probe. The review identifies the missing step but recognizes that the contract
binds the consumer, not the handoff document. A compliant unseen consumer could
still perform the check. It recommends an optional clarification and a targeted
inspection or probe, rather than asserting acceptance of invalid candidates.

The worker pair likewise changes its readiness conclusion only when the current
evidence changes. Neither response authorizes a prohibited editing fallback or
claims that implementation has begun. The missing feasibility label is retained
as a routing failure; it does not erase the substantive work done through other
lenses, nor is the frozen expectation rewritten after observing the result.

## Claim-level measurement

The edited [assessment ledger](assessment-01.json) retains 14 selected claims,
exact response excerpts, judgments and reasons. The builder read all responses;
the ledger is a selected sample, not an exhaustive atomic extraction of them.
It includes all three final consequence fields, splitting one into two claims.

| Selected claims | Supported | Overstated | Inconclusive |
| --- | --- | --- | --- |
| Defect or asserted obligation | 3 | 1 | 0 |
| Consequence | 4 | 0 | 0 |
| Correction | 5 | 0 | 1 |

Consequence overstatement is 0/4 in this sample. Correction support is 5/5 among
adjudicated claims, with one additional inconclusive claim reported separately.
These tiny selected denominators are not estimates of general accuracy.

The retained overstatement is case 50's check that the handoff *must* specify
revalidation. The supplied contract requires consumer behavior; it does not
require that document to state it. Executing the faulty consumer does not create
a new documentation obligation. Case 49 handles that distinction more carefully.

The inconclusive correction is the added constant-time comparison advice. The
packet supplies neither a timing threat model nor such a requirement. This
assessment leaves its appropriateness unresolved, rather than treating it as
either a demonstrated need or a defective implementation.

Reproduce the ledger counts without model access:

```sh
python3 evals/score_claims.py evals/claim-evidence-v1/assessment-01.json
```

That helper was added during assessment. It counts explicit assessor judgments,
preserves inconclusive counts and returns null rates for empty denominators.
It does not verify quotations, judge claims, or convert the reviewer's own
support labels into a quality score.

## Limits

All traces contained the exact candidate skill body, preserved host-provided
provenance and left input snapshots unchanged. Capture, candidate, runner and
fixture hashes matched. Raw traces remain private; the public ledger contains
edited excerpts and hashes identifying private originals, not independently
auditable invocation evidence.

The assessor was the Codex builder with prior label knowledge. No independent
adjudication, previous-skill comparison or no-skill comparison ran. These explicit
synthetic cases demonstrate how the new report distinction can be exercised;
they do not establish an accuracy improvement or calibrated confidence. Severity
remains diagnostic. Structural validation cannot detect the retained unsupported
documentation obligation.
