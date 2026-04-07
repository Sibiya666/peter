## Task 8: Audit Logger

**Files:**
- Create: `src/database/audit_logger.py`
- Modify: `src/database/__init__.py`
- Create: `tests/unit/test_audit_logger.py`

- [ ] **Step 1: Write test for audit logger**

Create `tests/unit/test_audit_logger.py`:

```python
import pytest
from unittest.mock import Mock, call
from database.audit_logger import AuditLogger
from datetime import datetime


class TestAuditLogger:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        return conn, cursor

    def test_ensure_audit_table_exists(self, mock_connection):
        conn, cursor = mock_connection

        logger = AuditLogger(conn)

        # Verify table creation SQL was executed
        cursor.execute.assert_called()
        conn.commit.assert_called()

    def test_log_run_start(self, mock_connection):
        conn, cursor = mock_connection

        logger = AuditLogger(conn)
        logger.log_run_start("run_123", "test_user", ["missing_in_db", "pk_diff"])

        # Verify INSERT was called with correct parameters
        assert cursor.execute.call_count >= 2  # CREATE + INSERT
        conn.commit.assert_called()

    def test_log_run_complete(self, mock_connection):
        conn, cursor = mock_connection

        logger = AuditLogger(conn)
        logger.log_run_complete("run_123", 5)

        # Verify UPDATE was called
        cursor.execute.assert_called()
        args = cursor.execute.call_args[0]
        assert "UPDATE" in args[0]
        assert args[1] == (5, "run_123")

    def test_log_run_failure(self, mock_connection):
        conn, cursor = mock_connection

        logger = AuditLogger(conn)
        logger.log_run_failure("run_123", "Error message")

        # Verify UPDATE with FAILED status
        cursor.execute.assert_called()
        args = cursor.execute.call_args[0]
        assert "FAILED" in args[0]

    def test_get_run_history(self, mock_connection):
        conn, cursor = mock_connection

        # Mock history data
        mock_row = Mock()
        mock_row.run_id = "run_123"
        mock_row.timestamp = datetime(2026, 4, 7, 14, 30)
        mock_row.username = "test_user"
        mock_row.check_types = "missing_in_db,pk_diff"
        mock_row.total_issues = 5
        mock_row.status = "SUCCESS"
        mock_row.error_message = None
        cursor.fetchall.return_value = [mock_row]

        logger = AuditLogger(conn)
        history = logger.get_run_history(10)

        assert len(history) == 1
        assert history[0]['run_id'] == "run_123"
        assert history[0]['check_types'] == ["missing_in_db", "pk_diff"]
        assert history[0]['total_issues'] == 5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_audit_logger.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement audit logger**

Create `src/database/audit_logger.py`:

```python
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """Manages audit log table for tracking run history"""

    TABLE_NAME = "peter_audit_log"

    def __init__(self, connection):
        self.connection = connection
        self._ensure_audit_table_exists()

    def _ensure_audit_table_exists(self):
        """Create audit log table if it doesn't exist"""
        create_table_sql = f"""
            IF NOT EXISTS (
                SELECT * FROM sys.objects
                WHERE object_id = OBJECT_ID(N'[dbo].[{self.TABLE_NAME}]')
                AND type in (N'U')
            )
            BEGIN
                CREATE TABLE [dbo].[{self.TABLE_NAME}] (
                    run_id VARCHAR(50) PRIMARY KEY,
                    timestamp DATETIME2 NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    check_types VARCHAR(500),
                    total_issues INT NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    error_message VARCHAR(MAX) NULL
                )
            END
        """
        cursor = self.connection.cursor()
        cursor.execute(create_table_sql)
        self.connection.commit()
        logger.debug("Audit table verified/created")

    def log_run_start(self, run_id: str, username: str, check_types: List[str]) -> None:
        """Log the start of a check run"""
        insert_sql = f"""
            INSERT INTO [dbo].[{self.TABLE_NAME}]
            (run_id, timestamp, username, check_types, total_issues, status)
            VALUES (?, GETDATE(), ?, ?, 0, 'RUNNING')
        """
        cursor = self.connection.cursor()
        cursor.execute(insert_sql, (
            run_id,
            username,
            ','.join(check_types)
        ))
        self.connection.commit()
        logger.info(f"Logged run start: {run_id}")

    def log_run_complete(self, run_id: str, total_issues: int) -> None:
        """Update run record on successful completion"""
        update_sql = f"""
            UPDATE [dbo].[{self.TABLE_NAME}]
            SET total_issues = ?, status = 'SUCCESS'
            WHERE run_id = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(update_sql, (total_issues, run_id))
        self.connection.commit()
        logger.info(f"Logged run completion: {run_id} ({total_issues} issues)")

    def log_run_failure(self, run_id: str, error_message: str) -> None:
        """Update run record on failure"""
        update_sql = f"""
            UPDATE [dbo].[{self.TABLE_NAME}]
            SET status = 'FAILED', error_message = ?
            WHERE run_id = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(update_sql, (error_message, run_id))
        self.connection.commit()
        logger.info(f"Logged run failure: {run_id}")

    def get_run_history(self, limit: int = 10) -> List[Dict]:
        """Get recent run history"""
        query = f"""
            SELECT TOP (?)
                run_id, timestamp, username, check_types,
                total_issues, status, error_message
            FROM [dbo].[{self.TABLE_NAME}]
            ORDER BY timestamp DESC
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (limit,))

        history = []
        for row in cursor.fetchall():
            history.append({
                'run_id': row.run_id,
                'timestamp': row.timestamp,
                'username': row.username,
                'check_types': row.check_types.split(',') if row.check_types else [],
                'total_issues': row.total_issues,
                'status': row.status,
                'error_message': row.error_message
            })

        return history
```

- [ ] **Step 4: Update database/__init__.py**

```python
from .connection import DatabaseConnectionManager
from .schema_reader import MsSqlSchemaReader
from .audit_logger import AuditLogger

__all__ = ["DatabaseConnectionManager", "MsSqlSchemaReader", "AuditLogger"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_audit_logger.py -v
```

Expected: PASS

- [ ] **Step 6: Commit audit logger**

```bash
git add src/database/ tests/unit/test_audit_logger.py
git commit -m "feat: add audit logger for run tracking

- Implement AuditLogger with auto-table creation
- Add methods for logging run lifecycle
- Add run history retrieval
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

