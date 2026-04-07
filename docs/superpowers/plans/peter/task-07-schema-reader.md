## Task 7: Schema Reader (INFORMATION_SCHEMA)

**Files:**
- Create: `src/database/schema_reader.py`
- Modify: `src/database/__init__.py`
- Create: `tests/unit/test_schema_reader.py`

- [ ] **Step 1: Write test for schema reader**

Create `tests/unit/test_schema_reader.py`:

```python
import pytest
from unittest.mock import Mock, MagicMock
from database.schema_reader import MsSqlSchemaReader
from models.data_models import DatabaseTable, DatabaseColumn


class TestMsSqlSchemaReader:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        return conn, cursor

    def test_get_table_names(self, mock_connection):
        conn, cursor = mock_connection

        # Mock table names
        mock_row1 = Mock()
        mock_row1.TABLE_NAME = 'users'
        mock_row2 = Mock()
        mock_row2.TABLE_NAME = 'orders'
        cursor.fetchall.return_value = [mock_row1, mock_row2]

        reader = MsSqlSchemaReader(conn)
        tables = reader._get_table_names()

        assert tables == ['users', 'orders']
        cursor.execute.assert_called_once()

    def test_get_table_columns(self, mock_connection):
        conn, cursor = mock_connection

        # Mock column data
        mock_row = Mock()
        mock_row.COLUMN_NAME = 'id'
        mock_row.DATA_TYPE = 'int'
        mock_row.IS_NULLABLE = 'NO'
        mock_row.COLUMN_DEFAULT = None
        mock_row.CHARACTER_MAXIMUM_LENGTH = None
        cursor.fetchall.return_value = [mock_row]

        reader = MsSqlSchemaReader(conn)
        columns = reader._get_table_columns('users')

        assert len(columns) == 1
        assert columns[0].column_name == 'id'
        assert columns[0].data_type == 'int'
        assert columns[0].is_nullable is False

    def test_get_primary_key_columns(self, mock_connection):
        conn, cursor = mock_connection

        # Mock PK columns
        mock_row = Mock()
        mock_row.COLUMN_NAME = 'id'
        cursor.fetchall.return_value = [mock_row]

        reader = MsSqlSchemaReader(conn)
        pk_columns = reader._get_primary_key_columns('users')

        assert pk_columns == {'id'}

    def test_read_schema(self, mock_connection):
        conn, cursor = mock_connection

        # Mock table names
        mock_table_row = Mock()
        mock_table_row.TABLE_NAME = 'users'

        # Mock columns
        mock_col_row = Mock()
        mock_col_row.COLUMN_NAME = 'id'
        mock_col_row.DATA_TYPE = 'int'
        mock_col_row.IS_NULLABLE = 'NO'
        mock_col_row.COLUMN_DEFAULT = None
        mock_col_row.CHARACTER_MAXIMUM_LENGTH = None

        # Mock PK
        mock_pk_row = Mock()
        mock_pk_row.COLUMN_NAME = 'id'

        # Setup fetch calls in sequence
        cursor.fetchall.side_effect = [
            [mock_table_row],  # table names
            [mock_col_row],    # columns
            [mock_pk_row]      # pk columns
        ]

        reader = MsSqlSchemaReader(conn)
        schema = reader.read_schema()

        assert len(schema) == 1
        assert 'users' in schema
        assert isinstance(schema['users'], DatabaseTable)
        assert len(schema['users'].columns) == 1
        assert schema['users'].columns[0].is_primary_key is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_schema_reader.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement schema reader**

Create `src/database/schema_reader.py`:

```python
from typing import Dict, List, Set
from models.data_models import DatabaseTable, DatabaseColumn
import logging

logger = logging.getLogger(__name__)


class MsSqlSchemaReader:
    """Read database schema from MS SQL INFORMATION_SCHEMA"""

    def __init__(self, connection):
        self.connection = connection

    def read_schema(self, schema: str = 'dbo') -> Dict[str, DatabaseTable]:
        """
        Read complete schema for all tables.

        Args:
            schema: Database schema name (default: dbo)

        Returns:
            Dictionary mapping table_name to DatabaseTable
        """
        logger.info(f"Reading schema from database (schema: {schema})")
        tables = {}

        table_names = self._get_table_names(schema)
        logger.info(f"Found {len(table_names)} tables")

        for table_name in table_names:
            columns = self._get_table_columns(table_name, schema)
            pk_columns = self._get_primary_key_columns(table_name, schema)

            # Mark PK columns
            for col in columns:
                col.is_primary_key = col.column_name in pk_columns

            tables[table_name] = DatabaseTable(
                table_name=table_name,
                columns=columns
            )

        return tables

    def _get_table_names(self, schema: str = 'dbo') -> List[str]:
        """Get list of all user tables"""
        query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
              AND TABLE_SCHEMA = ?
            ORDER BY TABLE_NAME
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (schema,))
        return [row.TABLE_NAME for row in cursor.fetchall()]

    def _get_table_columns(self, table_name: str, schema: str = 'dbo') -> List[DatabaseColumn]:
        """Get column information for a table"""
        query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
              AND TABLE_SCHEMA = ?
            ORDER BY ORDINAL_POSITION
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (table_name, schema))

        columns = []
        for row in cursor.fetchall():
            column = DatabaseColumn(
                column_name=row.COLUMN_NAME,
                data_type=row.DATA_TYPE.lower(),
                is_nullable=(row.IS_NULLABLE == 'YES'),
                column_default=row.COLUMN_DEFAULT,
                character_maximum_length=row.CHARACTER_MAXIMUM_LENGTH,
                is_primary_key=False  # Will be set later
            )
            columns.append(column)

        return columns

    def _get_primary_key_columns(self, table_name: str, schema: str = 'dbo') -> Set[str]:
        """Get set of column names that are part of primary key"""
        query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(
                    OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME),
                    'IsPrimaryKey'
                  ) = 1
              AND TABLE_NAME = ?
              AND TABLE_SCHEMA = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (table_name, schema))
        return {row.COLUMN_NAME for row in cursor.fetchall()}
```

- [ ] **Step 4: Update database/__init__.py**

```python
from .connection import DatabaseConnectionManager
from .schema_reader import MsSqlSchemaReader

__all__ = ["DatabaseConnectionManager", "MsSqlSchemaReader"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_schema_reader.py -v
```

Expected: PASS

- [ ] **Step 6: Commit schema reader**

```bash
git add src/database/ tests/unit/test_schema_reader.py
git commit -m "feat: add MS SQL schema reader

- Implement MsSqlSchemaReader using INFORMATION_SCHEMA
- Add methods to read tables, columns, and primary keys
- Add comprehensive unit tests with mocking
- Support configurable schema name

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

