# reviewerest 1.4.0

Skill 1.4.0 strengthens how a reviewer investigates candidate findings and checks
proposed corrections. The report format remains version 3.

Since the public 1.2.0 package, the guidance adds requirement tracing and targeted
counterevidence retrieval (1.3.0), then path tracing across boundaries, checks
that distinguish a plausible failure from success, and validation of each repair
alternative against the constraints it must preserve (1.4.0). The deterministic
helpers are unchanged. Reinstall by repeating the copy command in the
[README](../README.md) after updating the repository.

The [package manifest](../evals/package-manifest.json) identifies the released
bytes. The [evaluation summary](evaluations.md#skill-130-and-140) reports mixed
development results and their limits. This release makes no general improvement,
equivalence or calibrated accuracy claim.

## Historical evaluations

Frozen fixtures, expected answers, manifests and evaluation runner sources are
preserved. The historical skill-effect pipeline still binds to 1.2.0 and refuses
the newer live package. Its offline tests now use a temporary root with two exact
[archived inputs](../tests/fixtures/skill-effect-v1/README.md); the original hash
checks remain active, including a new corruption check. No test is skipped and
no historical model run is relabeled as evidence about 1.4.0.

## Verification

The offline release gate passes 174 tests with no skips and validates the
fictional example, package hashes, public inventory, local links and content
patterns. All 19 historical skill-effect tests run, including the added
corruption check. The release workflow also verifies the committed snapshot
in a fresh clone before publication. These checks do not call models or
establish review quality.
