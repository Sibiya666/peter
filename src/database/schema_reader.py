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
