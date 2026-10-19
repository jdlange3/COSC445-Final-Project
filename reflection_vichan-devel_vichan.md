# Reflection: vichan-devel_vichan

**Netid:** ttb615 | **Status:** Inactive (archived 2026-07-06) | **Longest gap:** 2020-02 to 2020-07 (6 months) | **Gaps of 3+ months:** 5

## Activity pattern
Vichan has 4,814 commits on master from 219 author identities (name plus email), starting 2010-11-02 with the Tinyboard history it forked from. Commits per year: 2010: 297, 2011: 793, 2012: 535, 2013: 1080, 2014: 750, 2015: 237, 2016: 104, 2017: 95, 2018: 24, 2019: 13, 2020: 17, 2021: 51, 2022: 48, 2023: 152, 2024: 521, 2025: 95, 2026: 2.

The shape is a boom, a long fade, a revival and a second fade, so I classified it as **irregular**. Growth peaked around 2011-2014 (1,080 commits in 2013), activity fell steadily to 13-24 commits a year in 2018-2020, rose again to 152 (2023) and 521 (2024), and fell to 95 (2025) and 2 (2026).

## Gaps of 3+ months
There are five: 2018-12 to 2019-02 (3 months), 2020-02 to 2020-07 (6, the longest), 2025-06 to 2025-08 (3), 2025-11 to 2026-01 (3) and 2026-03 to 2026-06 (4). Four of the five are in the final year, which fits a project winding down.

## Interpreting the longest gap
Moderately easy. The last commits before the gap (Jan 2020) are PHP 7.4 fixes by maintainer Fredrick Brennan, and nothing follows until August 2020. The README's maintainer timeline lists him as maintainer 2017-2021, and his Nov 2020 README edit says paid support is not offered right now. No commit gives a reason, so the cause is an inference. GitHub issues and PRs from early 2020 were not checked.

## Recovery
The restart on 2020-08-10 came from outside contributors, not the maintainer: PRs #376, #377, #378 and #380 fix a ban lookup variable, an information leak in `thread.html`, and a Chromium capitalization bug. 880 commits follow the gap. The bigger revival in 2023-2024 came from new people (Zankaria 279 commits, Lorenzo Yario 277, RealAngeleno 101 after the gap; RealAngeleno is named in the README timeline, the other two are not), which matches the README's maintainer timeline (a development commission in 2023, then @perdedora and @RealAngeleno).

## End of life
The README now says Vichan has reached end of life, because many maintainers lost interest and because of ID verification laws, big social media companies and hostility from Google toward smaller sites. The repo was archived by the owner on 2026-07-06, and the last commit is the README EOL update. By the assignment's date rule this would read Active, since the last commit is after 2025-04-01, but the repo is archived, so I marked it Inactive.

## Themes
- Before the gap: Bug fixes:Dependency updates (PHP 7.4 compatibility)
- After the gap: Bug fixes:Documentation updates
- Recent: Release:Documentation updates (5.2.2 release, then the EOL notice)
