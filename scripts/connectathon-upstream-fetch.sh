#!/usr/bin/env bash
# Fetch Connectathon upstream remotes and print commits since last recorded SHA.
# Usage (from HL7-FHIR-quality-testing repo root):
#   ./scripts/connectathon-upstream-fetch.sh
# Optional: CONNECTATHON_WATCH_DIR=~/work/upstream-watches
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="${ROOT}/scripts/connectathon-upstream-shas.json"
WATCH_DIR="${CONNECTATHON_WATCH_DIR:-${HOME}/work/upstream-watches}"
mkdir -p "$WATCH_DIR"

if [[ ! -f "$STATE" ]]; then
  echo "Missing state file: $STATE" >&2
  exit 1
fi

python3 - "$STATE" "$WATCH_DIR" <<'PY'
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

state_path, watch_dir = Path(sys.argv[1]), Path(sys.argv[2])
state = json.loads(state_path.read_text())
repos = state.get("repos", {})
changed_any = False
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"cmd failed ({r.returncode}): {' '.join(cmd)}\n{msg}")
    return r

for key, meta in repos.items():
    url = meta["url"]
    branch = meta.get("branch", "main")
    dest = watch_dir / key
    print(f"\n==> {key} ({url} @ {branch})")
    if not (dest / ".git").exists():
        print(f"    cloning shallow into {dest}")
        run(["git", "clone", "--depth", "50", "--branch", branch, url, str(dest)])
    else:
        run(["git", "fetch", "--depth", "50", "origin", branch], cwd=dest)

    new_sha = run(["git", "rev-parse", f"origin/{branch}"], cwd=dest).stdout.strip()
    old_sha = meta.get("sha") or ""
    short_new = new_sha[:12]
    tip_subj = run(
        ["git", "log", "-1", "--format=%s", new_sha], cwd=dest
    ).stdout.strip()
    tip_date = run(
        ["git", "log", "-1", "--format=%cs", new_sha], cwd=dest
    ).stdout.strip()

    if old_sha and old_sha == new_sha:
        print(f"    unchanged {short_new} — {tip_subj}")
    elif old_sha:
        # May fail if old_sha fell off shallow history; fall back to last 15
        try:
            log = run(
                ["git", "log", "--oneline", f"{old_sha}..{new_sha}"], cwd=dest
            ).stdout.strip()
        except RuntimeError:
            log = run(["git", "log", "--oneline", "-15", new_sha], cwd=dest).stdout.strip()
            log = f"(shallow history missed {old_sha[:12]}; recent tips)\n{log}"
        print(f"    UPDATED {old_sha[:12]} -> {short_new} ({tip_date})")
        print(log if log else "    (no commits listed)")
        changed_any = True
    else:
        print(f"    baseline {short_new} ({tip_date}) — {tip_subj}")
        changed_any = True

    meta["sha"] = new_sha
    meta["short"] = short_new
    meta["tip_date"] = tip_date
    meta["tip_subject"] = tip_subj
    meta["checked_at"] = now

    # Optional: latest release tag via gh/api not required; record if present
    try:
        tags = run(["git", "tag", "--sort=-creatordate"], cwd=dest).stdout.splitlines()
        if tags:
            meta["latest_tag_seen"] = tags[0]
    except RuntimeError:
        pass

state["updated_at"] = now
state_path.write_text(json.dumps(state, indent=2) + "\n")
print(f"\nState written: {state_path}")
print("CHANGED" if changed_any else "NO_CHANGES")
sys.exit(0)
PY
