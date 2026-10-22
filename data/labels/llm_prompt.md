# AI labeling instructions

Used for the 3,022 commits that no keyword or file rule could sort (`llm_queue.csv`).
The model was Claude (Anthropic, `claude-opus-5-5`). It read each commit's subject, the first
300 characters of its body, and up to six changed file paths, in batches of about 400 commits,
and returned one label per commit. The answers are saved in `llm_labels.csv`, so the pipeline
can be re-run without the model.

## Prompt

Sort each commit from the Vichan imageboard repository into exactly one category:

- **Feature**: adds a new capability, option, page, theme, or user-visible behavior, including
  changes to defaults and anti-spam or captcha features.
- **Bug Fix**: corrects behavior that was wrong, including fixes for new PHP, browser, or library
  versions.
- **Security Fix**: closes a vulnerability or hardens the software against attack: XSS, injection,
  information or IP leaks, missing permission checks, unsafe escaping, weak password or cookie
  handling.
- **Code Cleanup**: changes the code without changing what it does: refactoring, formatting,
  removing dead code, moving or renaming files, library upgrades, build and Docker setup, version
  bumps, and reverts that only undo an unfinished change.
- **Documentation**: README, comments, docs, license text, and translations.

If a message is vague (for example "..." or "Update post.php"), use the file paths to make the
best guess. Answer with one letter per commit: F, B, S, C, or D.
