"""Verify the postmortem entry against the 400-char gate and ship a receipt."""
import json
import os
import re
import sys
from pathlib import Path

LIMIT = 400
TAG = "pm-webhook-1947"
STORY = (
    "I asked the agent to remove the deprecated retry logic, so it removed "
    "retries from the payment webhook too, and in the six minutes before "
    "anyone noticed we charged 1,947 customers once and refunded them twice."
)


def audit(text):
    problems = []
    if not text.strip():
        problems.append("blank")
    if len(text) > LIMIT:
        problems.append("over limit: %d" % len(text))
    if "\n" in text:
        problems.append("newline inside story")
    clauses = re.split(r"[.;!?]", text.strip())
    beats = [c for c in clauses if c.strip()]
    if len(beats) > 2:
        problems.append("more than two sentences")
    return {"problems": problems, "chars": len(text), "beats": len(beats)}


def ship():
    root = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    root.mkdir(parents=True, exist_ok=True)
    dest = root / "entry.txt"
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(STORY + "\n")
    back = dest.read_text(encoding="utf-8").strip()
    if back != STORY:
        print(json.dumps({"ok": False, "why": "readback mismatch"}))
        return 2
    report = audit(back)
    report["ok"] = not report["problems"]
    report["dest"] = str(dest)
    report["limit"] = LIMIT
    report["tag"] = TAG
    print(json.dumps(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(ship())
