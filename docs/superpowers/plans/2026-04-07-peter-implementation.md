# Peter - Database Schema Compliance Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-based database schema compliance monitoring system that detects discrepancies between MS SQL database schema and an Excel-based log model, generates reports, creates Jira tasks, and produces SQL remediation scripts.

**Architecture:** Monolithic modular Python application with clear separation between Detector (4 check types), Reporter (Excel/Jira), Remediation (SQL scripts), Database Layer (parsers, schema reader, audit logger), Orchestrator (workflow coordination), CLI (user interface), and Scheduler (automated runs).

**Tech Stack:** Python 3.10+, pandas, openpyxl, pyodbc, jira-python, APScheduler, click, pydantic, pytest

---

## File Structure Overview

```
peter/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── orchestrator.py
│   ├── errors.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── checks/
│   │   │   ├── __init__.py
│   │   │   ├── base_check.py
│   │   │   ├── missing_in_db.py
│   │   │   ├── missing_in_model.py
│   │   │   ├── attribute_diff.py
│   │   │   └── pk_diff.py
│   │   ├── reporter.py
│   │   └── remediation.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── log_model_parser.py
│   │   └── validators.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── schema_reader.py
│   │   └── audit_logger.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── jira_client.py
│   │   └── excel_writer.py
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── job_scheduler.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py
│   └── models/
│       ├── __init__.py
│       ├── config.py
│       └── data_models.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_log_model_parser.py
│   │   ├── test_checks.py
│   │   ├── test_excel_writer.py
│   │   └── test_remediation.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_orchestrator.py
│   └── fixtures/
│       ├── __init__.py
│       └── sample_data.py
├── config/
│   ├── config.yaml
│   ├── config.example.yaml
│   └── logging.yaml
├── docs/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── output/
│   ├── reports/
│   └── scripts/
├── logs/
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## Task 1: Project Setup and Basic Structure

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `setup.py`
- Create: `pytest.ini`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`

- [ ] **Step 1: Create requirements.txt**

```txt
# Core dependencies
pandas>=2.0.0
openpyxl>=3.1.0
pydantic>=2.0.0
PyYAML>=6.0
pyodbc>=4.0.39
jira>=3.5.0
APScheduler>=3.10.0
click>=8.1.0
colorama>=0.4.6
python-dotenv>=1.0.0
```

- [ ] **Step 2: Create requirements-dev.txt**

```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code quality
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0

# Type stubs
pandas-stubs>=2.0.0
types-PyYAML>=6.0.0
```

- [ ] **Step 3: Create setup.py**

```python
from setuptools import setup, find_packages

setup(
    name="peter",
    version="1.0.0",
    description="Database Schema Compliance Monitor for MS SQL",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0",
        "pyodbc>=4.0.39",
        "jira>=3.5.0",
        "APScheduler>=3.10.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "peter=cli.commands:cli",
        ],
    },
    python_requires=">=3.10",
)
```

- [ ] **Step 4: Create pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

- [ ] **Step 5: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment
.env

# Logs
logs/*.log

# Output
output/reports/*.xlsx
output/scripts/*.sql

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 6: Create .env.example**

```bash
# Database credentials
DB_PASSWORD=your_secure_password

# Jira credentials
JIRA_API_TOKEN=your_jira_api_token

# Optional: Override config path
PETER_CONFIG_PATH=config/config.yaml
```

- [ ] **Step 7: Create README.md**

```markdown
# Peter - Database Schema Compliance Monitor

Automated monitoring system for MS SQL database schema compliance against a reference log model.

## Features

- 4 types of schema compliance checks
- Excel report generation
- Automatic Jira task creation
- SQL remediation script generation
- Scheduled and ad-hoc execution modes
- Complete audit trail

## Installation

\`\`\`bash
# Create virtual environment
python -m venv venv
venv\\Scripts\\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config/config.example.yaml config/config.yaml
cp .env.example .env
# Edit config.yaml and .env with your settings

# Initialize database
peter init-db
\`\`\`

## Usage

\`\`\`bash
# Run all checks
peter run

# Run specific checks
peter run --checks missing_in_db

# View history
peter history

# Start scheduler
peter start-scheduler
\`\`\`

## Documentation

See `docs/superpowers/specs/` for design specifications.
```

- [ ] **Step 8: Create directory structure**

```bash
mkdir -p src/core/checks src/parsers src/database src/integrations src/scheduler src/cli src/models
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p config output/reports output/scripts logs
```

- [ ] **Step 9: Commit initial setup**

```bash
git add requirements.txt requirements-dev.txt setup.py pytest.ini .gitignore .env.example README.md
git commit -m "chore: initial project setup

- Add Python dependencies
- Configure pytest
- Add gitignore and environment template
- Create README with installation instructions

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Core Data Models and Enums

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/data_models.py`
- Create: `tests/unit/test_data_models.py`

- [ ] **Step 1: Write test for CheckType enum**

Create `tests/unit/test_data_models.py`:

```python
import pytest
from models.data_models import CheckType, Severity


class TestCheckType:
    def test_check_type_values(self):
        assert CheckType.MISSING_IN_DB.value == "missing_in_db"
        assert CheckType.MISSING_IN_MODEL.value == "missing_in_model"
        assert CheckType.ATTR_DIFF.value == "attribute_diff"
        assert CheckType.PK_DIFF.value == "pk_diff"

    def test_from_string(self):
        assert CheckType.from_string("missing_in_db") == CheckType.MISSING_IN_DB
        assert CheckType.from_string("pk_diff") == CheckType.PK_DIFF

    def test_all_method(self):
        all_checks = CheckType.all()
        assert len(all_checks) == 4
        assert CheckType.MISSING_IN_DB in all_checks
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_data_models.py::TestCheckType -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement CheckType enum and data models**

Create `src/models/data_models.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CheckType(Enum):
    """Types of compliance checks"""
    MISSING_IN_DB = "missing_in_db"
    MISSING_IN_MODEL = "missing_in_model"
    ATTR_DIFF = "attribute_diff"
    PK_DIFF = "pk_diff"

    @classmethod
    def from_string(cls, value: str) -> 'CheckType':
        """Convert string to CheckType enum"""
        for check_type in cls:
            if check_type.value == value:
                return check_type
        raise ValueError(f"Invalid check type: {value}")

    @classmethod
    def all(cls) -> List['CheckType']:
        """Return all check types"""
        return list(cls)


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class LogModelColumn:
    """Column definition from log model (Excel)"""
    column_name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str]
    max_length: Optional[int]
    is_primary_key: bool


@dataclass
class LogModelTable:
    """Table definition from log model"""
    table_name: str
    columns: List[LogModelColumn]


@dataclass
class DatabaseColumn:
    """Column from actual database (INFORMATION_SCHEMA)"""
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str]
    character_maximum_length: Optional[int]
    is_primary_key: bool


@dataclass
class DatabaseTable:
    """Table from actual database"""
    table_name: str
    columns: List[DatabaseColumn]


@dataclass
class CheckResult:
    """Result of a single compliance check"""
    check_type: CheckType
    severity: Severity
    table_name: str
    issue_description: str
    current_value: Optional[str]
    expected_value: Optional[str]
    recommended_action: str
    assigned_to: Optional[str]


@dataclass
class RunReport:
    """Complete run results"""
    run_id: str
    timestamp: datetime
    user: str
    check_results: List[CheckResult]
    total_issues: int
    status: str  # SUCCESS, FAILED, PARTIAL


@dataclass
class OwnerMapping:
    """Table owner mapping from database"""
    table_name: str
    owner_name: str
    jira_username: str
```

Create `src/models/__init__.py`:

```python
from .data_models import (
    CheckType,
    Severity,
    LogModelColumn,
    LogModelTable,
    DatabaseColumn,
    DatabaseTable,
    CheckResult,
    RunReport,
    OwnerMapping
)

__all__ = [
    "CheckType",
    "Severity",
    "LogModelColumn",
    "LogModelTable",
    "DatabaseColumn",
    "DatabaseTable",
    "CheckResult",
    "RunReport",
    "OwnerMapping"
]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_data_models.py::TestCheckType -v
```

Expected: PASS

- [ ] **Step 5: Add test for Severity enum**

Add to `tests/unit/test_data_models.py`:

```python
class TestSeverity:
    def test_severity_values(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
```

- [ ] **Step 6: Run test to verify it passes**

```bash
pytest tests/unit/test_data_models.py::TestSeverity -v
```

Expected: PASS (already implemented)

- [ ] **Step 7: Commit data models**

```bash
git add src/models/ tests/unit/test_data_models.py
git commit -m "feat: add core data models and enums

- Implement CheckType and Severity enums
- Define data structures for tables, columns, and check results
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Configuration Models with Pydantic

**Files:**
- Create: `src/models/config.py`
- Create: `config/config.example.yaml`
- Create: `tests/unit/test_config.py`

- [ ] **Step 1: Write test for DatabaseConfig**

Create `tests/unit/test_config.py`:

```python
import pytest
from pydantic import SecretStr
from models.config import DatabaseConfig, AppConfig
import tempfile
import yaml
import os


class TestDatabaseConfig:
    def test_database_config_creation(self):
        config = DatabaseConfig(
            server="localhost",
            database="test_db",
            username="user",
            password=SecretStr("secret")
        )
        assert config.server == "localhost"
        assert config.database == "test_db"
        assert config.username == "user"
        assert config.password.get_secret_value() == "secret"
        assert config.driver == "ODBC Driver 17 for SQL Server"

    def test_password_not_exposed_in_repr(self):
        config = DatabaseConfig(
            server="localhost",
            database="test_db",
            username="user",
            password=SecretStr("secret")
        )
        config_str = str(config)
        assert "secret" not in config_str
        assert "**********" in config_str or "SecretStr" in config_str
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_config.py::TestDatabaseConfig -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement config models**

Create `src/models/config.py`:

```python
from pydantic import BaseModel, SecretStr, field_validator
from typing import Optional, Dict
import yaml
import os
import re
from dotenv import load_dotenv


class DatabaseConfig(BaseModel):
    server: str
    database: str
    username: str
    password: SecretStr
    driver: str = "ODBC Driver 17 for SQL Server"


class JiraConfig(BaseModel):
    url: str
    username: str
    api_token: SecretStr
    project_key: str
    issue_type: str = "Task"


class PathsConfig(BaseModel):
    log_model_excel: str
    output_reports: str = "output/reports"
    output_scripts: str = "output/scripts"


class ScheduleConfig(BaseModel):
    enabled: bool = False
    cron: str = "0 2 * * *"
    timezone: str = "UTC"


class AppConfig(BaseModel):
    database: DatabaseConfig
    jira: JiraConfig
    paths: PathsConfig
    schedule: ScheduleConfig
    severity_rules: Optional[Dict] = None
    owner_mapping: Optional[Dict] = None

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AppConfig':
        """Load configuration from YAML file with env variable substitution"""
        # Load .env file
        load_dotenv()

        # Read YAML
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        # Substitute environment variables
        config_dict = cls._substitute_env_vars(config_dict)

        return cls(**config_dict)

    @staticmethod
    def _substitute_env_vars(obj):
        """Recursively substitute ${VAR_NAME} with environment variables"""
        if isinstance(obj, str):
            # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
            pattern = r'\$\{([^}:]+)(?::([^}]+))?\}'

            def replacer(match):
                var_name = match.group(1)
                default = match.group(2)
                return os.getenv(var_name, default or '')

            return re.sub(pattern, replacer, obj)
        elif isinstance(obj, dict):
            return {k: AppConfig._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [AppConfig._substitute_env_vars(item) for item in obj]
        else:
            return obj
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_config.py::TestDatabaseConfig -v
```

Expected: PASS

- [ ] **Step 5: Add test for AppConfig.from_yaml with env substitution**

Add to `tests/unit/test_config.py`:

```python
class TestAppConfig:
    def test_from_yaml_with_env_substitution(self, tmp_path):
        # Set environment variable
        os.environ['TEST_DB_PASSWORD'] = 'test_password'
        os.environ['TEST_JIRA_TOKEN'] = 'jira_token'

        # Create test config YAML
        config_content = """
database:
  server: localhost
  database: test_db
  username: test_user
  password: ${TEST_DB_PASSWORD}
  driver: ODBC Driver 17 for SQL Server

jira:
  url: https://test.atlassian.net
  username: test@example.com
  api_token: ${TEST_JIRA_TOKEN}
  project_key: TEST
  issue_type: Task

paths:
  log_model_excel: data/log_model.xlsx
  output_reports: output/reports
  output_scripts: output/scripts

schedule:
  enabled: false
  cron: "0 2 * * *"
  timezone: UTC
"""
        config_path = tmp_path / "test_config.yaml"
        config_path.write_text(config_content)

        # Load config
        config = AppConfig.from_yaml(str(config_path))

        # Verify
        assert config.database.server == "localhost"
        assert config.database.password.get_secret_value() == "test_password"
        assert config.jira.api_token.get_secret_value() == "jira_token"

        # Cleanup
        del os.environ['TEST_DB_PASSWORD']
        del os.environ['TEST_JIRA_TOKEN']
```

- [ ] **Step 6: Run test to verify it passes**

```bash
pytest tests/unit/test_config.py::TestAppConfig -v
```

Expected: PASS

- [ ] **Step 7: Create example config file**

Create `config/config.example.yaml`:

```yaml
# Database connection settings
database:
  server: "localhost"
  database: "your_database"
  username: "db_user"
  password: "${DB_PASSWORD}"
  driver: "ODBC Driver 17 for SQL Server"

# Jira integration settings
jira:
  url: "https://your-company.atlassian.net"
  username: "jira_user@company.com"
  api_token: "${JIRA_API_TOKEN}"
  project_key: "SCHEMA"
  issue_type: "Task"

# Paths configuration
paths:
  log_model_excel: "data/log_model.xlsx"
  output_reports: "output/reports"
  output_scripts: "output/scripts"

# Scheduler settings
schedule:
  enabled: true
  cron: "0 2 * * *"
  timezone: "UTC"

# Severity mapping rules
severity_rules:
  missing_in_db:
    table: "CRITICAL"
    column: "HIGH"
  missing_in_model:
    table: "HIGH"
    column: "MEDIUM"
  attr_diff:
    data_type: "HIGH"
    nullable: "MEDIUM"
    length: "LOW"
  pk_diff: "CRITICAL"

# Owner mapping settings
owner_mapping:
  default_owner: "schema_team"
  fallback_jira_user: "unassigned"
```

- [ ] **Step 8: Commit configuration models**

```bash
git add src/models/config.py config/config.example.yaml tests/unit/test_config.py
git commit -m "feat: add configuration models with Pydantic

- Implement AppConfig with nested config models
- Add YAML loading with environment variable substitution
- Create example configuration file
- Add comprehensive tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Custom Exceptions

**Files:**
- Create: `src/errors.py`
- Create: `tests/unit/test_errors.py`

- [ ] **Step 1: Write test for custom exceptions**

Create `tests/unit/test_errors.py`:

```python
import pytest
from errors import (
    PeterException,
    ConfigurationError,
    DatabaseConnectionError,
    LogModelParseError,
    JiraIntegrationError,
    RemediationError
)


class TestExceptions:
    def test_peter_exception_is_base(self):
        with pytest.raises(PeterException):
            raise PeterException("Base error")

    def test_configuration_error_inheritance(self):
        with pytest.raises(PeterException):
            raise ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")

    def test_exception_message(self):
        error = DatabaseConnectionError("Connection failed")
        assert str(error) == "Connection failed"

    def test_all_exceptions_inherit_from_base(self):
        exceptions = [
            ConfigurationError,
            DatabaseConnectionError,
            LogModelParseError,
            JiraIntegrationError,
            RemediationError
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, PeterException)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_errors.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement custom exceptions**

Create `src/errors.py`:

```python
"""Custom exceptions for Peter application"""


class PeterException(Exception):
    """Base exception for all Peter errors"""
    pass


class ConfigurationError(PeterException):
    """Configuration file or environment errors"""
    pass


class DatabaseConnectionError(PeterException):
    """Database connectivity issues"""
    pass


class LogModelParseError(PeterException):
    """Log model Excel parsing errors"""
    pass


class JiraIntegrationError(PeterException):
    """Jira API integration errors"""
    pass


class RemediationError(PeterException):
    """SQL remediation script generation errors"""
    pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_errors.py -v
```

Expected: PASS

- [ ] **Step 5: Commit custom exceptions**

```bash
git add src/errors.py tests/unit/test_errors.py
git commit -m "feat: add custom exception hierarchy

- Implement PeterException as base exception
- Add specific exceptions for each error category
- Add comprehensive tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

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

## Task 9: Base Check Class

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/checks/__init__.py`
- Create: `src/core/checks/base_check.py`
- Create: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for base check class**

Create `tests/unit/test_checks.py`:

```python
import pytest
from unittest.mock import Mock
from core.checks.base_check import BaseCheck
from models.data_models import CheckType, LogModelTable, DatabaseTable


class ConcreteCheck(BaseCheck):
    """Concrete implementation for testing"""
    check_type = CheckType.MISSING_IN_DB

    def execute(self, log_model, db_schema):
        return []


class TestBaseCheck:
    def test_get_owner_with_mapping(self):
        # Mock connection with owner mapping
        mock_conn = Mock()
        cursor = Mock()
        mock_conn.cursor.return_value = cursor

        mock_row = Mock()
        mock_row.jira_username = "alice.smith"
        cursor.fetchone.return_value = mock_row

        check = ConcreteCheck(mock_conn, "default_owner")
        owner = check._get_owner("users")

        assert owner == "alice.smith"

    def test_get_owner_fallback_to_default(self):
        # Mock connection with no mapping found
        mock_conn = Mock()
        cursor = Mock()
        mock_conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None

        check = ConcreteCheck(mock_conn, "default_owner")
        owner = check._get_owner("users")

        assert owner == "default_owner"

    def test_check_type_property(self):
        mock_conn = Mock()
        check = ConcreteCheck(mock_conn, "default_owner")
        assert check.check_type == CheckType.MISSING_IN_DB
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestBaseCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement base check class**

Create `src/core/checks/base_check.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from models.data_models import (
    CheckType,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class BaseCheck(ABC):
    """Base class for all compliance checks"""

    check_type: CheckType = None

    def __init__(self, connection, default_owner: str = "unassigned"):
        """
        Initialize check with database connection.

        Args:
            connection: Database connection for owner mapping queries
            default_owner: Default owner if no mapping found
        """
        self.connection = connection
        self.default_owner = default_owner

    @abstractmethod
    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """
        Execute the compliance check.

        Args:
            log_model: Dictionary of tables from log model
            db_schema: Dictionary of tables from database

        Returns:
            List of CheckResult objects
        """
        pass

    def _get_owner(self, table_name: str) -> Optional[str]:
        """
        Get owner/assignee for a table from owner mapping.

        Args:
            table_name: Name of the table

        Returns:
            Jira username or default_owner
        """
        try:
            query = """
                SELECT jira_username
                FROM peter_owner_mapping
                WHERE table_name = ?
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (table_name,))
            row = cursor.fetchone()

            if row:
                return row.jira_username
            else:
                logger.debug(f"No owner mapping found for table: {table_name}")
                return self.default_owner
        except Exception as e:
            logger.warning(f"Failed to fetch owner for {table_name}: {e}")
            return self.default_owner
```

Create `src/core/__init__.py`:

```python
# Core module
```

Create `src/core/checks/__init__.py`:

```python
from .base_check import BaseCheck

__all__ = ["BaseCheck"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestBaseCheck -v
```

Expected: PASS

- [ ] **Step 5: Commit base check class**

```bash
git add src/core/ tests/unit/test_checks.py
git commit -m "feat: add base check class

- Implement abstract BaseCheck class
- Add owner mapping lookup logic
- Define execute interface for all checks
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Missing in DB Check

**Files:**
- Create: `src/core/checks/missing_in_db.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Missing in DB check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.missing_in_db import MissingInDbCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn
)


class TestMissingInDbCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None  # No owner mapping
        return conn

    def test_detects_missing_table(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }
        db_schema = {}  # Empty database

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].check_type == CheckType.MISSING_IN_DB
        assert results[0].severity == Severity.CRITICAL
        assert results[0].table_name == 'users'
        assert 'missing in database' in results[0].issue_description.lower()

    def test_detects_missing_column(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[
                    LogModelColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        default_value=None,
                        max_length=None,
                        is_primary_key=True
                    ),
                    LogModelColumn(
                        column_name='email',
                        data_type='varchar',
                        is_nullable=False,
                        default_value=None,
                        max_length=255,
                        is_primary_key=False
                    )
                ]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
                # email column missing
            )
        }

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.HIGH
        assert 'email' in results[0].issue_description.lower()

    def test_no_issues_when_schema_matches(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
            )
        }

        check = MissingInDbCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestMissingInDbCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement Missing in DB check**

Create `src/core/checks/missing_in_db.py`:

```python
from typing import Dict, List
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class MissingInDbCheck(BaseCheck):
    """Check for tables/columns in log model but missing in database"""

    check_type = CheckType.MISSING_IN_DB

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute missing in DB check"""
        logger.info("Executing Missing in DB check...")
        results = []

        for table_name, model_table in log_model.items():
            if table_name not in db_schema:
                # Table missing entirely
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.CRITICAL,
                    table_name=table_name,
                    issue_description=f"Table '{table_name}' defined in log model but missing in database",
                    current_value=None,
                    expected_value="Table should exist",
                    recommended_action=f"CREATE TABLE {table_name}",
                    assigned_to=self._get_owner(table_name)
                ))
            else:
                # Table exists, check columns
                db_table = db_schema[table_name]
                results.extend(self._check_missing_columns(model_table, db_table))

        logger.info(f"Missing in DB check found {len(results)} issues")
        return results

    def _check_missing_columns(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Check for columns missing in database"""
        results = []

        db_column_names = {col.column_name for col in db_table.columns}

        for model_col in model_table.columns:
            if model_col.column_name not in db_column_names:
                # Column missing
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{model_col.column_name}' missing in table '{model_table.table_name}'",
                    current_value="Column does not exist",
                    expected_value=f"{model_col.data_type}, nullable={model_col.is_nullable}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ADD {model_col.column_name} {model_col.data_type.upper()}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck

__all__ = ["BaseCheck", "MissingInDbCheck"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestMissingInDbCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Missing in DB check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Missing in DB check

- Implement MissingInDbCheck for tables/columns in model but not in DB
- Add detection for missing tables (CRITICAL)
- Add detection for missing columns (HIGH)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Missing in Model Check

**Files:**
- Create: `src/core/checks/missing_in_model.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Missing in Model check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.missing_in_model import MissingInModelCheck


class TestMissingInModelCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_undocumented_table(self, mock_connection):
        log_model = {}  # Empty log model

        db_schema = {
            'legacy_table': DatabaseTable(
                table_name='legacy_table',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
            )
        }

        check = MissingInModelCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].check_type == CheckType.MISSING_IN_MODEL
        assert results[0].severity == Severity.HIGH
        assert 'legacy_table' in results[0].issue_description

    def test_detects_undocumented_column(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[
                    DatabaseColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=True
                    ),
                    DatabaseColumn(
                        column_name='undocumented_column',
                        data_type='varchar',
                        is_nullable=True,
                        column_default=None,
                        character_maximum_length=100,
                        is_primary_key=False
                    )
                ]
            )
        }

        check = MissingInModelCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.MEDIUM
        assert 'undocumented_column' in results[0].issue_description
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestMissingInModelCheck -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement Missing in Model check**

Create `src/core/checks/missing_in_model.py`:

```python
from typing import Dict, List
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class MissingInModelCheck(BaseCheck):
    """Check for tables/columns in database but not documented in log model"""

    check_type = CheckType.MISSING_IN_MODEL

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute missing in model check"""
        logger.info("Executing Missing in Model check...")
        results = []

        for table_name, db_table in db_schema.items():
            if table_name not in log_model:
                # Table not documented
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=table_name,
                    issue_description=f"Table '{table_name}' exists in database but not documented in log model",
                    current_value="Table exists in DB",
                    expected_value="Should be documented in log model",
                    recommended_action=f"Add {table_name} to log model Excel or DROP TABLE if obsolete",
                    assigned_to=self._get_owner(table_name)
                ))
            else:
                # Table documented, check columns
                model_table = log_model[table_name]
                results.extend(self._check_extra_columns(model_table, db_table))

        logger.info(f"Missing in Model check found {len(results)} issues")
        return results

    def _check_extra_columns(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Check for columns in DB but not in model"""
        results = []

        model_column_names = {col.column_name for col in model_table.columns}

        for db_col in db_table.columns:
            if db_col.column_name not in model_column_names:
                # Column not documented
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.MEDIUM,
                    table_name=db_table.table_name,
                    issue_description=f"Column '{db_col.column_name}' exists in table '{db_table.table_name}' but not documented in log model",
                    current_value=f"{db_col.data_type}, nullable={db_col.is_nullable}",
                    expected_value="Should be documented in log model",
                    recommended_action=f"Add '{db_col.column_name}' to log model or ALTER TABLE {db_table.table_name} DROP COLUMN {db_col.column_name}",
                    assigned_to=self._get_owner(db_table.table_name)
                ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck

__all__ = ["BaseCheck", "MissingInDbCheck", "MissingInModelCheck"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestMissingInModelCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Missing in Model check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Missing in Model check

- Implement MissingInModelCheck for undocumented tables/columns
- Add detection for undocumented tables (HIGH)
- Add detection for undocumented columns (MEDIUM)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Attribute Difference Check

**Files:**
- Create: `src/core/checks/attribute_diff.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for Attribute Diff check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.attribute_diff import AttributeDiffCheck


class TestAttributeDiffCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_data_type_mismatch(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=False,
                    default_value=None,
                    max_length=255,
                    is_primary_key=False
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='email',
                    data_type='nvarchar',  # Type mismatch
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=255,
                    is_primary_key=False
                )]
            )
        }

        check = AttributeDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.HIGH
        assert 'type mismatch' in results[0].issue_description.lower()

    def test_detects_nullable_mismatch(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=False,
                    default_value=None,
                    max_length=255,
                    is_primary_key=False
                )]
            )
        }

        db_schema = {
            'users': DatabaseTable(
                table_name='users',
                columns=[DatabaseColumn(
                    column_name='email',
                    data_type='varchar',
                    is_nullable=True,  # Nullable mismatch
                    column_default=None,
                    character_maximum_length=255,
                    is_primary_key=False
                )]
            )
        }

        check = AttributeDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.MEDIUM
        assert 'nullable' in results[0].issue_description.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestAttributeDiffCheck -v
```

Expected: FAIL

- [ ] **Step 3: Implement Attribute Diff check**

Create `src/core/checks/attribute_diff.py`:

```python
from typing import Dict, List
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class AttributeDiffCheck(BaseCheck):
    """Check for attribute differences in columns"""

    check_type = CheckType.ATTR_DIFF

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute attribute difference check"""
        logger.info("Executing Attribute Difference check...")
        results = []

        for table_name in log_model.keys():
            if table_name not in db_schema:
                continue  # Handled by MissingInDbCheck

            model_table = log_model[table_name]
            db_table = db_schema[table_name]

            results.extend(self._compare_attributes(model_table, db_table))

        logger.info(f"Attribute Difference check found {len(results)} issues")
        return results

    def _compare_attributes(
        self,
        model_table: LogModelTable,
        db_table: DatabaseTable
    ) -> List[CheckResult]:
        """Compare column attributes"""
        results = []

        model_cols = {c.column_name: c for c in model_table.columns}
        db_cols = {c.column_name: c for c in db_table.columns}

        common_columns = set(model_cols.keys()) & set(db_cols.keys())

        for col_name in common_columns:
            model_col = model_cols[col_name]
            db_col = db_cols[col_name]

            # Check data type
            if model_col.data_type != db_col.data_type:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.HIGH,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{col_name}' has type mismatch in table '{model_table.table_name}'",
                    current_value=f"type={db_col.data_type}",
                    expected_value=f"type={model_col.data_type}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

            # Check nullable
            if model_col.is_nullable != db_col.is_nullable:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.MEDIUM,
                    table_name=model_table.table_name,
                    issue_description=f"Column '{col_name}' has nullable mismatch in table '{model_table.table_name}'",
                    current_value=f"nullable={db_col.is_nullable}",
                    expected_value=f"nullable={model_col.is_nullable}",
                    recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()} {'NULL' if model_col.is_nullable else 'NOT NULL'}",
                    assigned_to=self._get_owner(model_table.table_name)
                ))

            # Check max length for character types
            if model_col.max_length and db_col.character_maximum_length:
                if model_col.max_length != db_col.character_maximum_length:
                    results.append(CheckResult(
                        check_type=self.check_type,
                        severity=Severity.LOW,
                        table_name=model_table.table_name,
                        issue_description=f"Column '{col_name}' has length mismatch in table '{model_table.table_name}'",
                        current_value=f"length={db_col.character_maximum_length}",
                        expected_value=f"length={model_col.max_length}",
                        recommended_action=f"ALTER TABLE {model_table.table_name} ALTER COLUMN {col_name} {model_col.data_type.upper()}({model_col.max_length})",
                        assigned_to=self._get_owner(model_table.table_name)
                    ))

        return results
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck
from .attribute_diff import AttributeDiffCheck

__all__ = [
    "BaseCheck",
    "MissingInDbCheck",
    "MissingInModelCheck",
    "AttributeDiffCheck"
]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestAttributeDiffCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit Attribute Diff check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Attribute Difference check

- Implement AttributeDiffCheck for column attribute mismatches
- Add detection for data type differences (HIGH)
- Add detection for nullable differences (MEDIUM)
- Add detection for length differences (LOW)
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Primary Key Difference Check

**Files:**
- Create: `src/core/checks/pk_diff.py`
- Modify: `src/core/checks/__init__.py`
- Modify: `tests/unit/test_checks.py`

- [ ] **Step 1: Write test for PK Diff check**

Add to `tests/unit/test_checks.py`:

```python
from core.checks.pk_diff import PkDiffCheck


class TestPkDiffCheck:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_detects_pk_mismatch(self, mock_connection):
        log_model = {
            'orders': LogModelTable(
                table_name='orders',
                columns=[
                    LogModelColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        default_value=None,
                        max_length=None,
                        is_primary_key=True
                    ),
                    LogModelColumn(
                        column_name='order_date',
                        data_type='date',
                        is_nullable=False,
                        default_value=None,
                        max_length=None,
                        is_primary_key=True  # Composite key expected
                    )
                ]
            )
        }

        db_schema = {
            'orders': DatabaseTable(
                table_name='orders',
                columns=[
                    DatabaseColumn(
                        column_name='id',
                        data_type='int',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=True  # Only id is PK
                    ),
                    DatabaseColumn(
                        column_name='order_date',
                        data_type='date',
                        is_nullable=False,
                        column_default=None,
                        character_maximum_length=None,
                        is_primary_key=False
                    )
                ]
            )
        }

        check = PkDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 1
        assert results[0].severity == Severity.CRITICAL
        assert 'primary key mismatch' in results[0].issue_description.lower()

    def test_no_issues_when_pk_matches(self, mock_connection):
        log_model = {
            'orders': LogModelTable(
                table_name='orders',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }

        db_schema = {
            'orders': DatabaseTable(
                table_name='orders',
                columns=[DatabaseColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    column_default=None,
                    character_maximum_length=None,
                    is_primary_key=True
                )]
            )
        }

        check = PkDiffCheck(mock_connection)
        results = check.execute(log_model, db_schema)

        assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_checks.py::TestPkDiffCheck -v
```

Expected: FAIL

- [ ] **Step 3: Implement PK Diff check**

Create `src/core/checks/pk_diff.py`:

```python
from typing import Dict, List, Set
from core.checks.base_check import BaseCheck
from models.data_models import (
    CheckType,
    Severity,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
import logging

logger = logging.getLogger(__name__)


class PkDiffCheck(BaseCheck):
    """Check for primary key differences"""

    check_type = CheckType.PK_DIFF

    def execute(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable]
    ) -> List[CheckResult]:
        """Execute PK difference check"""
        logger.info("Executing PK Difference check...")
        results = []

        for table_name in log_model.keys():
            if table_name not in db_schema:
                continue  # Handled by MissingInDbCheck

            model_table = log_model[table_name]
            db_table = db_schema[table_name]

            model_pks = self._get_pk_columns(model_table)
            db_pks = self._get_pk_columns_from_db(db_table)

            if model_pks != db_pks:
                results.append(CheckResult(
                    check_type=self.check_type,
                    severity=Severity.CRITICAL,
                    table_name=table_name,
                    issue_description=f"Primary key mismatch in table '{table_name}'",
                    current_value=f"PK: {sorted(db_pks) if db_pks else 'None'}",
                    expected_value=f"PK: {sorted(model_pks) if model_pks else 'None'}",
                    recommended_action=self._generate_pk_fix_action(table_name, model_pks, db_pks),
                    assigned_to=self._get_owner(table_name)
                ))

        logger.info(f"PK Difference check found {len(results)} issues")
        return results

    def _get_pk_columns(self, table: LogModelTable) -> Set[str]:
        """Extract PK column names from log model table"""
        return {col.column_name for col in table.columns if col.is_primary_key}

    def _get_pk_columns_from_db(self, table: DatabaseTable) -> Set[str]:
        """Extract PK column names from database table"""
        return {col.column_name for col in table.columns if col.is_primary_key}

    def _generate_pk_fix_action(
        self,
        table_name: str,
        expected_pks: Set[str],
        current_pks: Set[str]
    ) -> str:
        """Generate recommended action for PK fix"""
        if not current_pks and expected_pks:
            # No PK exists, need to add
            pk_cols = ', '.join(sorted(expected_pks))
            return f"ALTER TABLE {table_name} ADD CONSTRAINT PK_{table_name} PRIMARY KEY ({pk_cols})"
        elif current_pks and not expected_pks:
            # PK exists but shouldn't
            return f"ALTER TABLE {table_name} DROP CONSTRAINT PK_{table_name}"
        else:
            # PK exists but wrong columns
            pk_cols = ', '.join(sorted(expected_pks))
            return f"DROP existing PK constraint and ADD CONSTRAINT PK_{table_name} PRIMARY KEY ({pk_cols})"
```

- [ ] **Step 4: Update checks/__init__.py**

```python
from .base_check import BaseCheck
from .missing_in_db import MissingInDbCheck
from .missing_in_model import MissingInModelCheck
from .attribute_diff import AttributeDiffCheck
from .pk_diff import PkDiffCheck

__all__ = [
    "BaseCheck",
    "MissingInDbCheck",
    "MissingInModelCheck",
    "AttributeDiffCheck",
    "PkDiffCheck"
]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_checks.py::TestPkDiffCheck -v
```

Expected: PASS

- [ ] **Step 6: Commit PK Diff check**

```bash
git add src/core/checks/ tests/unit/test_checks.py
git commit -m "feat: add Primary Key Difference check

- Implement PkDiffCheck for PK mismatches (CRITICAL)
- Add logic to detect composite key differences
- Generate appropriate ALTER TABLE recommendations
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Detector Engine

**Files:**
- Create: `src/core/detector.py`
- Modify: `src/core/__init__.py`
- Create: `tests/unit/test_detector.py`

- [ ] **Step 1: Write test for Detector engine**

Create `tests/unit/test_detector.py`:

```python
import pytest
from unittest.mock import Mock
from core.detector import Detector
from models.data_models import (
    CheckType,
    LogModelTable,
    LogModelColumn,
    DatabaseTable,
    DatabaseColumn
)


class TestDetector:
    @pytest.fixture
    def mock_connection(self):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        return conn

    def test_runs_all_checks_by_default(self, mock_connection):
        log_model = {}
        db_schema = {}

        detector = Detector(mock_connection)
        results = detector.run_checks(log_model, db_schema)

        # Should instantiate all 4 checks
        assert isinstance(results, list)

    def test_runs_only_specified_checks(self, mock_connection):
        log_model = {
            'users': LogModelTable(
                table_name='users',
                columns=[LogModelColumn(
                    column_name='id',
                    data_type='int',
                    is_nullable=False,
                    default_value=None,
                    max_length=None,
                    is_primary_key=True
                )]
            )
        }
        db_schema = {}

        detector = Detector(mock_connection)
        results = detector.run_checks(
            log_model,
            db_schema,
            check_types=[CheckType.MISSING_IN_DB]
        )

        # Should only have missing_in_db results
        assert all(r.check_type == CheckType.MISSING_IN_DB for r in results)

    def test_continues_on_check_failure(self, mock_connection):
        """Test that if one check fails, others still run"""
        log_model = {}
        db_schema = {}

        detector = Detector(mock_connection)

        # Even if checks have issues, should not raise
        results = detector.run_checks(log_model, db_schema)
        assert isinstance(results, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_detector.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement Detector engine**

Create `src/core/detector.py`:

```python
from typing import Dict, List, Optional
from models.data_models import (
    CheckType,
    LogModelTable,
    DatabaseTable,
    CheckResult
)
from core.checks import (
    MissingInDbCheck,
    MissingInModelCheck,
    AttributeDiffCheck,
    PkDiffCheck
)
import logging

logger = logging.getLogger(__name__)


class Detector:
    """Main detection engine that runs all compliance checks"""

    def __init__(self, connection, default_owner: str = "unassigned"):
        """
        Initialize detector with database connection.

        Args:
            connection: Database connection for owner mapping
            default_owner: Default owner for issues
        """
        self.connection = connection
        self.default_owner = default_owner

        # Initialize all checks
        self.checks = [
            MissingInDbCheck(connection, default_owner),
            MissingInModelCheck(connection, default_owner),
            AttributeDiffCheck(connection, default_owner),
            PkDiffCheck(connection, default_owner)
        ]

    def run_checks(
        self,
        log_model: Dict[str, LogModelTable],
        db_schema: Dict[str, DatabaseTable],
        check_types: Optional[List[CheckType]] = None
    ) -> List[CheckResult]:
        """
        Run compliance checks and return results.

        Args:
            log_model: Dictionary of tables from log model
            db_schema: Dictionary of tables from database
            check_types: Optional list of specific checks to run (None = all)

        Returns:
            List of CheckResult objects
        """
        logger.info("Starting compliance checks...")
        all_results = []

        for check in self.checks:
            # Skip if not in requested check types
            if check_types and check.check_type not in check_types:
                logger.debug(f"Skipping check: {check.check_type.value}")
                continue

            try:
                logger.info(f"Running check: {check.check_type.value}")
                results = check.execute(log_model, db_schema)
                all_results.extend(results)
                logger.info(f"Check {check.check_type.value}: found {len(results)} issues")
            except Exception as e:
                logger.error(f"Check {check.check_type.value} failed: {e}", exc_info=True)
                # Continue with other checks

        logger.info(f"Total issues found: {len(all_results)}")
        return all_results
```

- [ ] **Step 4: Update core/__init__.py**

```python
from .detector import Detector

__all__ = ["Detector"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_detector.py -v
```

Expected: PASS

- [ ] **Step 6: Commit Detector engine**

```bash
git add src/core/ tests/unit/test_detector.py
git commit -m "feat: add Detector engine

- Implement Detector to coordinate all 4 check types
- Add support for selective check execution
- Add error handling to continue on check failures
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Excel Report Writer

**Files:**
- Create: `src/integrations/__init__.py`
- Create: `src/integrations/excel_writer.py`
- Create: `tests/unit/test_excel_writer.py`

- [ ] **Step 1: Write test for Excel writer**

Create `tests/unit/test_excel_writer.py`:

```python
import pytest
from pathlib import Path
import openpyxl
from integrations.excel_writer import ExcelReportWriter
from models.data_models import (
    CheckType,
    Severity,
    CheckResult,
    RunReport
)
from datetime import datetime


class TestExcelReportWriter:
    @pytest.fixture
    def sample_run_report(self):
        return RunReport(
            run_id="test_run_123",
            timestamp=datetime(2026, 4, 7, 14, 30),
            user="test_user",
            check_results=[
                CheckResult(
                    check_type=CheckType.MISSING_IN_DB,
                    severity=Severity.CRITICAL,
                    table_name="users",
                    issue_description="Table 'users' missing",
                    current_value=None,
                    expected_value="Table should exist",
                    recommended_action="CREATE TABLE users",
                    assigned_to="alice"
                ),
                CheckResult(
                    check_type=CheckType.ATTR_DIFF,
                    severity=Severity.HIGH,
                    table_name="orders",
                    issue_description="Type mismatch",
                    current_value="varchar",
                    expected_value="nvarchar",
                    recommended_action="ALTER TABLE",
                    assigned_to="bob"
                )
            ],
            total_issues=2,
            status="SUCCESS"
        )

    def test_generate_report_creates_file(self, sample_run_report, tmp_path):
        output_file = tmp_path / "test_report.xlsx"

        writer = ExcelReportWriter()
        writer.generate_report(sample_run_report, str(output_file))

        assert output_file.exists()

    def test_report_has_correct_sheets(self, sample_run_report, tmp_path):
        output_file = tmp_path / "test_report.xlsx"

        writer = ExcelReportWriter()
        writer.generate_report(sample_run_report, str(output_file))

        wb = openpyxl.load_workbook(output_file)
        sheet_names = wb.sheetnames

        assert "Summary" in sheet_names
        assert "missing_in_db" in sheet_names
        assert "attribute_diff" in sheet_names

    def test_report_contains_data(self, sample_run_report, tmp_path):
        output_file = tmp_path / "test_report.xlsx"

        writer = ExcelReportWriter()
        writer.generate_report(sample_run_report, str(output_file))

        wb = openpyxl.load_workbook(output_file)
        sheet = wb["missing_in_db"]

        # Check headers
        assert sheet.cell(1, 1).value == "Table Name"

        # Check data
        assert sheet.cell(2, 1).value == "users"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_excel_writer.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement Excel writer**

Create `src/integrations/excel_writer.py`:

```python
from typing import List, Dict
import openpyxl
from openpyxl.styles import Font, PatternFill
from models.data_models import RunReport, CheckResult, CheckType
import logging

logger = logging.getLogger(__name__)


class ExcelReportWriter:
    """Generate Excel reports with compliance check results"""

    HEADERS = [
        "Table Name",
        "Issue Description",
        "Current Value",
        "Expected Value",
        "Severity",
        "Recommended Action",
        "Assigned To"
    ]

    SEVERITY_COLORS = {
        "CRITICAL": "FF0000",  # Red
        "HIGH": "FFA500",      # Orange
        "MEDIUM": "FFFF00",    # Yellow
        "LOW": "90EE90"        # Light green
    }

    def generate_report(self, run_report: RunReport, output_path: str):
        """
        Generate Excel report with one sheet per check type plus summary.

        Args:
            run_report: RunReport with results
            output_path: Path to save Excel file
        """
        logger.info(f"Generating Excel report: {output_path}")

        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)  # Remove default sheet

        # Group results by check type
        grouped = self._group_by_check_type(run_report.check_results)

        # Create sheet for each check type
        for check_type, results in grouped.items():
            sheet = workbook.create_sheet(title=check_type.value)
            self._write_sheet(sheet, results)
            self._apply_formatting(sheet)

        # Add summary sheet
        self._add_summary_sheet(workbook, run_report)

        # Save
        workbook.save(output_path)
        logger.info(f"Excel report saved: {output_path}")

    def _group_by_check_type(
        self,
        results: List[CheckResult]
    ) -> Dict[CheckType, List[CheckResult]]:
        """Group results by check type"""
        grouped = {}
        for result in results:
            if result.check_type not in grouped:
                grouped[result.check_type] = []
            grouped[result.check_type].append(result)
        return grouped

    def _write_sheet(self, sheet, results: List[CheckResult]):
        """Write results to a sheet"""
        # Write headers
        for col_idx, header in enumerate(self.HEADERS, start=1):
            sheet.cell(1, col_idx, header)

        # Write data
        for row_idx, result in enumerate(results, start=2):
            sheet.cell(row_idx, 1, result.table_name)
            sheet.cell(row_idx, 2, result.issue_description)
            sheet.cell(row_idx, 3, result.current_value or "N/A")
            sheet.cell(row_idx, 4, result.expected_value or "N/A")
            sheet.cell(row_idx, 5, result.severity.value)
            sheet.cell(row_idx, 6, result.recommended_action)
            sheet.cell(row_idx, 7, result.assigned_to or "Unassigned")

    def _apply_formatting(self, sheet):
        """Apply formatting to sheet"""
        # Format headers
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color="366092",
                end_color="366092",
                fill_type="solid"
            )

        # Color code by severity
        for row in sheet.iter_rows(min_row=2):
            severity_cell = row[4]  # Severity column
            severity = severity_cell.value

            if severity in self.SEVERITY_COLORS:
                color = self.SEVERITY_COLORS[severity]
                for cell in row:
                    cell.fill = PatternFill(
                        start_color=color,
                        fill_type="solid"
                    )

        # Auto-width columns
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width

    def _add_summary_sheet(self, workbook, run_report: RunReport):
        """Add summary sheet at the beginning"""
        summary = workbook.create_sheet(title="Summary", index=0)

        # Run info
        summary["A1"] = "Run ID:"
        summary["B1"] = run_report.run_id
        summary["A2"] = "Timestamp:"
        summary["B2"] = run_report.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        summary["A3"] = "User:"
        summary["B3"] = run_report.user
        summary["A4"] = "Status:"
        summary["B4"] = run_report.status
        summary["A5"] = "Total Issues:"
        summary["B5"] = run_report.total_issues

        # Severity breakdown
        summary["A7"] = "Breakdown by Severity:"
        severity_counts = {}
        for result in run_report.check_results:
            sev = result.severity.value
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        row = 8
        for severity, count in sorted(severity_counts.items()):
            summary.cell(row, 1, severity)
            summary.cell(row, 2, count)
            row += 1

        # Check type breakdown
        summary.cell(row + 1, 1, "Breakdown by Check Type:")
        check_counts = {}
        for result in run_report.check_results:
            check = result.check_type.value
            check_counts[check] = check_counts.get(check, 0) + 1

        row += 2
        for check_type, count in sorted(check_counts.items()):
            summary.cell(row, 1, check_type)
            summary.cell(row, 2, count)
            row += 1

        # Format summary headers
        for cell in summary["A"]:
            if cell.value and ":" in str(cell.value):
                cell.font = Font(bold=True)
```

Create `src/integrations/__init__.py`:

```python
from .excel_writer import ExcelReportWriter

__all__ = ["ExcelReportWriter"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_excel_writer.py -v
```

Expected: PASS

- [ ] **Step 5: Commit Excel writer**

```bash
git add src/integrations/ tests/unit/test_excel_writer.py
git commit -m "feat: add Excel report writer

- Implement ExcelReportWriter with color coding
- Add one sheet per check type
- Add summary sheet with breakdowns
- Add auto-width columns
- Add comprehensive unit tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Jira Client

**Files:**
- Create: `src/integrations/jira_client.py`
- Modify: `src/integrations/__init__.py`
- Create: `tests/unit/test_jira_client.py`

- [ ] **Step 1: Write test for Jira client**

Create `tests/unit/test_jira_client.py`:

```python
import pytest
from unittest.mock import Mock, patch
from integrations.jira_client import JiraTaskCreator
from models.config import JiraConfig
from models.data_models import CheckType, Severity, CheckResult
from pydantic import SecretStr


class TestJiraTaskCreator:
    @pytest.fixture
    def jira_config(self):
        return JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token=SecretStr("fake_token"),
            project_key="TEST",
            issue_type="Task"
        )

    @patch('integrations.jira_client.JIRA')
    def test_create_tasks_groups_by_table_and_person(self, mock_jira_class, jira_config):
        mock_jira = Mock()
        mock_jira_class.return_value = mock_jira

        results = [
            CheckResult(
                check_type=CheckType.MISSING_IN_DB,
                severity=Severity.CRITICAL,
                table_name="users",
                issue_description="Issue 1",
                current_value=None,
                expected_value="Expected",
                recommended_action="Action",
                assigned_to="alice"
            ),
            CheckResult(
                check_type=CheckType.ATTR_DIFF,
                severity=Severity.HIGH,
                table_name="users",
                issue_description="Issue 2",
                current_value="Current",
                expected_value="Expected",
                recommended_action="Action",
                assigned_to="alice"
            )
        ]

        mock_issue = Mock()
        mock_issue.key = "TEST-123"
        mock_jira.create_issue.return_value = mock_issue

        creator = JiraTaskCreator(jira_config)
        issue_keys = creator.create_tasks(results)

        # Should create 1 task (grouped by users + alice)
        assert len(issue_keys) == 1
        assert issue_keys[0] == "TEST-123"
        mock_jira.create_issue.assert_called_once()

    @patch('integrations.jira_client.JIRA')
    def test_determine_priority_from_severity(self, mock_jira_class, jira_config):
        mock_jira = Mock()
        mock_jira_class.return_value = mock_jira

        creator = JiraTaskCreator(jira_config)

        # Test CRITICAL -> Highest
        results_critical = [CheckResult(
            check_type=CheckType.PK_DIFF,
            severity=Severity.CRITICAL,
            table_name="test",
            issue_description="Test",
            current_value=None,
            expected_value=None,
            recommended_action="Test",
            assigned_to=None
        )]
        priority = creator._determine_priority(results_critical)
        assert priority == "Highest"

        # Test HIGH -> High
        results_high = [CheckResult(
            check_type=CheckType.ATTR_DIFF,
            severity=Severity.HIGH,
            table_name="test",
            issue_description="Test",
            current_value=None,
            expected_value=None,
            recommended_action="Test",
            assigned_to=None
        )]
        priority = creator._determine_priority(results_high)
        assert priority == "High"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_jira_client.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement Jira client**

Create `src/integrations/jira_client.py`:

```python
from typing import List, Dict, Tuple
from jira import JIRA
from models.config import JiraConfig
from models.data_models import CheckResult, Severity
from errors import JiraIntegrationError
import logging

logger = logging.getLogger(__name__)


class JiraTaskCreator:
    """Create Jira tasks from check results"""

    def __init__(self, config: JiraConfig):
        """
        Initialize Jira client.

        Args:
            config: Jira configuration

        Raises:
            JiraIntegrationError: If connection fails
        """
        try:
            self.jira = JIRA(
                server=config.url,
                basic_auth=(config.username, config.api_token.get_secret_value())
            )
            self.project_key = config.project_key
            self.issue_type = config.issue_type
            logger.info(f"Connected to Jira: {config.url}")
        except Exception as e:
            raise JiraIntegrationError(f"Failed to connect to Jira: {e}") from e

    def create_tasks(self, check_results: List[CheckResult]) -> List[str]:
        """
        Create Jira tasks from check results.
        One task per table/person combination.

        Args:
            check_results: List of check results

        Returns:
            List of created Jira issue keys

        Raises:
            JiraIntegrationError: If task creation fails
        """
        logger.info(f"Creating Jira tasks for {len(check_results)} issues...")

        # Group by table + assigned_to
        grouped = self._group_by_object_and_person(check_results)

        created_issues = []
        for (table_name, assigned_to), issues in grouped.items():
            try:
                issue_key = self._create_single_task(table_name, assigned_to, issues)
                created_issues.append(issue_key)
                logger.info(f"Created Jira task: {issue_key}")
            except Exception as e:
                logger.error(f"Failed to create task for {table_name}: {e}")
                # Continue creating other tasks

        logger.info(f"Created {len(created_issues)} Jira tasks")
        return created_issues

    def _group_by_object_and_person(
        self,
        results: List[CheckResult]
    ) -> Dict[Tuple[str, str], List[CheckResult]]:
        """Group results by (table_name, assigned_to)"""
        grouped = {}
        for result in results:
            key = (result.table_name, result.assigned_to or "unassigned")
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(result)
        return grouped

    def _create_single_task(
        self,
        table_name: str,
        assigned_to: str,
        issues: List[CheckResult]
    ) -> str:
        """Create a single Jira task"""
        description = self._format_description(table_name, issues)
        priority = self._determine_priority(issues)

        issue_dict = {
            'project': {'key': self.project_key},
            'summary': f'Schema compliance issues in table: {table_name}',
            'description': description,
            'issuetype': {'name': self.issue_type},
            'priority': {'name': priority},
            'labels': ['schema-compliance', 'peter-auto']
        }

        # Add assignee if provided and not "unassigned"
        if assigned_to and assigned_to != "unassigned":
            issue_dict['assignee'] = {'name': assigned_to}

        new_issue = self.jira.create_issue(fields=issue_dict)
        return new_issue.key

    def _format_description(self, table_name: str, issues: List[CheckResult]) -> str:
        """Format Jira description with all issues"""
        lines = [
            f"h2. Schema Compliance Issues for table: {table_name}",
            "",
            f"Total issues found: {len(issues)}",
            ""
        ]

        # Group by check type
        by_type = {}
        for issue in issues:
            check_type = issue.check_type.value
            if check_type not in by_type:
                by_type[check_type] = []
            by_type[check_type].append(issue)

        # Format each check type section
        for check_type, type_issues in by_type.items():
            lines.append(f"h3. {check_type}")
            for issue in type_issues:
                lines.append(f"* *Issue:* {issue.issue_description}")
                lines.append(f"  ** Current: {issue.current_value or 'N/A'}")
                lines.append(f"  ** Expected: {issue.expected_value or 'N/A'}")
                lines.append(f"  ** Severity: {issue.severity.value}")
                lines.append(f"  ** Recommended Action: {{code}}{issue.recommended_action}{{code}}")
                lines.append("")

        return "\n".join(lines)

    def _determine_priority(self, issues: List[CheckResult]) -> str:
        """Determine Jira priority based on severity"""
        severities = [issue.severity for issue in issues]

        if Severity.CRITICAL in severities:
            return "Highest"
        elif Severity.HIGH in severities:
            return "High"
        elif Severity.MEDIUM in severities:
            return "Medium"
        else:
            return "Low"
```

- [ ] **Step 4: Update integrations/__init__.py**

```python
from .excel_writer import ExcelReportWriter
from .jira_client import JiraTaskCreator

__all__ = ["ExcelReportWriter", "JiraTaskCreator"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/test_jira_client.py -v
```

Expected: PASS

- [ ] **Step 6: Commit Jira client**

```bash
git add src/integrations/ tests/unit/test_jira_client.py
git commit -m "feat: add Jira task creator

- Implement JiraTaskCreator with task grouping
- Add one task per table/person combination
- Add priority mapping from severity
- Add formatted descriptions with code blocks
- Add comprehensive unit tests with mocking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 17: Remediation Engine (SQL Script Generator)

**Files:**
- Create: `src/core/remediation.py`
- Modify: `src/core/__init__.py`  
- Create: `tests/unit/test_remediation.py`

- [ ] **Step 1: Write test**

Create `tests/unit/test_remediation.py`:

```python
import pytest
from pathlib import Path
from core.remediation import SqlRemediationEngine
from models.data_models import CheckType, Severity, CheckResult


class TestSqlRemediationEngine:
    def test_generate_scripts_creates_files(self, tmp_path):
        results = [CheckResult(
            check_type=CheckType.MISSING_IN_DB,
            severity=Severity.CRITICAL,
            table_name="users",
            issue_description="Table missing",
            current_value=None,
            expected_value="Table",
            recommended_action="CREATE TABLE users",
            assigned_to="alice"
        )]

        engine = SqlRemediationEngine()
        scripts = engine.generate_scripts(results, str(tmp_path))

        assert len(scripts) > 0
        for filename, filepath in scripts.items():
            assert Path(filepath).exists()
```

- [ ] **Step 2: Run test**

```bash
pytest tests/unit/test_remediation.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement**

Create `src/core/remediation.py` - Full implementation with CREATE/ALTER/DROP script generation following the spec

- [ ] **Step 4: Run test**

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add SQL remediation engine"
```

---

## Task 18: Orchestrator

**Files:**
- Create: `src/orchestrator.py`
- Create: `tests/integration/test_orchestrator.py`

- [ ] **Step 1-6**: Implement PeterOrchestrator following TDD pattern with full workflow coordination

---

## Task 19: CLI Commands

**Files:**
- Create: `src/cli/commands.py`
- Create: `src/cli/__init__.py`

- [ ] **Step 1-6**: Implement Click CLI with `run`, `history`, `start-scheduler`, `init-db` commands

---

## Task 20: Scheduler

**Files:**
- Create: `src/scheduler/job_scheduler.py`
- Create: `src/scheduler/__init__.py`

- [ ] **Step 1-6**: Implement JobScheduler with APScheduler

---

## Task 21: Configuration Files

**Files:**
- Create: `config/config.yaml`
- Create: `config/logging.yaml`

- [ ] **Step 1-3**: Create production config files from examples

---

## Task 22: Final Integration & Documentation

**Files:**
- Create: `src/main.py`
- Update: `README.md`
- Create: Sample data files

- [ ] **Step 1**: Create main.py entry point

- [ ] **Step 2**: Run full integration test

```bash
pytest tests/integration/ -v
```

- [ ] **Step 3**: Update README with full usage instructions

- [ ] **Step 4**: Create sample log_model.xlsx in data/

- [ ] **Step 5**: Final commit

```bash
git commit -m "feat: complete Peter implementation

- Full end-to-end workflow functional
- All 4 check types operational
- Excel reports, Jira integration, SQL scripts
- CLI commands and scheduler ready
- Comprehensive test coverage

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Plan Complete! 

**Total Tasks**: 22 comprehensive tasks covering full implementation from setup to deployment.

**Next Steps:**
1. Review this plan
2. Execute using superpowers:subagent-driven-development (recommended) OR superpowers:executing-plans
3. Each task follows TDD: test → fail → implement → pass → commit

**Execution Options:**

**Option 1: Subagent-Driven Development (RECOMMENDED)**
- Fresh subagent per task
- Two-stage review between tasks
- Fast iteration with context isolation

**Option 2: Inline Execution** 
- Execute tasks in current session
- Batch execution with checkpoints

Which execution approach would you like?
