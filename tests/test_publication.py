"""Publication controls tested with temporary repositories and local remotes."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verifier = load("verify")
pusher = load("push_verified")


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.remote = Path(self.temp.name) / "remote.git"
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                        GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        self.environment = patch.dict(os.environ, self.env)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        subprocess.run(["git", "init", "-b", "main", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(self.remote))
        (self.root / "scripts").mkdir()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE, text=True).strip()

    def commit(self, gate="raise SystemExit(0)\n"):
        (self.root / "scripts/verify.py").write_text(gate)
        self.git("add", ".")
        self.git("commit", "-m", "Synthetic publication fixture")
        return self.git("rev-parse", "HEAD")

    def remote_head(self):
        return subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "refs/heads/main"],
                              capture_output=True, text=True)

    def test_failed_gate_never_pushes(self):
        self.commit("raise SystemExit(7)\n")
        with self.assertRaises(subprocess.CalledProcessError):
            pusher.push_verified(self.root, "origin", "main")
        self.assertNotEqual(self.remote_head().returncode, 0)

    def test_dirty_tree_never_pushes(self):
        self.commit()
        (self.root / "private.txt").write_text("pending")
        with self.assertRaises(ValueError):
            pusher.push_verified(self.root, "origin", "main")
        self.assertNotEqual(self.remote_head().returncode, 0)

    def test_success_pushes_verified_commit_without_tags(self):
        commit = self.commit()
        self.git("tag", "do-not-publish")
        self.git("config", "push.followTags", "true")
        self.assertEqual(pusher.push_verified(self.root, "origin", "main"), commit)
        self.assertEqual(self.remote_head().stdout.strip(), commit)
        tags = subprocess.check_output(["git", "--git-dir", str(self.remote), "tag"], text=True)
        self.assertEqual(tags, "")

    def test_changed_head_does_not_change_pushed_commit(self):
        verified = self.commit()
        original = pusher.subprocess.run
        def run(command, **kwargs):
            result = original(command, **kwargs)
            if len(command) > 2 and command[1] == "-B" and command[2].endswith("/scripts/verify.py"):
                (self.root / "later.txt").write_text("not verified")
                self.git("add", ".")
                self.git("commit", "-m", "Later local change")
            return result
        with patch.object(pusher.subprocess, "run", side_effect=run):
            pusher.push_verified(self.root, "origin", "main")
        self.assertNotEqual(self.git("rev-parse", "HEAD"), verified)
        self.assertEqual(self.remote_head().stdout.strip(), verified)

    def test_removed_sensitive_blob_is_still_detected_in_history(self):
        (self.root / "old.txt").write_text("sk-" + "x" * 32)
        self.commit()
        self.git("rm", "old.txt")
        self.git("commit", "-m", "Remove fixture token")
        errors, count = verifier.check_history(self.root)
        self.assertEqual(count, 2)
        self.assertTrue(any("credential token" in e for e in errors))
        self.assertTrue(all("x" * 32 not in e for e in errors))

    def test_metadata_and_escaped_json_are_detected(self):
        path = "/Us" + "ers/fixture/private"
        data = json.dumps({"path": path}).replace("/", "\\/").encode()
        self.assertTrue(verifier.content_errors("fixture.json", data))
        self.assertTrue(verifier.content_errors("data.json", json.dumps({"session" + "_id": "fixture"}).encode()))
        self.assertEqual(verifier.content_errors("fixture.txt", b"fixture@example.invalid"), [])

    def test_ignored_directory_cannot_hide_tracked_private_file(self):
        (self.root / ".gitignore").write_text(".scratch/\n")
        (self.root / ".scratch").mkdir()
        (self.root / ".scratch/private.txt").write_text("private")
        self.git("add", "-f", ".scratch/private.txt")
        self.assertIn(".scratch/private.txt", verifier.source_files(self.root))
        self.assertTrue(verifier.private_path(".scratch/private.txt"))


if __name__ == "__main__":
    unittest.main()
