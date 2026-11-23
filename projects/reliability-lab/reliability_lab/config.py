from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import math

STAGES = ("ingest", "retrieve", "analyze", "validate", "commit")
POLICIES = ("baseline", "retry", "resilient", "no_timeout")
PROFILES = ("clean", "transient", "mixed", "ack_loss", "permanent", "slow")
VERSION = "0.2.0"
SLOW_DELAY_MS = 140.0

@dataclass(frozen=True)
class Config:
    count: int = 24
    concurrency: int = 4
    seed: int = 42
    profile: str = "mixed"
    timeout_ms: float = 70.0
    budget_ms: float = 1000.0
    attempts: int = 3
    base_ms: float = 12.0
    backoff_ms: float = 8.0

    def __post_init__(self):
        for name, low, high in (("count", 1, 200), ("concurrency", 1, 16),
                               ("seed", 0, 2**31-1), ("attempts", 1, 5)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be integer in [{low},{high}]")
        for name, low, high in (("timeout_ms", 5, 1000), ("budget_ms", 20, 10000),
                               ("base_ms", 1, 100), ("backoff_ms", 0, 200)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f"{name} must be finite in [{low},{high}]")
        if self.profile not in PROFILES:
            raise ValueError("unknown profile")

    def dict(self):
        return asdict(self)

    def signature(self):
        payload = {"version": VERSION, **self.dict()}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def unit(seed: int, task: int, stage: str, salt: str = "fault") -> float:
    raw = f"{seed}:{task}:{stage}:{salt}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / 2**64


def fault_for(config: Config, task: int, stage: str) -> str:
    """Immutable first-attempt fault manifest; not influenced by policy."""
    if stage == "ingest":
        return "none"
    x = unit(config.seed, task, stage)
    profile = config.profile
    if profile == "clean":
        return "none"
    if profile == "ack_loss":
        return "ack_lost" if stage == "commit" and x < .55 else "none"
    if profile == "permanent":
        return "permanent" if stage == "analyze" and x < .45 else "none"
    if profile == "slow":
        return "slow" if stage in ("retrieve", "analyze") and x < .4 else "none"
    if profile == "transient":
        return "transient" if x < .25 else "none"
    if stage == "commit":
        return "ack_lost" if x < .22 else "none"
    if stage == "validate":
        return "invalid" if x < .07 else "none"
    if x < .16:
        return "transient"
    if x < .25:
        return "slow"
    if x < .29:
        return "permanent"
    return "none"


def manifest(config: Config):
    return [{"task": t, "stages": {s: fault_for(config, t, s) for s in STAGES}}
            for t in range(config.count)]
