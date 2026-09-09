#!/usr/bin/env python3
"""Resolve a local review comparison without writes, fetching, or prompting.

Python 3.11+, standard library. Exit 0: ready; 3: needs_scope; 2: usage.
This resolves declared/inferred ranges, not the truth of inferred user intent.
"""

import argparse
import json
import os
import subprocess
from pathlib import Path


class Git:
    def __init__(self, repo):
        self.repo = str(Path(repo).resolve())

    def run(self, *args, input_text=None):
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        return subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", self.repo, *args],
            input=input_text, capture_output=True, text=True, env=env, timeout=30,
        )

    def value(self, *args):
        result = self.run(*args)
        return result.stdout.strip() if result.returncode == 0 else None

    def commit(self, ref):
        return self.value("rev-parse", "--verify", "--end-of-options", ref + "^{commit}")

    def empty_tree(self):
        result = self.run("hash-object", "-t", "tree", "--stdin", input_text="")
        if result.returncode:
            raise ValueError("Cannot determine the repository's empty-tree identity.")
        return result.stdout.strip()


def needs_scope(reason, candidates=()):
    return {"status": "needs_scope", "missing_input": reason, "candidates": list(candidates)}


def ready(git, mode, base, head, reason, *, target=None, target_commit=None,
          assumed=False, untracked=False, notes=()):
    return {
        "status": "ready", "repo": git.repo, "mode": mode,
        "base": base, "head": head,
        "endpoint": "index" if mode == "staged" else "working_tree" if mode == "working" else "commit",
        "target_ref": target, "target_commit": target_commit,
        "selection_reason": reason, "assumed": assumed,
        "include_untracked": untracked, "notes": list(notes),
    }


def default_targets(git):
    """Prefer local remote HEADs; do not mistake feature tracking for PR target."""
    current = git.value("symbolic-ref", "--quiet", "HEAD")
    upstream = git.value("rev-parse", "--symbolic-full-name", "@{upstream}")
    branch = current.removeprefix("refs/heads/") if current else None
    upstream_is_self = bool(branch and upstream and upstream.endswith("/" + branch))
    refs = git.value("for-each-ref", "--format=%(refname)", "refs/remotes") or ""
    remote_heads = sorted(ref for ref in refs.splitlines() if ref.endswith("/HEAD"))
    if "refs/remotes/origin/HEAD" in remote_heads:
        remote_heads.remove("refs/remotes/origin/HEAD")
        remote_heads.insert(0, "refs/remotes/origin/HEAD")
    candidates = [git.value("symbolic-ref", "--quiet", ref) for ref in remote_heads]
    candidates.extend(["refs/remotes/origin/main", "refs/remotes/origin/master",
                       "refs/heads/main", "refs/heads/master"])
    seen = set()
    for ref in candidates:
        if not ref or ref in seen or ref == current:
            continue
        seen.add(ref)
        if upstream_is_self and ref == upstream:
            continue
        if git.commit(ref):
            yield ref


def resolve(repo, mode="auto", base=None, target=None, head_ref=None):
    git = Git(repo)
    if git.value("rev-parse", "--is-inside-work-tree") != "true":
        return needs_scope("A local working-tree repository is required; use whole-artifact review for non-git targets.")
    head = git.commit(head_ref or "HEAD")
    if head_ref and head is None:
        return needs_scope("The explicit head reference cannot be resolved.", [head_ref])
    if head_ref and mode in {"working", "staged"}:
        return needs_scope("An explicit committed head is incompatible with working-tree or staged review.")
    if target and mode in {"working", "staged", "commit"}:
        return needs_scope("A target branch requires branch or auto mode; use an exact base for other comparisons.")

    status = git.run("status", "--porcelain=v1", "-z", "--untracked-files=normal", "--ignore-submodules=all")
    if status.returncode:
        return needs_scope("Cannot inspect local change state; no scope assumption was made.")
    dirty = bool(status.stdout)

    if base:
        resolved_base = git.commit(base)
        if resolved_base is None:
            return needs_scope("The explicit comparison base cannot be resolved.", [base])
        if head is None:
            return needs_scope("An explicit commit base requires a resolvable head.", [base])
        actual_mode = mode
        if actual_mode == "auto":
            actual_mode = "working" if dirty and not head_ref else "branch"
        return ready(git, actual_mode, resolved_base, head, "explicit_exact_base",
                     target=base, target_commit=resolved_base,
                     untracked=actual_mode == "working",
                     notes=["Exact endpoints; no merge-base inference."])

    if mode in {"working", "staged"} or (mode == "auto" and dirty and not target and not head_ref):
        actual_mode = mode if mode != "auto" else "working"
        return ready(git, actual_mode, head or git.empty_tree(), head,
                     "explicit_local_changes" if mode != "auto" else "assumed_local_changes",
                     assumed=mode == "auto", untracked=actual_mode == "working",
                     notes=["Committed branch changes are outside this range.",
                            "Submodule worktrees were not traversed; inspect explicitly if in scope."])

    if not head:
        if mode == "auto" and not target and not head_ref:
            return ready(git, "working", git.empty_tree(), None, "unborn_working_tree",
                         assumed=True, untracked=True)
        return needs_scope("No committed head exists for the requested comparison.")

    if mode != "commit":
        targets = [target] if target else list(default_targets(git))
        for ref in targets:
            target_commit = git.commit(ref)
            if target_commit is None:
                return needs_scope("The explicit target branch cannot be resolved.", [ref])
            result = git.run("merge-base", "--all", head, target_commit)
            ancestors = result.stdout.split()
            if result.returncode or len(ancestors) != 1:
                return needs_scope("The target has no unique known merge base; supply an exact base.", [ref])
            # An empty inferred branch range is not a meaningful auto review.
            # Explicit branch/target requests retain their legitimate empty range.
            if mode == "auto" and not target and ancestors[0] == head:
                continue
            return ready(git, "branch", ancestors[0], head,
                         "explicit_target_merge_base" if target else "assumed_default_merge_base",
                         target=ref, target_commit=target_commit, assumed=not bool(target),
                         notes=["Local reference snapshot; remote freshness not checked.",
                                "Staged, unstaged, and untracked changes are outside this committed range."])
        if mode == "branch" or target:
            return needs_scope("No target branch is established; specify the branch or an exact base.", targets)

    parents = git.value("rev-list", "--parents", "-n", "1", head)
    if not parents:
        return needs_scope("Cannot read the selected commit's ancestry.")
    parent_ids = parents.split()[1:]
    if not parent_ids and git.value("rev-parse", "--is-shallow-repository") == "true":
        return needs_scope("Parent history may be missing in this shallow repository; supply a known base.")
    if len(parent_ids) > 1:
        return needs_scope("The selected merge commit has multiple parents; specify an exact comparison base.", parent_ids)
    return ready(git, "commit", parent_ids[0] if parent_ids else git.empty_tree(), head,
                 "explicit_latest_commit" if mode == "commit" else "assumed_latest_commit",
                 assumed=mode != "commit",
                 notes=["Only the selected commit is covered; this is not a whole-branch review."])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--mode", choices=["auto", "working", "staged", "branch", "commit"], default="auto")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--base", help="Exact base commit/ref; never silently replaced")
    group.add_argument("--target", help="Target branch/ref whose unique merge base is selected")
    parser.add_argument("--head", help="Committed endpoint; defaults to HEAD")
    args = parser.parse_args()
    try:
        result = resolve(args.repo, args.mode, args.base, args.target, args.head)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        result = needs_scope(f"Local comparison unavailable: {type(exc).__name__}.")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] == "ready" else 3


if __name__ == "__main__":
    raise SystemExit(main())
