# Repeated behavioral gate pilot

The goal is a repeatable, calibrated gate for behaviors the skill must preserve.
This first milestone measures variation on two existing authority fixtures with
three fresh sessions each. It does not establish unit-test-like reliability.
The skill is unchanged at 1.2.0.

The [first six-trial pilot](baseline-01.md) passed the five targeted conditions
in the builder's assessment. Its release decision remained inconclusive because
independent calibration is missing; citation errors are retained separately.

[policy.json](policy.json) pins the original case bytes, five semantic conditions,
three repetitions, and the failure threshold. Case order alternates by round.
All six scheduled attempts remain in the denominator. No best-of selection,
response repair, or adaptive retry is allowed. A setup/runtime failure stops
further spending and leaves the remaining trials unperformed.

## Run the bounded pilot

Requires an authenticated Claude Code CLI and authorization to consume usage.
The sum of per-case caps cannot exceed the declared total budget; actual CLI
estimates can overshoot a response. Use a new output directory:

```sh
python3 evals/run_repeated.py --policy evals/repeated-v1/policy.json --output .scratch/repeated-01 --budget-per-case 1 --total-budget 6 --timeout 240
```

The runner freezes the candidate, policy, case bytes and its own sources before
starting. Each session sees only one packet, the copied skill and host provenance.
Policy labels and prior answers never enter the review workspace. Actual model
identity is checked across trials; this uses the CLI default, not an immutable
model snapshot. The host and its default configuration remain a material limit.

## Assess and decide

Assess the complete responses against every policy condition. Record each
assessor's identity and prior exposure. Bind each assessment to the exact saved
response digest, and cite evidence for each judgment. Start the separate JSON
assessment file with this shape; the placeholders are not a completed assessment:

```json
{
  "policy_sha256": "digest of the frozen policy file",
  "trials": {
    "r01-47": {
      "record_sha256": "digest of this trial's record.json",
      "assessor": {"identity": "actual assessor", "prior_exposure": "actual exposure"},
      "conditions": {
        "readiness": {"outcome": "inconclusive", "reason": "Not yet assessed", "evidence_refs": ["pending"]}
      }
    }
  }
}
```

Complete all five condition entries in every assessed trial. Outcomes are
`pass`, `fail`, or `inconclusive`. A substantive fail needs an explicit
`confirmation: {"by": "adjudicator", "reference": "counterexample or adjudication record"}`;
otherwise it stays inconclusive. Never manufacture confirmation to satisfy a gate.
The default fails on one confirmed occurrence of a condition. A higher threshold
counts recurrence of the same condition in the same case, not unrelated failures.

```sh
python3 evals/repeated_gate.py .scratch/repeated-01 --policy evals/repeated-v1/policy.json --assessments .scratch/repeated-01/assessments.json
```

The helper checks captured output, exact skill loading, source preservation,
provided provenance, model consistency, report structure and assessment links.
Use a checkout whose validator matches the evaluated package. The result records
policy, assessment, gate and validator hashes, plus per-trial eligibility details.
Missing trials and ineligible host runs stay inconclusive. Captured malformed
reports count as structural failures. A confirmed failure is not outvoted by
passing repeats. It returns exit 0 for pass, 3 for fail, and 4 for inconclusive.

There are two results:

- `observed_behavior`: the result of these trials under the supplied judgments.
- `decision`: the release gate result. Even all passing trials remain
  inconclusive without independent calibration of the exact policy.

Supply an actual calibration record with `--calibration <path>` only after it
exists. It must contain the policy digest, `approved: true`, `independent: true`,
the real `reviewed_by` identity, and `evidence_ref` to the calibration work. This
records an attestation; the helper does not authenticate the person or verify
that the calibration was adequate. Field presence is not scientific validation.

## What calibration still requires

Before making this a blocking release gate:

1. Independently review fixture expectations and acceptable alternative wording.
2. Exercise the grading procedure on known supported, overstated and unresolved
   responses, including deliberately altered responses. Measure grading errors
   and disagreement instead of accepting the grader's self-confidence.
3. Resolve disagreements and freeze the resulting criteria and grading protocol.
4. Collect repeated baseline and candidate runs with matching host/model settings.
   Measure false alarms on unchanged candidates and sensitivity to known regressions.
5. Choose repetitions and blocking thresholds from those observations and the
   consequences of missed regressions versus false alarms.

Three repeats of two explicit cases are a starting denominator, not a reliability
estimate, independent sample guarantee, regression comparison or confidence
percentage. This live gate is separate from offline CI. The offline gate tests
its bookkeeping and failure handling without a model account.
