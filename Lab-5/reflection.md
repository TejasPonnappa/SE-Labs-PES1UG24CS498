# Reflection

**1. Which issues were the easiest and which the hardest to fix?**
Style issues (Flake8 blank lines, line length, naming) were easiest because the fix is mechanical. The hardest were the bare `except` blocks: removing them is easy, but deciding what to do instead needed thought. Each one was hiding a real behaviour, such as an unparseable date being treated as "not expired".

**2. Did the tools report any false positives?**
Mostly no. Bandit's B311 on `random` is arguably low value for a toy permit number, but a guessable permit number is a real weakness, so switching to `secrets` was cheap and sensible. Pylint's docstring warnings are style rather than bugs, but they were still worth fixing.

**3. How would you integrate static analysis into your workflow?**
Run Flake8 and Pylint in an editor plugin or pre-commit hook, and run all three tools in CI so a pull request fails if the Pylint score drops or Bandit finds anything. Bandit especially should run on every change.

**4. What tangible improvements did you see?**
Pylint went from 6.32 to 10.00, Bandit from 2 findings to 0 and Flake8 from 16 to 0. The code is also safer: errors are no longer swallowed, files are always closed, and permit numbers are unpredictable. Running the program also exposed bugs no tool flagged (invalid plates and zones accepted, an expired permit not being flagged), which shows static analysis complements testing rather than replacing it.
