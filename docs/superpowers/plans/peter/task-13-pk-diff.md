## Task 13: Primary Key Difference Check

**Files:**
- Create: `src/core/checks/pk_diff.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for PK Diff check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.pk_diff import PkDiffCheck


class TestPkDiffCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_pk_mismatch(self, mock_connection):
        log_model = {
            'orders': LogModelTable(
                table_name='orders',
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
                        column_name='order_date',
                        data_type='date',
                        is_nullable=False,
                        default_value=None,
                        max_length=None,
                        is_primary_key=True  # Composite key expected
                    )
                ]
            )
        }

        db_schema = {
            'orders': DatabaseTable(
                table_name='orders',
                columns=[
                    DatabaseColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=True  # Only id is PK
                    ),
                    DatabaseColumn(
                        column_name='order_date',
                        data_type='date',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=False
                    )
                ]
            )
        }

        check = PkDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.CRITICAL
        assert 'primary key mismatch' in results[0].issue_description.lower()

    def test_no_issues_when_pk_matches(self, mock_connection):
        log_model = {
            'orders': LogModelTable(
                table_name='orders',
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
            'orders': DatabaseTable(
                table_name='orders',
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

        check = PkDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestPkDiffCheck -v
```

Expected: FAIL

- [ ] **Step 3: Implement PK Diff check**

Create `src/core/checks/pk_diff.py`:

```python
from typing import Dict, List, Set
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


class PkDiffCheck(BaseCheck):
    """Check for primary key differences"""

    check_type = CheckType.PK_DIFF

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute PK difference check"""
        logger.info("Executing PK Difference check...")
        results = []

        for table_name in log_model.keys():
            if table_name not in db_schema:
                continue  # Handled by MissingInDbCheck

            model_table = log_model[table_name]
            db_table = db_schema[table_name]

            model_pks = self._get_pk_columns(model_table)
            db_pks = self._get_pk_columns_from_db(db_table)

            if model_pks != db_pks:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.CRITICAL,
                    table_name=table_name,
                    issue_description=f"Primary key mismatch in table '{table_name}'",
                    current_value=f"PK: {sorted(db_pks) if db_pks else 'None'}",
                    expected_value=f"PK: {sorted(model_pks) if model_pks else 'None'}",
                    recommended_action=self._generate_pk_fix_action(table_name, model_pks, db_pks),
                    assigned_to=self._get_owner(table_name)
                ))

        logger.info(f"PK Difference check found {len(results)} issues")
        return results

    def _get_pk_columns(self, table: LogModelTable) -> Set[str]:
        """Extract PK column names from log model table"""
        return {col.column_name for col in table.columns if col.is_primary_key}

    def _get_pk_columns_from_db(self, table: DatabaseTable) -> Set[str]:
        """Extract PK column names from database table"""
        return {col.column_name for col in table.columns if col.is_primary_key}

    def _generate_pk_fix_action(
        self,
        table_name: str,
        expected_pks: Set[str],
        current_pks: Set[str]
    ) -> str:
        """Generate recommended action for PK fix"""
        if not current_pks and expected_pks:
            # No PK exists, need to add
            pk_cols = ', '.join(sorted(expected_pks))
            return f"ALTER TABLE {table_name} ADD CONSTRAINT PK_{table_name} PRIMARY KEY ({pk_cols})"
        elif current_pks and not expected_pks:
            # PK exists but shouldn't
            return f"ALTER TABLE {table_name} DROP CONSTRAINT PK_{table_name}"
        else:
            # PK exists but wrong columns
            pk_cols = ', '.join(sorted(expected_pks))
            return f"DROP existing PK constraint and ADD CONSTRAINT PK_{table_name} PRIMARY KEY ({pk_cols})"
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck
from .attribute_diff import AttributeDiffCheck
from .pk_diff import PkDiffCheck

__all__ = [
    "BaseCheck",
    "MissingInDbCheck",
    "MissingInModelCheck",
    "AttributeDiffCheck",
    "PkDiffCheck"
]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestPkDiffCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit PK Diff check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Primary Key Difference check

- Implement PkDiffCheck for PK mismatches (CRITICAL)
- Add logic to detect composite key differences
- Generate appropriate ALTER TABLE recommendations
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

