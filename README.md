# Analyzing the Development Lifecycle of Vichan

COSC 445 final project. Team: Jonathan Lange, Tristan Lopez, Noah Cash, Ar-Raniry Ar-Rasyid.

Vichan is an open-source PHP imageboard engine whose public history runs from its first commit in
2010 to its end-of-life notice in 2026. We mined its Git history, cleaned it, sorted every change into
Feature, Bug Fix, Security Fix, Code Cleanup, or Documentation, and measured how the mix of work changed
across the project's life. We asked two questions:

1. As the project got older, did the developers stop adding features and spend most of their time on
   bug and security fixes?
2. How much of the work was forced on them from outside (security holes, new PHP and browser
   versions), and how much was cleanup the team chose to do?

The full write-up is in [`docs/report/`](docs/report) and the slides are in
[`docs/presentation/`](docs/presentation).

## Data

Source: the official repository, https://github.com/vichan-devel/vichan (all 27 branches).

| Step | Count |
|---|---|
| Commits extracted (all branches) | 9,646 |
| After removing merge commits | 8,396 |
| After removing duplicate copies of the same change on other branches | 5,241 |
| Changed code blocks (diff hunks) extracted | 65,641 |
| Hunks in the kept commits | 46,290 |
| Author name/email pairs | 248 |
| Developers after combining aliases | 194 |

The raw clone (`data/raw/`, about 48 MB) is not committed; `src/extract.py` downloads it again.
Everything after that is committed so the results can be checked without re-running anything.

## Repository layout

```
src/
  extract.py      1. clone the repo and save commits, file changes and hunks as CSV
  clean.py        2. drop merges and branch duplicates, UTC times, combine developer aliases
  classify.py     3. keyword/file rules, then AI labels for the rest
  evaluate.py     4. compare automatic labels to a 200-commit reference sample
  analyze.py      5. tables and graphs by year and by era
data/
  extracted/      raw CSV output of extract.py
  clean/          cleaned commits, hunks, identity map, cleaning summary
  labels/         commit_labels.csv (final labels), llm_queue.csv, llm_labels.csv,
                  llm_prompt.md (the AI instructions), hand_sample.csv (reference sample)
results/
  tables/         counts and shares by year and era, accuracy, confusion matrix
  figures/        commits_by_year.png, share_by_era.png, security_vs_cleanup.png
docs/
  proposal/       Deliverable 3 proposal
  report/         final report (report.html source, report.pdf to submit)
  presentation/   final presentation slides
preliminary/      first commit-activity analysis from the progress check-in
```

## How to reproduce

Requires Git and Python 3.10+.

```
pip install -r requirements.txt
python src/extract.py     # about 30 seconds, needs internet
python src/clean.py
python src/classify.py    # uses data/labels/llm_labels.csv for commits the rules cannot sort
python src/evaluate.py
python src/analyze.py
```

`classify.py` writes `data/labels/llm_queue.csv`, the commits that still need an AI label. Their labels
are stored in `llm_labels.csv`; the instructions given to the model are in `llm_prompt.md`. If the
upstream repository changes and new commits appear in the queue, they need labels added to
`llm_labels.csv` before they are counted.

## Main results

| Era | Commits | Feature | Bug Fix | Security Fix | Code Cleanup | Documentation |
|---|---|---|---|---|---|---|
| Tinyboard (2010-2013) | 2,335 | 35% | 40% | 2.3% | 12% | 10% |
| vichan-devel and 8chan (2014-2016) | 1,771 | 34% | 38% | 3.1% | 14% | 11% |
| Decline (2017-2022) | 224 | 21% | 42% | 4.5% | 16% | 17% |
| Revival and end (2023-2026) | 911 | 29% | 22% | 2.3% | 41% | 6.5% |

During the decline, feature work fell from about a third of commits to a fifth and fixes made up most of
what was left. The 2023-2026 revival did not continue that pattern. It was mostly planned cleanup and
modernization. Security fixes and other outside-driven work never passed about 10% of commits in any
era. The automatic labels matched the reference labels on 77% of a 200-commit random sample. Details
are in `results/tables/`.
