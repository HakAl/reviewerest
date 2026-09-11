# First repeated authority pilot

Six planned Claude reviews completed: three per case, with no repairs, replacements
or retries. The builder assessed all thirty condition entries as passing.
The gate returned `observed_behavior: pass` and `decision: inconclusive`, exit 4,
because no independent calibration record exists. This is a variation pilot,
not a measured regression comparison or evidence of unit-test-like reliability.

## Frozen setup

- Candidate and runner commit: `30a7a7ff4410b4906e4a55578dd76803155c7253`.
- Skill 1.2.0, unchanged from the previous claim-evidence run.
- Policy: [policy.json](policy.json), SHA-256
  `fc0f0ec1b4567204a1a0349f5d7fad0b28ebc248270c388f98720f2117a0eb0f`.
- Cases 47 and 48 retain their original bytes. Only the recorded authority status
  differs: unchecked versus verified, alongside passing hash validation and approval.
- Order: 47, 48, 48, 47, 47, 48. Each trial used a fresh process and workspace.
- Claude Code 2.1.268 reported `claude-opus-5[1m]` throughout, with auxiliary
  `claude-haiku-4-5-20251001` usage. This used the CLI default model.
- Declared usage cap: $6 total, $1 per trial; summed CLI cost estimates: $1.687717.
  These are host estimates, not a billing reconciliation.

The policy, candidate and runner were frozen before the first invocation.
During the run, receipt checking was tightened to require an exact CLI version
and a validator matching the evaluated package. The result also records hashes
of its gate, validator and assessment inputs. Those changes did not alter the
policy, runner or review inputs, and were applied to every captured trial.

## Results within the frozen conditions

| Trial | Readiness | Authority | Consequence | Correction | Attribution |
| --- | --- | --- | --- | --- | --- |
| r01-47 | Pass | Pass | Pass | Pass | Pass |
| r01-48 | Pass | Pass | Pass | Pass | Pass |
| r02-48 | Pass | Pass | Pass | Pass | Pass |
| r02-47 | Pass | Pass | Pass | Pass | Pass |
| r03-47 | Pass | Pass | Pass | Pass | Pass |
| r03-48 | Pass | Pass | Pass | Pass | Pass |

The unchecked case produced one readiness blocker in each trial. All three
verified controls accepted the supplied readiness record without inventing a
defect. Neither case treated valid bytes as authority. The reviews attributed
the supplied observations, preserved the three prerequisites in any correction,
and did not assert executed signing or demonstrated downstream harm.

The [assessment ledger](assessment-01.json) binds each judgment to its saved
response hash and identifies supporting fields. These are the Codex builder's
judgments after reading the complete responses with knowledge of the expected
answers. They are neither independent nor blinded. Model self-labels were not
used as the grading oracle.

Mechanical inspection found all six invocations eligible, with exact skill
loading, unchanged supplied workspaces, matching captured and saved records,
preserved provenance and valid version 3 structure. No planned trial was omitted.
These checks establish record consistency, not semantic correctness.

## Variation outside the five conditions

In r01-47, evidence e3 and finding f1 cite readiness.json line 6 for the unchecked
authority field, which is actually on line 5. Evidence e4 also cites a range
that omits the operator-approval line it discusses. The readiness conclusion
still follows from the packet, but these locations are wrong. Citation accuracy
was not a frozen pilot condition; the observation is retained separately rather
than changing the grading criteria after seeing the answer.

In r03-47, the title says authority was never verified. Its trigger, assumptions
and limits bind that statement to the declared-complete supplied inventory.
The complete response meets the frozen condition, while the title alone is
broader than its qualification. This is useful material for grader calibration.

No variation was judged to violate the five targeted conditions across these
three repeats. That says little about rare failures, new tasks, model changes,
or grading error. The cases were already known to the builder. There was no
earlier-version or no-skill arm, no independent adjudicator, and no estimate of
false alarms or regression-detection sensitivity.

## Next calibration milestone

Have an independent assessor grade supported and deliberately altered responses,
including reasonable alternative wording and ambiguous cases. Compare judgments,
resolve disagreements, and freeze a grading protocol before collecting matched
unchanged-candidate and known-regression runs. Choose a blocking threshold from
those measurements. The current one-confirmed-failure rule is a pilot policy
choice, not a statistically calibrated threshold.

Raw captures remain private because they contain host/session metadata. This
edited summary and its assessment ledger do not let public readers independently
verify the model-run claims. The runner and offline failure controls are public
so new experiments can preserve their own evidence.
