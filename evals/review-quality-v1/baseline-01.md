# First review quality baseline

2026-09-11. Eight packets, expectations, rubric and matcher oracle were frozen
at `de75dee` before this run. Skill version 1.1.0 stayed unchanged. Each case
received one isolated Claude session, with no retries or response repair.
The host reported Claude Code 2.1.268, `claude-opus-5[1m]` and auxiliary Haiku
usage. Summed case time was about 506 seconds; CLI-estimated usage was $2.26.

The targeted rubric conditions pass in the builder's assessment. Two frozen
finding-count checks fail. This is not a clean pass of the evaluation suite.

| Case | Findings | Mechanical result | Targeted behavior |
| --- | --- | --- | --- |
| 39 | 1 | Pass | Catches lost plurals and supplies a correction that passes all twelve matcher examples |
| 40 | 0 | Pass | Accepts the valid replacement; proposes no change |
| 41 | 2 | Pass | Rejects the 0/4 frequency claim while preserving the possible bug |
| 42 | 0 | Pass | Accepts 3/4 as meeting the stated threshold in this corpus |
| 43 | 1 | Pass | Finds an exact but irrelevant quote; leaves the requirement unsupported |
| 44 | 2 | Count fails | Finds supporting line 4 and corrects the citation; adds a reference-frame ambiguity finding |
| 45 | 0 | Count fails | Records conflicting policies under needs_scope and offers conditional next steps |
| 46 | 1 | Pass | Finds missed retries under aligned policies; preserves eventual abort |

All eight responses passed strict extraction, report structure and lens checks.
The result checker exited 3 because of the two count failures. Severity was
diagnostic only: the responses used blocker, major and minor labels.

## Executable correction and citation results

Case 39's proposed module was inspected before a separate host check ran it
against [matcher-oracle.json](matcher-oracle.json). All twelve expected booleans
matched, including plural acceptance and Bellman rejection. The review session
itself did not execute the code. The returned module was:

```python
import re

_TOKEN = re.compile(r'\bllms?\b', re.IGNORECASE)


def matches(text):
    return _TOKEN.search(text) is not None
```

The frozen invalid fixture fails three plural examples; the valid fixture and
this correction pass all twelve. These are bounded examples, not proof of every
possible token or Unicode behavior.

The citation checker exited 0 for cases 43 and 44. All ten evidence annotations
matched the specified source, revision, line range and exact quote; none were
unchecked. Separately, the builder assessed the reasoning: both responses
distinguished the irrelevant line 3 quote from support for the future-date
claim. Only case 44 had that support, on line 4. Neither claimed an external
retrieval or an observed server response. Quote matching alone proves none of
those semantic conclusions.

## Retained failures and interpretation

Case 44 exceeded the maximum of one finding by additionally flagging the
unspecified reference frame in "future date". It accepted the main requirement
and recommended naming the server's UTC date. That is a plausible precision
concern, but whether it deserves a separate finding needs independent
calibration. The count label remains unchanged.

Case 45 fell below the minimum of one finding. It explicitly named the policy
conflict, stated which policy the code followed, and completed the shared abort
check. It put the unresolved choice in `missing_input` and conditional
`candidates_for_scope`, with status `needs_scope`. The frozen semantic rubric
requires the distinction, not a particular output field, so those conditions
pass while the count check fails. Whether this packaging adds unnecessary user
friction remains open; the unattended invocation returned a record successfully.

The frequency pair has another caveat. Case 41 reported the draft's single-word
exclusion as incomplete using a hypothetical word outside the corpus. Case 42
discarded the same class of concern as outside scope. The bounded frequency
distinction passes, but these responses do not show consistent treatment of the
remedy. A future version should isolate the frequency claim from remedy wording.

## Evidence limits

All eight traces contained the exact skill body, preserved provided provenance
and left the input snapshots unchanged. Capture, candidate, fixture and runner
hashes matched. This edited report omits private host metadata and raw traces;
readers cannot independently establish these invocation claims from it alone.

The assessor was the Codex builder with prior knowledge of the labels. There
was no blind or independent adjudication and no comparison with the skill
disabled. Targeted rubric passes do not validate every sentence of the reports.
These compact, explicit fictional cases do not establish performance on long
real reviews, severity calibration, or a skill improvement. Existing failures
and frozen labels remain intact.
