#!/usr/bin/env python3
"""Verify an isolated committed snapshot, then push only that commit."""

import argparse
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def output(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def push_verified(root, remote, branch):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", remote):
        raise ValueError("Use a configured remote name, not a URL or option.")
    subprocess.run(["git", "check-ref-format", "refs/heads/" + branch], check=True)
    if output(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Commit or set aside pending changes before verifying a push.")
    commit = output(root, "rev-parse", "HEAD")
    destinations = output(root, "remote", "get-url", "--push", "--all", remote).splitlines()
    if len(destinations) != 1 or destinations[0].startswith("-"):
        raise ValueError("The selected remote must have one push destination.")
    with tempfile.TemporaryDirectory(prefix="reviewerest-push-") as temporary:
        snapshot = Path(temporary) / "source"
        subprocess.run(["git", "clone", "--local", "--no-hardlinks", "--no-checkout",
                        str(root), str(snapshot)], check=True)
        subprocess.run(["git", "-C", str(snapshot), "checkout", "--detach", commit], check=True)
        gate = snapshot / "scripts/verify.py"
        if not gate.is_file():
            raise ValueError("The committed snapshot has no verification gate.")
        subprocess.run([sys.executable, "-B", str(gate)], cwd=snapshot, check=True)
        if output(snapshot, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError("Verification changed the snapshot; refusing the push.")
    print("Verified commit " + commit + "; pushing only that commit.", flush=True)
    subprocess.run(["git", "-C", str(root), "-c", "push.followTags=false", "push",
                    "--no-follow-tags", destinations[0], commit + ":refs/heads/" + branch], check=True)
    return commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("remote")
    parser.add_argument("branch")
    args = parser.parse_args()
    try:
        root = Path(output(Path.cwd(), "rev-parse", "--show-toplevel"))
        push_verified(root, args.remote, args.branch)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print("Push stopped: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
