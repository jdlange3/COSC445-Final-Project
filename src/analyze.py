"""Step 5: count changes per year and per era by category, and draw the graphs.

Outputs:
  results/tables/  commits_by_year.csv, hunks_by_year.csv, shares_by_era.csv, top_developers_by_era.csv
  results/figures/ commits_by_year.png, share_by_era.png, security_vs_cleanup.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"

CATEGORIES = ["Feature", "Bug Fix", "Security Fix", "Code Cleanup", "Documentation"]
COLORS = dict(zip(CATEGORIES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]))
# eras follow the maintainer timeline in the Vichan README
ERAS = [("Tinyboard\n2010-2013", 2010, 2013), ("vichan-devel and 8chan\n2014-2016", 2014, 2016),
        ("Decline\n2017-2022", 2017, 2022), ("Revival and end\n2023-2026", 2023, 2026)]


def era_of(year):
    for name, start, end in ERAS:
        if start <= year <= end:
            return name


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")
    ax.tick_params(colors="#444444")
    ax.grid(axis="y", color="#e5e5e5", linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    labels = pd.read_csv(ROOT / "data" / "labels" / "commit_labels.csv", keep_default_na=False)
    labels["external"] = labels["external"].astype(str) == "True"
    hunks = pd.read_csv(ROOT / "data" / "clean" / "hunks.csv", usecols=["sha", "added", "removed"])
    hunks = hunks.merge(labels[["sha", "year", "label"]], on="sha")
    labels["era"] = labels["year"].map(era_of)
    hunks["era"] = hunks["year"].map(era_of)

    by_year = pd.crosstab(labels["year"], labels["label"]).reindex(columns=CATEGORIES, fill_value=0)
    by_year["Total"] = by_year.sum(axis=1)
    by_year["External"] = labels.groupby("year")["external"].sum()
    by_year.to_csv(TABLES / "commits_by_year.csv")
    hunks_year = pd.crosstab(hunks["year"], hunks["label"]).reindex(columns=CATEGORIES, fill_value=0)
    hunks_year["Total"] = hunks_year.sum(axis=1)
    hunks_year.to_csv(TABLES / "hunks_by_year.csv")

    eras = [e[0] for e in ERAS]
    commit_share = pd.crosstab(labels["era"], labels["label"], normalize="index").reindex(index=eras, columns=CATEGORIES)
    hunk_share = pd.crosstab(hunks["era"], hunks["label"], normalize="index").reindex(index=eras, columns=CATEGORIES)
    era_table = pd.DataFrame({
        "commits": labels.groupby("era").size().reindex(eras),
        "hunks": hunks.groupby("era").size().reindex(eras),
        **{f"{c} % of commits": (commit_share[c] * 100).round(1) for c in CATEGORIES},
        **{f"{c} % of hunks": (hunk_share[c] * 100).round(1) for c in CATEGORIES},
        "external % of commits": (labels.groupby("era")["external"].mean().reindex(eras) * 100).round(1),
    })
    era_table.index = [e.replace("\n", " ") for e in era_table.index]
    era_table.to_csv(TABLES / "shares_by_era.csv")

    top = (labels.groupby(["era", "developer"]).size().rename("commits").reset_index()
           .sort_values(["era", "commits"], ascending=[True, False]).groupby("era").head(3))
    top["era"] = top["era"].str.replace("\n", " ")
    top.to_csv(TABLES / "top_developers_by_era.csv", index=False)

    # Figure 1: commits per year, stacked by category
    fig, ax = plt.subplots(figsize=(10, 4.8))
    bottom = pd.Series(0, index=by_year.index)
    for c in CATEGORIES:
        ax.bar(by_year.index, by_year[c], bottom=bottom, color=COLORS[c], label=c,
               edgecolor="white", linewidth=1, width=0.75)
        bottom += by_year[c]
    style(ax)
    ax.set_xticks(by_year.index)
    ax.set_xticklabels(by_year.index, rotation=45)
    ax.set_ylabel("Commits")
    ax.set_title("Vichan commits per year by category", loc="left")
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "commits_by_year.png", dpi=300)
    plt.close(fig)

    # Figure 2: share of commits in each era, 100% stacked bars
    fig, ax = plt.subplots(figsize=(10, 4.8))
    left = pd.Series(0.0, index=eras)
    for c in CATEGORIES:
        vals = commit_share[c] * 100
        ax.barh(eras, vals, left=left, color=COLORS[c], label=c, edgecolor="white", linewidth=1.5, height=0.6)
        for i, (v, l) in enumerate(zip(vals, left)):
            if v >= 6:
                ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=9, color="#1a1a1a")
        left += vals
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of commits in the era (%)")
    ax.set_title("What the work was in each era of Vichan", loc="left")
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "share_by_era.png", dpi=300)
    plt.close(fig)

    # Figure 3: forced work vs chosen work by era
    measures = {
        "Security Fix": commit_share["Security Fix"] * 100,
        "Code Cleanup": commit_share["Code Cleanup"] * 100,
    }
    ext = labels.groupby("era")["external"].mean().reindex(eras) * 100
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = range(len(eras))
    w = 0.26
    bars = [("Security fixes", measures["Security Fix"], COLORS["Security Fix"]),
            ("All outside-driven work\n(security + PHP/browser/library compatibility)", ext, "#2a78d6"),
            ("Code cleanup", measures["Code Cleanup"], COLORS["Code Cleanup"])]
    for k, (name, vals, color) in enumerate(bars):
        pos = [i + (k - 1) * w for i in x]
        ax.bar(pos, vals, width=w - 0.02, color=color, label=name, edgecolor="white", linewidth=1)
        for p, v in zip(pos, vals):
            ax.text(p, v + 0.5, f"{v:.1f}", ha="center", va="bottom", fontsize=8, color="#444444")
    style(ax)
    ax.set_xticks(list(x))
    ax.set_xticklabels(eras)
    ax.set_ylabel("Share of commits in the era (%)")
    ax.set_title("Work forced from outside vs. cleanup the team chose", loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "security_vs_cleanup.png", dpi=300)
    plt.close(fig)

    print(era_table.T.to_string())
    print(top.to_string(index=False))


if __name__ == "__main__":
    main()
