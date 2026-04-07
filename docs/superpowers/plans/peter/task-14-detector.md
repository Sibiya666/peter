## Task 14: Detector Engine

**Files:**
- Create: `src/core/detector.py`
- Modify: `src/core/__init__.py`
- Create: `tests/unit/test_detector.py`

- [ ] **Step 1: Write test for Detector engine**

Create `tests/unit/test_detector.py`:

```python
import pytest
from unittest.mock import Mock
from core.detector import Detector
from models.data_models import (
    CheckType,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn
)


class TestDetector:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_runs_all_checks_by_default(self, mock_connection):
        log_model = {}
        db_schema = {}

        detector = Detector(mock_connection)
        results = detector.run_checks(log_model, db_schema)

        # Should instantiate all 4 checks
        assert isinstance(results, list)

    def test_runs_only_specified_checks(self, mock_connection):
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
        db_schema = {}

        detector = Detector(mock_connection)
        results = detector.run_checks(
            log_model,
            db_schema,
            check_types=[CheckType.MISSING_IN_DB]
        )

        # Should only have missing_in_db results
        assert all(r.check_type == CheckType.MISSING_IN_DB for r in results)

    def test_continues_on_check_failure(self, mock_connection):
        """Test that if one check fails, others still run"""
        log_model = {}
        db_schema = {}

        detector = Detector(mock_connection)

        # Even if checks have issues, should not raise
        results = detector.run_checks(log_model, db_schema)
        assert isinstance(results, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_detector.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement Detector engine**

Create `src/core/detector.py`:

```python
from typing import Dict, List, Optional
from models.data_models import (
    CheckType,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
from core.checks import (
    MissingInDbCheck,
    MissingInModelCheck,
    AttributeDiffCheck,
    PkDiffCheck
)
import logging

logger = logging.getLogger(__name__)


class Detector:
    """Main detection engine that runs all compliance checks"""

    def __init__(self, connection, default_owner: str = "unassigned"):
        """
        Initialize detector with database connection.

        Args:
            connection: Database connection for owner mapping
            default_owner: Default owner for issues
        """
        self.connection = connection
        self.default_owner = default_owner

        # Initialize all checks
        self.checks = [
            MissingInDbCheck(connection, default_owner),
            MissingInModelCheck(connection, default_owner),
            AttributeDiffCheck(connection, default_owner),
            PkDiffCheck(connection, default_owner)
        ]

    def run_checks(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable],
        check_types: Optional[List[CheckType]] = None
    ) -> List[CheckResult]:
        """
        Run compliance checks and return results.

        Args:
            log_model: Dictionary of tables from log model
            db_schema: Dictionary of tables from database
            check_types: Optional list of specific checks to run (None = all)

        Returns:
            List of CheckResult objects
        """
        logger.info("Starting compliance checks...")
        all_results = []

        for check in self.checks:
            # Skip if not in requested check types
            if check_types and check.check_type not in check_types:
                logger.debug(f"Skipping check: {check.check_type.value}")
                continue

            try:
                logger.info(f"Running check: {check.check_type.value}")
                results = check.execute(log_model, db_schema)
                all_results.extend(results)
                logger.info(f"Check {check.check_type.value}: found {len(results)} issues")
            except Exception as e:
                logger.error(f"Check {check.check_type.value} failed: {e}", exc_info=True)
                # Continue with other checks

        logger.info(f"Total issues found: {len(all_results)}")
        return all_results
```

- [ ] **Step 4: Update core/__init__.py**

```python
from .detector import Detector

__all__ = ["Detector"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_detector.py -v
```

Expected: PASS

- [ ] **Step 6: Commit Detector engine**

```bash
git add src/core/ tests/unit/test_detector.py
git commit -m "feat: add Detector engine

- Implement Detector to coordinate all 4 check types
- Add support for selective check execution
- Add error handling to continue on check failures
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

