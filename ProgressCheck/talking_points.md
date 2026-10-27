# Progress Check Talking Points

About 5 minutes. Run `python ProgressCheck/demo.py` from the project folder and press Enter to move through each step.

## 1. Project status (~45 sec)

We're studying Vichan, an open-source PHP imageboard whose history runs from 2010 until it reached end of life in 2026. We want to know two things. First, as the project got older, did the developers stop adding features and spend most of their time fixing bugs and security problems? Second, how much of the work was forced on them from outside, and how much was cleanup they chose to do?

So far we've extracted the full Git history, cleaned it, and labeled every commit as Feature, Bug Fix, Security Fix, Code Cleanup or Documentation. Right now we're finishing the analysis and writing it up.

## 2. Data collected (~1 min)

**Demo step 1: Data collected**

Our source is the official GitHub repo, https://github.com/vichan-devel/vichan, all 27 branches. We cloned it, and `src/extract.py` reads every commit and diff into CSV files.

- Raw data is 9,646 commits and 65,641 changed code blocks (hunks).
- After cleaning, 5,241 commits and 46,290 hunks are left.
- 248 author name/email pairs come down to 194 developers once we combine aliases.

Each commit row has the sha, developer, UTC date, year, whether it's on master, and the message subject and body.

## 3. Live evidence (~1.5 min)

**Demo step 2: Cleaning step.** This shows the drop from 9,646 commits to 8,396 after removing merges, then to 5,241 after removing duplicate copies of the same change on other branches.

**Demo step 3: Labels.** This shows how many commits got each label, and a sample of commits with their label and where it came from (keyword rule, file rule, or AI).

**Demo step 4: Analysis by era.** This shows each era's share of commits by category.

**Demo step 5: Graph.** This opens `share_by_era.png`.

In the decline years (2017 to 2022), feature work dropped from about a third of commits to a fifth, and fixes took over. The 2023 to 2026 revival was mostly planned cleanup, at 41%. Security fixes never went above about 5% in any era.

## 4. Problems and risks (~1 min)

- The same change often shows up on several branches, so we had to remove duplicates. Otherwise those commits would have been counted twice.
- One developer can appear under several names and emails, so we had to merge the aliases.
- The keyword and file rules can't sort most commits. About 2,860 needed an AI label. We checked the labels against 200 commits we labeled by hand and got 77% agreement overall. The keyword rules are the weakest part at 70%.
- Commit messages are short and sometimes vague, so some labels are judgment calls.

## 5. Next steps (~30 sec)

Next we'll improve the weak keyword rules, finish the final report, and prepare the presentation for November 17.
