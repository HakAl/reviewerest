# Historical skill-effect test inputs

The two text files preserve the exact skill 1.2.0 bytes from public commit
`23e4451`. Their hashes match the unchanged
[candidate manifest](../../../evals/skill-effect-v1/candidate-manifest.json).
The `.txt` suffix distinguishes these archived inputs from the installed skill.

The offline tests copy the evaluation sources and package into a temporary root,
overlay these two historical files, and run the original hash checks there.
Every other pinned file must still match its frozen hash. The workspace default
and candidate/assessor roots point to that same temporary tree for these tests;
all patches are restored afterward. A corruption test checks that changes to
either the archived skill or runner are rejected.

This keeps the historical harness tests active while the live package advances.
It does not evaluate the current skill's behavior or authorize live calls.
Use public commit `23e4451` for the original pipeline commands; its manifests
intentionally reject a newer live package. The current package is checked
separately by the release gate and the remaining tests.
