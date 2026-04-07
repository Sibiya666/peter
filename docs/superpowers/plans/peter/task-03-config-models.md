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

