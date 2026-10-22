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

From a full clone of vichan-devel/vichan (all branches):

- 9,646 commits (8,396 non-merge), 2010-11-02 to 2026-07-06
- 25,276 file changes
- 65,641 changed code blocks (diff hunks), the record count used in the proposal

Commands:

```
git rev-list --all --count
git log --all --no-merges --numstat --format= | grep -c .
git log --all --no-merges -p --format= | grep -c '^@@'
```
