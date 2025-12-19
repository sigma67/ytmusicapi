# Development Guide

## Quick Start

### Setup Development Environment

1. **Prerequisites**
   - Python 3.10 or higher
   - PDM (Python Dependency Manager)
   - Pre-commit

2. **Install Dependencies**
   ```bash
   make dev-install
   ```
   
   Or manually:
   ```bash
   pip install pipx
   pipx install pdm pre-commit
   pdm install
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   python scripts/check_dev_env.py
   ```

## Development Workflow

### Common Tasks

Use the Makefile for convenience:

```bash
make help          # Show all available commands
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Check code quality
make format        # Format code
make type-check    # Run type checker
make pre-commit    # Run all pre-commit checks
```

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   make lint
   make type-check
   make test
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   make pre-commit    # or: pre-commit run
   git commit -m "feat: your descriptive message"
   ```

## Project Structure

```
ytmusicapi/
├── config.py           # Configuration management
├── logging_utils.py    # Logging utilities
├── validation.py       # Input validation helpers
├── constants.py        # API constants
├── helpers.py          # Helper functions
├── ytmusic.py         # Main API class
├── auth/              # Authentication modules
├── mixins/            # API functionality mixins
├── parsers/           # Response parsers
└── models/            # Data models
```

## New Features Added

### Configuration Management (`config.py`)

Centralized configuration with validation:

```python
from ytmusicapi.config import validate_language, get_timeout

# Validate language codes
validate_language("en")  # OK
validate_language("xx")  # Raises ValueError

# Get timeout from environment or default
timeout = get_timeout()  # Returns DEFAULT_TIMEOUT or YTMUSIC_TIMEOUT env var
```

### Logging (`logging_utils.py`)

Structured logging with environment control:

```python
from ytmusicapi.logging_utils import get_logger, debug, info

logger = get_logger()
logger.info("Processing request")

# Or use convenience functions
debug("Debug message")
info("Info message")
```

Set log level via environment:
```bash
export YTMUSIC_LOG_LEVEL=DEBUG
export YTMUSIC_DEBUG=1
```

### Input Validation (`validation.py`)

Defensive validation helpers:

```python
from ytmusicapi.validation import require_non_empty, require_positive

playlist_id = require_non_empty(playlist_id, "playlist_id")
limit = require_positive(limit, "limit")
```

## Environment Variables

- `YTMUSIC_TIMEOUT`: Request timeout in seconds (default: 30)
- `YTMUSIC_DEBUG`: Enable debug mode (1/true/yes)
- `YTMUSIC_LOG_LEVEL`: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)

## Code Quality Standards

- **Type Hints**: All functions must have type hints
- **Docstrings**: All public functions must have docstrings
- **Line Length**: Maximum 110 characters
- **Testing**: All new features must have tests
- **Linting**: Code must pass ruff and mypy checks

## Testing

### Run All Tests
```bash
make test
```

### Run with Coverage
```bash
make test-cov
```

### Run Specific Tests
```bash
pdm run pytest tests/test_specific.py
pdm run pytest tests/test_specific.py::test_function_name
```

## Documentation

### Build Documentation
```bash
make docs
```

Documentation is built with Sphinx and available at `docs/build/html/index.html`.

## Troubleshooting

### Pre-commit Fails
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files
```

### Type Checking Issues
```bash
# Install missing type stubs
pdm run mypy --install-types
```

### Dependency Issues
```bash
# Update dependencies
pdm update

# Rebuild lock file
pdm lock --update-reuse
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policy and reporting vulnerabilities.
