## Task 11: Missing in Model Check

**Files:**
- Create: `src/core/checks/missing_in_model.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Missing in Model check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.missing_in_model import MissingInModelCheck


class TestMissingInModelCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_undocumented_table(self, mock_connection):
        log_model = {}  # Empty log model

        db_schema = {
            'legacy_table': DatabaseTable(
                table_name='legacy_table',
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

        check = MissingInModelCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].check_type == CheckType.MISSING_IN_MODEL
        assert results[0].severity == Severity.HIGH
        assert 'legacy_table' in results[0].issue_description

    def test_detects_undocumented_column(self, mock_connection):
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
                columns=[
                    DatabaseColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=True
                    ),
                    DatabaseColumn(
                        column_name='undocumented_column',
                        data_type='varchar',
                        is_nullable=True,
                        column_default=None,
                        character_maximum_length=100,
                        is_primary_key=False
                    )
                ]
            )
        }

        check = MissingInModelCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.MEDIUM
        assert 'undocumented_column' in results[0].issue_description
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestMissingInModelCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement Missing in Model check**

Create `src/core/checks/missing_in_model.py`:

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


class MissingInModelCheck(BaseCheck):
    """Check for tables/columns in database but not documented in log model"""

    check_type = CheckType.MISSING_IN_MODEL

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute missing in model check"""
        logger.info("Executing Missing in Model check...")
        results = []

        for table_name, db_table in db_schema.items():
            if table_name not in log_model:
                # Table not documented
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=table_name,
                    issue_description=f"Table '{table_name}' exists in database but not documented in log model",
                    current_value="Table exists in DB",
                    expected_value="Should be documented in log model",
                    recommended_action=f"Add {table_name} to log model Excel or DROP TABLE if obsolete",
                    assigned_to=self._get_owner(table_name)
                ))
            else:
                # Table documented, check columns
                model_table = log_model[table_name]
                results.extend(self._check_extra_columns(model_table, db_table))

        logger.info(f"Missing in Model check found {len(results)} issues")
        return results

    def _check_extra_columns(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Check for columns in DB but not in model"""
        results = []

        model_column_names = {col.column_name for col in model_table.columns}

        for db_col in db_table.columns:
            if db_col.column_name not in model_column_names:
                # Column not documented
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.MEDIUM,
                    table_name=db_table.table_name,
                    issue_description=f"Column '{db_col.column_name}' exists in table '{db_table.table_name}' but not documented in log model",
                    current_value=f"{db_col.data_type}, nullable={db_col.is_nullable}",
                    expected_value="Should be documented in log model",
                    recommended_action=f"Add '{db_col.column_name}' to log model or ALTER TABLE {db_table.table_name} DROP COLUMN {db_col.column_name}",
                    assigned_to=self._get_owner(db_table.table_name)
                ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck

__all__ = ["BaseCheck", "MissingInDbCheck", "MissingInModelCheck"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestMissingInModelCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Missing in Model check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Missing in Model check

- Implement MissingInModelCheck for undocumented tables/columns
- Add detection for undocumented tables (HIGH)
- Add detection for undocumented columns (MEDIUM)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

