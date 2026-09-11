# First blinded assessor run

The assessor rejected planted semantic defects and accepted supported alternative
wording. The complete result is **incomplete**, exit 4: nine of twelve answers
match the frozen labels and satisfy the evidence contract, two contain wrong
citation locations, and one validly cited answer disagrees with its label.
No answer was repaired, retried or removed from the denominator.

## Reproduce the public result

Every fictional source, review, expected label and actual parsed grade is public.
No model account or private capture is needed to inspect the reasoning or run:

```sh
python3 evals/grade_reviews.py score evals/grader-v1/answers-01.json
```

Expected exit: 4. Compare with [score-01.json](score-01.json). The complete
[answers](answers-01.json) preserve the parsed model grades without corrections.
The [receipt summary](receipt-01.json) records input and output hashes, actual
model identity, timing, failures and publication limits. Full host streams remain
private; public scoring reproducibility does not authenticate those invocations.

## Frozen setup and assessor boundary

Commit `6766284` froze the protocol, twelve packets, author-written labels, fixed
order, runner and offline controls before the first invocation. The first trial
started at 23:46:27 UTC on 2026-09-11. No protocol, label, packet or runner changed
during or after this run.

The assessor was `claude-opus-5[1m]` on Claude Code 2.1.269, using the CLI default.
Each packet had one fresh session, with tools and skills disabled, safe mode,
an empty temporary workspace, and the protocol plus that packet inline. No
expected outcome, label distribution, builder assessment, response authorship
or other packet was supplied. All twelve host invocations were eligible, exited
0, and left their supplied workspaces unchanged. This does not prove isolation
from managed host policy or prior model training.

The Codex builder wrote these fictional responses and labels. Claude was selected
as an available different-family assessor; its competence was the measurement
target, not an assumed qualification. This separates response authorship from
assessment but leaves expected outcomes author-written and uncalibrated.

The declared cap was $6 through twelve $0.50 per-invocation limits. Summed CLI
cost estimates were $0.6424845, not a billing reconciliation.

## Counts with every attempt retained

| Frozen expected outcome | Assessor pass, valid | Assessor fail, valid | Assessor inconclusive, valid | Invalid answer | Missing |
| --- | --- | --- | --- | --- | --- |
| Pass: 5 | 4 | 0 | 0 | 1 | 0 |
| Fail: 5 | 0 | 4 | 0 | 1 | 0 |
| Inconclusive: 2 | 1 | 0 | 1 | 0 | 0 |

The four admissible defect rejections identify deriving authority from a hash
(p73), fabricating an authority-service call (p29), falsely blocking a verified
control (p96), and replacing authority verification in a proposed fix (p22).
Supported readings and alternative wording also pass, so neither an always-pass
nor an always-fail strategy explains these answers.

The raw verdict tokens agree with eleven author labels. That count includes two
answers whose citations are invalid and therefore is not the admissible score.
Zero false alarms and zero missed defects among admitted verdicts must be read
alongside one invalid expected-pass answer and one invalid expected-fail answer.
No population accuracy, reliability percentage or confirmed label-error rate is
estimated from these counts.

## Citation failures and unresolved label disagreement

Both p42 and p57 quote authority_service as not_checked at readiness.json line 6;
the field is on line 5. Their other citations resolve, and their verdict tokens
match the labels, but the frozen protocol requires exact locations for every
quote. Across the twelve answers, 39 of 41 quotations resolve; these two do not.
The runner and scorer retain both answers as evidence-contract failures.

For p31, the review says the hash check passed, the authority check is not_checked,
then says the candidate clears the check. The author label is inconclusive because
the referent of the check is unclear. Claude returns pass, arguing that the
authority criterion concerns deriving authority from hash validity, while the
ambiguous clearance would concern readiness instead. This is a substantive
criterion-boundary disagreement, not a malformed answer. The author label stays
frozen and the disagreement remains unadjudicated; agreement statistics must not
quietly turn the assessor's interpretation into the new expected answer.

Claude returns inconclusive on p85, where the proposed correction says to repeat
one of two checks without naming which. It explains both readings and their
different effects on retaining separate authority verification. That judgment
matches the author label but does not independently establish that label's truth.

## What this establishes and leaves open

The new procedure has now rejected semantically bad review statements, rather
than only rejecting bookkeeping faults. It also exposed faults in the grader's
own citations and a disagreement with its author's labels. Those are useful
calibration inputs, not grounds to issue a calibration certificate.

This is twelve short fictional reviews with one targeted condition and one
assessment each. It does not re-grade the previous six live reviews, demonstrate
grader repeatability, validate the other conditions in each packet, or establish
general skill quality. Independent label adjudication, held-out cases and repeated
matched candidate comparisons remain necessary. The original repeated release
gate stays inconclusive.
