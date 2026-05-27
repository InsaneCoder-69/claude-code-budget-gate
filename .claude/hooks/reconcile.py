import sys
import os
import json

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not os.environ.get("CLAUDE_PROJECT_DIR"):
    os.environ["CLAUDE_PROJECT_DIR"] = _PROJECT_ROOT
sys.path.insert(0, _PROJECT_ROOT)

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
        BudgetLedger.reconcile_transcript(path, extract_usage)
    except Exception:
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
