## Task 10: Missing in DB Check

**Files:**
- Create: `src/core/checks/missing_in_db.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Missing in DB check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.missing_in_db import MissingInDbCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn
)


class TestMissingInDbCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None  # No owner mapping
        return conn

    def test_detects_missing_table(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }
        db_schema = {}  # Empty database

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].check_type == CheckType.MISSING_IN_DB
        assert results[0].severity == Severity.CRITICAL
        assert results[0].table_name == 'users'
        assert 'missing in database' in results[0].issue_description.lower()

    def test_detects_missing_column(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[
                    LogModelColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        default_value=None,
                        max_length=None,
                        is_primary_key=True
                    ),
                    LogModelColumn(
                        column_name='email',
                        data_type='varchar',
                        is_nullable=False,
                        default_value=None,
                        max_length=255,
                        is_primary_key=False
                    )
                ]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
                # email column missing
            )
        }

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.HIGH
        assert 'email' in results[0].issue_description.lower()

    def test_no_issues_when_schema_matches(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
            )
        }

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestMissingInDbCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement Missing in DB check**

Create `src/core/checks/missing_in_db.py`:

```python
from typing import Dict, List
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class MissingInDbCheck(BaseCheck):
    """Check for tables/columns in log model but missing in database"""

    check_type = CheckType.MISSING_IN_DB

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute missing in DB check"""
        logger.info("Executing Missing in DB check...")
        results = []

        for table_name, model_table in log_model.items():
            if table_name not in db_schema:
                # Table missing entirely
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.CRITICAL,
                    table_name=table_name,
                    issue_description=f"Table '{table_name}' defined in log model but missing in database",
                    current_value=None,
                    expected_value="Table should exist",
                    recommended_action=f"CREATE TABLE {table_name}",
                    assigned_to=self._get_owner(table_name)
                ))
            else:
                # Table exists, check columns
                db_table = db_schema[table_name]
                results.extend(self._check_missing_columns(model_table, db_table))

        logger.info(f"Missing in DB check found {len(results)} issues")
        return results

    def _check_missing_columns(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Check for columns missing in database"""
        results = []

        db_column_names = {col.column_name for col in db_table.columns}

        for model_col in model_table.columns:
            if model_col.column_name not in db_column_names:
                # Column missing
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{model_col.column_name}' missing in table '{model_table.table_name}'",
                    current_value="Column does not exist",
                    expected_value=f"{model_col.data_type}, nullable={model_col.is_nullable}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ADD {model_col.column_name} {model_col.data_type.upper()}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck

__all__ = ["BaseCheck", "MissingInDbCheck"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestMissingInDbCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Missing in DB check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Missing in DB check

- Implement MissingInDbCheck for tables/columns in model but not in DB
- Add detection for missing tables (CRITICAL)
- Add detection for missing columns (HIGH)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

