import sys
import os
import json

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not os.environ.get("CLAUDE_PROJECT_DIR"):
    os.environ["CLAUDE_PROJECT_DIR"] = _PROJECT_ROOT
sys.path.insert(0, _PROJECT_ROOT)

try:
    from budget import BudgetLedger, FLOOR, estimate_tokens
except Exception:
    sys.exit(0)

OUTPUT_RESERVE = 24_000


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = event.get("tool_input", {}) or {}
    text = " ".join(str(tool_input.get(k, "")) for k in ("description", "prompt", "subagent_type"))

    try:
        led = BudgetLedger.load()
        predicted = estimate_tokens(text, OUTPUT_RESERVE)
        available = led.remaining() - FLOOR
    except Exception:
        sys.exit(0)

    if predicted > available:
        sys.stderr.write(
            f"BUDGET GATE: blocked. ~{predicted:,} tokens needed, only "
            f"{available:,} available above the {FLOOR:,} floor.\n"
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
