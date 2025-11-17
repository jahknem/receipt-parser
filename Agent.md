# Agent Notes

## November 17, 2025
- Jules repeatedly committed runtime artifacts (`uploads/*.png`, `__pycache__/`) to multiple PR branches. These directories must stay out of git; use `.gitignore` and clean the working tree before pushing.
- Please verify new endpoints against `api/openapi.yaml` before opening a PR. The last three PRs diverged from the documented contract, which creates churn for reviewers and testers.

## Safe GH heredoc command for posting long comments

If `gh pr comment` needs a long body and you want to avoid shell quoting issues, use a heredoc (EOF) in zsh/bash like this:

```sh
gh pr comment 18 --body "$(cat <<'EOF'
<PASTE YOUR COMMENT HERE>
EOF
 )"
```

This will send the exact contents inside the heredoc to the GitHub CLI as the `--body` value and avoids problems with embedded quotes or special characters.
