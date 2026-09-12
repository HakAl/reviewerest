# Draft skill-effect run plan: grading and reporting

Status: preparation only. Criteria acceptance remains unset. This is not a frozen
execution plan and does not authorize model calls or spending. It specifies the
grading records and reporting commitments to carry into the eventual run plan.

The pending [operator criteria decision](operator-decision-01.md) remains the
source of proposed semantic rules. Candidate output stays restricted to finding,
location, claim and severity. Assessor records are separate artifacts; they may
contain grading explanations and evidence without expanding the candidate schema
or revealing the candidate's condition.

## Per-entry assessor record

Assign each original candidate entry a stable identifier before assessment.
Preserve the exact entry and its original order. For every entry, require:

- A substantive classification: supported in-scope defect, supported secondary
  observation, neutral non-finding, unsupported assertion, out-of-scope assertion,
  mixed, or unresolved.
- A concise reason explaining the classification with located source evidence
  where applicable. Explain what the entry asserts and why the source supports
  or fails to support it. A label or severity token is not a reason.
- Required-defect identifiers recovered, if any, and duplicate/root-cause
  grouping. Splitting one defect cannot create extra recovery credit.
- Independent diagnostics for misplaced neutral entry and severity mismatch,
  each with its own reason, plus location validity as a separate result.

Mixed entries require identification of their supported and unsupported
assertions. A correctly located defect with an exaggerated consequence can
recover the defect and still contain an unsupported assertion. Do not rewrite
the candidate or discard either part. A coverage note accompanying a substantive
finding does not by itself make the whole entry a misplaced neutral entry.

Classify claim meaning before considering severity. A neutral-only entry in the
findings array is a misplaced non-finding. If that entry carries high, medium or
low severity, also record a severity mismatch. It is not a substantive false
positive unless its wording makes an unsupported defect or obligation claim.
An unsupported assertion remains unsupported when marked `unrated`.

For substantive findings, retain the severity token and its stated consequence.
Do not invent a calibrated high-versus-medium boundary: unresolved severity
calibration stays unresolved. The simple token comparison only follows the
assessor's semantic classification of an entry as neutral.

Empty findings arrays require a case-level explanation of clean status or missed
required defects; no entry record is fabricated. Record unresolved required
defects separately from recovered or affirmatively missed defects. Missing
assessment explanations make the assessment incomplete, not automatically wrong
candidate behavior. Preserve the original assessment and any later completion.

## Reporting commitments before execution

After assessment records are saved, join them to the private condition mapping.
Report these counts separately for each arm, with trial and case breakdowns:

| Measure | Counting unit and treatment |
| --- | --- |
| Required defects recovered | Unique required defect per trial, regardless of entry count. |
| Required defects missed or unresolved | Separate counts; neither is recovery. Unavailable assessment remains visible. |
| Unsupported or out-of-scope assertions | Separate counts of entries containing each, with reasons; mixed entries may appear in both. |
| Clean trials with unsupported defect/obligation claims | Count affected clean trials as well as offending entries. |
| Misplaced neutral notes | Count neutral-only entries placed in findings, irrespective of severity. Diagnostic only. |
| Severity mismatches | Count established mismatches separately, alongside unresolved severity judgments and token distributions. Diagnostic only. |
| Duplicate restatements | Count extra entries about an already identified core defect. Diagnostic only. |
| Structural and location failures | Report separately; retain original attempts and planned denominators. |
| Observed host behavior | Distinguish attempts, execution, blocked actions and unavailable telemetry. |

Misplaced-note and severity-mismatch counts cannot be folded into recovery,
false-positive counts or a combined quality score after seeing results. Do not
present a sum of overlapping entry counts as a unique-finding total. Report
assessment completeness beside all counts; unknown is not zero.

The proposed design has six cases, two conditions and three repeats: 18 trials
per arm, including six clean-case trials and twelve required-defect opportunities.
Those are planned denominators, not completed observations or independent source
cases. Keep every scheduled trial represented if parsing, invocation or assessment
fails. Show paired outcomes and repeat variation, without an accuracy or causal
generalization from this small development sample. Whether both arms recover all
seeded defects is a hypothesis, not an observed result.

## Remaining execution-plan work

Before any live call, record operator criteria acceptance and freeze a criteria
version. Then specify and commit the exact skill/package, runner and assessor
protocol digests; treatment and matched reference access; isolated workspace and
loading checks; candidate and assessor identities, settings and exposure records;
interleaved trial schedule; call, spending and timeout caps; failure handling; and
explicit live-run authorization. The future assessment validator and aggregation
tests must check per-entry coverage and separate diagnostic reporting. This draft
does not claim those mechanisms have been implemented or tested.
