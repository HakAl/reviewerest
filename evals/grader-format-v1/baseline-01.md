# Scope-position pilot: first eight assessments

Moving the unchanged scope field below the cited readiness fields coincided with
fewer citation failures in this small run. Raw verdicts stayed the same in all
four original-versus-moved comparisons and across both rounds for every packet.
This does not establish that terminal wrapping caused the original errors.

The plan, inputs and runner were committed at
`2e83ad9950099ccbbc10666b6b8ffe899b28ef46` before the first invocation on
2026-09-12. Two rounds each assessed p42, p14, p68 and p57 in that fixed order.
All eight calls completed and were eligible; no attempt was repaired or replaced.
The host reported `claude-opus-5[1m]`, Claude Code 2.1.269, with auxiliary Haiku
usage. Temperature was not pinned. Total CLI-estimated cost was $0.338813 against
a $4 cap; estimates are not bills.

## Separate verdict and citation observations

| Observation | Original layout | Scope moved to end |
| --- | --- | --- |
| Planned and completed answers | 4 | 4 |
| Raw verdict matches inherited author label | 4 | 4 |
| Answers with all citations resolving | 1 | 4 |
| Individual quotes resolving | 9 of 12 | 12 of 12 |
| Authority-field quotes resolving | 1 of 4 | 3 of 3 |
| Answers omitting the authority-field quote | 0 | 1 |

| Round | Original correction p42 | Moved correction p14 | Moved consequence p68 | Original consequence p57 |
| --- | --- | --- | --- | --- |
| 01 | pass, citations resolve | pass, citations resolve | fail, citations resolve | fail, citation invalid |
| 02 | pass, citation invalid | pass, citations resolve | fail, citations resolve | fail, citation invalid |

All three failures quote `authority_service` from readiness.json at line 6,
where it actually occurs on line 5: p57 in round 01, and p42 and p57 in round 02.
These are three observations of the same offset pattern, not three established
independent causes. The moved field occurs on line 4, and all three answers that
quote it cite line 4 correctly. Round 01 p68 instead cites the review, context
and policy. Its valid citations do not demonstrate authority-field relocation.
Round 02 p14 includes the authority field's trailing comma, which is unchanged
by this manipulation. These answers do not test quotation of the changed commas
on scope or provider.

The two consequence packets received raw fail verdicts in both rounds. The two
original-layout rejections have invalid citations, leaving only the two
moved-layout rejections admissible under the response contract. Across all eight
answers, five are admissible label matches. Both batch runners and the overall
orchestrator exited 4 because citation failures are retained. The offline
comparator exits 0 because all raw verdict pairs can be compared with matching
recorded host identity; that is not a model-quality pass.

## What this establishes and leaves open

The [frozen manipulation](README.md) preserves parsed JSON values, review text,
other artifacts and protocol. Original packet bytes and reconstructed prompts
match grader-v1. Moving scope jointly changes key order, logical field positions
and scope/provider comma placement; variant packet IDs also differ. The observed
split supports further investigation of format sensitivity, without identifying
which change matters or ruling out sampling variation. Order was fixed rather
than randomized or reversed, and fresh sessions are not established statistically
independent samples.

The long scope value remains present. No 80-column renderer feeding the assessor
was observed; the prompt encodes artifact newlines inside JSON. These results do
not prove a wrapping mechanism, establish an error rate, or justify a calibrated
release pass. Labels remain author-written, and the two review cases concern
explicit short claims in one domain. Protocol v1 and its unresolved p31 label
remain unchanged.

## Reproduce without a model account

```sh
python3 evals/format_pairs.py compare evals/grader-format-v1/answers-01.json evals/grader-format-v1/answers-02.json
python3 scripts/verify.py
```

[Answers 01](answers-01.json), [answers 02](answers-02.json), and
[comparison-01.json](comparison-01.json) preserve the parsed judgments and both
score columns. The offline test re-computes the complete comparison and checks
published answer and comparison hashes against [receipt-01.json](receipt-01.json).
The receipt also records source hashes, invocation times, prompt/capture hashes,
cost estimates and locally checked execution properties. Raw captures and local
session metadata remain private. Public hashes do not authenticate model
execution; public answers do make the reported scoring independently reproducible.
