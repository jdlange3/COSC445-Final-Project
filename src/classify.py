"""Step 3: sort each commit into Feature, Bug Fix, Security Fix, Code Cleanup or Documentation.

1. keyword rules on the commit subject (and file rules for documentation/translation-only commits)
2. commits no rule matches take their label from data/labels/llm_labels.csv (AI language model)

A second flag, `external`, marks work forced by outside changes: security holes and
compatibility with new PHP/browser/library versions.

Outputs: data/labels/commit_labels.csv, and data/labels/llm_queue.csv (commits still needing an AI label)
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
LABELS = ROOT / "data" / "labels"
CATEGORIES = ["Feature", "Bug Fix", "Security Fix", "Code Cleanup", "Documentation"]

# checked in this order; the first match wins
RULES = [
    ("Security Fix", r"\bxss\b|csrf|(?<!dependency )injection|vulnerab|exploit|security|\bcve\b|sanitiz|"
                     r"info(rmation)? leak|\bleak|brute.?force|clickjack|\brce\b"),
    ("Documentation", r"^(update[ds]? |added |add |fix(ed)? )?(the )?(readme|license|changelog|docs?|documentation|"
                      r"comments?|translations?|locales?)\b|translation|\blocale\b|\btypos?\b|\bcomments? (in|for|to|about)\b|"
                      r"\bcopyright|(?-i:\b[a-z]{2}_[A-Z]{2}\b)"),
    ("Bug Fix", r"\bfix|\bbug|broken|\bcrash|doesn'?t work|not working|\berror\b|\bwrong\b|\bissue\b|"
                r"\bcorrect(ed|s)?\b|\bproblem\b|\bhotfix"),
    ("Code Cleanup", r"refactor|clean ?up|cleanup|\bunused\b|\bformat(ting)?\b|whitespace|\bindent|"
                     r"\btidy\b|simplif|reorganiz|\blint|\bcosmetic|\bcruft\b|\bdeprecat|\bremove dead|"
                     r"\bstyle fix|code style|\bpsr\b"),
    ("Feature", r"^(add(ed|s)?|implement(ed|s)?|introduc(e|ed|es)|new|support|allow(s|ed)?|enable)\b|"
                r"\bnew (feature|option|theme|board|page)|\boption to\b|\bsupport for\b"),
]
EXTERNAL = (r"\bxss\b|csrf|(?<!dependency )injection|vulnerab|exploit|security|\bcve\b|sanitiz|info(?:rmation)? leak|"
            r"\bphp ?[5-8](?:\.\d)?\b|\bphp[5-8]|deprecat|\bcompat|chrom(?:e|ium)|firefox|safari|\bopera\b|"
            r"\bbrowser|\bie ?\d+\b|internet explorer|jquery ?\d|mysql ?\d|mariadb|\bupstream\b")
DOC_FILE = re.compile(r"(\.md$|\.txt$|^readme|/readme|^license|^docs?/|\.po$|\.mo$|^inc/locale/)", re.I)


def keyword_label(subject):
    if subject.lower().startswith("revert"):
        return None  # a revert's purpose depends on what it undoes, so the AI labels it
    for label, pattern in RULES:
        if re.search(pattern, subject, re.I):
            return label
    return None


def main():
    commits = pd.read_csv(CLEAN / "commits.csv", keep_default_na=False)
    files = pd.read_csv(ROOT / "data" / "extracted" / "file_changes.csv", keep_default_na=False)
    files = files[files["sha"].isin(commits["sha"])]
    doc_only = files.groupby("sha")["path"].apply(lambda p: len(p) > 0 and all(DOC_FILE.search(x) for x in p))

    commits["label"] = commits["subject"].map(keyword_label)
    commits["source"] = commits["label"].notna().map({True: "keyword", False: None})
    by_file = commits["sha"].map(doc_only).eq(True) & (commits["label"] != "Security Fix")
    commits.loc[by_file, ["label", "source"]] = ["Documentation", "file"]

    llm_path = LABELS / "llm_labels.csv"
    if llm_path.exists():
        llm = pd.read_csv(llm_path).set_index("sha")["label"]
        todo = commits["label"].isna()
        commits.loc[todo, "label"] = commits.loc[todo, "sha"].map(llm)
        commits.loc[todo & commits["label"].notna(), "source"] = "llm"

    commits["external"] = (commits["label"] == "Security Fix") | commits["subject"].str.contains(EXTERNAL, case=False, regex=True)

    queue = commits[commits["label"].isna()]
    paths = files.groupby("sha")["path"].apply(lambda p: " ".join(p[:6]))
    queue = queue.assign(files=queue["sha"].map(paths).fillna(""), body=queue["body"].str[:300])
    queue[["sha", "subject", "body", "files"]].to_csv(LABELS / "llm_queue.csv", index=False)

    commits[["sha", "year", "developer", "subject", "label", "source", "external"]].to_csv(
        LABELS / "commit_labels.csv", index=False)
    print(commits["source"].value_counts(dropna=False).to_string())
    print(commits["label"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
