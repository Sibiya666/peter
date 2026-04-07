## Task 12: Attribute Difference Check

**Files:**
- Create: `src/core/checks/attribute_diff.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Attribute Diff check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.attribute_diff import AttributeDiffCheck


class TestAttributeDiffCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_data_type_mismatch(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=False,
                    default_value=None,
                    max_length=255,
                    is_primary_key=False
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='email',
                    data_type='nvarchar',  # Type mismatch
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=255,
                    is_primary_key=False
                )]
            )
        }

        check = AttributeDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.HIGH
        assert 'type mismatch' in results[0].issue_description.lower()

    def test_detects_nullable_mismatch(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=False,
                    default_value=None,
                    max_length=255,
                    is_primary_key=False
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=True,  # Nullable mismatch
                    column_default=None,
                    character_maximum_length=255,
                    is_primary_key=False
                )]
            )
        }

        check = AttributeDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.MEDIUM
        assert 'nullable' in results[0].issue_description.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestAttributeDiffCheck -v
```

Expected: FAIL

- [ ] **Step 3: Implement Attribute Diff check**

Create `src/core/checks/attribute_diff.py`:

```python
from typing import Dict, List
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class AttributeDiffCheck(BaseCheck):
    """Check for attribute differences in columns"""

    check_type = CheckType.ATTR_DIFF

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute attribute difference check"""
        logger.info("Executing Attribute Difference check...")
        results = []

        for table_name in log_model.keys():
            if table_name not in db_schema:
                continue  # Handled by MissingInDbCheck

            model_table = log_model[table_name]
            db_table = db_schema[table_name]

            results.extend(self._compare_attributes(model_table, db_table))

        logger.info(f"Attribute Difference check found {len(results)} issues")
        return results

    def _compare_attributes(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Compare column attributes"""
        results = []

        model_cols = {c.column_name: c for c in model_table.columns}
        db_cols = {c.column_name: c for c in db_table.columns}

        common_columns = set(model_cols.keys()) & set(db_cols.keys())

        for col_name in common_columns:
            model_col = model_cols[col_name]
            db_col = db_cols[col_name]

            # Check data type
            if model_col.data_type != db_col.data_type:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{col_name}' has type mismatch in table '{model_table.table_name}'",
                    current_value=f"type={db_col.data_type}",
                    expected_value=f"type={model_col.data_type}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

            # Check nullable
            if model_col.is_nullable != db_col.is_nullable:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.MEDIUM,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{col_name}' has nullable mismatch in table '{model_table.table_name}'",
                    current_value=f"nullable={db_col.is_nullable}",
                    expected_value=f"nullable={model_col.is_nullable}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()} {'NULL' if model_col.is_nullable else 'NOT NULL'}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

            # Check max length for character types
            if model_col.max_length and db_col.character_maximum_length:
                if model_col.max_length != db_col.character_maximum_length:
                    results.append(CheckResult(
                        check_type=self.check_type,
                        severity=Severity.LOW,
                        table_name=model_table.table_name,
                        issue_description=f"Column '{col_name}' has length mismatch in table '{model_table.table_name}'",
                        current_value=f"length={db_col.character_maximum_length}",
                        expected_value=f"length={model_col.max_length}",
                        recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()}({model_col.max_length})",
                        assigned_to=self._get_owner(model_table.table_name)
                    ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck
from .attribute_diff import AttributeDiffCheck

__all__ = [
    "BaseCheck",
    "MissingInDbCheck",
    "MissingInModelCheck",
    "AttributeDiffCheck"
]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestAttributeDiffCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Attribute Diff check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Attribute Difference check

- Implement AttributeDiffCheck for column attribute mismatches
- Add detection for data type differences (HIGH)
- Add detection for nullable differences (MEDIUM)
- Add detection for length differences (LOW)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

