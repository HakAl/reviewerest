# Long-ledger evidence locations

This experiment extends the [short-source line-number test](../grader-lines-v1/baseline-01.md)
with four new synthetic cases. A long ledger contains 24 similar records, only
one of which matches the operation, candidate digest and evidence revision in
request.json. Distractors differ in one identity field and carry the opposite
authority status. Repeated key/value lines make it possible to quote real text
from the wrong record.

The [first 24 assessments](baseline-01.md) all match the readiness labels and
locate the six required facts exactly. Both presentations pass, so no added
numbering benefit is demonstrated. Regular ten-line records and the target's
unique authority status remain limitations. Public answers reproduce offline.

## Frozen comparison

Each case has a current record that either satisfies all three policy
prerequisites or lacks authority verification, and a review claiming ready or
not ready. The four combinations supply two supported and two contradicted
controls. The target record occurs at a different position in each ledger.
These cases are new to the local live evaluation series, not established unseen
in model training or independent of the builder.

Numbered and unnumbered presentations use the same source rows and instructions.
Adding numeric prefixes is the only paired prompt change. Packet IDs and source
bytes stay identical across arms. There are three repetitions per case and arm:
24 calls. [design.json](design.json) fixes the schedule. Adjacent calls pair
presentations of one packet; each packet's first presentation reverses between
rounds. Case order rotates. This is fixed interleaving, not randomization.

The renderer and host runner come from numbered_evidence.py. The extension adds
case loading and a stricter evidence checker; sources and inputs are snapshotted
before the first call. Earlier suites and their results retain their original
contracts. The product review skill is unchanged.

## New evidence contract

This suite's [protocol.json](protocol.json), version 2, requires citations of
review.md and policy.md, plus exactly six separate single-line citations from
the matching ledger record:

- operation
- candidate_sha256
- evidence_revision
- byte_hash_revalidation
- authority_service
- operator_approval

Each ledger quote must include the complete JSON key and value. An exact quote
at a different record's location does not establish the target fact. A broad
range containing the right line also fails this new single-line contract.
Omissions, duplicate field citations and extra ledger citations are retained as
failures. This is a dedicated retrieval-and-assessment task with required
evidence, not a direct comparison against the earlier optional-evidence protocol.

The host runner's existing checks record malformed or nonresolving citations
during each call. The extension checks the full exact-evidence contract after
the planned calls finish. Wrong-record or broad-range citations can satisfy the
older quote-resolution check while failing this extension. All raw verdicts
remain visible regardless of citation failure.

## Mechanically derived expectations

[long_evidence.py](../long_evidence.py) builds deterministic packets and derives
expectations from their actual bytes. It parses the request and ledger, requires
exactly one matching record, locates that complete record in canonical JSON, and
records the six field lines. Policy satisfaction is the conjunction of the
three explicit status requirements. A fixed ready/not-ready review claim can
then be compared with that state without a model judge.

[expectations.json](expectations.json) freezes those locations and labels; input
loading recomputes them and rejects disagreement. Author-written construction,
policy and oracle code are not independent semantic ground truth. This oracle
does not certify the free-form reasoning in an answer or general review quality.
Expected labels and locations, case construction and execution schedule are not
included in assessor prompts.

Offline negative controls demonstrate distinctions the experiment depends on:
a quote that resolves in the wrong record, a valid but overbroad range, a missing
fact, duplicate citations, fabricated text, out-of-bounds locations and a verdict
flip masked by an invalid citation. The builder reproduces the frozen files byte
for byte and refuses to overwrite an existing destination.

## Run and report

Requires Python 3.11+, git, a compatible authenticated Claude Code CLI, and
authorization for account usage:

```sh
python3 evals/long_evidence.py run --output .scratch/long-01
python3 evals/long_evidence.py compare .scratch/long-01/answers.json
```

The 24 planned calls have $0.50 per-call caps ($12 combined) and 120-second
timeouts. Cost estimates are not bills and caps may overshoot a response.
Citation failures do not cancel other preplanned observations. There are no
automatic retries, repairs or replacements. Ineligible invocations or observed
model/CLI changes stop further calls; missing trials keep the planned denominator.
Temperature is unpinned and fresh sessions are not established independent samples.

Run exit 0 means all 24 answers meet the new evidence contract. Exit 4 retains
an incomplete run or failed contract. This is separate from agreement with
readiness labels. Comparison exit 0 means all trials have eligible, comparable
raw verdicts and matching recorded host identity; it does not mean citations or
judgments pass. Input errors exit 2.

Report raw verdict agreement, quote resolution, exact-evidence completion and
individual fact failure categories separately. Each arm has twelve planned
answers and 72 required facts. Keep every attempt and publish only inspected
parsed answers and edited receipts; private raw host metadata stays ignored.
Report counts, not general accuracy or escape rates. Four synthetic cases do
not establish a calibrated release gate.
