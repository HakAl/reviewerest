# First live attempt: stopped on host compatibility

The first candidate call at frozen commit `63e62f7` stopped the sequence before
the second call. There is no skill-versus-control result. One of 36 scheduled
reviews ran; none was eligible for assessment, and no Gemini call ran.
The operator approved both bounded stages before this attempt.

The [edited receipt](attempt-01.json) records the failures, usage and private
capture digests. Claude Code reported exit 0, 26.306 seconds and $0.2155555 in
usage. The candidate record passed structural and source-location checks;
workspace file bytes were unchanged. These are mechanical observations, not an
assessment of finding quality.

Two frozen adapter requirements failed:

1. Usage included `claude-haiku-4-5-20251001` alongside the requested
   `claude-opus-5[1m]`. The plan allowed no auxiliary models. Reported Haiku usage
   was 1,070 input tokens, 14 output tokens and $0.00114. The trace does not
   establish the auxiliary call's purpose or its contribution to the review.
2. The adapter searched for the exact skill body inside a successful Skill tool
   result. That result contained only `Launching skill: reviewerest-eval:review`.
   The exact body was present in the immediately following synthetic user
   message, event 6 in the saved NDJSON trace. This is an adapter-location
   mismatch, not evidence that the skill body was absent from the session.

The controller retained the raw streams and failed trial, and stopped without
retrying or changing its checks. Offline export produced zero assessor packets.
Aggregation retains all 36 scheduled slots, including the failed first trial
and 35 unattempted trials. No semantic recovery or false-positive comparison is
available.

The next runner revision needs a loading-evidence check for the observed paired
events, with negative controls for wrong skill, failed invocation, unrelated
body text and wrong body bytes. It also needs an explicit auxiliary-model policy:
either prevent that usage with a measured host configuration or disclose and
bound it in a new plan. A new attempt must retain this failed attempt and freeze
the revised adapter and plan before execution. This document authorizes no retry.

The original criteria, prompts, plan, runner and manifests remain unchanged.
The raw host captures remain private because they contain local paths and session
metadata. Their hashes bind this receipt to those captures for local checking;
they do not make the observations independently reproducible from public files.
