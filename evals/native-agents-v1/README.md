# Native-Agent comparison protocol v1

This freezes a prospective comparison using Claude Code native Agents with
explicit skill preloading. It follows the operator-relayed exploratory pair
and the successful persisted-transcript loading probe. No prospective trial
under this protocol has run. The earlier Opus runner and its stopped attempt
remain separate historical experiments.

The [protocol](protocol.md) and [plan](plan.json) keep the accepted semantic
criteria and six development cases. The requested model is now explicitly
claude-fable-5-1. Both arms must return the same four-field JSON record. This is
an intentional change from the exploratory pair's free-form Markdown reports;
that pair is not one of the planned 36 trials.

The [manifest](manifest.json) pins the protocol, plan, candidate instructions,
both Agent definitions, accepted criteria, source packets, output schema and
complete skill package. It is a content freeze, not proof of execution or an
authorization to consume model usage. A new version is required for changes to
these inputs after execution starts.

The runtime and capture method still need an execution receipt and an operator
approved live run plan. Native Agent launch works and exact skill delivery has
been observed in a child transcript. That does not certify arbitrary workspace
isolation, a 36-trial batch, or independent semantic grading.

## Exploratory pair assessment

The earlier pair used one shared inline password-reset prompt, free-form
responses and concurrent children. Both child message streams reported
claude-fable-5-1. Local inspection confirmed the pinned skill body in treatment,
its absence from the control capture, matching task prompts, parent-child joins
and unchanged preserved-file digests. This establishes one observed pair, not
a reliable average treatment effect.

A private two-packet handoff prepares independent assessment of only the
numbered findings in those replies. Each packet contains original finding text,
source code and the accepted case criteria. It excludes arm names, host paths,
the report's scope/receipt sections, prior judgments and the coordinator map.
An exact extraction map records all exclusions outside assessor access.
Formatting, length and prose can still reveal the condition. This is masking
explicit metadata, not a guarantee of successful blinding.

The [exploratory assessment instructions](exploratory-assessor.md) were authored
after the builder saw both outputs. These assessments cannot become a
preregistered result or establish full-report quality. Unsupported assertions
outside the numbered findings are outside this particular assessment. No
candidate text is rewritten to make an answer fit the prospective schema.

Raw transcripts and the handoff remain private because the original records
contain personal paths and host metadata. A human may relay each isolated
START-HERE.md to a fresh Gemini session; no account or model invocation is
required to prepare the handoff. Keep one candidate per assessor session.
