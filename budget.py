import json
import os
import tempfile
import time
from pathlib import Path

WINDOW_HOURS    = 5
BUDGET_CAP      = 2_000_000
FLOOR           = 150_000
CHARS_PER_TOKEN = 4
_LOCK_TIMEOUT   = 3.0
_LOCK_STALE     = 30.0


def _project_dir():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent


def _ledger_path():
    return _project_dir() / ".claude" / "budget_ledger.json"


def _lock_path():
    return _project_dir() / ".claude" / "budget_ledger.lock"


def _coerce_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class _FileLock:
    def __init__(self):
        self.path = _lock_path()
        self.acquired = False

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + _LOCK_TIMEOUT
        while time.time() < deadline:
            try:
                if self.path.exists() and time.time() - self.path.stat().st_mtime > _LOCK_STALE:
                    self.path.unlink()
            except OSError:
                pass
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self.acquired = True
                return self
            except FileExistsError:
                time.sleep(0.05)
            except OSError:
                break
        return self

    def __exit__(self, *exc):
        if self.acquired:
            try:
                self.path.unlink()
            except OSError:
                pass
        return False


class BudgetLedger:
    def __init__(self, window_start=None, tokens_spent=0, offsets=None):
        self.window_start = _coerce_float(window_start, time.time())
        self.tokens_spent = max(0, _coerce_int(tokens_spent, 0))
        self.offsets = offsets if isinstance(offsets, dict) else {}

    @classmethod
    def load(cls):
        p = _ledger_path()
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if not isinstance(data, dict):
                    data = {}
            except (json.JSONDecodeError, ValueError, OSError):
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
        payload = json.dumps({
            "window_start": self.window_start,
            "tokens_spent": self.tokens_spent,
            "offsets": self.offsets,
        }, indent=2)
        fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(payload)
            os.replace(tmp, str(p))
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    def _maybe_reset(self):
        if time.time() - self.window_start > WINDOW_HOURS * 3600:
            self.window_start = time.time()
            self.tokens_spent = 0
            self.offsets = {
                path: end for path, end in self.offsets.items()
                if os.path.exists(path)
            }

    def remaining(self):
        self._maybe_reset()
        return BUDGET_CAP - self.tokens_spent

    def record(self, tokens):
        with _FileLock():
            fresh = BudgetLedger.load()
            fresh.tokens_spent += max(0, _coerce_int(tokens, 0))
            fresh.save()
            self.window_start = fresh.window_start
            self.tokens_spent = fresh.tokens_spent
            self.offsets = fresh.offsets

    def calibrate(self, true_remaining_pct):
        pct = max(0.0, min(100.0, _coerce_float(true_remaining_pct, 100.0)))
        with _FileLock():
            fresh = BudgetLedger.load()
            fresh.tokens_spent = int(BUDGET_CAP * (1 - pct / 100))
            fresh.save()
            self.tokens_spent = fresh.tokens_spent

    @classmethod
    def reconcile_transcript(cls, transcript_path, extract_fn):
        with _FileLock():
            led = cls.load()
            if not os.path.exists(transcript_path):
                return led
            start = _coerce_int(led.offsets.get(transcript_path, 0), 0)
            size = os.path.getsize(transcript_path)
            if size < start:
                start = 0
            with open(transcript_path, "rb") as f:
                f.seek(start)
                chunk = f.read()
            end = start + len(chunk)
            counted = 0
            for line in chunk.decode("utf-8", errors="ignore").splitlines():
                counted += _coerce_int(extract_fn(line), 0)
            led.tokens_spent += counted
            led.offsets[transcript_path] = end
            led.save()
            return led


def estimate_tokens(text, output_reserve):
    return int(len(text) / CHARS_PER_TOKEN) + int(output_reserve)
