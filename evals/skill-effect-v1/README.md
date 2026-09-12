# Matched skill-effect pipeline

The pipeline implements the operator-accepted
[criteria v1](../skill-effect-adjudication-v1/accepted-criteria-v1.json) and the
[bounded comparison design](../skill-effect-adjudication-v1/coordinator/run-plan-01.md).
It has not performed a live comparison. Candidate and assessor stages each
require a separate explicit operator authorization bound to their frozen manifest.

The treatment is the full installed skill package under a shared minimal output
schema. The control gets the same case and common output instructions, without
the package or skill expansion. Packaged references are part of the treatment.
No candidate receives accepted labels, old judgments or the assessor protocol.
The fixed schedule is six cases, two arms and three repeats: 36 candidate calls.

## Commands

```sh
python3 evals/effect_candidates.py --check
python3 evals/effect_candidates.py --output .scratch/effect-candidates-01 --authorization .scratch/candidate-authorization.json
python3 evals/effect_assessments.py export .scratch/effect-candidates-01 .scratch/effect-handoff-01
python3 evals/effect_assessments.py run .scratch/effect-handoff-01 .scratch/effect-assessments-01 --authorization .scratch/assessor-authorization.json
python3 evals/effect_assessments.py aggregate .scratch/effect-candidates-01 .scratch/effect-handoff-01 .scratch/effect-assessments-01
```

Alternatively, give one exported START-HERE.md to a fresh external Gemini session
and import its complete response using `effect_assessments.py import EXPORT ID
RESPONSE OUTPUT/ID`. Never give that session the export root's coordinator map,
other packets or repository access. Individual packet directories contain only
that packet and its prompt. Random assessment IDs and export order withhold the
explicit arm and repeat identity; writing style may still reveal the condition.

## Usage authorization

There is deliberately no approved authorization file in this package. After
explicit operator approval, the surrounding workflow records an authorization
with approved=true, an operator description, stage, exact manifest_sha256 and
max_calls=36. Candidate approval additionally records budget_per_call_usd=1 and
cli_cap_overshoot_acknowledged=true. Assessor approval additionally binds the
export_map_sha256 and records no_dollar_cap_acknowledged=true. The local one-use
`.used` receipt prevents accidentally reusing that same authorization file.
This is bookkeeping of operator intent, not cryptographic identity verification.

Claude receives a $1 requested limit per call: $36 in summed nominal limits,
not a prediction or guaranteed billing ceiling. Candidate calls are sequential,
with 240-second timeouts and no automatic retry or fallback. The runner stops
before another call on missing usage, model or tool-inventory drift, a missing
exact skill load, a prohibited tool attempt, workspace changes, or input drift.
Candidate formatting and location failures remain recorded outcomes.

Gemini uses the locally listed selector gemini-3.8-flash-high, at most 36 calls,
180-second timeouts, fresh temporary workspaces and new CLI projects. Antigravity
exposes no dollar cap here: its stage requires separate acceptance of call/time
limits without a dollar ceiling. Raw stdout/stderr and host results are retained.
CLI JSON and declared model/exposure do not authenticate served identity, tool
activity or source isolation. The adapter supports a final assessment object or
a single result wrapper, and stops on incompatible output; live compatibility
has not been measured. Sandbox/plan flags are not an enforcement guarantee.
Call limits count CLI invocations, not individual provider requests or internal
agent turns. A local timeout stops the launched process group; cancellation of
already issued provider work and its billing is not guaranteed.

## What the checks establish

Candidate structure and source bounds are checked separately. Assessor packets
preserve all original candidate text; malformed four-field records are unavailable
for semantic grading, without selective metadata removal or claim repair.

Each assessment must cover every entry with reasons and citations, plus every
required defect. Citation failure retains raw judgments separately from their
admissibility. Disputed criteria remain unavailable for aggregate semantic counts.
Aggregation rechecks raw captures and bindings, keeps the 18 planned trials per
arm visible, and never adds misplaced-note or severity-mismatch diagnostics to
recovery or false-positive counts. Mixed entries can recover a defect and still
contain an unsupported assertion. No composite quality score is produced.

Offline tests use synthetic host events and assessor records. They test isolation,
failure handling and arithmetic over judgments, not model behavior or substantive
truth. The frozen scripts and protocols can still contain mistakes. Host traces
and new-project metadata stay in ignored storage; publication needs a separate
content review. Prior adjudications, criteria and model outputs remain unchanged.
