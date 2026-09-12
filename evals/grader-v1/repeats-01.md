# Two unchanged reruns before variants

Two preplanned reruns repeated the frozen twelve packets before any formatting or
paraphrase variants were authored. All 24 new host invocations completed and were
eligible. Raw verdicts were stable across all three runs for eleven packets;
p85 changed from inconclusive to pass. Citation errors occurred on unchanged
inputs, including a recurrence of the authority-field off-by-one.

## What stayed fixed

Both reruns executed the saved original runner from the first experiment, whose
SHA-256 is `aa67b4623f667c0fb6db315850da6115a9eeca763c888b8a2e2074550c980755`.
The transport source, protocol, all packet bytes, order, per-call budget, timeout
and session-isolation procedure stayed the same. Every new prompt was compared
byte-for-byte with its corresponding original prompt. All three runs recorded
`claude-opus-5[1m]` and Claude Code 2.1.269. Model aliases and recorded settings
cannot guarantee immutable provider behavior or statistical independence.

The plan declared two batches at the original $0.50 per-call caps, $6 maximum
per batch. CLI cost estimates were $0.5869145 and $0.572197, totaling $1.1591115.
No response was repaired, retried or replaced. The current scorer changed while
the reruns used the saved original runner; scorer changes never reached their
prompts or execution path. The [receipt](repeat-receipt-01.json) records that
boundary and hashes, along with publication limits.

## Raw verdict and citation validity

Here I means inconclusive; P means pass; F means fail. Citation cells show whether
all quotes in that answer resolve. The v1 author label for p31 remains unresolved
and does not supply calibration correctness or error judgments.

| Packet | Criterion | Original verdict | Rerun 1 verdict | Rerun 2 verdict | Citations: original / rerun 1 / rerun 2 |
| --- | --- | --- | --- | --- | --- |
| p73 | Authority | F | F | F | yes / yes / yes |
| p18 | Readiness | P | P | P | yes / yes / yes |
| p64 | Consequence | P | P | P | yes / yes / yes |
| p29 | Attribution | F | F | F | yes / yes / yes |
| p85 | Correction | I | I | P | yes / yes / yes |
| p42 | Correction | P | P | P | no / yes / yes |
| p96 | Readiness | F | F | F | yes / yes / yes |
| p31 | Authority | P | P | P | yes / yes / yes |
| p57 | Consequence | F | F | F | no / yes / no |
| p06 | Authority | P | P | P | yes / yes / yes |
| p48 | Attribution | P | P | P | yes / yes / no |
| p22 | Correction | F | F | F | yes / yes / no |

All five planted defects received raw fail verdicts in each run: five stated
rejections, zero raw escapes, zero unresolved expected defects, zero missing
verdicts per run. Admissible rejections were four, five and three respectively
because of citation failures. These are counts on five distinct defects, not
an estimate of an escape rate. The five author-labeled supported reviews received
raw pass verdicts in every run, with citation-invalid answers retained separately.

The raw label-agreement counts are eleven, eleven and ten. The admissible counts
are nine, eleven and seven. These are descriptive comparisons to author labels;
p31 is not counted as a known grading error, and p85's author label is not newly
validated by repetition or overturned by the third answer.

## The two observed sources of variation

p85's third answer resolves "that check" through "the remaining prerequisite":
the record leaves only authority unverified. The first two answers treat the
referent as unresolved. No packet or protocol changed. A later wording variant
that flips this verdict cannot by itself establish an effect of that wording.

| Quote measurement | Original | Rerun 1 | Rerun 2 |
| --- | --- | --- | --- |
| All quotes resolving / supplied | 39 / 41 | 43 / 43 | 39 / 42 |
| Unchecked authority quotes resolving / supplied | 6 / 8 | 7 / 7 | 6 / 8 |
| Unchecked authority quotes with wrong location | 2 | 0 | 2 |

The original wrong authority citations were p42 and p57; rerun 2's were p57 and
p22. Each points to line 6 while the field is on line 5. Rerun 2 also locates
the provider field on line 8 rather than line 7 in p48. p57 does not quote the
authority field in rerun 1, so that run is not evidence of p57 correctly relocating
that field. The grader chooses its quotations; the authority-quote denominator
is therefore seven or eight, not a fixed set of independent observations.

This confirms recurrence of the observed miscount on unchanged input. It does
not establish its cause, a population error rate or a stable long-run noise
estimate. The observed variation is now available when planning format pairs.

## Reproduce both columns mechanically

The [comparison result](repeats-01.json) is computed from all three public answer
files. The new [answers-02.json](answers-02.json) and [answers-03.json](answers-03.json)
preserve parsed grade objects from the captured responses without correction.

```sh
python3 evals/compare_grader_runs.py evals/grader-v1/answers-01.json evals/grader-v1/answers-02.json evals/grader-v1/answers-03.json
python3 evals/grade_reviews.py score evals/grader-v1/answers-03.json
```

The comparison exits 0 when it can compare every raw verdict under matching
recorded model/CLI identity. It does not mean the answers pass. The second command
exits 4 because citation-invalid answers remain. Score version 2 records raw
outcomes independently of citation resolution. Use `--legacy-score` with the
original answer file to reproduce the unchanged historical score-01.json.

Public files support independent scoring and inspection, not authentication of
the private host captures. Frozen v1 labels and protocol remain unchanged.
The [next-experiment constraints](next-experiments.md) separate formatting changes,
independently checked paraphrases and the protocol-only v2 comparison.
