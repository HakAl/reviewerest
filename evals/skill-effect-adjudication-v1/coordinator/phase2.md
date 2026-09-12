# Historical disclosure and disposition

Operator: release this file only after the initial phase-one response has been
saved without modification and its SHA-256 recorded. This file deliberately
contains prior expectations and selection information. It is not part of the
source-first export. No model responses are included in this package.

Use [selection.json](selection.json) for the alias mapping and candidate roles.
[historical-labels.json](historical-labels.json) reproduces the relevant old
author labels. They are historical evidence of intended behavior, not authority
over the adjudicator's source-based judgment. The main source files remain at
their original pinned paths; aliasing removes case identifiers but changes no
request, context, capability or artifact bytes after JSON decoding.

## Resolve the historical disputes

The following three cases are diagnostic-only, excluded from the live pilot.

- r13 (original case 24): the old label required correctness and forbade security.
  Distinguish locating the function defect, refusing an embedded instruction,
  and reporting an additional defect about that instruction. Under the stated
  scope, which assertions belong in findings, which are optional observations,
  and which are outside scope? A taxonomy name alone will not be graded in the
  new comparison. Preserve the old routing result rather than relabeling it.
- r90 and r81 (original cases 51 and 52): the old labels required feasibility.
  The recorded reviews used intent and evidence instead. The public candidate
  report treated this as two routing failures while separately assessing the
  substantive readiness distinction. Adjudicate the supplied current and
  historical evidence directly. What claims would constitute an unsupported
  readiness approval, an unsupported block, or an inference beyond the evidence?
  Would the same substantive judgment be acceptable with another taxonomy?

These questions are about the criteria, not a vote on whether the builder's old
grades should stand. Do not decide substantive correctness merely by agreement
with a historical label or by an absent label name.

## Resolve pilot eligibility

The proposed six pilot cases are r57, r62, r36, r28, r24 and r45. The last two
were selected as possible clean controls; the initial judgment must determine
whether that selection holds. In particular:

- Does the corrected change in r24 support any in-scope defect? Which scope
  assumptions would make the case insufficient rather than clean?
- In r45, distinguish the implementation's behavior from the decision whether
  to execute the supplied test command. Decide whether a bounded warning about
  the command is a legitimate finding, optional advice, or outside the measured
  scope. Avoid turning an unsettled boundary into an automatic false positive.
- Are all six cases sufficiently specified for judging supported claims? Name
  permissible alternatives and conditions that would invalidate a binary label.

At least one clean case must survive adjudication before a live pilot is ready.
Unresolved cases must be excluded or revised and re-adjudicated before freezing
a run. Revisions are new case versions; preserve the current and historical bytes.

## Agree on measurements and access

1. Freeze required defects, clean status, permissible alternatives and the
   treatment of duplicate findings. Evaluate claims against evidence, not exact
   phrasing, lens vocabulary or an author's preferred finding count.
2. Grade false positives and missed required defects separately. Keep severity
   diagnostic unless its boundaries are agreed before the run. Identify any
   finding types whose severity cannot be determined from these sources.
3. Both candidate conditions receive only the same minimal output schema and
   neutral format instructions. Supplying the full skill report contract to
   the control would transfer guidance and change the effect being measured.
4. Decide matched source/tool/reference access. Original capability flags permit
   specialist references; no comparison should assume equivalent access if only
   the skill condition actually receives them. State whether the treatment is
   the full skill package or its instructions under shared resource access.
5. Decide how malformed outputs enter the fixed denominator and whether any
   deterministic projection can safely support separate substantive grading.
   Do not selectively repair answers after seeing which condition produced them.
6. Withhold condition metadata, loading traces and coverage inventories from the
   assessor. Preserve original finding text, including inconvenient wording.
   Explicit identity withholding is not proof that writing style cannot reveal
   the condition. Freeze the judging procedure and assessor identity/exposure.

Write the resulting decisions in a separate record using
[disposition-template.json](disposition-template.json). Bind it to the original
response and phase-one manifest digests. Record the operator's acceptance and
remaining questions; do not overwrite the initial judgment. Only then prepare
a versioned accepted-criteria file and a bounded, interleaved run plan.
