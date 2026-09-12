# Supplying source line numbers

This frozen experiment asks whether explicitly supplied source line numbers
improve citation reliability without changing substantive verdicts. It follows
the [scope-position pilot](../grader-format-v1/baseline-01.md).

## Matched presentation

Both arms present each original source line as a JSON-encoded string on its own
physical display row. Encoding retains whitespace, line endings and delimiters.
The numbered arm adds a 1-based integer prefix. The plain arm has the same rows,
separators, protocol and display instructions, with those integers absent:

```text
| "  \"authority_service\": \"not_checked\",\n"
5 | "  \"authority_service\": \"not_checked\",\n"
```

The display instructions tell the assessor to decode the strings and quote the
original source, excluding display prefixes. The unchanged scorer checks quoted
text against original source lines. Source names and artifact text are escaped
inside the untrusted-content boundary; embedded delimiters cannot close it.
This is framing, not a general prompt-injection guarantee.

The plain arm is a new concurrent control. Both arms differ from the earlier
prompt that embedded the entire packet in one escaped JSON line. Comparing new
results directly with that historical prompt would confound row layout and line
numbering. The paired comparison here changes only numeric display prefixes.
Adding prefixes also adds tokens; this measures the practical presentation change.

## Frozen scope and schedule

The four packet files, inherited author labels and protocol are byte-identical
to grader-format-v1. The supported correction appears as p42 (original field
order) and p14 (scope moved); the unsupported executed-harm claim appears as p57
(original) and p68 (moved). Packet IDs stay identical across presentation arms.

Two cases, two field orders, two presentations and three repetitions produce
24 planned assessments. [design.json](design.json) fixes the full schedule before
execution. Adjacent calls pair presentations of the same packet; case order
rotates between rounds and presentation order alternates. Each presentation goes
first in six pairs. This is fixed interleaving, not randomization. Labels,
schedule, pair mappings and previous answers are withheld from the assessor.
Each invocation uses a fresh empty workspace with tools and skills disabled.
Temperature is unpinned and fresh sessions are not established independent samples.

The runner freezes its sources and inputs before calling the host. Each call has
a $0.50 cap and 120-second timeout; the 24 planned caps total $12. CLI estimates
are not bills and a response can overshoot a cap. There are no automatic retries,
repairs or replacement attempts. Citation failures are retained while remaining
planned calls continue. An ineligible invocation or recorded model/CLI change
stops further calls. Missing observations remain in the denominator.

## Run and compare

Requires Python 3.11+, git, an authenticated Claude Code CLI supporting the runner
flags, and authorization to consume account usage:

```sh
python3 evals/numbered_evidence.py run --output .scratch/lines-01
python3 evals/numbered_evidence.py compare .scratch/lines-01/answers.json
```

Run exit 0 means all planned answers satisfy the response contract. Exit 4
retains an incomplete run or failed answer. Comparison exit 0 means all 24
eligible observations have comparable raw verdicts and matching recorded host
identity, not that citations resolve or that the model passes. Input errors exit 2.
Raw traces contain private host metadata; publication requires a separate review.

## Predeclared measurements and limits

Report counts per presentation and field-order cell, each with six observations:

- Raw verdicts and original-versus-numbered agreement, retaining invalid citations.
- Answers with all quotes resolving, plus individual quote counts and locations.
- Authority evidence cited correctly, cited incorrectly, omitted or unavailable.
- Matches with inherited author labels, with admissible matches separate.
- Per-trial outcomes for inspecting variation across the three repetitions.

An omitted authority quote is not successful relocation. These two cases do not
establish general error rates or semantic calibration. Labels remain authored
controls. A favorable result supports a further test on unseen documents; it
does not establish a wrapping cause or a calibrated release gate.
If both presentations have no observed citation failures, this set cannot show
an added benefit from numbering. The shared row layout may already make these
short sources easy to cite; that result would call for harder unseen sources.

Offline tests check source reconstruction (including blank lines, Unicode and
line endings), matched prompts, fixed schedules, stale and fabricated citation
rejection, preserved verdict flips, quote omissions and stop-on-host-failure.
They require no model account. The product review skill remains unchanged.
