# Prospective native-Agent comparison

Question: does supplying the complete reviewerest skill package improve review
quality under a shared minimal output request on these six development cases?
This measures supplied guidance, not automatic skill selection or discovery.

## Frozen treatment and control

Use Claude Code 2.1.269, requesting claude-fable-5-1 explicitly for each child,
with high effort and no persistent Agent memory. Do not inherit an unspecified
parent model. The two definitions have the same reviewer prompt, Read/Glob/Grep
tools, denied dynamic Skill and Agent tools, permission mode and turn limit.
Only treatment declares skills: [review]. The different registration names are
coordination identifiers and must not enter the assessment packet.

Prepare an isolated input workspace containing only the source packets, the
frozen full skill package, output schema and launch configuration. Do not launch
from a development checkout containing labels, earlier reviews or coordinator
records. Capture ambient CLAUDE.md instructions and host attachments; identical
configuration is not proof of identical rendered context. Withhold labels and
criteria from the coordinator as well as candidate children.

Pin the actual registered package and resolve its base directory before use.
The native lookup name is review in the measured installation. A directory
alias alone is insufficient. Verify the loaded body and any reference-file
contents against the package manifest; a matching SKILL.md does not pin a
subsequently read reference. The treatment includes optional reference access.

Every dispatch gives exactly the common candidate instructions followed by the
selected case as escaped JSON in an artifact_content block. Replace literal
<, > and & in serialized case text with JSON Unicode escapes. The output schema
is appended identically to both arms. Capture the actual delegation message and
compare it to the prepared task bytes. No parent-added hints or summaries.

Use six cases, two arms, three repeats: 36 fresh child instances, 18 per arm.
Follow the plan's sequential interleaved schedule. Never resume or fork a child.
No retries, fallback model or rewriting of an answer within a trial. Stop the
batch on runtime, loading, identity, input-drift or unexpected-read failures.
Structural output failures remain outcomes in the planned denominator.

## Delivery and capture admission

For treatment, require a parent Agent/Task invocation joined by tool_use_id to
a successful structured child result, the expected Agent type, consistent child
and session identities, and the pinned skill body in a host isMeta user message
before the child's first assistant message. Bind original and copied transcript
bytes with digests. A result that mentions an ID in arbitrary prose does not
establish the identity join.

For control, require the same identity and capture checks, absence of the
pinned body and distinctive skill excerpts from captured context, no skill-load
events and no reads of the skill package. Missing or incomplete context capture
is inconclusive; an absence search alone does not prove isolation. Inspect
rendered attachments and tool responses as well as ordinary messages.

Each child's first prompt must match the frozen task. Native model metadata
must identify the requested reviewer model. Observed child tools must be the
allowlisted read tools and confined to its supplied sources; treatment may also
read the frozen skill references. No artifact execution, network retrieval or
editing. These capture checks establish observed behavior, not adversarial
host permission enforcement. Do not claim stronger enforcement without probes.

Extract the original final child answer and join it to the child tool return.
The coordinator's summary is never the review. Record requested model, observed
child model, CLI version, input digests, child identity and usage separately.
Aggregate host modelUsage can include coordinator and auxiliary models. Preserve
all reported models and do not attribute their aggregate tokens/cost to a child.
Record missing usage explicitly; token totals are not dollar costs.

## Assessment and reporting

Use the accepted skill-effect-criteria-v1 without changing author labels after
seeing results. Both candidates return only finding, location, claim and severity
inside a findings array. Invalid records are retained; do not repair or project
them into passing records. The existing shared schema and per-entry assessor
protocol apply to prospective valid records.

Use a fresh Gemini assessor session for each anonymized candidate, recording
declared model/family and actual prior exposure. Keep explicit arm metadata,
other answers and builder judgments out. Candidate prose may reveal condition;
do not claim perfect blinding. Keep reasons and located evidence for each entry,
deduplicated core-defect recovery, unsupported assertions, out-of-scope claims,
neutral misplaced notes, severity diagnostics and criteria disputes separate.

Report exact counts by arm/case/repeat with 18 planned slots per arm. Required
defect opportunities are 12 per arm; clean trials are six per arm. Inconclusive
does not count as recovery, and unavailable grading does not mean no errors.
No composite score or population accuracy claim. The fixtures are development
cases, including cases already seen in pilots, not a held-out benchmark.

Before live execution, record the operator-approved call/time/usage limits,
coordinator model, assessor model, exact capture/checker bytes and their
compatibility checks in a separate hashed execution receipt. This protocol
does not authorize a batch or supply missing runtime evidence.
