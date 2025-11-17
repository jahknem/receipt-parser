# Agent Notes

## November 17, 2025
- Jules repeatedly committed runtime artifacts (`uploads/*.png`, `__pycache__/`) to multiple PR branches. These directories must stay out of git; use `.gitignore` and clean the working tree before pushing.
- Please verify new endpoints against `api/openapi.yaml` before opening a PR. The last three PRs diverged from the documented contract, which creates churn for reviewers and testers.
