#!/usr/bin/env python3
"""Frame artifact text for a composed prompt. Reads input; writes only stdout.

Framing preserves text and marks provenance. It does not prevent prompt injection
or confer trust on metadata. The caller owns retrieval identity and instructions.
"""

import argparse
import json
import sys
from pathlib import Path


def frame(text, source_id, revision=None):
    payload = json.dumps({"source_id": source_id, "revision": revision, "text": text}, ensure_ascii=True)
    for char, escaped in [("<", r"\u003c"), (">", r"\u003e"), ("&", r"\u0026")]:
        payload = payload.replace(char, escaped)
    return "<artifact_content>\n" + payload + "\n</artifact_content>\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="UTF-8 artifact path, or - to read stdin")
    parser.add_argument("--source-id", required=True, help="Retrieval-assigned source identity")
    parser.add_argument("--revision", help="Resolved source revision, if known")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"error": type(exc).__name__, "message": "Artifact text unavailable."}), file=sys.stderr)
        return 3
    sys.stdout.write(frame(text, args.source_id, args.revision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
