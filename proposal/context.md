# Project Context and History

Background for the COSC 445 final project: Analyzing the Development Lifecycle of Vichan.

## Team

Tristan Lopez, Noah Cash, Jonathan Lange, Ar-Raniry Ar-Rasyid (full team, not recruiting).

## Deliverable history

### Project pitch

- **Title:** Analyzing the Development Lifecycle of Vichan
- **Objective:** Mine and analyze the repository metadata of Vichan, a mid-sized open-source imageboard engine.
  Development has stopped, so the full history can be studied. The goal is to retrieve the data and build a timeline
  of the project with context.
- **Data source:** https://github.com/vichan-devel/vichan. A script extracts the commit history to build the timeline.

### Progress check-in

1. Team: Tristan Lopez, Noah Cash, Jonathan Lange, Ar-Raniry Ar-Rasyid
2. Blockers: none
3. Progress: created project stats, summary, and timeseries files to analyze the commit history of Vichan
   (`vichan_analysis.py` and its CSV/PNG outputs in the repo root).
4. GitHub: https://github.com/jdlange3/COSC445-Final-Project

### Deliverable 3: Project Proposal (this folder)

- `proposal.html` is the source. `proposal.pdf` is the file to submit (one PDF per team).
- Rebuild the PDF after editing:
  ```
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --no-pdf-header-footer --print-to-pdf="proposal.pdf" proposal.html
  ```

## Assignment requirements: Final Project Deliverable 3

**Format:** one PDF per team, 2–3 pages, 11–12 pt font, single or 1.15 spacing, 1-inch margins, clear section headings.

**Required sections:**

| Section | Must cover |
|---|---|
| Project title | |
| Objective | Question/problem/goal; what we are trying to discover, analyze, recover, build, or demonstrate |
| Motivation | Why it is interesting or useful; why it is worth investigating |
| Data | What data; sources; how it is obtained (downloads, APIs, scraping, repo mining, DBs); **estimated amount**; expected challenges (missing values, formats, context, validation, integration) |
| Approach | What we do with the data; methods, tools, analyses, components. May focus on one or more of discovery, retrieval, storage, cleaning, context recovery, analysis, app development |
| Team Responsibilities | A meaningful role for each member |
| Timeline and Milestones | Major steps in a realistic order |
| Expected Outcome | Data analysis with a meaningful finding, or a working tool |

**Scope:** substantial but realistic. Needs a clear objective, a meaningful data source, nontrivial data work, an
explainable result, and a connection to course topics. Target **at least tens of thousands of records, 50,000+ as a useful
target**. Downloading a clean dataset and making a few charts is not sufficient. The project may change after the
proposal.

## Data sizing (measured 2026-10-22)

The proposal's volume estimates come from bare clones of the four lineage repositories, fetched into one object database
so that shared history is counted once:

| Repository | Commits (all refs) | Non-merge | File-change rows | Date range |
|---|---|---|---|---|
| vichan-devel/vichan | 9,646 | 8,396 | 25,276 | 2010-11-02 → 2026-07-06 |
| savetheinternet/Tinyboard | 2,201 | 2,140 | 4,986 | 2010-11-02 → 2014-07-08 |
| ctrlcctrlv/infinity | 7,796 | 6,920 | 19,820 | 2010-11-02 → 2020-06-12 |
| lainchan/lainchan | 4,307 | 3,959 | 10,503 | 2010-11-02 → 2026-08-09 |
| **Combined, deduplicated** | **10,189** | **8,862** | **27,404** | 68,957 diff hunks, 259 author emails |

Vichan's `master` branch alone has 4,814 commits, which is the number the existing `vichan_project_stats.csv` uses.
On GitHub, Vichan has about 458 issues, 490 PRs, 769 stars, and 216 forks, and its parent repository is
`savetheinternet/Tinyboard`.

Commands used (run inside the combined bare repo):

```
git rev-list --all --count
git rev-list --all --no-merges --count
git log --all --no-merges --numstat --format= | grep -c .
git log --all --no-merges -p --format= | grep -c '^@@'
```
