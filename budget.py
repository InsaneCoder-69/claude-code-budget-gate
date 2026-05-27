import json
import os
import time
from pathlib import Path

WINDOW_HOURS    = 5
BUDGET_CAP      = 2_000_000
FLOOR           = 150_000
CHARS_PER_TOKEN = 4

def _ledger_path() -> Path:
    base = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    return Path(base) / ".claude" / "budget_ledger.json"

class BudgetLedger:
    def __init__(self, window_start=None, tokens_spent=0, offsets=None):
        self.window_start = window_start if window_start is not None else time.time()
        self.tokens_spent = tokens_spent
        self.offsets = offsets or {}

    @classmethod
    def load(cls):
        p = _ledger_path()
        if p.exists():
            try:
                data = json.loads(p.read_text())
            except (json.JSONDecodeError, ValueError):
                data = {}
            led = cls(
                window_start=data.get("window_start"),
                tokens_spent=data.get("tokens_spent", 0),
                offsets=data.get("offsets", {}),
            )
            led._maybe_reset()
            return led
        return cls()

    def save(self):
        p = _ledger_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "window_start": self.window_start,
            "tokens_spent": self.tokens_spent,
            "offsets": self.offsets,
        }, indent=2))

    def _maybe_reset(self):
        if time.time() - self.window_start > WINDOW_HOURS * 3600:
            self.window_start = time.time()
            self.tokens_spent = 0
            self.offsets = {}

    def remaining(self):
        self._maybe_reset()
        return BUDGET_CAP - self.tokens_spent

    def record(self, tokens):
        self.tokens_spent += max(0, int(tokens))
        self.save()

    def calibrate(self, true_remaining_pct):
        true_remaining_pct = max(0.0, min(100.0, float(true_remaining_pct)))
        self.tokens_spent = int(BUDGET_CAP * (1 - true_remaining_pct / 100))
        self.save()

def estimate_tokens(text, output_reserve):
    return int(len(text) / CHARS_PER_TOKEN) + int(output_reserve)
