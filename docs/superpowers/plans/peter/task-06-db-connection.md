## Task 6: Database Connection Manager

**Files:**
- Create: `src/database/__init__.py`
- Create: `src/database/connection.py`
- Create: `tests/unit/test_connection.py`

- [ ] **Step 1: Write test for connection manager**

Create `tests/unit/test_connection.py`:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from database.connection import DatabaseConnectionManager
from models.config import DatabaseConfig
from pydantic import SecretStr
from errors import DatabaseConnectionError


class TestDatabaseConnectionManager:
    @pytest.fixture
    def db_config(self):
        return DatabaseConfig(
            server="localhost",
            database="test_db",
            username="test_user",
            password=SecretStr("test_pass"),
            driver="ODBC Driver 17 for SQL Server"
        )

    def test_create_connection_string(self, db_config):
        manager = DatabaseConnectionManager(db_config)
        conn_str = manager._create_connection_string()

        assert "SERVER=localhost" in conn_str
        assert "DATABASE=test_db" in conn_str
        assert "UID=test_user" in conn_str
        assert "PWD=test_pass" in conn_str
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str

    @patch('database.connection.pyodbc.connect')
    def test_connect_success(self, mock_connect, db_config):
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        manager = DatabaseConnectionManager(db_config)
        connection = manager.connect()

        assert connection == mock_conn
        mock_connect.assert_called_once()

    @patch('database.connection.pyodbc.connect')
    def test_connect_failure(self, mock_connect, db_config):
        mock_connect.side_effect = Exception("Connection failed")

        manager = DatabaseConnectionManager(db_config)
        with pytest.raises(DatabaseConnectionError):
            manager.connect()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_connection.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement connection manager**

Create `src/database/connection.py`:

```python
import pyodbc
from models.config import DatabaseConfig
from errors import DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages MS SQL database connections"""

    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        """
        Create and return a database connection.

        Returns:
            pyodbc.Connection

        Raises:
            DatabaseConnectionError: If connection fails
        """
        try:
            connection_string = self._create_connection_string()
            logger.info(f"Connecting to database: {self.config.server}/{self.config.database}")
            connection = pyodbc.connect(connection_string)
            logger.info("Database connection established successfully")
            return connection
        except Exception as e:
            error_msg = f"Failed to connect to database: {e}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    def _create_connection_string(self) -> str:
        """Build ODBC connection string"""
        return (
            f"DRIVER={{{self.config.driver}}};"
            f"SERVER={self.config.server};"
            f"DATABASE={self.config.database};"
            f"UID={self.config.username};"
            f"PWD={self.config.password.get_secret_value()}"
        )
```

Create `src/database/__init__.py`:

```python
from .connection import DatabaseConnectionManager

__all__ = ["DatabaseConnectionManager"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_connection.py -v
```

Expected: PASS

- [ ] **Step 5: Commit connection manager**

```bash
git add src/database/ tests/unit/test_connection.py
git commit -m "feat: add database connection manager

- Implement DatabaseConnectionManager with ODBC
- Add connection string builder
- Add error handling with custom exceptions
- Add comprehensive unit tests with mocking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

