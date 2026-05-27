#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, os.environ.get("CLAUDE_PROJECT_DIR", "."))

try:
    from budget import BudgetLedger
except Exception:
    sys.exit(0)

def extract_usage(line):
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(obj, dict):
        return 0
    usage = None
    msg = obj.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
        usage = msg["usage"]
    elif isinstance(obj.get("usage"), dict):
        usage = obj["usage"]
    if not usage:
        return 0
    return (
        int(usage.get("input_tokens", 0) or 0)
        + int(usage.get("output_tokens", 0) or 0)
        + int(usage.get("cache_creation_input_tokens", 0) or 0)
        + int(usage.get("cache_read_input_tokens", 0) or 0)
    )

def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    path = event.get("transcript_path")
    if not path or not os.path.exists(path):
        sys.exit(0)

    try:
        led = BudgetLedger.load()
        start = int(led.offsets.get(path, 0))
        size = os.path.getsize(path)
        if size < start:
            start = 0
        with open(path, "rb") as f:
            f.seek(start)
            chunk = f.read()
        end = start + len(chunk)
        counted = 0
        for line in chunk.decode("utf-8", errors="ignore").splitlines():
            counted += extract_usage(line)
        led.tokens_spent += counted
        led.offsets[path] = end
        led.save()
    except Exception:
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
