# Contributing to ytmusicapi

Thank you for your interest in contributing to ytmusicapi!

## Issues

Before submitting an issue, please make sure to include:

- **Version**: The version of ytmusicapi you're using
- **Reproduction Steps**: Detailed instructions for reproducing the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **API Response**: If applicable, the YouTube Music API response (responses may differ based on user account)

## Pull Requests

Please open an issue before submitting a pull request, unless it's just a typo or small error.

### Setup Development Environment

1. Install development dependencies:

```bash
pip install pipx
pipx install pdm pre-commit
pdm install
```

2. Set up pre-commit hooks:

```bash
pre-commit install
```

### Before Committing

Stage your files and run style/linter checks:

```bash
git add .
pre-commit run
```

Pre-commit will unstage any files that don't pass. Fix the issues until all checks pass, then commit.

### Code Quality Standards

- Follow Python best practices and PEP 8
- Write clear, descriptive commit messages
- Add type hints to all new functions
- Ensure all tests pass
- Add tests for new functionality

### Code Structure

The `ytmusicapi` folder contains the main library distributed to users. Each main library function in `ytmusic.py` is covered by a test in the `tests` folder.

If you contribute a new function, please create a corresponding unittest.

### Testing

Run tests with:

```bash
pdm run pytest
```

Run with coverage:

```bash
pdm run pytest --cov
```

## Questions?

Feel free to ask questions in:
- [GitHub Issues](https://github.com/sigma67/ytmusicapi/issues)
- [Gitter Chat](https://gitter.im/sigma67/ytmusicapi)

We appreciate your contributions!
