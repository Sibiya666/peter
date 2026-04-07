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

