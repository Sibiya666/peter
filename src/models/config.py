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
