import pytest
from parsers.log_model_parser import LogModelParser
from models.data_models import LogModelTable, LogModelColumn
from errors import LogModelParseError
from tests.fixtures.sample_data import (
    create_sample_log_model_excel,
    create_invalid_log_model_excel
)


class TestLogModelParser:
    def test_parse_valid_excel(self, tmp_path):
        # Create sample Excel
        excel_path = create_sample_log_model_excel(tmp_path)

        # Parse
        parser = LogModelParser()
        tables = parser.parse(str(excel_path))

        # Verify structure
        assert len(tables) == 2
        assert 'users' in tables
        assert 'orders' in tables

        # Verify users table
        users_table = tables['users']
        assert isinstance(users_table, LogModelTable)
        assert users_table.table_name == 'users'
        assert len(users_table.columns) == 3

        # Verify first column
        id_col = users_table.columns[0]
        assert isinstance(id_col, LogModelColumn)
        assert id_col.column_name == 'id'
        assert id_col.data_type == 'int'
        assert id_col.is_nullable is False
        assert id_col.is_primary_key is True

    def test_parse_missing_required_columns(self, tmp_path):
        # Create invalid Excel
        excel_path = create_invalid_log_model_excel(tmp_path)

        # Parse should raise error
        parser = LogModelParser()
        with pytest.raises(LogModelParseError, match="Missing required columns"):
            parser.parse(str(excel_path))

    def test_parse_nonexistent_file(self):
        parser = LogModelParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.xlsx")

    def test_normalize_data_type(self):
        parser = LogModelParser()
        assert parser._normalize_data_type("VARCHAR(50)") == "varchar"
        assert parser._normalize_data_type("INT") == "int"
        assert parser._normalize_data_type("DECIMAL(10,2)") == "decimal"

    def test_parse_boolean_values(self):
        parser = LogModelParser()
        assert parser._parse_boolean(True) is True
        assert parser._parse_boolean(False) is False
        assert parser._parse_boolean(1) is True
        assert parser._parse_boolean(0) is False
        assert parser._parse_boolean("yes") is True
        assert parser._parse_boolean("no") is False
        assert parser._parse_boolean("TRUE") is True
        assert parser._parse_boolean("Y") is True
