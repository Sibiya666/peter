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

