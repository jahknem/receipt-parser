# Receipt Parser

This project contains helpers and fixtures for parsing receipts.

## CI Checks

This project uses GitHub Actions to run CI checks on every push and pull request. The CI workflow is defined in `.github/workflows/ci.yml`.

The CI workflow performs the following checks:
- Lints the code with `ruff`.
- Runs tests with `pytest`.

### Running Checks Locally

To run the CI checks locally, you can use the following commands:

```bash
# Install dependencies
poetry install

# Run linter
poetry run ruff .

# Run tests
poetry run pytest
```
