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
