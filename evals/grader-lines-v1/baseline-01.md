# Numbered evidence: no added benefit demonstrated on this set

All 24 assessments had resolving citations, and all twelve paired raw verdicts
agreed. Numbered and unnumbered rows both passed the frozen response contract.
This experiment therefore did not demonstrate an added benefit from supplying
line numbers on these two short review cases. It does not establish that numbers
are unnecessary on longer or more difficult evidence.

The plan, renderer, original sources and criteria were committed at
`292fd704bdc20bdb4e0a6b0b8fb8a2f6cd83d801` at 10:07:01 UTC on 2026-09-12.
The first invocation began at 10:07:14 UTC. All 24 planned calls completed without
replacement, repair or retry. The host reported `claude-opus-5[1m]` and Claude
Code 2.1.269, with auxiliary Haiku usage. Temperature was unpinned. CLI-estimated
cost was $0.930008 against $12 in planned call caps; estimates are not bills.

## Frozen measurements

Each cell contains six assessments: two cases repeated three times. Original
field order places authority_service on line 5; moved order places it on line 4.

| Observation | Plain, original | Plain, moved | Numbered, original | Numbered, moved |
| --- | --- | --- | --- | --- |
| Planned / eligible completed | 6 / 6 | 6 / 6 | 6 / 6 | 6 / 6 |
| Answers with resolving citations | 6 | 6 | 6 | 6 |
| Individual quotes resolving | 19 of 19 | 18 of 18 | 18 of 18 | 20 of 20 |
| Answers with resolving authority quotes | 4 | 6 | 4 | 6 |
| Answers omitting the authority quote | 2 | 0 | 2 | 0 |
| Admissible author-label matches | 6 | 6 | 6 | 6 |

All 75 quotes resolve within their stated source ranges. Raw verdicts were pass
for every correction case and fail for every unsupported-consequence case, with
no variation across presentation, field order or repetition. These are matches
with inherited author labels, not independent certification of each rationale.

The four authority omissions are t01 (plain p42, round 1), t14 (plain p57,
round 2), t07 (numbered p57, round 1) and t13 (numbered p57, round 2). Those
answers cite other relevant evidence. Omissions are allowed by the frozen
protocol and are not counted as successful authority-field relocation.

In t23 (numbered p14, round 3), the authority quote cites lines 3 through 5,
containing the actual field on line 4. This passes the frozen inclusive-range
contract; it does not demonstrate exact single-line selection. The other nineteen
authority quotes cite the field's single source line. The broader range remains
in the published answer, without repair or retroactive failure labeling.

The runner and comparator both exited 0. Runner success means every planned
answer met the response contract. Comparator success means all observations were
eligible and comparable under matching recorded host identity; neither exit code
establishes a calibrated semantic release pass.

## Interpretation and remaining limits

The matched prompts differ only by numeric display prefixes. Both arms encode
one original source line per physical display row, preserving original content
and line endings. The plain arm is thus a new concurrent control, not the old
prompt containing the entire packet on one escaped JSON line. Its clean result
means this set cannot distinguish numbering from an already sufficient shared
row display. It does not establish that row display caused improvement over
historical runs, or that terminal wrapping caused historical citation failures.

This test retains the small, familiar cases selected after earlier errors. It is
not a holdout or an estimate of general citation reliability. The schedule
balances which presentation goes first across the twelve pairs, but each packet
keeps the same presentation first in all three repetitions. Case order rotates;
execution is not randomized. Fresh sessions and matching model aliases do not
establish independent samples or identical provider state.

A more discriminating follow-up would use unseen, longer sources with repeated
near-matching passages and relevant evidence farther apart. Exact single-line
selection, if desired, needs its own frozen criterion before that run. This
result does not justify silently tightening the current range contract or
changing the product skill on a claim of measured numbering improvement.

## Reproduce without a model account

```sh
python3 evals/numbered_evidence.py compare evals/grader-lines-v1/answers-01.json
python3 scripts/verify.py
```

[answers-01.json](answers-01.json) preserves every parsed grade, including quote
omissions and the broader range. [comparison-01.json](comparison-01.json) records
all 24 trial rows, twelve paired verdict comparisons and cell counts. The offline
test reproduces the complete comparison and checks public answer/comparison
hashes against [receipt-01.json](receipt-01.json).

The edited receipt includes frozen source and input hashes, invocation times,
prompt and capture digests, model/CLI identity and estimated costs. Local checks
confirmed that exported grades equal the captured results, prompts equal the
frozen renderer, all invocation exits were 0, and no tools, skills, MCP servers,
tool-use events or workspace changes were observed. Private raw captures and
local session metadata are not published. Public readers can reproduce scoring;
the public hashes alone do not authenticate model execution.
