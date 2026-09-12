# Scope-position formatting pilot

This experiment repeats two original reviews and two scope-position variants
twice each: eight assessments. It follows the
[unchanged-run measurement](../grader-v1/repeats-01.md), which found raw-verdict
variation on p85 and recurring +1 citation offsets on readiness.json.

## Frozen manipulation

Original packets p42 and p57 are byte-identical to grader-v1. Variants p14 and p68
respectively move the unchanged scope field to the end of readiness.json. Parsed
JSON values, the other artifacts, review text, target condition and protocol are
identical. Variant packet IDs differ to identify their results; the assessor is
not given the pair mapping or variant names.

| Field | Original line | Moved-scope line |
| --- | --- | --- |
| scope | 2 | 7 |
| authority_service | 5 | 4 |
| provider | 7 | 6 |

This changes key order, logical line numbers and provider/scope comma placement
together. It tests sensitivity to that manipulation, not a specific 80-column
wrapping mechanism. The original scope line is 104 characters. The runner embeds
artifacts in JSON with escaped newlines; no 80-column rendering step feeding the
assessor was observed. Other artifacts also contain lines longer than 80 characters.

[pairing.json](pairing.json) specifies the transformation, two repeats, budget and
limits. [manifest.json](manifest.json) pins it alongside the packets, protocol,
order and labels. Labels are inherited from the base cases: p42 is a supported
correction, p57 asserts unsupported executed harm. Parsing equality validates the
format manipulation, not the original semantic labels.

The fixed four-packet order is p42, p14, p68, p57, repeated in the second batch:
original first for the correction pair, moved first for the consequence pair.
Order is not randomized or reversed between rounds. Each assessment has a fresh
session, no tools or skills, and receives only the unchanged protocol and one
packet. Labels, pair mappings and earlier answers are withheld. Fresh sessions
are not established statistically independent samples; temperature is not pinned.

## Run the eight planned assessments

Requires Python 3.11+, git and an authenticated Claude Code CLI supporting the
existing grader runner flags, with authorization for account usage:

```sh
python3 evals/format_pairs.py run --output .scratch/format-01
```

The plan has $0.50 per-call limits, $2 per batch, $4 maximum across eight calls,
and a 120-second timeout per call. CLI estimates are not bills and caps may
overshoot a response. No repair, retry, fallback or replacement is automatic.
An ineligible or unfinished first batch stops the second. Citation-invalid
answers are retained and do not cancel the other preplanned observations.

Run exit 0 means all eight answers satisfy the response contract; exit 4 retains
failed or unfinished observations. Raw captures and local metadata remain in
ignored storage. Public answer files require a separate publication review.

## Compare raw verdicts and citations separately

```sh
python3 evals/format_pairs.py compare .scratch/format-01/answers-01.json .scratch/format-01/answers-02.json
```

The comparator verifies the manipulation, input hashes, and recorded model/CLI
identity. It reports original-versus-moved verdict agreement for each round,
within-arm verdict stability, citation resolution by arm and selected authority
quote counts. A missing grade yields an unknown comparison. A citation-invalid
answer retains its raw verdict. Quote omission is not successful field relocation.

Comparison exit 0 means all raw verdict pairs can be compared with matching
recorded model and CLI, not that verdicts are stable or citations valid. An unknown
pair or host-identity mismatch exits 4. Command/input errors exit 2.

Report counts and individual failures. Two repeats per arm cannot establish an
effect size or rule out the variation seen in unchanged runs. Preserve v1 labels
and all failures; no result here supplies a calibrated release pass.
