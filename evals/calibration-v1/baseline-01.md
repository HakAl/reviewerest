# First calibration baseline

2026-09-10. The six packets, rubric and expectations were committed as `de0d5f5`
before this batch. Skill version 1.1.0 was unchanged. Each case ran once in a
separate Claude session; no retries, response repair or instruction tuning ran.

The host reported Claude Code 2.1.268, `claude-opus-5[1m]`, and auxiliary Haiku
usage. All six traces contained the exact skill body, preserved the host-provided
record provenance and left their input snapshots unchanged. The batch took
about 332 seconds of summed case time, at about $1.55 CLI-estimated usage.

This is an edited summary. Raw responses and host traces remain private because
they contain local metadata. Historical invocation claims cannot be independently
verified from this public summary alone.

## Mechanical results

All six responses passed strict extraction, version 2 structure, lens routing
and finding-count bounds. Three failed their frozen severity expectations, so
the checker exited 3. They remain failures under that frozen rubric.

| Case | Findings | Severity | Frozen mechanical result |
| --- | --- | --- | --- |
| 27 | 0 | None | Pass |
| 28 | 1 | blocker | Fail: expected major |
| 29 | 1 | blocker | Fail: expected major |
| 30 | 1 | blocker | Fail: expected major |
| 31 | 0 | None | Pass |
| 32 | 2 | blocker, blocker | Pass |

These outcomes are separate from CI. CI tests the fixtures, harness and checker;
it does not require a model to meet the behavioral rubric or hide a failed run.

## Builder assessment of the paired behavior

- **Command effects:** 27 reported no write defect after inspecting the read
  path. In 28, the finding cited the inserted `write_text` and explained that a
  mismatch is overwritten before the failure result returns. Both distinguished
  source reasoning from an unperformed runtime check.
- **Omission to behavior:** 29 reported missing canceled coverage and explicitly
  left actual rendering unknown. In 30, the finding cited the `.get` fallback
  returning Running for canceled. Both kept the immediate UX consequence in
  one finding. The latter distinguished a source-derived label from an observed
  screen.
- **Decision stage:** 31 supported concept retention without findings. In 32,
  the missing accepted review ticket and passing unit result became two blockers
  to implementation authorization. It did not claim that the implementation
  was defective or that the missing checks had passed.

These observations satisfy the targeted conditions in [rubric.json](rubric.json)
in the builder's assessment. They do not validate every statement in the outputs.
Both decision-stage responses introduced an unsupported caveat about needing an
individual maintainer despite the stated team assignment. That did not change
the decision or finding count, but it remains useful feedback.

## The labels also need calibration

The three severity mismatches are not automatically three established reviewer
errors. Cases 28-30 request review against a contract but do not specify an
acceptance decision. The skill defines blocker relative to the intended decision.
A reviewer interpreting the decision as contract acceptance can defend blocker;
the author expected major for a material defect. This batch exposes that ambiguity.

Keep this version and its results unchanged. A future version should either
state the decision and its severity policy explicitly or treat severity as a
diagnostic dimension until humans calibrate the labels. The decision-stage
policy should also distinguish allowed prototype work from implementation
authorization so its prerequisite does not create a sequencing ambiguity.

The assessor was the Codex builder, with prior knowledge of the cases and labels.
No blind assessor or independent human adjudication ran. This is a single
development batch, not a general accuracy estimate or evidence of improvement
over a no-skill baseline.
