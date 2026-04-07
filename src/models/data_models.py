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
