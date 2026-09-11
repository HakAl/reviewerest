# First correction baseline

2026-09-10. Suite and labels frozen at `c79ac3c` before the run. Skill version
1.1.0 was unchanged. Six isolated sessions, one attempt each, no retries or
response repair. The host reported Claude Code 2.1.268, `claude-opus-5[1m]` and
auxiliary Haiku usage. Summed case time was about 340 seconds; CLI-estimated
usage was about $1.56.

All six traces contained the exact skill body, preserved provided provenance
and left input snapshots unchanged. Capture, fixture, candidate and runner
hashes matched. This is an edited summary; raw traces contain local metadata
and remain private. Invocation claims are not independently reproducible from
this public summary alone.

## Mechanical results

All six responses passed extraction, report structure, required/excluded lens
checks and finding-count bounds. The checker exited 0. All five nonempty reports
used blocker severity; severity is diagnostic only in this suite.

| Case | Findings | Targeted builder assessment |
| --- | --- | --- |
| 33 | 1 | Correct owner selected; unsupported handoff wording remains |
| 34 | 1 | Recommendation follows the changed owner |
| 35 | 0 | Cumulative agreement clause prevents the alleged bypass |
| 36 | 1 | Weakened clause permits the contested-response counterexample |
| 37 | 1 | Backup availability stays unknown, but a recovery-impossibility claim exceeds the evidence |
| 38 | 1 | Absence of an outside copy is bounded to the supplied inventory |

## Correction ownership

In 33 the response identifies Pack's missing destination-store access and rejects
the proposed move to Relay for the same reason. It recommends Vault. In 34 it
accepts moving the check to Relay, which owns the destination store in that
variant. Both retain destination-object reads and comparison to bundle hashes
without reallocating resource ownership. The targeted pair conditions pass in
the builder's assessment.

Case 33 also acknowledges that the route to Vault is unspecified, then refers
to an existing handoff in its recommendation. That wording is not established
by the packet. A valid ownership choice does not prove that the delivery path
already exists; it should remain an explicit wiring requirement.

## Cumulative acceptance

Case 35 evaluates A AND B and finds no bypass. Case 36 identifies the exact
same-version contested response that passes the weakened local rule while
violating the unanimity requirement. Both distinguish the proposed rule from
an exercised runtime gate. The targeted pair conditions pass. Case 35's extra
zero-owner generalization is outside the supplied scenario and is not validated
by this assessment.

## Bounded copy evidence

Case 37 explicitly leaves archive/backup copies unknown, and case 38 derives
absence within the three declared locations from the complete inventory.
Both withhold recycling readiness and recommend obtaining and verifying an
outside recoverable copy. Neither claims to have performed preservation.

However, case 37 states: "Because the file is untracked, version control cannot
restore it." Current tracking status does not establish repository history.
An untracked file may have recoverable bytes in an earlier commit.

The deterministic counterexample in
[test_correction_evals.py](../../tests/test_correction_evals.py) commits a file,
removes it from tracking while retaining its working copy, observes untracked
status, and retrieves the original bytes from the earlier commit. That test was
added during adjudication; it was not part of the frozen reviewer input.

The builder marks the copy-evidence pair as a substantive failure by interpreting
its second condition to prohibit categorical recovery-impossibility claims from
untracked status. The narrower archive/backup distinction passes. This grading
interpretation is explicit because the original condition names uniqueness and
inevitable loss rather than Git history specifically. The rubric and labels
have not been rewritten after the run.

## Limits and next evidence

The assessor was the Codex builder, with prior knowledge of the cases and labels.
No blind or independent adjudication ran. Pair outcomes concern targeted behavior,
not every sentence in the responses. These small explicit packets do not establish
transfer to a long multi-file review, and no skill improvement is claimed: the
skill was unchanged throughout.

This batch supports testing implied recovery claims and proposed wiring more
directly in future variants, while preserving the passing ownership and cumulative
clause controls. It does not justify declaring the real-world failure modes fixed.
