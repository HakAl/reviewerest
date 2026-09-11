#!/usr/bin/env python3
"""Resolve explicit evidence quotes inside supplied packets; never judge entailment."""

import argparse
import json
from pathlib import Path
import re


def assess(packet, record, *, require_quotes=False):
    errors, checked, unchecked = [], [], []
    sources = {}
    for artifact in packet.get("artifacts", []):
        name = artifact.get("source")
        if not isinstance(name, str) or name in sources:
            errors.append("Packet has missing or duplicate source identities.")
        else:
            sources[name] = artifact
    evidence = record.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
        errors.append("Record evidence must be a list.")
    for index, item in enumerate(evidence):
        label = f"evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(label + ": expected an object.")
            continue
        if "quote" not in item:
            unchecked.append(index)
            if require_quotes:
                errors.append(label + ": exact quote required.")
            continue
        quote = item["quote"]
        if not isinstance(quote, str) or not quote.strip():
            errors.append(label + ": quote must be a nonempty string.")
            continue
        name = item.get("source")
        source = sources.get(name) if isinstance(name, str) else None
        if source is None:
            errors.append(label + ": unknown packet source; no external file is read.")
            continue
        if item.get("revision") != source.get("revision"):
            errors.append(label + ": revision does not match packet source.")
            continue
        location = item.get("location")
        match = re.fullmatch(r"lines? ([1-9][0-9]*)(?:-([1-9][0-9]*))?", location or "") if isinstance(location, str) else None
        if not match:
            errors.append(label + ": use line N or lines N-M.")
            continue
        start, end = int(match[1]), int(match[2] or match[1])
        text = source.get("text")
        if not isinstance(text, str):
            errors.append(label + ": packet source is not text.")
            continue
        lines = text.splitlines(keepends=True)
        if end < start or end > len(lines):
            errors.append(label + ": line range is out of bounds or reversed.")
            continue
        if quote not in "".join(lines[start - 1:end]):
            errors.append(label + ": quote is absent from the cited range.")
            continue
        checked.append(index)
    if not checked:
        errors.append("No citation was successfully checked.")
    return {"valid": not errors, "checked_evidence": checked, "unchecked_evidence": unchecked,
            "errors": errors, "validation_scope": "quote_location_only", "semantic_support_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("record", type=Path)
    parser.add_argument("--require-quotes", action="store_true")
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text())
        record = json.loads(args.record.read_text())
        if not isinstance(packet, dict) or not isinstance(record, dict):
            raise ValueError("Packet and record must be JSON objects.")
        result = assess(packet, record, require_quotes=args.require_quotes)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        result = {"valid": False, "errors": [str(exc)], "semantic_support_verified": False}
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
