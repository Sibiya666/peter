import pandas as pd
from typing import Dict
from models.data_models import LogModelTable, LogModelColumn
from errors import LogModelParseError


class LogModelParser:
    """Parse Excel log model file into structured data"""

    REQUIRED_COLUMNS = [
        'table_name',
        'column_name',
        'data_type',
        'is_nullable',
        'default_value',
        'max_length',
        'is_primary_key'
    ]

    def parse(self, excel_path: str) -> Dict[str, LogModelTable]:
        """
        Parse Excel file and return dictionary of tables.

        Args:
            excel_path: Path to Excel file

        Returns:
            Dictionary mapping table_name to LogModelTable

        Raises:
            FileNotFoundError: If Excel file doesn't exist
            LogModelParseError: If Excel format is invalid
        """
        try:
            df = pd.read_excel(excel_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Log model Excel not found: {excel_path}") from e
        except Exception as e:
            raise LogModelParseError(f"Failed to read Excel file: {e}") from e

        # Validate required columns
        self._validate_columns(df)

        # Group by table and build structure
        tables = {}
        for table_name, group in df.groupby('table_name'):
            columns = []
            for _, row in group.iterrows():
                column = LogModelColumn(
                    column_name=row['column_name'],
                    data_type=self._normalize_data_type(row['data_type']),
                    is_nullable=self._parse_boolean(row['is_nullable']),
                    default_value=row['default_value'] if pd.notna(row['default_value']) else None,
                    max_length=int(row['max_length']) if pd.notna(row['max_length']) else None,
                    is_primary_key=self._parse_boolean(row['is_primary_key'])
                )
                columns.append(column)

            tables[table_name] = LogModelTable(
                table_name=table_name,
                columns=columns
            )

        return tables

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """Validate that all required columns are present"""
        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise LogModelParseError(f"Missing required columns in Excel: {missing}")

    def _normalize_data_type(self, data_type: str) -> str:
        """
        Normalize data type for comparison.
        VARCHAR(50) -> varchar
        INT -> int
        """
        data_type = str(data_type).lower().strip()

        # Remove size specification
        if '(' in data_type:
            data_type = data_type.split('(')[0]

        return data_type

    def _parse_boolean(self, value) -> bool:
        """Parse various boolean representations from Excel"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('yes', 'true', '1', 'y')
        return False
