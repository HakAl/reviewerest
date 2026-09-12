# Adjudication before a skill-effect pilot

Status: the operator accepted criteria v1 with the severity clarification.
[Resolved criteria](accepted-criteria-v1.json), the explicit
[acceptance record](operator-acceptance-01.json) and their
[frozen manifest](criteria-manifest-v1.json) are now recorded. No live comparison
or spending is approved. Historical proposals below retain their original status.

The [initial response](initial-01.json) is a public copy with only its reported
local source path replaced. The [receipt](initial-receipt-01.json) binds that copy
and the private byte-identical original to the frozen manifest. All 26 located
evidence quotations resolve. Model identity and source-only access are reported,
not authenticated by a host trace. These checks do not verify the judgments.

The [phase-two response](coordinator/phase2-response.json) confirms four defect
cases and two clean controls in the pilot, with bounded consequences and
diagnostic severity. It is public byte for byte; its
[receipt](phase2-receipt-01.json) verifies bindings and selection roles.
Its clean-case wording lets severity alone determine a false positive despite
accepting diagnostic severity. The
[operator decision proposal](coordinator/operator-decision-01.md) makes the
resolution explicit; the operator has now accepted it. Claim meaning determines
false positives and severity stays diagnostic. The accepted criteria supersede
that conflicting wording without rewriting the initial or phase-two records or
attributing the final resolution to Gemini. Acceptance does not establish a
skill effect.

The [draft run-plan grading requirements](coordinator/run-plan-draft-01.md)
require a reason per assessed entry and commit to separate per-arm diagnostics
for misplaced notes and severity mismatches. They cannot be folded into recovery
or false-positive totals after results are known. The
[bounded comparison plan](coordinator/run-plan-01.md) now specifies 36 candidate
calls, an interleaved schedule, the full-package treatment and proposed limits.
The [matched pipeline](../skill-effect-v1/README.md) is now implemented and tested
offline. Its candidate and assessor usage boundaries require separate explicit
approvals; live host compatibility has not yet been measured. The earlier plan
files preserve the preparation state that preceded implementation.

The question is whether adding the review skill improves finding quality under
a shared minimal output format. Earlier experiments assessed outputs, graders
and evidence handling; they did not establish this effect. This packet prepares
a small comparison by asking an independent adjudicator to settle source-level
criteria before candidate outputs exist.

## Operator workflow

1. Export phase one into a fresh directory, using the command below.
2. Give only its START-HERE.md to the adjudicator, or give the exported directory
   with instructions to start there. It contains the protocol, proposed shared
   schema, response template and nine source cases, with neutral aliases.
3. Have the adjudicator complete an initial source-only judgment. Record identity
   and prior exposure. Save and hash that response before revealing phase two.
4. Then disclose [coordinator/phase2.md](coordinator/phase2.md) and the matching
   historical-label extracts. Preserve the initial response; write subsequent
   disposition separately and bind it to the initial digest.
5. Resolve substantive disagreements with the operator. Freeze accepted criteria
   in a new version before authorizing comparison runs. Unresolved cases remain
   visibly excluded, not silently scored as failures.

```sh
python3 evals/adjudication_packet.py --output .scratch/skill-effect-adjudication-phase1
python3 evals/adjudication_packet.py --record evals/skill-effect-adjudication-v1/initial-01.json
python3 evals/adjudication_packet.py --disposition evals/skill-effect-adjudication-v1/coordinator/phase2-response.json
```

The exporter copies a fixed allowlist and checks its manifest hashes. It never
reads coordinator material, historical labels, model outputs or the skill.
It refuses an existing destination. Its successful exit certifies export and
integrity only; it does not perform adjudication. Use a fresh-context seat with
no repository access if labels are to be withheld: coordinator files are public
and adjacent to phase one in this repository. Prompts alone cannot enforce that
separation. The exported bundle escapes artifact delimiter characters, including
the embedded directive in one diagnostic source.

## Proposed pilot boundary

Six candidates from the original 26 cases cover code, migration and planning,
with two proposed clean controls. The documented tuned cases 08, 19, 20 and 24
are excluded from the live pilot. Three additional packets are diagnostic-only
and address the historical scope/routing disputes; their judgments do not enter
the pilot's sample. Selection and alias mapping are in
[coordinator/selection.json](coordinator/selection.json), withheld during phase one.

These are development cases, not a claimed holdout. Excluding the four known
tuning cases does not establish absence of indirect exposure or influence. The
adjudicator must confirm at least one clean control and bounded defect cases.
If all clean candidates are disputed, the pilot stays unready; do not infer a
clean label from the builder's selection rationale.

At the proposed size, two conditions and three repeats mean 36 candidate review
calls. No calls are authorized or executed by this packet. A later run plan must
pin the skill, common instructions, accepted criteria, host settings, interleaved
schedule, call caps, judging procedure and handling of malformed outputs.

Both conditions would get the same source packet and minimal output schema.
The skill-on condition additionally receives the skill; skill-off must have no
access to it or its report contract. The effect measured would therefore be the
skill's contribution given that shared format, not an unconstrained assistant
versus the complete default skill UX. Original capabilities requesting specialist
references require a matched access policy before running; providing such
references only to one condition would change the treatment being measured.

## What will be judged separately

- Finding validity and in-scope defect recovery, including clean-case false positives.
- Omitted required defects and duplicate restatements, with adjudicated alternatives.
- Formatting and location validity, which do not establish finding truth.
- Severity as a diagnostic until its boundaries are independently agreed.
- Host actions, provenance and actual skill loading in private receipts.

Candidate content exposed to the assessor contains only finding, location, claim
and severity. No taxonomy agreement is a common metric. Extra metadata must not
be silently rewritten or selectively removed from claim text; retain malformed
attempts and decide their handling before execution. Withholding explicit arm
identity does not guarantee that the assessor cannot infer it from writing style.

The helper's minimal-shape validator is a mechanical aid for that proposal. It
accepts empty findings and checks source bounds, but cannot identify false
positives, missed defects, reliable severity, or inferred arm identity. Tests
cover the export boundary, input fidelity and metadata rejection. They are not
independent judgments on these cases. The product skill and all historical
fixtures, expectations and model outputs remain unchanged.
