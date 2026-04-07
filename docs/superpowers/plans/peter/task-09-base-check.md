## Task 9: Base Check Class

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/checks/__init__.py`
- Create: `src/core/checks/base_check.py`
- Create: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for base check class**

Create `tests/unit/test_checks.py`:

```python
import pytest
from unittest.mock import Mock
from core.checks.base_check import BaseCheck
from models.data_models import CheckType, LogModelTable, DatabaseTable


class ConcreteCheck(BaseCheck):
    """Concrete implementation for testing"""
    check_type = CheckType.MISSING_IN_DB

    def execute(self, log_model, db_schema):
        return []


class TestBaseCheck:
    def test_get_owner_with_mapping(self):
        # Mock connection with owner mapping
        mock_conn = Mock()
        cursor = Mock()
        mock_conn.cursor.return_value = cursor

        mock_row = Mock()
        mock_row.jira_username = "alice.smith"
        cursor.fetchone.return_value = mock_row

        check = ConcreteCheck(mock_conn, "default_owner")
        owner = check._get_owner("users")

        assert owner == "alice.smith"

    def test_get_owner_fallback_to_default(self):
        # Mock connection with no mapping found
        mock_conn = Mock()
        cursor = Mock()
        mock_conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None

        check = ConcreteCheck(mock_conn, "default_owner")
        owner = check._get_owner("users")

        assert owner == "default_owner"

    def test_check_type_property(self):
        mock_conn = Mock()
        check = ConcreteCheck(mock_conn, "default_owner")
        assert check.check_type == CheckType.MISSING_IN_DB
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestBaseCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement base check class**

Create `src/core/checks/base_check.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from models.data_models import (
    CheckType,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class BaseCheck(ABC):
    """Base class for all compliance checks"""

    check_type: CheckType = None

    def __init__(self, connection, default_owner: str = "unassigned"):
        """
        Initialize check with database connection.

        Args:
            connection: Database connection for owner mapping queries
            default_owner: Default owner if no mapping found
        """
        self.connection = connection
        self.default_owner = default_owner

    @abstractmethod
    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """
        Execute the compliance check.

        Args:
            log_model: Dictionary of tables from log model
            db_schema: Dictionary of tables from database

        Returns:
            List of CheckResult objects
        """
        pass

    def _get_owner(self, table_name: str) -> Optional[str]:
        """
        Get owner/assignee for a table from owner mapping.

        Args:
            table_name: Name of the table

        Returns:
            Jira username or default_owner
        """
        try:
            query = """
                SELECT jira_username
                FROM peter_owner_mapping
                WHERE table_name = ?
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (table_name,))
            row = cursor.fetchone()

            if row:
                return row.jira_username
            else:
                logger.debug(f"No owner mapping found for table: {table_name}")
                return self.default_owner
        except Exception as e:
            logger.warning(f"Failed to fetch owner for {table_name}: {e}")
            return self.default_owner
```

Create `src/core/__init__.py`:

```python
# Core module
```

Create `src/core/checks/__init__.py`:

```python
from .base_check import BaseCheck

__all__ = ["BaseCheck"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestBaseCheck -v
```

Expected: PASS

- [ ] **Step 5: Commit base check class**

```bash
git add src/core/ tests/unit/test_checks.py
git commit -m "feat: add base check class

- Implement abstract BaseCheck class
- Add owner mapping lookup logic
- Define execute interface for all checks
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

