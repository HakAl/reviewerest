# Long ledgers: both presentations satisfy the stricter contract

All 24 assessments matched the packet-derived readiness labels and supplied
the six required ledger facts from the correct record at their exact single
lines. Numbered and unnumbered presentations both passed. This experiment did
not demonstrate an added accuracy benefit from supplying line numbers, even
with 245-line sources and similar records for other identities.

The new checker does establish a narrower mechanical distinction: a real quote
from the wrong record is rejected as evidence for the requested operation.
Offline negative controls exercise that distinction, along with broad ranges,
omissions, duplicates, fabricated text and out-of-bounds locations. Successful
model answers and successful negative-control tests are different evidence.

## Frozen inputs and execution

The cases, protocol, expected locations, oracle and schedule were committed at
`a26de0d59f85c88205fb825c99a35d04dedb7739` at 10:40:09 UTC on 2026-09-12.
The first invocation began at 10:47:40 UTC. All 24 planned calls completed; no
attempt was replaced, repaired or retried by the runner. The host reported
`claude-opus-5[1m]` and Claude Code 2.1.269, with auxiliary Haiku usage.
Temperature was unpinned. CLI-estimated cost was $3.284492 against $12 in planned
call caps; estimates are not bills.

Each packet has a 245-line ledger with 24 records, exactly one matching all
three request identity fields. Each was assessed three times per presentation.

| Case | Current request | Review claim | Expected grade | Six target field lines |
| --- | --- | --- | --- | --- |
| p61 | Missing authority | Ready | fail | 35 through 40 |
| p26 | All prerequisites satisfied | Ready | pass | 125 through 130 |
| p83 | Missing authority | Not ready | pass | 205 through 210 |
| p94 | All prerequisites satisfied | Not ready | fail | 85 through 90 |

## Separate outcomes

| Measurement | Plain rows | Numbered rows |
| --- | --- | --- |
| Planned / eligible completed | 12 / 12 | 12 / 12 |
| Raw readiness-label matches | 12 | 12 |
| Answers with resolving quotes | 12 | 12 |
| Answers satisfying exact-evidence contract | 12 | 12 |
| Required facts at correct record and exact line | 72 of 72 | 72 of 72 |
| Wrong-record, wrong-line, broad-range or omitted facts | 0 | 0 |
| Contradicted review claims rejected | 6 | 6 |
| Contradicted claims accepted / inconclusive | 0 / 0 | 0 / 0 |

All 192 individual quotes resolve. All twelve paired verdicts agree, and each
packet retains its verdict across all three repetitions. The raw rejections
are also admissible under this suite's stricter evidence contract. The six
rejections per arm represent repetitions of two contradicted claims, not six
independent kinds of defect. Counts do not establish general accuracy or escape
rates, and the oracle does not certify every free-form assertion in the reasons.

The runner and comparator both exited 0. Runner success here covers completion
and the exact-evidence contract, while comparison success covers eligible and
comparable observations. Agreement with readiness labels is a separate reported
measurement. No exit code supplies a calibrated general review release pass.

## What the clean result leaves open

These sources are longer than the previous cases but remain highly regular.
Every ledger record occupies ten lines with the same key order. All distractors
have the opposite authority status from the target, so the target is also the
only record with its authority status. Those properties offer potential shortcuts
for locating the target and calculating line numbers. The observations do not
establish which strategy the assessor used. This is a controlled structured
retrieval task, not a test of irregular prose, ambiguous policy, mixed document
formats or evidence spread across an entire codebase.

The protocol now requires six complete key/value quotes on exact single lines.
That requirement deliberately removes the optional-evidence and broad-range
allowances from earlier experiments. It is frozen in this suite only. Historical
results keep their original scoring and are not a matched baseline for this
stricter task. The product review skill remains unchanged.

Within this experiment, the two prompts differ only by numeric display prefixes;
the source rows, instructions and packet IDs are identical. Each packet's first
presentation reverses between rounds and case order rotates. The schedule is
fixed, not randomized. Fresh sessions and matching recorded model/CLI identity
do not establish statistical independence or identical provider state. New cases
were not previously used in this local evaluation series, but are not proven
unseen in model training. The cases, policy and oracle are author-written.

The current evidence supports preserving this narrow behavior as a regression
case. It does not justify a claim that adding line numbers improves review
accuracy. A future test intended to distinguish presentations would need to
remove the regular-block and unique-status shortcuts before collecting results.

## Offline reproduction and provenance

```sh
python3 evals/long_evidence.py compare evals/grader-long-v1/answers-01.json
python3 scripts/verify.py
```

[answers-01.json](answers-01.json) preserves every parsed answer.
[comparison-01.json](comparison-01.json) contains all 24 trial rows, six field
statuses per trial and the twelve presentation pairs. An offline test recomputes
the complete comparison and checks answer/comparison hashes against the edited
[receipt-01.json](receipt-01.json). No model account is needed for reproduction.

Local checks confirmed that all exported grades equal their parsed captured
results, frozen input and source hashes match, and all prompts equal the frozen
renderer. All invocation exits were 0; no timeouts, tools, skills, MCP servers,
tool-use events or workspace changes were observed. Raw captures and local
session metadata stay private. The public receipt records their digests and
edited execution measurements; hashes alone do not authenticate model execution.
