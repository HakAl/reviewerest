# Verify, then push

The public source starts with fresh history. Private development history and
raw evaluation output are intentionally absent. Do not push the development
repository or copy its `.git` directory into this one.

After creating an empty public repository, configure its SSH remote once:

```sh
git remote add origin git@github.com:YOUR_ACCOUNT/reviewerest.git
```

Review and commit the intended changes, then run:

```sh
python3 scripts/push_verified.py origin main
```

The wrapper requires a clean working tree, captures the current commit, checks
it out in a temporary clone, runs `scripts/verify.py` there, scans the history
reachable from that commit, and pushes only that exact commit to the named
branch if all checks pass. It does not force-push or push tags. Ordinary `git
push` bypasses this wrapper; this is a workflow, not host-enforced permission.

CI invokes the same gate on Ubuntu with Python 3. It performs no live model
runs. A local pass reduces surprises but cannot guarantee CI availability,
platform parity, or a successful merge with newer remote changes. Configure
`verify` as a required check in your repository settings after the first run.

`public-files.json` is the deliberate inventory of public files. Adding a file
requires updating it after inspecting the contents. The scanner rejects common
personal paths, host/session fields, credential formats, unapproved files and
private directories. It reports categories and locations, not matched values.
It cannot identify every secret, private project detail, or licensing issue.

The release includes the skill, deterministic tests, synthetic cases, an edited
evaluation summary, and a fictional example. External references are linked,
not bundled. The project is licensed under Apache-2.0; see LICENSE and NOTICE.
