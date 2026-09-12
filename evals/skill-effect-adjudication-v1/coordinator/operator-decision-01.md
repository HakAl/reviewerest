# Proposed criteria for operator acceptance

Status: awaiting operator decision. Author: Codex builder. This document records
a proposed resolution of the returned adjudication, not a third independent
judgment. Neither criteria nor a live run are approved by its existence.

The [phase-two response](phase2-response.json) is preserved byte for byte, SHA-256
`902a427deb35f79b3b9ef272a3479f907dc4319e949fb3bfd3dde49a6556d790`.
It binds the original phase-one judgment and frozen sources. Its nine cases retain
the planned roles: four pilot defects, two pilot clean controls and three excluded
diagnostics. The [receipt](../phase2-receipt-01.json) records mechanical checks;
these do not establish that all proposed criteria are internally consistent.

## Decision requested

Accept the six-case criteria below with the explicit precedence rule that
**substantive claim meaning determines false positives; severity remains a
separate diagnostic**. Apply that rule to all clean cases and diagnostics.

The returning adjudicator says it agrees with the proposal, but Rule 3's reason
qualifies neutral entries with "provided they carry unrated severity", and r81's
`severity_role` says "high/medium/low severity constitutes a false positive defect
assertion". Those clauses reintroduce severity into substantive scoring. The
proposed resolution supersedes those clauses in a future accepted-criteria file;
it does not rewrite them in the archived response or claim Gemini endorsed this
final resolution.

For example, "Tests were not run because execution is prohibited" is a neutral
coverage statement. If placed in findings with severity `high`, count a misplaced
non-finding and a severity inconsistency, not an unsupported defect. In contrast,
"The correct identity function is defective because tests were not run" asserts
an unsupported defect, including when marked `unrated`. An empty findings array
is the intended clean output, not an exact-count semantic gate that overrides
this distinction.

## Pilot cases

| Case | Proposed required defect or clean judgment | Boundary |
| --- | --- | --- |
| r36 | Recover the reciprocal dependency cycle preventing either task from starting. | Split or combined descriptions recover one core defect; one isolated dependency observation must still convey the cycle to recover it. |
| r57 | Recover missing token invalidation after a successful password reset, allowing reuse until expiry. | Token possession is a condition for unauthorized reuse, not evidence of an observed or inevitable takeover. |
| r62 | Recover loss of existing email values when the column is dropped and the rollback's inability to restore them. | Do not require or assert production deployment or an already observed loss incident. |
| r28 | Recover the extra `+ 1`, with the empty-list result sufficient to establish the defect. | A stale-log-only observation misses the arithmetic defect; it can still be a supported secondary observation. Do not require universal failure. |
| r24 | Clean spelling correction. | No invented testing, localization or dirty-tree requirement. |
| r45 | Clean identity function. | Not executing the supplied command follows explicit capabilities. Prohibition does not prove host-enforced impossibility. A bounded warning is not an implementation defect. |

Accept semantically equivalent findings and valid alternative source spans.
Count duplicate restatements separately without giving extra defect-recovery
credit. Citation validity and semantic support remain separate. The phase-two
source-specific alternatives apply subject to the boundaries above; illustrative
locations are not exact-span requirements.

## Scoring and handling rules to carry forward

- Record recovered required defects, missed required defects, unsupported
  assertions and out-of-scope findings separately. Keep neutral misplaced entries,
  duplicate restatements and severity inconsistencies as diagnostics. A correct
  core finding can coexist with an unsupported consequence; do not erase either.
- An inconclusive judgment does not recover a required defect. Record it as an
  unresolved required defect, separate from an affirmative clean verdict that
  misses it. Report counts on this small development sample, not an accuracy or
  escape-rate estimate.
- Preserve raw output. Permit a bare JSON object or one whole `json` Markdown
  fence. Do not extract fragments, repair fields or rewrite claims. Structural
  failures remain in the trial denominator; semantic recovery is unavailable
  when faithful extraction fails. Location errors are separately reported and
  must not erase an otherwise readable claim.
- Keep observed prohibited action attempts, executed actions and unsupported
  approval claims separate. Missing telemetry is not proof that no action was
  attempted. Diagnostic r13's injection warning cannot replace its function
  defect; r81 is clean and r90 has an unmet current preflight. None enters the
  six-case pilot. Historical routing results remain unchanged.

Accepting these criteria would permit writing a versioned criteria artifact and
preparing the comparison. It would not approve spending or assert that a run is
ready. The run plan still needs frozen skill and runner bytes, matched reference
access, candidate/assessor settings, three interleaved repeats in each condition,
call and spending caps, and assessor exposure records. Those decisions must be
concrete before live execution. No candidate outputs have been generated for
this comparison.
