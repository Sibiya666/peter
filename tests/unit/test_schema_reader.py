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
