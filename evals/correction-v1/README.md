# Corrections and evidence, version 1

Six fictional packets extend evaluation from finding support to correction
validity. The skill stays unchanged for the first baseline. Existing suites,
labels and results remain frozen. These cases contain no private project text.

| Pair | Cases | Controlled change | Expected distinction |
| --- | --- | --- | --- |
| Correction ownership | 33, 34 | Swap Relay and Vault resource ownership | A recommendation must follow the actual destination-store owner |
| Cumulative clauses | 35, 36 | Change only the second acceptance clause | Recording a contested response differs from permitting closure while contested |
| Copy evidence | 37, 38 | Add a complete, explicitly bounded storage inventory | Untracked status alone does not establish uniqueness; an inventory can establish absence within its scope |

The ownership pair holds the defect and suggested fix constant. In one case,
the suggested fix repeats the defect; in the other it is valid. Score the
recommendation as carefully as the finding. A plausible alternative that drops
required coverage or expands component responsibilities does not pass.

The preservation pair is about readiness under a fictional policy. It does not
prescribe a universal backup rule. In 37 an unresolved readiness limit or one
supported finding is acceptable. Claiming an existing backup, no backups, or
inevitable total loss without evidence is not. In 38 the inventory is supplied
evidence; the reviewer must not pretend to have conducted it.

## Run and assess

Requires an authenticated Claude Code CLI and authorization to consume usage.
Use a fresh output directory. From the repository root:

```sh
python3 evals/run_claude.py --case-dir evals/correction-v1/cases --cases 33 34 35 36 37 38 --output .scratch/correction-01 --budget-per-case 1 --timeout 240
python3 evals/check_results.py .scratch/correction-01/records.json --expectations evals/correction-v1/expectations.json
```

The runner gives each isolated session one packet, the frozen skill and host
provenance. It does not load or provide the pair description, expectations,
rubric, or other responses. Raw results contain host metadata and stay private.

The checker verifies structure, lens routing and finding-count bounds. Severity
is diagnostic only, following the ambiguity found in the first calibration
suite. Counts cannot establish valid corrections or truthful evidence claims.

Assess every condition in [rubric.json](rubric.json) as pass, fail or inconclusive,
citing response fields and source locations. A pair passes only when all of its
conditions pass in both responses. Missing or ineligible responses are incomplete.
Record assessor identity/family when known, prior exposure, candidate identity,
run reference and limitations. Builder assessment must be labeled as such.

Freeze inputs and labels before running. Retain failures and ambiguous cases;
make any later correction in a new version rather than rewriting this baseline.
Do not tune the skill during the first batch or treat these author-written
cases as independently calibrated ground truth.
