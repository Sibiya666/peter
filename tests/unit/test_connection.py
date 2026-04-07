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
