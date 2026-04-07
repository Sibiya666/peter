## Task 5: Log Model Parser (Excel)

**Files:**
- Create: `src/parsers/__init__.py`
- Create: `src/parsers/log_model_parser.py`
- Create: `tests/unit/test_log_model_parser.py`
- Create: `tests/fixtures/sample_data.py`

- [ ] **Step 1: Create test fixture for sample Excel data**

Create `tests/fixtures/sample_data.py`:

```python
import pandas as pd
from pathlib import Path


def create_sample_log_model_excel(output_path: Path) -> Path:
    """Create a sample log model Excel file for testing"""
    df = pd.DataFrame({
        'table_name': ['users', 'users', 'users', 'orders', 'orders'],
        'column_name': ['id', 'email', 'created_at', 'id', 'total'],
        'data_type': ['int', 'varchar(255)', 'datetime2', 'int', 'decimal(10,2)'],
        'is_nullable': [False, False, False, False, False],
        'default_value': [None, None, 'GETDATE()', None, '0.00'],
        'max_length': [None, 255, None, None, None],
        'is_primary_key': [True, False, False, True, False]
    })

    excel_path = output_path / "sample_log_model.xlsx"
    df.to_excel(excel_path, index=False)
    return excel_path


def create_invalid_log_model_excel(output_path: Path) -> Path:
    """Create an invalid log model Excel file (missing required columns)"""
    df = pd.DataFrame({
        'table_name': ['users'],
        'column_name': ['id']
        # Missing required columns
    })

    excel_path = output_path / "invalid_log_model.xlsx"
    df.to_excel(excel_path, index=False)
    return excel_path
```

Create `tests/fixtures/__init__.py`:

```python
from .sample_data import create_sample_log_model_excel, create_invalid_log_model_excel

__all__ = ["create_sample_log_model_excel", "create_invalid_log_model_excel"]
```

- [ ] **Step 2: Write test for log model parser**

Create `tests/unit/test_log_model_parser.py`:

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/unit/test_log_model_parser.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 4: Implement log model parser**

Create `src/parsers/log_model_parser.py`:

```python
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
```

Create `src/parsers/__init__.py`:

```python
from .log_model_parser import LogModelParser

__all__ = ["LogModelParser"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_log_model_parser.py -v
```

Expected: PASS

- [ ] **Step 6: Commit log model parser**

```bash
git add src/parsers/ tests/unit/test_log_model_parser.py tests/fixtures/
git commit -m "feat: add log model Excel parser

- Implement LogModelParser with validation
- Add data type normalization
- Add boolean parsing for various formats
- Create test fixtures for sample Excel files
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

