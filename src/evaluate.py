"""Step 4: check how accurate the automatic labels are against a hand-labeled random sample.

First run: writes data/labels/hand_sample.csv with an empty hand_label column to fill in.
After it is filled in: compares hand labels to automatic labels and writes
results/tables/accuracy_by_source.csv and results/tables/confusion_matrix.csv.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / "data" / "labels"
TABLES = ROOT / "results" / "tables"
SAMPLE = LABELS / "hand_sample.csv"
SAMPLE_SIZE = 200
CATEGORIES = ["Feature", "Bug Fix", "Security Fix", "Code Cleanup", "Documentation"]


def main():
    labels = pd.read_csv(LABELS / "commit_labels.csv", keep_default_na=False)
    if not SAMPLE.exists():
        sample = labels.sample(SAMPLE_SIZE, random_state=445)[["sha", "year", "subject"]]
        sample["hand_label"] = ""
        sample.to_csv(SAMPLE, index=False)
        print(f"wrote {SAMPLE}; fill in hand_label and run again")
        return

    sample = pd.read_csv(SAMPLE, keep_default_na=False)
    df = sample.merge(labels[["sha", "label", "source"]], on="sha")
    df["correct"] = df["hand_label"] == df["label"]

    TABLES.mkdir(parents=True, exist_ok=True)
    by_source = df.groupby("source")["correct"].agg(commits="size", correct="sum")
    by_source.loc["all"] = [len(df), df["correct"].sum()]
    by_source["accuracy"] = (by_source["correct"] / by_source["commits"]).round(3)
    by_source.to_csv(TABLES / "accuracy_by_source.csv")

    confusion = pd.crosstab(df["hand_label"], df["label"]).reindex(
        index=CATEGORIES, columns=CATEGORIES, fill_value=0)
    confusion.index.name, confusion.columns.name = "hand label", "automatic label"
    confusion.to_csv(TABLES / "confusion_matrix.csv")

    print(by_source.to_string())
    print(confusion.to_string())


if __name__ == "__main__":
    main()
