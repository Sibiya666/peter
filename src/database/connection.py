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
