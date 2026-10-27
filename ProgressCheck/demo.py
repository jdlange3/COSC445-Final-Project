"""Progress check demo: show the data, run the cleaning and analysis steps, open the main graph.

Press Enter to move to the next step.
"""
import subprocess
import sys
import webbrowser
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def step(title):
    input(f"\n--- {title} (press Enter) ---")


step("1. Data collected")
commits = pd.read_csv(ROOT / "data" / "clean" / "commits.csv", keep_default_na=False)
hunks = pd.read_csv(ROOT / "data" / "clean" / "hunks.csv", usecols=["sha"])
print(f"{len(commits):,} commits, {len(hunks):,} hunks, {commits['developer'].nunique()} developers")
print(commits[["sha", "developer", "date_utc", "subject"]].head(10).to_string(index=False))

step("2. Cleaning step")
subprocess.run([sys.executable, str(ROOT / "src" / "clean.py")], check=True)

step("3. Labels")
labels = pd.read_csv(ROOT / "data" / "labels" / "commit_labels.csv", keep_default_na=False)
print(labels["label"].value_counts().to_string())
print(labels[["year", "subject", "label", "source"]].sample(10, random_state=1).to_string(index=False))

step("4. Analysis by era")
subprocess.run([sys.executable, str(ROOT / "src" / "analyze.py")], check=True)

step("5. Graph")
webbrowser.open((ROOT / "results" / "figures" / "share_by_era.png").as_uri())
