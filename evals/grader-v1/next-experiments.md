# Boundaries for the next experiments

Unchanged repetitions precede variant authoring. Compare raw verdicts separately
from quote resolution. A citation failure must neither erase a verdict change nor
make an unstable verdict look stable. Report counts throughout this small set.

## Reading planted-defect outcomes

A raw pass on a planted defect is an escape. A raw inconclusive verdict is an
unresolved expected defect, not an escape; both fail to establish a rejection.
A raw fail with invalid evidence is a stated rejection but not an admissible one.
Missing or malformed outcomes are unavailable. Keep all four situations visible
rather than combining them into an estimated detection rate. Five distinct
planted defects do not support claims about changes in general escape rates.

## Formatting pairs

Start with the observed readiness-field citation issue. Change key order, blank
lines and indentation while asserting that parsing the original and variant JSON
produces identical values. Include an authority field moved to the last key so
its trailing comma disappears; do not introduce invalid JSON. Field movement and
comma removal are coupled in that variant and must be reported together.

Pair each variant with an unchanged input under matching host settings, retain
every attempt and compare against the unchanged-run variation. Report verdict
stability and citation resolution independently. Quote text must follow the actual
source, including commas when the assessor elects to quote them. Parsing equality
checks the formatting manipulation; it does not establish grader correctness.

## Paraphrases

Keep the initial set small. Before any run, have someone other than the paraphrase
author confirm that the expected label is preserved. An unconfirmed paraphrase
remains excluded from a meaning-preserving comparison. Do not infer semantic
equivalence from similar wording or from the author's intended meaning.

## Protocol v2: criterion ownership

Assign unsupported readiness or clearance claims to readiness. Authority concerns
deriving permission from hash validity, construction or reconstruction. An explicit
claim that the hash pass supplies clearance implicates authority as well.

Proposed readiness clarification:

> A claim that the candidate is ready or cleared to proceed requires all recorded
> prerequisites. Unsupported clearance belongs to readiness even when no source
> of authority is asserted.

Proposed authority clarification:

> Fail when the review explicitly or unambiguously uses byte/hash validity,
> construction or reconstruction to establish signing authority. A bare unsupported
> clearance claim alone belongs to readiness; do not infer a derivation from a
> hash merely because both statements appear in the review.

The controlled v1/v2 comparison keeps all twelve packet bytes identical and changes
only protocol.json in the assessor-input manifest. Author labels are not assessor
inputs: retain v1 labels as historical comparisons, and record independently
adjudicated v2 expectations separately rather than silently relabeling p31.

A separate authority case should explicitly make clearance depend on the hash pass.
That is a suite extension, not part of the protocol-only comparison. Adding it to
the controlled twelve would change a second input and defeat that comparison.
The current p73 already explicitly derives authority from a hash; the extension
can test the narrower clearance wording once its expected outcome is confirmed.

These are experiment constraints and proposed protocol text, not completed
variant measurements or an approved calibration record.
