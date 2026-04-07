## Task 4: Custom Exceptions

**Files:**
- Create: `src/errors.py`
- Create: `tests/unit/test_errors.py`

- [ ] **Step 1: Write test for custom exceptions**

Create `tests/unit/test_errors.py`:

```python
import pytest
from errors import (
    PeterException,
    ConfigurationError,
    DatabaseConnectionError,
    LogModelParseError,
    JiraIntegrationError,
    RemediationError
)


class TestExceptions:
    def test_peter_exception_is_base(self):
        with pytest.raises(PeterException):
            raise PeterException("Base error")

    def test_configuration_error_inheritance(self):
        with pytest.raises(PeterException):
            raise ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")

    def test_exception_message(self):
        error = DatabaseConnectionError("Connection failed")
        assert str(error) == "Connection failed"

    def test_all_exceptions_inherit_from_base(self):
        exceptions = [
            ConfigurationError,
            DatabaseConnectionError,
            LogModelParseError,
            JiraIntegrationError,
            RemediationError
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, PeterException)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_errors.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement custom exceptions**

Create `src/errors.py`:

```python
"""Custom exceptions for Peter application"""


class PeterException(Exception):
    """Base exception for all Peter errors"""
    pass


class ConfigurationError(PeterException):
    """Configuration file or environment errors"""
    pass


class DatabaseConnectionError(PeterException):
    """Database connectivity issues"""
    pass


class LogModelParseError(PeterException):
    """Log model Excel parsing errors"""
    pass


class JiraIntegrationError(PeterException):
    """Jira API integration errors"""
    pass


class RemediationError(PeterException):
    """SQL remediation script generation errors"""
    pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_errors.py -v
```

Expected: PASS

- [ ] **Step 5: Commit custom exceptions**

```bash
git add src/errors.py tests/unit/test_errors.py
git commit -m "feat: add custom exception hierarchy

- Implement PeterException as base exception
- Add specific exceptions for each error category
- Add comprehensive tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

