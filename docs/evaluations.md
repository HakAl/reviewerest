# Evaluation status

This is an experimental skill with deterministic helpers and a small development
suite. The public repository includes reproducible tests and 26 frozen synthetic
case packets with author-written routing expectations, plus a separate
[six-case calibration suite](../evals/calibration-v1/README.md). Those labels are not
independent ground truth.

A second [six-case suite](../evals/correction-v1/README.md) tests whether proposed
corrections respect resource ownership, acceptance clauses are read cumulatively,
and claims about copies stay within the available evidence. Severity is diagnostic
only in this suite; finding and recommendation support require substantive assessment.

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
publication. Recheck old version 1 records only with explicit `--allow-legacy`.

Before making stronger quality claims, use unseen human-calibrated cases,
an independent assessor, and a matched comparison with the skill disabled.
