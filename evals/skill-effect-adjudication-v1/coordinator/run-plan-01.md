# Bounded skill-effect comparison plan

Criteria v1 is accepted and frozen. The operator's explicit acceptance is in
[operator-acceptance-01.json](../operator-acceptance-01.json); it does not approve
spending or a live run. [run-plan-01.json](run-plan-01.json) records the proposed
schedule, treatment, host settings, limits and implementation prerequisites.
This plan is prepared but not executable: the matched runner and assessor
pipeline still need implementation, offline tests and a source freeze.

## Treatment and sequence

Compare the full installed review skill package with no skill, using the same
source packet and minimal four-field output schema in both conditions. The
skill-on arm gets the pinned package, including its references. Those references
are part of the treatment; this experiment does not isolate the core SKILL.md
instructions from the rest of the package. Both arms have read-only local
inspection and no artifact execution, edits, network retrieval or external
references. The control receives neither the skill nor its report contract.

The candidate host is Claude Code, locally observed at 2.1.269. Request the same
model selector `claude-opus-5[1m]` and high effort in both arms; actual model
identity must be confirmed in traces before accepting any trial. Do not substitute
a model silently. Keep a new isolated workspace and session for every call.

Six cases times two arms times three repeats gives 36 candidate calls. The JSON
plan specifies every call in order. Each pair uses the same case and repeat,
with nine pairs starting skill-on and nine starting skill-off. Case order rotates
between repeats. Sequential pairs reduce time drift; there is no claim that
this small development sample supports broad causal conclusions.

## Proposed limits

| Stage | Calls | Timeout per call | Usage boundary |
| --- | --- | --- | --- |
| Candidate reviews | 36 maximum, sequential | 240 seconds | Request a $1 CLI limit per call: $36 summed nominal limits. This is not predicted cost or a guaranteed billing ceiling. |
| Gemini assessments | At most 36, sequential and fresh context per candidate | 180 seconds | Dollar estimate and cap method unresolved. Local Antigravity help exposes no dollar-cap flag. |
| Automatic retries, repairs or fallback | 0 | Not applicable | Preserve failures; no unplanned calls. |

Claude's in-flight responses may overshoot its requested limit and its estimates
can differ from billing. Before any paid calls, choose an explicit assessor usage
boundary and capture method and obtain approval for the complete live plan.
No total-dollar ceiling for both stages is claimed here.

The assessor is proposed as Gemini 3.8 Flash (High), from a different family than
the candidate and builder. Its exact selector and host behavior still need
verification. Each assessment sees only one case, its accepted criteria/common
rules and the candidate's original four-field entries. No arm mapping, candidate
trace, skill body, peer answer or historical adjudication is provided. Record
identity and exposure; declarations alone do not authenticate model identity or
prove the host withheld other context. Style can still reveal the condition.

## Assessment and reporting

Carry forward the [per-entry grading requirements](run-plan-draft-01.md): every
classification needs a concise source-based reason. Record supported and
unsupported parts of mixed entries, required-defect recovery, duplicate groups,
and case-level reasons for empty reviews. Record misplaced notes and severity
mismatches separately per arm; neither may enter recovery or false-positive
totals later. Do not invent calibrated severity ranges for substantive findings.

Report all 18 scheduled trials per arm, including six clean trials and twelve
required-defect opportunities. Missing calls, malformed records and incomplete
assessments stay visible; absence is not a clean result. Preserve raw output and
allow only the accepted bare-object/whole-json-fence parsing rule. Location
validity remains separate from semantic judgment. No composite quality score or
after-the-fact diagnostic weighting is planned.

## Before execution

Implement and test the matched runner, assessor capture adapter, assessment
validator and aggregator. Freeze their exact bytes, common prompts, assessor
protocol and record schema. Existing runners invoke the skill in every case and
do not implement this control condition or the new assessor contract; their
passing tests do not establish a matched experiment.

Require integrity, model identity, loading, workspace and usage checks between
calls. A runtime or integrity failure stops further spending and preserves the
unfinished schedule. Candidate formatting or location errors are retained as
outcomes without retries. Assessment failures remain recorded; no automatic
repair is permitted. Resolve the assessor usage boundary and obtain explicit
live-run approval only after those mechanisms are concrete and tested.
