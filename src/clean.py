"""Step 2: clean the extracted history.

- drop merge commits
- drop duplicate copies of the same change that live on more than one branch
  (same author email, author time and subject; the copy on master is kept)
- convert author times to UTC
- combine the different names and emails that belong to the same developer

Outputs (data/clean/): commits.csv, hunks.csv, identities.csv, cleaning_summary.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "extracted"
OUT = ROOT / "data" / "clean"

# names and emails too generic to prove two identities are the same person
GENERIC_NAMES = {"", "root", "unknown", "your name", "michael", "chris", "matthieu"}
GENERIC_EMAILS = {"you@example.com", "no@no.com"}

# links that share neither a name nor an email (checked by hand in commit history and README)
MANUAL_LINKS = [
    ("name:savetheinternet", "email:savetheinternet@mint"),           # "Michael" on host "mint"
    ("name:savetheinternet", "email:savetheinternet@omegadev.org"),   # name field holds an email
]

# display name for developers whose most used name is a handle or a site name (from the README timeline)
DISPLAY_NAMES = {
    "admin@8chan.co": "Fredrick Brennan",
    "savetheinternet@n0v4.com": "Michael Foster",
    "angeleno@screamer.wiki": "RealAngeleno",
    "89118232+perdedora@users.noreply.github.com": "perdedora",
}


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def identities(commits):
    pairs = commits.groupby(["author_name", "author_email"], dropna=False).size().reset_index(name="n")
    pairs["author_name"] = pairs["author_name"].fillna("")
    uf = UnionFind()
    for p in pairs.itertuples():
        node = f"pair:{p.author_name}|{p.author_email}"
        uf.find(node)
        name, email = p.author_name.strip().lower(), p.author_email.strip().lower()
        if name not in GENERIC_NAMES:
            uf.union(node, f"name:{name}")
        if email not in GENERIC_EMAILS and "localhost" not in email and "(none)" not in email:
            uf.union(node, f"email:{email}")
    for a, b in MANUAL_LINKS:
        uf.union(a, b)
    pairs["cluster"] = [uf.find(f"pair:{p.author_name}|{p.author_email}") for p in pairs.itertuples()]
    # developer name = display name if set, else the most used name in the cluster
    top = pairs.sort_values("n", ascending=False).drop_duplicates("cluster").set_index("cluster")
    canon = top["author_email"].map(DISPLAY_NAMES).fillna(top["author_name"])
    generic = canon.str.lower().isin(GENERIC_NAMES)
    canon[generic] = canon[generic] + " <" + top["author_email"][generic] + ">"
    pairs["developer"] = pairs["cluster"].map(canon)
    return pairs.drop(columns="cluster")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    commits = pd.read_csv(IN / "commits.csv", keep_default_na=False)
    hunks = pd.read_csv(IN / "hunks.csv", keep_default_na=False)
    steps = [("extracted commits (all branches)", len(commits))]

    commits = commits[commits["n_parents"] < 2]
    steps.append(("after removing merge commits", len(commits)))

    commits = (commits.sort_values(["on_master", "commit_time"], ascending=[False, True])
               .drop_duplicates(["author_email", "author_time", "subject"]))
    steps.append(("after removing duplicate copies on other branches", len(commits)))

    ids = identities(commits)
    commits = commits.merge(ids[["author_name", "author_email", "developer"]],
                            on=["author_name", "author_email"], how="left")
    commits["date_utc"] = pd.to_datetime(commits["author_time"], unit="s", utc=True)
    commits["year"] = commits["date_utc"].dt.year
    commits = commits.sort_values("author_time").reset_index(drop=True)

    hunks = hunks[hunks["sha"].isin(commits["sha"])]
    steps += [("raw author name/email pairs", len(ids)),
              ("developers after combining identities", ids["developer"].nunique()),
              ("extracted hunks", len(pd.read_csv(IN / "hunks.csv", usecols=["sha"]))),
              ("hunks in kept commits", len(hunks))]

    cols = ["sha", "developer", "author_name", "author_email", "author_time", "date_utc",
            "year", "author_tz", "on_master", "subject", "body"]
    commits[cols].to_csv(OUT / "commits.csv", index=False)
    hunks.to_csv(OUT / "hunks.csv", index=False)
    ids.sort_values(["developer", "n"], ascending=[True, False]).to_csv(OUT / "identities.csv", index=False)
    summary = pd.DataFrame(steps, columns=["step", "count"])
    summary.to_csv(OUT / "cleaning_summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
