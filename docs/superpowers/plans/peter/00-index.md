# Peter Implementation Plan - Index

**Project:** Peter - Database Schema Compliance Monitor for MS SQL
**Total Tasks:** 22
**Status:** In Progress
**Started:** 2026-04-07

---

## Overview

This plan implements a comprehensive database schema compliance monitoring system that:
- Detects discrepancies between MS SQL database and Excel-based log model
- Generates detailed Excel reports with color-coded severity
- Creates Jira tasks automatically for responsible teams
- Generates SQL remediation scripts

**Architecture:** Monolithic modular Python application
**Tech Stack:** Python 3.10+, pandas, openpyxl, pyodbc, jira-python, APScheduler, click, pydantic, pytest

---

## Task List

### Phase 1: Foundation (Tasks 1-5)
- [Task 1: Project Setup and Basic Structure](./task-01-project-setup.md) ✅
- [Task 2: Core Data Models and Enums](./task-02-data-models.md) ✅
- [Task 3: Configuration Models with Pydantic](./task-03-config-models.md)
- [Task 4: Custom Exceptions](./task-04-exceptions.md)
- [Task 5: Log Model Parser (Excel)](./task-05-log-model-parser.md)

### Phase 2: Database Layer (Tasks 6-8)
- [Task 6: Database Connection Manager](./task-06-db-connection.md)
- [Task 7: Schema Reader (INFORMATION_SCHEMA)](./task-07-schema-reader.md)
- [Task 8: Audit Logger](./task-08-audit-logger.md)

### Phase 3: Detection Engine (Tasks 9-14)
- [Task 9: Base Check Class](./task-09-base-check.md)
- [Task 10: Missing in DB Check](./task-10-missing-in-db.md)
- [Task 11: Missing in Model Check](./task-11-missing-in-model.md)
- [Task 12: Attribute Difference Check](./task-12-attribute-diff.md)
- [Task 13: Primary Key Difference Check](./task-13-pk-diff.md)
- [Task 14: Detector Engine](./task-14-detector.md)

### Phase 4: Reporting & Remediation (Tasks 15-18)
- [Task 15: Excel Report Writer](./task-15-excel-writer.md)
- [Task 16: Jira Client](./task-16-jira-client.md)
- [Task 17: Remediation Engine](./task-17-remediation.md)
- [Task 18: Orchestrator](./task-18-orchestrator.md)

### Phase 5: User Interface (Tasks 19-21)
- [Task 19: CLI Commands](./task-19-cli.md)
- [Task 20: Scheduler](./task-20-scheduler.md)
- [Task 21: Configuration Files](./task-21-config-files.md)

### Phase 6: Integration (Task 22)
- [Task 22: Final Integration & Documentation](./task-22-final-integration.md)

---

## Dependencies

```
Task 1 (Setup)
  └─→ Task 2 (Data Models)
      └─→ Task 3 (Config)
          ├─→ Task 4 (Exceptions)
          ├─→ Task 5 (Parser) ──┐
          ├─→ Task 6 (DB Conn) ─┤
          │   └─→ Task 7 (Schema) ─┤
          │       └─→ Task 8 (Audit) ─┤
          │                           ├─→ Task 9 (Base Check)
          │                           │   ├─→ Task 10-13 (4 Checks)
          │                           │   └─→ Task 14 (Detector)
          └───────────────────────────┤
                                      ├─→ Task 15 (Excel)
                                      ├─→ Task 16 (Jira)
                                      └─→ Task 17 (Remediation)
                                          └─→ Task 18 (Orchestrator)
                                              ├─→ Task 19 (CLI)
                                              ├─→ Task 20 (Scheduler)
                                              ├─→ Task 21 (Config Files)
                                              └─→ Task 22 (Integration)
```

---

## Progress Tracking

**Completed:** 2/22 (9.1%)
**In Progress:** None (ready for Task 3)
**Remaining:** 20

**Last completed:** Task 2 - Core Data Models and Enums (2026-04-07)
**Next task:** Task 3 - Configuration Models with Pydantic

---

## Execution Method

Using **Subagent-Driven Development**:
- Fresh subagent per task
- Two-stage review (spec compliance → code quality)
- Automatic commits after each task

---

## Notes

- Each task follows TDD: test → fail → implement → pass → commit
- Tasks are designed to be independent where possible
- Each task file is self-contained with full specifications
