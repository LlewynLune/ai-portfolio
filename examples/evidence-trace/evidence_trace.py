#!/usr/bin/env python3
"""Build a readable trace from JSONL workflow events.

This is a deterministic starter example: it does not call an LLM or claim
that a product has been completed. It demonstrates how evidence can be
replayed and reviewed before a real AI project is added.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ALLOWED_ACTORS = {"human", "rule", "system", "model"}


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            missing = {"case_id", "title", "actor", "status", "evidence"} - event.keys()
            if missing:
                raise ValueError(f"line {line_number}: missing {sorted(missing)}")
            if event["actor"] not in ALLOWED_ACTORS:
                raise ValueError(f"line {line_number}: unknown actor {event['actor']}")
            if not isinstance(event["evidence"], list) or not event["evidence"]:
                raise ValueError(f"line {line_number}: evidence must be a non-empty list")
            events.append(event)
    if not events:
        raise ValueError("no events found")
    case_ids = {event["case_id"] for event in events}
    if len(case_ids) != 1:
        raise ValueError("all events must belong to one case_id")
    return events


def summarize(events: list[dict[str, Any]]) -> str:
    first = events[0]
    actors = Counter(event["actor"] for event in events)
    statuses = [event["status"] for event in events]
    lines = [
        f"Case: {first['case_id']}",
        f"Title: {first['title']}",
        f"Events: {len(events)}",
        "Actors: " + ", ".join(f"{name}={count}" for name, count in sorted(actors.items())),
        "Status path: " + " -> ".join(statuses),
        "",
        "Evidence:",
    ]
    for index, event in enumerate(events, start=1):
        note = event.get("note", "")
        lines.append(f"{index}. {event['actor']} / {event['status']} / {note}")
    if statuses[-1] != "reviewed":
        lines.append("", "Warning: trace has not reached a reviewed final state")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a JSONL evidence trace")
    parser.add_argument("input", type=Path, help="Path to a JSONL event file")
    parser.add_argument("-o", "--output", type=Path, help="Optional output text path")
    args = parser.parse_args()
    result = summarize(load_events(args.input))
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)


if __name__ == "__main__":
    main()
