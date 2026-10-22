import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# settings
NETID = "ttb615"
PROJECT = "vichan-devel_vichan"
REPO_URL = "https://github.com/vichan-devel/vichan.git"
BRANCH = "master"
MIN_GAP_MONTHS = 3        # a "gap" counts for NumberOfGapsInTimeline
N_GAP_COMMITS = 10        # commits taken before / after the longest gap

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output")
OUT.mkdir(parents=True, exist_ok=True)
CLONE = Path("vichan_repo.git")

# hand-entered (manual) data
MANUAL = {
    "#stars": 769,                      # read from the GitHub repo page
    "#forks": 216,                      # read from the GitHub repo page
    "LastGHCommitDate": "2026/07/06",   # last commit on master (GitHub)
    "ActivityPattern": "irregular",
    "BeforeThemes": "Bug fixes:Dependency updates",
    "AfterThemes": "Bug fixes:Documentation updates",
    "HypothesizedGapReason": (
        "Maintainer attention dropped after a PHP 7.4 compatibility push. "
        "The last pre-gap commits (Jan 2020) are PHP 7.4 deprecation fixes by "
        "maintainer Fredrick Brennan, and no commits appear Feb-Jul 2020. "
        "README lists Brennan as maintainer 2017-2021, and his Nov 2020 README "
        "edit says paid support is not offered right now. Cause not stated in "
        "any commit message."
    ),
    "HasRecovered": "Yes",
    "WhyRecovered": (
        "Outside contributors sent bug and security fixes through numbered PRs "
        "(#376, #377, #378, #380) on 2020-08-10 to 2020-08-15: ban lookup used "
        "the wrong variable, an information leak in thread.html, and a Chromium "
        "capitalization bug."
    ),
    "WhoRecovered": (
        "New people (papereth, Eman Gamer, Sardach and later panfu28), not the "
        "maintainer. Later revival (2023-2024) came from new contributors and "
        "maintainers (Zankaria, RealAngeleno, Lorenzo Yario)."
    ),
    "Currentstatus": "Inactive",   # archived 2026-07-06; the date rule alone would say Active
    "RecentThemes": "Release:Documentation updates",
    "Notes": (
        "Vichan grew fast from its Tinyboard fork origins (peak 1,080 commits in "
        "2013), shrank to 13-24 commits a year in 2018-2020, and had a revival in "
        "2023-2024 (152 and 521 commits) under new people. The 6-month gap in 2020 "
        "follows a maintainer-led PHP 7.4 fix and ends with outside contributors "
        "fixing bugs, and the README states the project reached end of life. The "
        "repo was archived by its owner on 2026-07-06, so it is marked Inactive "
        "even though that date is a commit."
    ),
}


# ------------------------------------------------------------------ Part 1
def get_commits() -> pd.DataFrame:
    """Clone (once) and read every commit on BRANCH, using author time."""
    if not CLONE.exists():
        subprocess.run(["git", "clone", "--bare", REPO_URL, str(CLONE)], check=True)
    # %x1f / %x1e are separator characters so multi-line messages are safe
    fmt = "%H%x1f%an <%ae>%x1f%at%x1f%B%x1e"
    raw = subprocess.run(
        ["git", f"--git-dir={CLONE}", "log", BRANCH, f"--format={fmt}"],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = []
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, author, t, msg = rec.split("\x1f", 3)
        rows.append([PROJECT, sha, author, int(t), msg.strip()])
    df = pd.DataFrame(rows, columns=["project", "sha", "author", "time", "msg"])
    df = df.sort_values("time").reset_index(drop=True)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["ym"] = df["dt"].dt.strftime("%Y-%m")
    return df


# ------------------------------------------------------------------ Part 2
def monthly_series(df: pd.DataFrame) -> pd.DataFrame:
    """One row per month from first to last commit; zero months included."""
    months = [str(m) for m in pd.period_range(df["ym"].min(), df["ym"].max(), freq="M")]
    counts = df.groupby("ym").size().reindex(months, fill_value=0)
    return pd.DataFrame({"Month": counts.index, "#Commits": counts.values})


def plot_series(ts: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(12, 5))
    plt.plot(ts["Month"], ts["#Commits"], marker="o", markersize=2, linestyle="-")
    plt.xlabel("Time (YYYY-MM)")
    plt.ylabel("Number of Commits")
    plt.title(f"Commit Activity: {PROJECT}")
    plt.grid(True)
    step = max(1, len(ts) // 20)
    plt.xticks(range(0, len(ts), step), ts["Month"][::step], rotation=45)
    plt.tight_layout()
    plt.savefig(path, dpi=300)  # >= 300 DPI
    plt.close()


def zero_runs(ts: pd.DataFrame):
    """All runs of consecutive zero-commit months as (start_idx, end_idx, length)."""
    runs, start = [], None
    for i, v in enumerate(ts["#Commits"]):
        if v == 0 and start is None:
            start = i
        if v != 0 and start is not None:
            runs.append((start, i - 1, i - start))
            start = None
    if start is not None:
        runs.append((start, len(ts) - 1, len(ts) - start))
    return runs


# ------------------------------------------------------------------ Part 3
def gap_commits(df: pd.DataFrame, gap_start: str, gap_end: str) -> pd.DataFrame:
    """Last N commits before the gap and first N after it (pre / post)."""
    pre = df[df["ym"] < gap_start].tail(N_GAP_COMMITS)
    post = df[df["ym"] > gap_end].head(N_GAP_COMMITS)
    rows = [
        [label, PROJECT, c.sha, c.author, c.time, c.msg]
        for label, part in (("pre", pre), ("post", post))
        for c in part.itertuples()
    ]
    return pd.DataFrame(rows, columns=["pre/post", "prj", "commit", "author", "time", "message"])


def main() -> None:
    df = get_commits()
    print(f"{len(df)} commits, {df['author'].nunique()} authors, "
          f"{df['dt'].min()} -> {df['dt'].max()}")

    
    df[["project", "sha", "author", "time", "msg"]].to_csv(
        OUT / f"{NETID}_vichan_project_summary.csv", sep=";", header=False, index=False)

    
    ts = monthly_series(df)
    ts.to_csv(OUT / f"{NETID}_commits_timeseries_{PROJECT}.csv", sep=";", index=False)
    plot_series(ts, OUT / f"{NETID}_timeseries_{PROJECT}.png")

    runs = zero_runs(ts)
    longest = max(runs, key=lambda r: r[2])
    gap_start, gap_end, gap_len = ts["Month"][longest[0]], ts["Month"][longest[1]], longest[2]
    n_gaps = sum(1 for r in runs if r[2] >= MIN_GAP_MONTHS)
    n_after = int((df["ym"] > gap_end).sum())
    print(f"longest gap {gap_start} -> {gap_end} ({gap_len} months); "
          f"{n_gaps} gaps >= {MIN_GAP_MONTHS} months; {n_after} commits after")

    
    gap_commits(df, gap_start, gap_end).to_csv(
        OUT / f"{NETID}_vichan_project_gap_commits.csv", sep=";", index=False)

    # Stats row: computed values + manual values
    stats = {
        "Project": PROJECT,
        "#commits": len(df),
        "#authors": df["author"].nunique(),   # unique "name <email>"
        "From": int(df["time"].min()),
        "To": int(df["time"].max()),
        "#stars": MANUAL["#stars"],
        "#forks": MANUAL["#forks"],
        "LastGHCommitDate": MANUAL["LastGHCommitDate"],
        "LongestGapStart": gap_start,
        "LongestGapEnd": gap_end,
        "LongestGapLength": gap_len,
        "NumCommitsAfterLastGap": n_after,
        "ActivityPattern": MANUAL["ActivityPattern"],
        "NumberOfGapsInTimeline": n_gaps,
    }
    for k in ("BeforeThemes", "AfterThemes", "HypothesizedGapReason", "HasRecovered",
              "WhyRecovered", "WhoRecovered", "Currentstatus", "RecentThemes", "Notes"):
        stats[k] = MANUAL[k]
    pd.DataFrame([stats]).to_csv(
        OUT / f"{NETID}_vichan_project_stats.csv", sep=";", index=False)
    print(f"files written to {OUT.resolve()}")


if __name__ == "__main__":
    main()