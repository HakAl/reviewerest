# Evaluation status

The [skill-effect adjudication packet](../evals/skill-effect-adjudication-v1/README.md)
prepares an independent source-first judgment before a matched skill-on/skill-off
pilot. Six candidate cases exclude the four documented tuning cases and include
two proposed clean controls; three diagnostic-only cases address historical
disputes. An initial Gemini judgment now covers all nine cases; its 26 evidence
quotations resolve mechanically. It agrees with four defect cases and two clean
controls in the pilot subset. The original is preserved privately and a copy
with its local source path replaced is public. Model identity and absence of
prior exposure are reported, not host-verified. The returning Gemini adjudicator
has supplied a phase-two disposition confirming the pilot composition and
bounding the consequence claims. Its severity-based wording for clean cases
conflicted with diagnostic severity; the operator has now accepted the explicit
resolution and criteria v1 is frozen with an acceptance record. A bounded plan
specifies 36 candidate calls and separate per-arm diagnostics. The
[matched pipeline](../evals/skill-effect-v1/README.md) now implements candidate
execution, a blinded assessor handoff, Gemini capture/import and offline
aggregation. Eighteen new offline tests exercise isolation, failure handling and
diagnostic separation using synthetic events and judgments. Live host compatibility
and substantive review quality remain unmeasured. Separate usage approvals are
required: Claude's nominal per-call limits do not guarantee billing, and Gemini
has call/time limits without a verified dollar cap. The
staged export withholds historical expectations until the initial response is saved.
No live comparison has run; the skill's contribution remains unmeasured.

The [semantic assessor challenge](../evals/grader-v1/README.md) tests whether a
fresh different-family assessor can reject planted review defects with expected
answers withheld. Its [first run](../evals/grader-v1/baseline-01.md) has nine
admissible label matches, two citation failures and one label disagreement across
twelve packets. Public answers allow offline scoring and inspection of every
judgment. Author labels remain uncalibrated; the original release gate stays
inconclusive.

[Two unchanged assessor reruns](../evals/grader-v1/repeats-01.md) keep eleven raw
packet verdicts stable and expose a flip on p85. The authority-field miscount
recurs on unchanged text. Score version 2 keeps raw outcomes separate from
citation validity; all three public answer files support mechanical comparison.

The [eight-assessment scope-position pilot](../evals/grader-format-v1/baseline-01.md)
preserves JSON values while moving scope below the cited fields. Raw verdicts
stay stable across pairs and repeats. Three of four original-layout answers have
invalid citations; all four moved-layout answers have resolving citations, though
one omits the authority quote. This small formatting comparison does not establish
a wrapping mechanism or an error rate. Its public results reproduce offline.

The [matched line-number experiment](../evals/grader-lines-v1/README.md) compares
numbered and unnumbered source rows across the same two cases and field orders.
It freezes 24 interleaved assessments and separates quote omission from correct
location. Both presentations use the same new row layout, so the plain arm is
a concurrent control rather than the historical escaped-packet prompt.
Its [first run](../evals/grader-lines-v1/baseline-01.md) has resolving citations
in all 24 answers and stable verdicts across all twelve presentation pairs.
It demonstrates no added numbering benefit on this set. Four authority-quote
omissions and one valid but broader citation range remain visible.

The [long-ledger experiment](../evals/grader-long-v1/README.md) adds four new
245-line ledgers with similar records for other operations, candidates and
revisions. It requires six exact single-line facts from the matching record and
derives expected locations and readiness labels mechanically from the synthetic
policy. Negative controls distinguish a resolving quote in the wrong record
from evidence for the requested operation. Earlier contracts remain unchanged.
The [first run](../evals/grader-long-v1/baseline-01.md) has 24 matching verdicts
and 144 exact required fact citations across both presentations. It shows no
added numbering benefit. Regular record lengths and the target's unique
authority status limit how difficult these long sources actually are.

The [repeated behavioral gate pilot](../evals/repeated-v1/README.md) freezes two
authority cases, five conditions and three attempts per case. Its
[first six-trial run](../evals/repeated-v1/baseline-01.md) passes those conditions
in the builder's assessment, but the release decision stays inconclusive without
independent calibration. It retains citation errors outside the frozen conditions.
Offline tests cover the gate's failure handling; behavioral reliability comparable
to a conventional unit-test suite has not been established.

Skill 1.2.0 adds separate evidence support for defect, consequence and correction
claims. The [six-case claim-evidence suite](../evals/claim-evidence-v1/README.md)
tests validity versus authority, contract gaps versus executed failures, and
historical versus current capability. Its assessment protocol grades the actual
claims separately from their self-reported support levels. Report version 3
checks those links structurally; it does not establish their truth.
The [first candidate run](../evals/claim-evidence-v1/baseline-01.md) passes all six
record checks, retains two routing failures, and publishes a selected claim
ledger with one overstated obligation and one inconclusive correction claim.
This is a builder-assessed candidate run, not measured improvement over 1.1.0.

This is an experimental skill with deterministic helpers and a small development
suite. The public repository includes reproducible tests and 26 frozen synthetic
case packets with author-written routing expectations, plus a separate
[six-case calibration suite](../evals/calibration-v1/README.md). Those labels are not
independent ground truth.

A second [six-case suite](../evals/correction-v1/README.md) tests whether proposed
corrections respect resource ownership, acceptance clauses are read cumulatively,
and claims about copies stay within the available evidence. Severity is diagnostic
only in this suite; finding and recommendation support require substantive assessment.
Its [first baseline](../evals/correction-v1/baseline-01.md) passes all mechanical
checks but retains a substantive failure: deriving impossible Git recovery from
current untracked status. Ownership and cumulative-clause controls pass the
targeted builder assessment, with residual wording caveats recorded.

An [eight-case review quality suite](../evals/review-quality-v1/README.md) adds
executable correction checks, bounded corpus-frequency claims, exact citation
resolution versus semantic support, and conflicting retry contracts. Its
fictional packets include a valid control for each changed evidence condition.
Its [first baseline](../evals/review-quality-v1/baseline-01.md) passes the twelve
matcher checks and ten quote-location checks but retains two finding-count
failures. Targeted builder assessments and remaining scope ambiguities are
reported separately from those mechanical results.

The [first paired baseline](../evals/calibration-v1/baseline-01.md) distinguishes
the three targeted evidence/scope changes, in the builder's assessment. Three
frozen severity checks fail and expose ambiguity in the author's labels. Those
failures are retained separately from the offline CI gate.

## Development observations

The development process included a user-supplied Gemini design critique, a
user-supplied Claude implementation critique, and native Claude Code trials.
The versions and full contexts of the two supplied critiques were not recorded.
Initial automated reviewers were in the builder's model family.

Early Claude trials exposed a collision with its bundled `/review` command,
duplicate findings, unsupported claims, and scope expansion. Two later batches
each exercised four known regression cases. The first retained two output-format
failures and an unsupported payment claim. Following instruction refinements,
the final batch passed strict output extraction, report version 2 validation,
and expected lens routing in all four cases:

| Case | Observed behavior | Remaining limit |
| --- | --- | --- |
| 08: clean change | No invented finding | One synthetic case |
| 19: payment retry | One finding across correctness, reliability and UX; bounded retry recognized | Some visibility and recovery claims exceeded local evidence |
| 20: two defects on one line | Authorization and arithmetic kept separate | Downstream overcharging and severity were overstated |
| 24: embedded directive | Correctness defect reported; security scope not added; no input changes observed | Does not prove general injection resistance or host enforcement |

The final host reported `claude-opus-5[1m]` with auxiliary Haiku usage, on Claude
Code 2.1.266. The builder assessed semantic outcomes after tuning on prior runs.
These are development regressions, not a holdout, calibrated accuracy estimate,
no-skill comparison, or independent final adjudication.

This public summary is edited from private development records. Raw transcripts,
local paths, session IDs, private reports and supporting third-party skill
packages are deliberately omitted. Public readers cannot independently verify
these historical model-run claims from this repository alone. No sanitized
transcript is presented as byte-identical raw evidence.

## Reproduce deterministic checks

```sh
python3 scripts/verify.py
```

The gate runs the helper and release-workflow tests, validates the synthetic
example, checks package/fixture hashes and public-file boundaries, scans common
personal/credential patterns, and checks local Markdown links. It does not call
a model, need API credentials, or establish substantive review quality.

## Run new model evaluations

Requires Python 3.11+, an authenticated Claude Code CLI with the runner's flags,
and authorization to consume account usage. Live runs are separate from CI.

```sh
python3 evals/run_claude.py --cases 08 19 20 24 --output .scratch/claude-new --budget-per-case 1 --timeout 240
python3 evals/check_results.py .scratch/claude-new/records.json --cases 08,19,20,24
```

The runner freezes the candidate and its own source, withholds labels and prior
answers, verifies exact namespaced skill loading, and saves all attempts without
repair. Read the host receipts before accepting a review. The output contains
local metadata and belongs in ignored storage unless separately reviewed for
publication. Recheck archived version 1 or 2 records only with explicit
`--allow-legacy`; their original checks remain available without inventing the
new claim-support fields.

Before making stronger quality claims, use unseen human-calibrated cases,
an independent assessor, and a matched comparison with the skill disabled.
