"""Step 1: download the Vichan repository and save its history as CSV files.

Outputs (data/extracted/):
  commits.csv       one row per commit on any branch (merges included)
  file_changes.csv  one row per file changed by a non-merge commit
  hunks.csv         one row per changed code block (diff hunk) of a non-merge commit
"""
import re
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/vichan-devel/vichan.git"
CLONE = ROOT / "data" / "raw" / "vichan.git"
OUT = ROOT / "data" / "extracted"

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@ ?(.*)$")


def git(*args):
    out = subprocess.run(["git", f"--git-dir={CLONE}", "-c", "core.quotepath=off", *args],
                         capture_output=True, check=True).stdout
    return out.decode("utf-8", errors="replace")


def clone():
    if not CLONE.exists():
        subprocess.run(["git", "clone", "--bare", REPO_URL, str(CLONE)], check=True)
    else:
        subprocess.run(["git", f"--git-dir={CLONE}", "fetch", "origin",
                        "+refs/heads/*:refs/heads/*", "--tags"], check=True)


def commits():
    fmt = "%H%x1f%P%x1f%an%x1f%ae%x1f%at%x1f%ai%x1f%cn%x1f%ce%x1f%ct%x1f%s%x1f%b%x1e"
    master = set(git("rev-list", "master").split())
    rows = []
    for rec in git("log", "--all", f"--format={fmt}").split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, parents, an, ae, at, ai, cn, ce, ct, subject, body = rec.split("\x1f")
        rows.append({
            "sha": sha, "parents": parents, "n_parents": len(parents.split()),
            "author_name": an, "author_email": ae, "author_time": int(at),
            "author_tz": ai[-5:], "committer_name": cn, "committer_email": ce,
            "commit_time": int(ct), "on_master": sha in master,
            "subject": subject, "body": body.strip(),
        })
    return pd.DataFrame(rows)


def file_changes():
    rows, sha = [], None
    for line in git("log", "--all", "--no-merges", "--numstat", "--format=\x01%H").splitlines():
        if line.startswith("\x01"):
            sha = line[1:]
        elif line:
            added, deleted, path = line.split("\t", 2)
            rows.append({"sha": sha, "path": path,
                         "added": None if added == "-" else int(added),
                         "deleted": None if deleted == "-" else int(deleted)})
    return pd.DataFrame(rows)


def hunks():
    rows, sha, path, cur = [], None, None, None
    for line in git("log", "--all", "--no-merges", "-p", "--format=\x01%H").splitlines():
        if line.startswith("\x01"):
            sha, cur = line[1:], None
        elif line.startswith("diff --git "):
            path, cur = line.split(" b/", 1)[-1], None
        elif line.startswith("+++ ") and cur is None:
            if line != "+++ /dev/null":
                path = line[6:]
        elif line.startswith("@@ "):
            m = HUNK_RE.match(line)
            cur = {"sha": sha, "path": path,
                   "old_start": int(m[1]), "old_len": int(m[2] or 1),
                   "new_start": int(m[3]), "new_len": int(m[4] or 1),
                   "added": 0, "removed": 0, "heading": m[5].strip()}
            rows.append(cur)
        elif cur is not None and line.startswith("+"):
            cur["added"] += 1
        elif cur is not None and line.startswith("-"):
            cur["removed"] += 1
    return pd.DataFrame(rows)


def main():
    clone()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("commits", commits), ("file_changes", file_changes), ("hunks", hunks)):
        df = fn()
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(df):,} rows")


if __name__ == "__main__":
    main()
