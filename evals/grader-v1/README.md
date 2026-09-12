# Testing the semantic assessor

This experiment asks whether a fresh assessor can distinguish supported,
unsupported and ambiguous review claims. The repeated pilot demonstrated receipt
checking, but its thirty builder grades were all pass. It had not demonstrated
a grading procedure rejecting a semantically bad review.

These twelve fictional short reviews were authored for public inspection. Each
packet targets exactly one of the repeated pilot's five semantic conditions.
Five are labeled pass, five fail and two inconclusive. This label distribution
and the labels themselves are withheld from the assessor. The set includes
alternative correct wording, invented harm, fabricated execution, false blocking
of a sound control, a correction that substitutes reconstruction for authority,
and unresolved referents. This is a controlled challenge set, not a sample of
natural full-length reviews or a report-version-3 conformance test.

Each planted defect is a single explicit sentence contradicting a short supplied
policy or context statement. All twelve packets share the policy, review context
and candidate; ten also share the same readiness record. This run does not measure
sensitivity to subtle defects, dispersed evidence or varied domains.

The [first run](baseline-01.md) retains nine admissible label matches, two citation
failures and one label disagreement. All source packets and actual grade objects
are public, so its scoring can be reproduced without private captures.

## What is frozen and withheld

[manifest.json](manifest.json) pins every packet, the protocol, fixed order and
expected outcomes. The repository fixture manifest also pins these files.
[protocol.json](protocol.json) specifies criteria, three possible verdicts and
located quotations. [expectations.json](expectations.json) records the author's
expected outcomes and reasons. Freeze these before invoking the assessor; do
not change them after seeing its answers.

The runner reads only the plan, protocol and packets. Each fresh Claude session
receives the protocol and one packet inline. It receives no answer labels, builder
grades, author identity, other packets, historical reviews or review skill.
Tools and skills are disabled; safe mode suppresses customizations and the
temporary working directory is empty. Actual tools, calls, model identity,
workspace preservation and CLI version are checked. Managed host policy and
the CLI system prompt remain limits; this is not proof of complete isolation.

Claude is selected because it is an available different-family assessor from the
Codex author of these responses and labels. That is a selection rationale, not
prior evidence of grading competence. The run tests competence on these cases.
Authorship separation and withheld answers do not independently validate the
author's labels or guarantee statistical independence.

## Run once, with a fixed denominator

Requires Python 3.11+, an authenticated Claude Code CLI supporting the flags in
the runner, and authorization to consume account usage. All twelve attempts are
planned before the first invocation. The example declares a $6 cap through
twelve $0.50 per-invocation caps and a 120-second timeout per invocation:

```sh
python3 evals/grade_reviews.py run --output .scratch/grader-01 --budget-per-packet 0.5 --total-budget 6 --timeout 120
```

No automatic retry, repair, fallback or best-of selection occurs. A host failure
stops further spending; missing attempts remain in the denominator. Invalid
answers and failed citation checks remain recorded. CLI dollar estimates and
limits can overshoot a response and are not billing reconciliations.

Raw prompts and host captures stay in ignored storage. Review the extracted
answers for publication separately: publish the actual grade objects, not a
rewritten transcript, and describe any surrounding metadata removed. A public
answer file enables independent inspection and scoring, but cannot authenticate
the private host invocation on its own.

## Score without a model

```sh
python3 evals/grade_reviews.py score .scratch/grader-01/answers.json
```

The scorer requires exact input hashes, one verdict per planned packet, a reason,
and quotes that resolve in both the reviewed text and source evidence. It reports
a confusion matrix with missing and invalid answers retained. It counts false
alarms (expected pass, observed fail), missed defects (expected fail, observed
pass), and unresolved expected defects separately.

Exit 0 means agreement with every author label, 3 means disagreement, and 4 means
incomplete or invalid answers. Invalid command inputs exit 2. Agreement is not a
release pass; disagreement is not an automatically confirmed model error. Review
the cited reasoning and adjudicate independently. Quote resolution checks source
location, not semantic support.

The offline tests include constant-pass and constant-fail controls. These prove
that scoring can expose those strategies, not that a model grader avoids them.
The live model responses supply the latter evidence within this limited set.

## Remaining calibration work

One answer per short review does not establish grader stability. Preserve any
disagreements for human adjudication, validate the labels independently, and use
held-out cases before tuning. Then repeat matched unchanged and deliberately
regressed candidates to measure false alarms and detection sensitivity. This
experiment does not authorize an independent calibration record for the original
repeated release gate, whose decision remains inconclusive.
