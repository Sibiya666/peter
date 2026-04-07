## Task 2: Core Data Models and Enums

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/data_models.py`
- Create: `tests/unit/test_data_models.py`

- [ ] **Step 1: Write test for CheckType enum**

Create `tests/unit/test_data_models.py`:

```python
import pytest
from models.data_models import CheckType, Severity


class TestCheckType:
    def test_check_type_values(self):
        assert CheckType.MISSING_IN_DB.value == "missing_in_db"
        assert CheckType.MISSING_IN_MODEL.value == "missing_in_model"
        assert CheckType.ATTR_DIFF.value == "attribute_diff"
        assert CheckType.PK_DIFF.value == "pk_diff"

    def test_from_string(self):
        assert CheckType.from_string("missing_in_db") == CheckType.MISSING_IN_DB
        assert CheckType.from_string("pk_diff") == CheckType.PK_DIFF

    def test_all_method(self):
        all_checks = CheckType.all()
        assert len(all_checks) == 4
        assert CheckType.MISSING_IN_DB in all_checks
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_data_models.py::TestCheckType -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement CheckType enum and data models**

Create `src/models/data_models.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CheckType(Enum):
    """Types of compliance checks"""
    MISSING_IN_DB = "missing_in_db"
    MISSING_IN_MODEL = "missing_in_model"
    ATTR_DIFF = "attribute_diff"
    PK_DIFF = "pk_diff"

    @classmethod
    def from_string(cls, value: str) -> 'CheckType':
        """Convert string to CheckType enum"""
        for check_type in cls:
            if check_type.value == value:
                return check_type
        raise ValueError(f"Invalid check type: {value}")

    @classmethod
    def all(cls) -> List['CheckType']:
        """Return all check types"""
        return list(cls)


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class LogModelColumn:
    """Column definition from log model (Excel)"""
    column_name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str]
    max_length: Optional[int]
    is_primary_key: bool


@dataclass
class LogModelTable:
    """Table definition from log model"""
    table_name: str
    columns: List[LogModelColumn]


@dataclass
class DatabaseColumn:
    """Column from actual database (INFORMATION_SCHEMA)"""
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str]
    character_maximum_length: Optional[int]
    is_primary_key: bool


@dataclass
class DatabaseTable:
    """Table from actual database"""
    table_name: str
    columns: List[DatabaseColumn]


@dataclass
class CheckResult:
    """Result of a single compliance check"""
    check_type: CheckType
    severity: Severity
    table_name: str
    issue_description: str
    current_value: Optional[str]
    expected_value: Optional[str]
    recommended_action: str
    assigned_to: Optional[str]


@dataclass
class RunReport:
    """Complete run results"""
    run_id: str
    timestamp: datetime
    user: str
    check_results: List[CheckResult]
    total_issues: int
    status: str  # SUCCESS, FAILED, PARTIAL


@dataclass
class OwnerMapping:
    """Table owner mapping from database"""
    table_name: str
    owner_name: str
    jira_username: str
```

Create `src/models/__init__.py`:

```python
from .data_models import (
    CheckType,
    Severity,
    LogModelColumn,
    LogModelTable,
    DatabaseColumn,
    DatabaseTable,
    CheckResult,
    RunReport,
    OwnerMapping
)

__all__ = [
    "CheckType",
    "Severity",
    "LogModelColumn",
    "LogModelTable",
    "DatabaseColumn",
    "DatabaseTable",
    "CheckResult",
    "RunReport",
    "OwnerMapping"
]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_data_models.py::TestCheckType -v
```

Expected: PASS

- [ ] **Step 5: Add test for Severity enum**

Add to `tests/unit/test_data_models.py`:

```python
class TestSeverity:
    def test_severity_values(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
```

- [ ] **Step 6: Run test to verify it passes**

```bash
pytest tests/unit/test_data_models.py::TestSeverity -v
```

Expected: PASS (already implemented)

- [ ] **Step 7: Commit data models**

```bash
git add src/models/ tests/unit/test_data_models.py
git commit -m "feat: add core data models and enums

- Implement CheckType and Severity enums
- Define data structures for tables, columns, and check results
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

