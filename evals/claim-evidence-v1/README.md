# Claim evidence, version 1

Six fictional cases test whether a review's claims change appropriately when
the available evidence changes. The candidate introduces skill 1.2.0 and report
version 3. Freeze the cases and [rubric](rubric.json) before running; retain
failures without relabeling or repairing responses.

The [first candidate run](baseline-01.md) passes all six version 3 record checks
but retains two routing failures. Its edited [claim ledger](assessment-01.json)
includes an overstated obligation and inconclusive correction advice.

| Pair | Cases | Changed evidence | Required distinction |
| --- | --- | --- | --- |
| Validity and authority | 47, 48 | Separate authority verification absent or recorded | Matching bytes cannot establish signing permission |
| Contract and execution | 49, 50 | Add consumer implementation and bounded execution result | A missing contract step differs from demonstrated acceptance; neither proves signing |
| Historical and current | 51, 52 | Add current preflight for the actual worker and sandbox | Old failure does not establish present incapability; current evidence can resolve readiness |

Readiness requirements in these packets are fictional project policies. Do not
generalize them into universal approval or preflight requirements. Host receipts
are synthetic inputs, not assertions about a real worker or signing service.
The deterministic tests reproduce the modified-candidate acceptance and show
that reconstruction succeeds in both authority states.

## Run

Requires Python 3.11+, authenticated Claude Code and authorization to consume
usage. Use a new output directory:

```sh
python3 evals/run_claude.py --case-dir evals/claim-evidence-v1/cases --cases 47 48 49 50 51 52 --output .scratch/claim-evidence-01 --budget-per-case 1 --timeout 240
python3 evals/check_results.py .scratch/claim-evidence-01/records.json --expectations evals/claim-evidence-v1/expectations.json
```

The runner supplies one packet, the frozen skill and host provenance per session.
It withholds labels, rubric and other responses. Raw traces remain private.
The mechanical checker assesses structure, claim-support links and lens routing.
There are no finding-count or severity gates in this suite.

## Measure the claims

Use an assessor separate from the candidate. Record identity, prior exposure,
review identity and evidence references; label builder assessment as such.
Read the complete response, including suggestions and claims outside findings.

First extract material claims into an assessment ledger: case, response location,
exact excerpt, role (defect, consequence or correction), supporting artifact
locations, judgment and reason. Split compound claims when their support differs.
Use `supported`, `overstated`, or `inconclusive`; a declared support level is not
evidence for itself. A correctly qualified unknown is supported as a statement
of limits. Do not count repeated paraphrases as independent evidence.

Report separate measures, with numerators and denominators:

- **Detection:** how many required problems or readiness limits were identified,
  plus whether each clean control was accepted. No findings alone cannot earn
  a positive result without supported coverage.
- **Consequence overstatement:** overstated consequence claims divided by
  supported plus overstated consequence claims. Report inconclusive and missing
  assessments separately; a zero denominator is unavailable, not zero error.
- **Correction support:** supported corrections divided by adjudicated corrections.
  Identify which were executed and which were assessed against contract invariants.
  Preserve authority, ownership and valid behavior when judging corrections.
- **Pair success:** all frozen conditions pass in both responses. Record fail or
  inconclusive conditions individually, not merely a total.

State extraction coverage. A selected sample is a sample, not the complete
response's error rate. These small author-written cases and builder judgments
do not establish calibrated confidence, independent ground truth or population
accuracy. Independent assessors can disagree about claim boundaries; retain
their disagreements instead of averaging them into certainty.

For an assessor-authored ledger in the shape of [assessment-01.json](assessment-01.json),
`python3 evals/score_claims.py <ledger.json>` reproduces counts and denominators.
It requires attribution and coverage descriptions but does not verify source
quotes, extraction completeness or judgments. Empty denominators yield null
rates; inconclusive counts remain visible alongside adjudicated counts.

Archived version 1 or 2 responses require `--allow-legacy`; their missing claim
support fields must not be filled retrospectively. New candidate runs use version
3. Existing frozen suites can still be run against the new candidate, but their
historical results concern the earlier skill.
