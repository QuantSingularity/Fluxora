# Contributing Guide

Thank you for considering contributing to Fluxora! This guide will help you get started with contributing code, documentation, tests, and more.

---

## 📑 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style & Standards](#code-style--standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.9+ installed
- Git configured with your name and email
- GitHub account
- Basic understanding of energy forecasting concepts (helpful but not required)

### Fork and Clone

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Fluxora.git
cd Fluxora

# 3. Add upstream remote
git remote add upstream https://github.com/quantsingularity/Fluxora.git

# 4. Verify remotes
git remote -v
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If exists

# Install pre-commit hooks
pre-commit install
```

### Verify Setup

```bash
# Run tests to ensure everything works
cd code
pytest ../tests/

# Start API server
python main.py

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Conventions

| Type        | Example                   | Purpose                  |
| ----------- | ------------------------- | ------------------------ |
| `feature/`  | `feature/add-lstm-model`  | New features             |
| `fix/`      | `fix/prediction-accuracy` | Bug fixes                |
| `docs/`     | `docs/update-api-guide`   | Documentation            |
| `test/`     | `test/add-model-tests`    | Adding tests             |
| `refactor/` | `refactor/database-layer` | Code refactoring         |
| `perf/`     | `perf/optimize-queries`   | Performance improvements |

### 2. Make Changes

```bash
# Edit files as needed
nano code/models/train.py

# Check status frequently
git status

# Stage changes
git add code/models/train.py

# Commit with descriptive message
git commit -m "feat: add LSTM model support for time-series prediction"
```

### 3. Keep Your Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Or merge if preferred
git merge upstream/main
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
```

---

## Code Style & Standards

### Python Style Guide

Follow **PEP 8** with these specific guidelines:

**Formatting:**

```python
# Use 4 spaces for indentation (no tabs)
def my_function(param1: str, param2: int) -> bool:
    """
    Docstring describing function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    return True

# Maximum line length: 100 characters
# Use double quotes for strings (except when avoiding escapes)
message = "This is a string"

# Imports: standard library, third-party, local
import os
import sys

import pandas as pd
from fastapi import FastAPI

import logging
```

**Type Hints:**

```python
# Always use type hints for function signatures
from typing import List, Dict, Optional, Any

def process_data(
    data: pd.DataFrame,
    user_id: int,
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, float]]:
    """Process energy data."""
    pass
```

**Naming Conventions:**

```python
# Variables and functions: snake_case
user_id = 123
def calculate_metrics():
    pass

# Classes: PascalCase
class EnergyPredictor:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Code Quality Tools

```bash
# Format code with Black
black code/

# Sort imports with isort
isort code/

# Lint with pylint
pylint code/

# Type checking with mypy (if configured)
mypy code/

# Run all pre-commit hooks
pre-commit run --all-files
```

### JavaScript/TypeScript Style

For frontend code (web-frontend, mobile-frontend):

```javascript
// Use ESLint configuration
// 2 spaces for indentation
// Use const/let (no var)
// Semicolons required

const apiUrl = "http://localhost:8000";

const fetchData = async () => {
  const response = await fetch(apiUrl);
  return response.json();
};
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_models.py
│   └── test_features.py
├── integration/       # Integration tests (slower, multiple components)
│   ├── test_api.py
│   └── test_database.py
└── e2e/              # End-to-end tests (slowest, full system)
    └── test_prediction_flow.py
```

### Writing Tests

**Example Unit Test:**

```python
# tests/test_circuit_breaker.py
import pytest
from core.circuit_breaker import CircuitBreaker

def test_circuit_breaker_opens_after_threshold():
    """Test that circuit opens after exceeding failure threshold."""
    breaker = CircuitBreaker(failure_threshold=3)

    # Simulate failures
    for _ in range(3):
        with pytest.raises(Exception):
            breaker.call(lambda: 1/0)

    # Circuit should be open now
    assert breaker.state == "OPEN"
```

**Example Integration Test:**

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predictions_requires_auth():
    """Test that predictions endpoint requires authentication."""
    response = client.get("/v1/predictions/")
    assert response.status_code == 401
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest tests/ --cov=code --cov-report=html

# Run tests matching pattern
pytest tests/ -k "test_circuit"

# Run with verbose output
pytest tests/ -v

# Run fast tests only (skip slow integration tests)
pytest tests/ -m "not slow"
```

### Test Coverage Requirements

- **New features:** Must have 80%+ test coverage
- **Bug fixes:** Must include regression test
- **Critical paths:** 90%+ coverage required

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_model_training():
    """Slow test for model training."""
    pass

@pytest.mark.integration
def test_database_connection():
    """Integration test."""
    pass

@pytest.mark.unit
def test_feature_extraction():
    """Fast unit test."""
    pass
```

---

## Documentation Guidelines

### Code Documentation

**Docstrings (Google Style):**

```python
def train_model(data: pd.DataFrame, model_type: str = "xgboost") -> Any:
    """
    Train a machine learning model on energy data.

    This function trains a forecasting model using the specified algorithm
    and returns the trained model along with evaluation metrics.

    Args:
        data: DataFrame containing energy consumption data with columns:
            - timestamp: Datetime of measurement
            - consumption_kwh: Energy consumption in kWh
            - user_id: User identifier
        model_type: Type of model to train. Options: "xgboost", "lstm", "prophet"

    Returns:
        Tuple containing:
            - trained_model: The trained model object
            - metrics: Dictionary of evaluation metrics (MSE, R2, etc.)

    Raises:
        ValueError: If model_type is not supported
        DataError: If data is invalid or insufficient

    Example:
        >>> df = load_data()
        >>> model, metrics = train_model(df, model_type="xgboost")
        >>> print(f"R2 Score: {metrics['r2_score']:.4f}")
        R2 Score: 0.8901
    """
    pass
```

### Markdown Documentation

**Structure:**

```markdown
# Title (H1 - only one per document)

Brief introduction (1-2 sentences).

## Table of Contents (if > 3 sections)

- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1 (H2 for main sections)

Content here.

### Subsection (H3 for subsections)

More content.

#### Sub-subsection (H4 if really needed)
```

**Code Examples:**

````markdown
```python
# Always include language identifier
def example():
    return True
```

```bash
# Shell commands
make install
```
````

**Tables:**

```markdown
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Value 1  | Value 2  | Value 3  |
```

### Updating Documentation

When adding features, update:

1. **README.md** - If feature is user-facing
2. **API.md** - If adding API endpoints
3. **FEATURE_MATRIX.md** - Add to feature table
4. **Examples/** - Add working example if applicable
5. **CHANGELOG.md** - Document changes (if exists)

---

## Pull Request Process

### Before Submitting

**Checklist:**

- [ ] Code follows style guidelines
- [ ] Tests pass locally (`pytest tests/`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] Branch is up-to-date with main
- [ ] Commits are descriptive and atomic

### PR Title Format

Use conventional commits format:

```
<type>(<scope>): <description>

Examples:
feat(api): add LSTM model endpoint
fix(predictions): correct confidence interval calculation
docs(api): update authentication examples
test(models): add unit tests for XGBoost training
refactor(database): optimize query performance
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### PR Description Template

```markdown
## Description

Brief description of changes.

## Motivation

Why is this change needed?

## Changes Made

- Change 1
- Change 2

## Testing

How was this tested?

## Screenshots (if applicable)

Add screenshots for UI changes.

## Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues

Fixes #123
Related to #456
```

### Review Process

1. **Automated Checks:** CI/CD runs tests
2. **Code Review:** Maintainers review code
3. **Feedback:** Address review comments
4. **Approval:** At least one maintainer approves
5. **Merge:** Squash and merge to main

### After Merge

```bash
# Update your local repository
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Issue Guidelines

### Creating Issues

**Bug Report Template:**

```markdown
**Describe the bug**
Clear description of the issue.

**To Reproduce**
Steps to reproduce:

1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.

**Environment**

- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Fluxora version: [e.g., 1.0.0]

**Additional context**
Logs, screenshots, etc.
```

**Feature Request Template:**

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives considered**
Alternative solutions or features.

**Additional context**
Any other context or screenshots.
```

### Issue Labels

| Label              | Purpose                       |
| ------------------ | ----------------------------- |
| `bug`              | Something isn't working       |
| `enhancement`      | New feature or request        |
| `documentation`    | Documentation improvements    |
| `good first issue` | Good for newcomers            |
| `help wanted`      | Extra attention needed        |
| `question`         | Further information requested |
| `wontfix`          | This will not be worked on    |

## License

By contributing to Fluxora, you agree that your contributions will be licensed under the MIT License.

---
