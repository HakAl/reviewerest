# Structured review record, version 3

Read only for requested machine-readable output or evaluation. Return JSON as response data; the host owns persistence. For JSON-only requests, return one bare JSON object, with scope and limitations inside its fields and no preface or code fences. This is a reporting contract, not evidence that the host enforces read-only access or that conclusions are correct.

Use this shape and populate it from the actual review. The empty example is a shape illustration, not a valid completed review:

```json
{
  "version": 3,
  "status": "complete",
  "scope": "One-line review boundary and purpose",
  "target": {"artifact": "path or source ID", "revision": null, "base": null, "assumptions": []},
  "provenance": {
    "skill_version": "1.2.0",
    "skill_revision": null,
    "run_id": null,
    "reviewer": {"model": null, "family": null},
    "generator": {"model": null, "family": null}
  },
  "no_review_reason": null,
  "lenses": [],
  "evidence": [],
  "checks": [],
  "candidates": [],
  "findings": [],
  "limits": [],
  "missing_input": null,
  "candidates_for_scope": [],
  "handoff": null
}
```

- `status`: `complete`, `partial`, or `needs_scope`. Complete means the scoped review was performed, not that the artifact is correct; failed checks and findings can accompany completion. Complete requires selected, checked coverage, evidence, and a performed check with a pass/fail outcome. Any selected lens with partial/unavailable coverage, or an unresolved lens, requires partial/needs_scope status and specific limits. Unperformed optional checks do not prevent completion of a narrower, explicitly checked scope. Needs-scope identifies an unresolved target/purpose; retain independently completed scope in `limits`.
- `no_review_reason`: normally null. For an empty diff or another evidenced target with nothing reviewable, record the reason and a performed check with evidence establishing it. Such a complete no-review outcome has no selected lenses or findings; a bare assertion of emptiness is insufficient.
- `provenance`: record the skill version supplying the lens/severity criteria, its revision or package digest when supplied, the host run ID when supplied, and reviewer/generator model and family identities when known. Read metadata supplied by the host if available. Unknown values are null; do not infer identity from branding, invent a run ID, or claim independence from unknown identities. A schema version is not a criteria version. These fields record attribution, not proof of it.
- `target.base`: null for whole-artifact reviews, otherwise the resolved base record including selection reason and endpoint identity. Preserve local-change coverage and stale-ref assumptions. `revision` may be a commit or a host-assigned fixture ID; null means unknown, not current by assertion.
- `lenses`: one object per considered lens with `id`, `selection` (`selected`, `excluded`, `unresolved`), `reason`, `coverage` (`checked`, `partial`, `unavailable`, or null for excluded), `depth` (`core`, `specialized`), `reference_reads`, and `evidence_ids`. Each reference-read entry has `path`, `outcome` (exactly `read`, `success`, or `unavailable`; `read` and `success` are equivalent), and an optional separate `reason`. Keep explanations out of the outcome value. If no read was attempted because capability was absent, use `unavailable` and explain that in `reason`; do not invent an attempted tool call. IDs: `intent`, `correctness`, `design`, `ux`, `security`, `reliability`, `performance`, `evidence`, `clarity`, `feasibility`. A checked lens needs supporting evidence; specialized coverage requires a successful relevant reference read. Do not invent a reason to include every lens.
- `evidence`: objects with unique `id`, `source`, `location`, `revision`, `kind` (`source`, `observation`, `execution`, `reference`), and `observation`. Cite original positions even when framing serialized text. An observation is data, not a pass verdict.
- `checks`: objects with unique `id`, `method` (`static`, `compare`, `host_execution`, `human`, `model`), `criterion` (expected behavior or decision rule), `status` (`pass`, `fail`, `not_run`, `inconclusive`), `evidence_ids` linking actual observations, and `limitation`. Make the comparison explicit; a verdict word is not an observation. If a criterion depends on a particular external standard or source revision, include that versioned source in evidence; if unavailable, disclose the limitation and avoid a version-specific compliance claim.
  - A failed check requires `finding_ids` referencing final findings, or an empty array plus a nonempty `disposition_reason` explaining why it is not reported (for example, an exploratory hypothesis refuted by evidence). A failed check does not automatically stop review or prove an artifact defect.
  - For `method: "model"`, include `assessor: {"model": null, "family": null}`, replacing null only with known identities.
  - For `method: "host_execution"`, include `execution: {"run_id": null, "result_ref": null}`. Use the supplied run ID and result location when available; otherwise keep null and explain missing provenance in `limitation`. A requested command stays `not_run` until invocation/results are supplied. Do not invent independent judges or execution evidence.
- `candidates`: objects with `id`, `disposition` (`reported`, `merged`, `discarded`), `finding_id` (null only if discarded), and `reason`. Every reported/merged candidate maps to exactly one final finding. A discarded candidate needs a scope/evidence reason.
- `findings`: objects with unique `id`, `severity` (`blocker`, `major`, `minor`), `title`, `locations`, `trigger`, `consequence`, `evidence_ids`, `lenses`, `basis` (`observed`, `inferred`), `uncertainty`, `recommendation`, and `claim_support` (below). Lens IDs refer to selected lenses. Group by root cause, sorted by impact, never by lens. Preserve independent defects sharing a location.
- `limits`: specific missing evidence, omitted coverage, unverifiable host enforcement, or remaining assumptions. Missing proof is not itself a defect finding.
- `missing_input` and `candidates_for_scope`: populate for needs-scope. Never issue an interactive prompt in an unattended run.
- `handoff`: null for review-only; for review-and-fix use `{ "phase": "edit", "authorized_by": "user request", "finding_ids": [], "suggested_diff": null, "applied": false }`. This record never claims edits occurred inside review. The orchestrator validates proposed edits against user intent before execution and reports its editing results separately.

## Claim support

Every finding includes `claim_support` with exactly these three roles: `defect`
(support for title and triggering discrepancy), `consequence` (support for the
consequence text), and `correction` (support for the recommendation). Each has:

```json
{
  "level": "inspected",
  "evidence_ids": ["e1", "e2"],
  "check_ids": ["k1"],
  "reasoning": "The required canceled state falls through to the running row in the supplied plan.",
  "assumptions": [],
  "next_check": null
}
```

- `demonstrated`: the particular claim was exercised by an actual execution
  result. Link a performed `host_execution` check (pass or fail) and matching
  `kind: "execution"` evidence. State the exercised inputs and bounds. Supplied
  results must be attributed to their provider; do not claim to have run them.
- `inspected`: a complete source-level comparison or derivation supports the
  stated claim without execution. Link evidence and explain the argument.
  Reading a requirement does not demonstrate implementation compliance.
- `conditional`: evidence supports a concrete path if a named, unverified
  assumption holds. List it in `assumptions` and give a concrete `next_check`.
  Keep the corresponding claim text conditional too.
- `unresolved`: explain the missing evidence in `reasoning` and supply a
  `next_check`. Evidence/check links may be empty. This is allowed for a
  finding's consequence or correction, not its defect: wholly unresolved
  concerns belong in limits or questions. Do not state unestablished harm or
  promise an effective fix in the corresponding text.

All roles require `reasoning`, `assumptions` (possibly empty), `evidence_ids`,
`check_ids` (possibly empty), and `next_check` (null only for demonstrated or
inspected support). A static correction can be inspected if its argument covers
both the defect and preserved requirements; execution is not mandatory. A
runtime test of a defect does not establish its downstream harm or its fix.
These are evidence categories, not confidence probabilities or severity levels.

The helper checks required fields and links. A fabricated result or invalid
inference may still satisfy that structure. Source authenticity, relevance,
assumption completeness and whether the prose actually respects the declared
support level need substantive assessment. Never treat a successful validation
receipt as proof that a claim is demonstrated.

The ordinary prose report follows the same evidence and scope rules without serializing this bookkeeping. Semantic support, correct lens selection, and legitimate deduplication need substantive assessment; field presence does not prove them.

The host can check an existing record with `python3 <skill-dir>/scripts/validate_record.py <record.json>` or supply JSON on stdin with `-`. Exit 0 means structurally consistent, 3 means invalid, and 2 is usage error. The helper writes only its receipt to stdout. It cannot verify source truth or actual tool execution from a self-reported record.

Version 3 adds separate support for each finding's defect, consequence and correction. The validator defaults to version 3. Use `--allow-legacy` only to read archived version 1 or 2 records with their historical checks; the receipt says `legacy_structure_only`. Version 2 retains its coverage/provenance checks but has no per-claim support requirement. Preserve historical records without inventing missing support retrospectively.

Development evidence is in the source repository at `tests/test_review_records.py`, `tests/fixtures/review-audit-2026-09-09/`, and `evals/`. These are outside the portable skill package and are not runtime dependencies.
