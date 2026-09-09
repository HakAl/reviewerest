#!/usr/bin/env python3
"""Offline tests and bounded publication checks. Does not verify review truth."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".scratch", ".agents", ".claude", "__pycache__", ".venv"}
PATTERNS = {
    "personal home path": r"/(?:Users|home)/(?!runner(?:/|\b))[^/\s\"\\]+/",
    "machine temporary path": r"/(?:private/)?var/folders/",
    "private key": r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----",
    "credential token": r"(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16})",
    "host/session metadata": r'"(?:session_id|sessionId|messaging_socket_path|authSource)"\s*:',
}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def own_repo(root):
    try:
        return Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() == root.resolve()
    except subprocess.CalledProcessError:
        return False


def private_path(name):
    p = Path(name)
    return (bool(set(p.parts) & IGNORED) or name.startswith("evals/results/")
            or p.name in {"capture.json", "invocation.json", ".env", ".DS_Store"}
            or p.name.startswith(".env."))


def content_errors(name, data):
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        return [f"{name}: binary/non-UTF-8 content requires separate publication review"]
    errors = []
    # Decode JSON strings so escaped paths and tokens receive the same scan.
    if name.endswith(".json"):
        try:
            text = json.dumps(json.loads(text), ensure_ascii=False).replace("\\/", "/")
        except ValueError:
            errors.append(f"{name}: invalid JSON")
    for category, pattern in PATTERNS.items():
        if re.search(pattern, text):
            errors.append(f"{name}: {category}")
    email_text = re.sub(r"\bgit@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+", "", text)
    if any(m.group(1).lower() not in {"example.com", "example.invalid"} for m in EMAIL.finditer(email_text)):
        errors.append(f"{name}: email address requires publication review")
    return errors


def source_files(root):
    if own_repo(root):
        return set(filter(None, git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").decode().split("\0")))
    return {p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and not private_path(p.relative_to(root).as_posix())}


def check_tree(root):
    errors = []
    actual = source_files(root)
    allowed = set(json.loads((root / "public-files.json").read_text())["files"])
    for name in sorted(actual - allowed):
        errors.append(f"{name}: not in the public inventory")
    for name in sorted(allowed - actual):
        errors.append(f"{name}: inventoried file is missing")
    for name in sorted(actual):
        p = root / name
        if private_path(name):
            errors.append(f"{name}: private path is included")
        if p.is_symlink():
            errors.append(f"{name}: symlinks require a separate distribution decision")
            continue
        if not p.is_file():
            errors.append(f"{name}: missing regular file")
            continue
        data = p.read_bytes()
        errors.extend(content_errors(name, data))
        if p.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", data.decode()):
                if re.match(r"[a-z]+://|#", target):
                    continue
                local = target.split("#", 1)[0]
                if local and not (p.parent / local).is_file():
                    errors.append(f"{name}: broken local link")
    for manifest_name in ("evals/package-manifest.json", "evals/fixture-manifest.json"):
        manifest = json.loads((root / manifest_name).read_text())
        for name, expected in manifest["files"].items():
            p = root / name
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
                errors.append(f"{name}: manifest hash mismatch")
    return errors


def check_history(root, revision="HEAD"):
    if not own_repo(root):
        return [], 0
    commits = git(root, "rev-list", revision).decode().splitlines()
    errors, seen = [], set()
    for commit in commits:
        metadata = git(root, "show", "-s", "--format=%an <%ae>%n%cn <%ce>%n%B", commit)
        errors.extend(content_errors("commit " + commit[:12], metadata))
        for entry in git(root, "ls-tree", "-rz", commit).split(b"\0"):
            if not entry:
                continue
            header, raw_name = entry.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            name = raw_name.decode()
            key = (name, oid)
            if key in seen:
                continue
            seen.add(key)
            if private_path(name) or mode not in {"100644", "100755"}:
                errors.append(f"history {name}: private path or non-regular file")
            if kind == "blob":
                errors.extend(content_errors("history " + name, git(root, "cat-file", "blob", oid)))
    return errors, len(commits)


def main():
    if sys.version_info < (3, 11):
        print("Python 3.11+ required.", file=sys.stderr)
        return 2
    errors = check_tree(ROOT)
    history_errors, count = check_history(ROOT)
    errors.extend(history_errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for command in ([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                    [sys.executable, "-B", "review/scripts/validate_record.py", "examples/review.json"]):
        result = subprocess.run(command, cwd=ROOT, env=env)
        if result.returncode:
            return result.returncode
    print(f"Verified public inventory, hashes, local links, content patterns and {count} reachable commits.")
    print("Tests and example structure passed. Review truth and exhaustive privacy are not established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
