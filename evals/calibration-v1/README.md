# Calibration pairs, version 1

Six fictional packets test three changes in evidence or decision scope. The
skill instructions are held constant. These are author-written development
cases, not a holdout or independent ground truth. No private project text,
paths, original reports or host transcripts are included.

| Pair | Cases | Controlled change | Expected distinction |
| --- | --- | --- | --- |
| Command effects | 27, 28 | Insert one fixture write; keep the command and README promise identical | Infer effects from implementation, including evidence contradicting the README |
| Omission to behavior | 29, 30 | Add the implementation to the same incomplete plan | A missing mapping is evidenced in both; only 30 establishes the specific wrong fallback |
| Decision stage | 31, 32 | Change only the requested decision | Missing implementation prerequisites do not block concept retention; they do block authorization to build |

The control pairs are deliberately small. Larger realistic tasks and paraphrase
variants are separate follow-up work. Cases 31/32 encode a specific fictional
decision policy; they do not prescribe a universal software process.

## Run

The original 26 cases and their expectations remain unchanged. This suite is
selected explicitly. Requires authenticated Claude Code and permission to consume
account usage. Run from the repository root, using a fresh output directory:

```sh
python3 evals/run_claude.py --case-dir evals/calibration-v1/cases --cases 27 28 29 30 31 32 --output .scratch/calibration-01 --budget-per-case 1 --timeout 240
python3 evals/check_results.py .scratch/calibration-01/records.json --expectations evals/calibration-v1/expectations.json
```

Each case gets a separate session with only its packet, the frozen candidate,
and host provenance. The reviewer receives no expected labels, pair description,
rubric, or response from the other case. The runner records the bytes it loaded
before the first invocation. All attempts, including failures, remain private
in the output directory. Never retry silently or update labels to fit a result.

## Assess

The checker validates report structure, selected lenses, finding-count bounds
and allowed severities. It does not establish whether the finding is supported.
For example, a structurally valid but unrelated finding can pass the mechanical
checks. The test suite explicitly demonstrates that limitation.

Apply [rubric.json](rubric.json) to the complete responses and their supplied
artifacts. For each pair, record pass, fail or inconclusive for every condition;
cite response fields and artifact locations. A pair passes only if every
condition passes in both responses. Missing/ineligible responses are incomplete,
never a pass. Keep mechanical results separate from this assessment.

Record assessor identity/family when known, prior exposure to cases or labels,
candidate package identity, run reference and limitations. A builder assessment
is useful diagnosis and must be labeled as such. Severity tolerances here apply
to these explicit fixture contracts. They do not replace contextual judgment.

Freeze the suite before a run. If a fixture is ambiguous, retain the original
attempt and document a versioned correction rather than revising its label
retroactively. Do not tune the skill during the first baseline batch.
