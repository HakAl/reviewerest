#!/usr/bin/env python3
"""Export only the source-first adjudication packet, without coordinator material."""

import argparse
import json
from pathlib import Path
import re
import shutil

import grade_reviews as grader

SUITE = grader.ROOT / "evals/skill-effect-adjudication-v1"
PHASE_FILES = ("protocol.md", "response-template.json", "shared-output.schema.json")


def phase_one(suite):
    manifest = grader.read(suite / "phase1/manifest.json")
    ids = manifest["case_ids"]
    if not isinstance(ids, list) or len(ids) != 9 or any(not isinstance(i, str) or not re.fullmatch(r"r\d{2}", i) for i in ids):
        raise ValueError("Phase-one case IDs must be nine neutral rNN aliases.")
    names = list(PHASE_FILES) + ["cases/" + ident + ".json" for ident in manifest["case_ids"]]
    if len(set(manifest["case_ids"])) != 9 or set(manifest["files"]) != set(names):
        raise ValueError("Phase one must contain exactly its fixed protocol and nine source packets.")
    for name in names:
        path = suite / "phase1" / name
        if grader.host.digest(path.read_bytes()) != manifest["files"][name]:
            raise ValueError("Frozen phase-one input changed: " + name)
    packets = [grader.read(suite / "phase1/cases" / (ident + ".json")) for ident in manifest["case_ids"]]
    for ident, packet in zip(manifest["case_ids"], packets):
        if set(packet) != {"id", "request", "mode", "capabilities", "context", "artifacts"} or packet["id"] != ident:
            raise ValueError("Unexpected source-packet fields or identity.")
    return manifest, packets


def bundle(suite):
    manifest, packets = phase_one(suite)
    parts = [(suite / "phase1/protocol.md").read_text(),
             "\nPhase-one manifest SHA-256: " + grader.host.digest((suite / "phase1/manifest.json").read_bytes()),
             "\nProposed common candidate-output schema:\n```json\n" + (suite / "phase1/shared-output.schema.json").read_text() + "```",
             "\nRecord your adjudication using this template:\n```json\n" + (suite / "phase1/response-template.json").read_text() + "```"]
    for packet in packets:
        encoded = json.dumps(packet, indent=2, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        parts += ["\nSource packet " + packet["id"], "<artifact_content>\n" + encoded + "\n</artifact_content>"]
    return "\n".join(parts) + "\n"


def export(suite, destination):
    manifest, _ = phase_one(suite)
    text = bundle(suite)
    destination.mkdir(parents=True, exist_ok=False)
    for name in (*manifest["files"], "manifest.json"):
        dest = destination / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / "phase1" / name, dest)
    (destination / "START-HERE.md").write_text(text)


def validate_candidate(value, packet):
    """Check the proposed common output shape and location bounds, not review truth."""
    if not isinstance(value, dict) or set(value) != {"findings"} or not isinstance(value["findings"], list):
        raise ValueError("Only a findings array is allowed at the root.")
    sources = {a["source"]: a["text"].splitlines() for a in packet["artifacts"]}
    for finding in value["findings"]:
        if not isinstance(finding, dict) or set(finding) != {"finding", "location", "claim", "severity"}:
            raise ValueError("Each finding must contain exactly finding, location, claim and severity.")
        if not all(isinstance(finding[k], str) and finding[k].strip() for k in ("finding", "claim")):
            raise ValueError("Finding and claim must be nonempty text.")
        if finding["severity"] not in ("high", "medium", "low", "unrated"):
            raise ValueError("Unknown severity token.")
        if not isinstance(finding["location"], list) or not finding["location"]:
            raise ValueError("Each finding requires at least one source location.")
        for loc in finding["location"]:
            if not isinstance(loc, dict) or set(loc) != {"source", "start_line", "end_line"}:
                raise ValueError("Location fields differ from the shared schema.")
            source, start, end = loc["source"], loc["start_line"], loc["end_line"]
            if (not isinstance(source, str) or source not in sources or type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= len(sources[source])):
                raise ValueError("Location does not resolve within a supplied source.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=SUITE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        export(args.suite, args.output)
        print("Exported source-first packet. This does not perform or certify adjudication.")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
