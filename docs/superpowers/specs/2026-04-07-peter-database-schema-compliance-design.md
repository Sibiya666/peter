# Peter - Database Schema Compliance Monitor

**Design Specification**

- **Date**: 2026-04-07
- **Status**: Draft
- **Version**: 1.0.0

---

## Executive Summary

Peter - это система автоматизированного мониторинга соответствия схемы MS SQL базы данных эталонной модели данных (log model). Система выполняет 4 типа проверок, генерирует детальные отчёты в Excel, создаёт задачи в Jira для ответственных и автоматически генерирует SQL скрипты для исправления найденных расхождений.

**Ключевые возможности:**
- Автоматическое обнаружение расхождений между БД и log model (Excel)
- Генерация детальных Excel отчётов с цветовым кодированием по severity
- Автоматическое создание Jira задач для ответственных за таблицы
- Генерация SQL remediation скриптов (CREATE/ALTER/DROP)
- Режимы работы: scheduled (cron) и ad-hoc (manual)
- Audit trail всех запусков в БД
- CLI интерфейс для управления

**Архитектурный подход:** Монолитное модульное Python приложение с чёткими границами между компонентами.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Data Models](#3-data-models)
4. [Core Components - Detector Module](#4-core-components---detector-module)
5. [Reporter Module](#5-reporter-module)
6. [Remediation Module](#6-remediation-module)
7. [Database Layer](#7-database-layer)
8. [Orchestrator & CLI](#8-orchestrator--cli)
9. [Configuration & Error Handling](#9-configuration--error-handling)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment & Installation](#11-deployment--installation)
12. [Usage Examples & Workflow](#12-usage-examples--workflow)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PETER Application                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │   CLI/API    │──▶│ Orchestrator │──▶│  Scheduler  │ │
│  └──────────────┘   └──────────────┘   └─────────────┘ │
│                            │                             │
│         ┌──────────────────┼──────────────────┐         │
│         ▼                  ▼                  ▼         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│  │ Detector │      │ Reporter │      │Remediator│      │
│  │  Module  │      │  Module  │      │  Module  │      │
│  └──────────┘      └──────────┘      └──────────┘      │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            ▼                             │
│                   ┌─────────────────┐                    │
│                   │  Database Layer │                    │
│                   └─────────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌────────┐         ┌──────────┐        ┌──────────┐
   │MS SQL  │         │Log Model │        │ Mapping  │
   │Database│         │  (Excel) │        │  Table   │
   └────────┘         └──────────┽        └──────────┘
```

### 1.2 Three-Phase Process

**PHASE 1 — DETECT**
- Чтение log model из Excel файла
- Чтение текущей схемы БД через INFORMATION_SCHEMA
- Выполнение 4 типов проверок:
  1. Missing in DB (есть в log model, нет в БД)
  2. Missing in Model (есть в БД, нет в log model)
  3. Attribute Differences (различия в типах данных, nullable, length)
  4. Primary Key Differences (несовпадение PK)

**PHASE 2 — REPORT**
- Генерация Excel отчёта (один лист на тип проверки)
- Создание Jira задач (одна задача на таблицу/ответственного)
- Запись результатов в audit log table

**PHASE 3 — REMEDIATE**
- Генерация SQL скриптов для исправления расхождений
- Скрипты сохраняются в файлы для manual review
- Скрипты обёрнуты в транзакции с ROLLBACK по умолчанию

### 1.3 Key Design Principles

- **Single Responsibility**: Каждый модуль отвечает за одну фазу
- **Dependency Injection**: Модули получают зависимости через конструктор
- **Configuration-Driven**: Все параметры в config файле
- **Fail-Safe**: Ошибка в одной проверке не останавливает остальные
- **Audit Everything**: Каждый запуск логируется в БД
- **Safe by Default**: SQL скрипты требуют manual review перед применением

---

## 2. Project Structure

```
peter/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── orchestrator.py            # Main workflow coordinator
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── detector.py            # Detection engine
│   │   ├── checks/
│   │   │   ├── __init__.py
│   │   │   ├── missing_in_db.py   # Check 1
│   │   │   ├── missing_in_model.py # Check 2
│   │   │   ├── attribute_diff.py   # Check 3
│   │   │   └── pk_diff.py          # Check 4
│   │   │
│   │   ├── reporter.py            # Report generation
│   │   └── remediation.py         # SQL script generator
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── log_model_parser.py    # Excel log model parser
│   │   └── validators.py          # Data validation
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # MS SQL connection manager
│   │   ├── schema_reader.py       # Read DB metadata
│   │   └── audit_logger.py        # Audit log operations
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── jira_client.py         # Jira API integration
│   │   └── excel_writer.py        # Excel report writer
│   │
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── job_scheduler.py       # APScheduler wrapper
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py            # Click CLI commands
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration models (Pydantic)
│   │   └── data_models.py         # Data structures
│   │
│   └── errors.py                  # Custom exceptions
│
├── config/
│   ├── config.yaml                # Main configuration
│   ├── config.example.yaml        # Example config
│   └── logging.yaml               # Logging configuration
│
├── tests/
│   ├── __init__.py
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── fixtures/                  # Test data
│
├── docs/
│   ├── superpowers/
│   │   └── specs/                 # Design specs
│   ├── setup.md                   # Setup instructions
│   └── usage.md                   # Usage guide
│
├── output/                        # Generated reports and scripts
│   ├── reports/                   # Excel reports
│   └── scripts/                   # SQL remediation scripts
│
├── logs/                          # Application logs
│
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package setup
├── pytest.ini                     # Pytest configuration
├── .env.example                   # Environment variables template
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker compose configuration
└── README.md
```

---

## 3. Data Models

### 3.1 Core Data Structures

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CheckType(Enum):
    """Типы проверок"""
    MISSING_IN_DB = "missing_in_db"
    MISSING_IN_MODEL = "missing_in_model"
    ATTR_DIFF = "attribute_diff"
    PK_DIFF = "pk_diff"

class Severity(Enum):
    """Уровни критичности"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class LogModelColumn:
    """Колонка из log model (Excel)"""
    column_name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str]
    max_length: Optional[int]
    is_primary_key: bool

@dataclass
class LogModelTable:
    """Таблица из log model"""
    table_name: str
    columns: List[LogModelColumn]

@dataclass
class DatabaseColumn:
    """Колонка из реальной БД (INFORMATION_SCHEMA)"""
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str]
    character_maximum_length: Optional[int]
    is_primary_key: bool

@dataclass
class DatabaseTable:
    """Таблица из реальной БД"""
    table_name: str
    columns: List[DatabaseColumn]

@dataclass
class CheckResult:
    """Результат одной проверки"""
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
    """Результаты полного запуска"""
    run_id: str
    timestamp: datetime
    user: str
    check_results: List[CheckResult]
    total_issues: int
    status: str  # SUCCESS, FAILED, PARTIAL

@dataclass
class OwnerMapping:
    """Маппинг таблица → ответственный"""
    table_name: str
    owner_name: str
    jira_username: str
```

### 3.2 Configuration Models

```python
from pydantic import BaseModel, SecretStr

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
```

---

## 4. Core Components - Detector Module

### 4.1 Overview

Detector Module выполняет 4 типа проверок, каждая из которых реализована как отдельный класс с методом `execute()`.

### 4.2 Check #1: Missing in DB

**Назначение**: Обнаруживает таблицы и колонки, описанные в log model, но отсутствующие в БД.

**Алгоритм**:
1. Итерация по всем таблицам в log model
2. Проверка существования таблицы в db_schema
3. Если таблица отсутствует → CRITICAL issue
4. Если таблица существует → проверка колонок
5. Для каждой колонки из log model, отсутствующей в БД → HIGH issue

**Severity**:
- Отсутствующая таблица: CRITICAL
- Отсутствующая колонка: HIGH

### 4.3 Check #2: Missing in Model

**Назначение**: Обнаруживает таблицы и колонки, существующие в БД, но не описанные в log model.

**Алгоритм**:
1. Итерация по всем таблицам в db_schema
2. Проверка наличия таблицы в log model
3. Если таблицы нет в log model → HIGH issue
4. Если таблица есть → проверка колонок
5. Для каждой колонки из БД, отсутствующей в log model → MEDIUM issue

**Severity**:
- Недокументированная таблица: HIGH
- Недокументированная колонка: MEDIUM

### 4.4 Check #3: Attribute Differences

**Назначение**: Обнаруживает различия в атрибутах колонок (data_type, is_nullable, max_length).

**Алгоритм**:
1. Для таблиц, существующих в обоих местах
2. Находим колонки, существующие в обоих местах
3. Сравниваем атрибуты:
   - **data_type**: нормализованное сравнение (varchar vs varchar(50))
   - **is_nullable**: boolean сравнение
   - **max_length**: для VARCHAR/CHAR типов
   - **default_value**: опционально

**Severity**:
- data_type mismatch: HIGH
- is_nullable mismatch: MEDIUM
- max_length mismatch: LOW

**Нормализация типов данных**:
- `VARCHAR(50)` → `varchar` (убираем размер для сравнения)
- `INT` → `int` (lowercase)
- `DECIMAL(10,2)` → `decimal`

### 4.5 Check #4: Primary Key Differences

**Назначение**: Обнаруживает несовпадения в primary key определениях.

**Алгоритм**:
1. Для каждой таблицы, существующей в обоих местах
2. Извлекаем набор PK колонок из log model
3. Извлекаем набор PK колонок из БД
4. Сравниваем множества
5. Если не совпадают → CRITICAL issue

**Severity**: CRITICAL (изменение PK — критичная операция)

### 4.6 Detector Engine Implementation

```python
# core/detector.py

class Detector:
    """Основной движок проверок"""

    def __init__(self):
        self.checks = [
            MissingInDbCheck(),
            MissingInModelCheck(),
            AttributeDiffCheck(),
            PkDiffCheck()
        ]

    def run_checks(self,
                   log_model: Dict[str, LogModelTable],
                   db_schema: Dict[str, DatabaseTable],
                   check_types: Optional[List[CheckType]] = None) -> List[CheckResult]:
        """
        Запускает проверки и возвращает список найденных проблем.

        Args:
            log_model: Эталонная модель из Excel
            db_schema: Текущая схема БД
            check_types: Список типов проверок (None = все)

        Returns:
            Список CheckResult объектов
        """
        all_results = []

        for check in self.checks:
            # Фильтрация по check_types если указано
            if check_types and check.check_type not in check_types:
                continue

            try:
                results = check.execute(log_model, db_schema)
                all_results.extend(results)
                logger.info(f"Check {check.check_type.value}: found {len(results)} issues")
            except Exception as e:
                logger.error(f"Check {check.check_type.value} failed: {e}", exc_info=True)
                # Продолжаем выполнение других проверок

        return all_results
```

---

## 5. Reporter Module

### 5.1 Excel Report Generation

**Формат отчёта**:
- Один Excel файл на запуск
- Один лист на тип проверки (4 листа)
- Дополнительный Summary лист

**Структура листа проверки**:
- **Колонки**: Table Name, Issue Description, Current Value, Expected Value, Severity, Recommended Action, Assigned To
- **Форматирование**:
  - Заголовки: жирный шрифт, синий фон
  - Строки: цветовое кодирование по severity
    - CRITICAL: красный (#FF0000)
    - HIGH: оранжевый (#FFA500)
    - MEDIUM: жёлтый (#FFFF00)
    - LOW: зелёный (#90EE90)
  - Автоширина колонок

**Summary лист**:
- Run ID
- Timestamp
- Username
- Total issues
- Breakdown по severity
- Breakdown по check type

**Naming convention**: `peter_{YYYYMMDD}_{HHMMSS}_{run_id}.xlsx`

### 5.2 Jira Integration

**Стратегия создания задач**: One task per table/person

**Алгоритм**:
1. Группировка результатов по `(table_name, assigned_to)`
2. Для каждой группы создаётся одна Jira задача
3. В description задачи перечисляются все найденные проблемы для этой таблицы

**Формат Jira задачи**:
- **Summary**: `Schema compliance issues in table: {table_name}`
- **Description**:
  ```
  h2. Schema Compliance Issues for table: {table_name}

  Total issues found: {count}

  h3. {CheckType1}
  * Issue: {description}
    ** Current: {current_value}
    ** Expected: {expected_value}
    ** Severity: {severity}
    ** Recommended Action: {code}{sql}{code}

  h3. {CheckType2}
  ...
  ```
- **Priority**: Определяется по максимальной severity среди проблем:
  - CRITICAL → Highest
  - HIGH → High
  - MEDIUM → Medium
  - LOW → Low
- **Assignee**: Из owner mapping
- **Labels**: `schema-compliance`, `peter-auto`

**Error Handling**:
- Если Jira недоступна → логируем ошибку, но не падаем
- Если assignee не найден в Jira → создаём unassigned задачу

---

## 6. Remediation Module

### 6.1 SQL Script Generation Strategy

**Принципы**:
- **Safe by Default**: Все скрипты в транзакциях с ROLLBACK по умолчанию
- **Manual Review Required**: Комментарии с инструкциями для review
- **Context Rich**: Обильные комментарии с issue descriptions
- **Separation**: Один файл на тип проверки

### 6.2 Script Types

**1. CREATE scripts (для Missing in DB)**:
```sql
-- Auto-generated CREATE scripts
-- Review carefully before executing!
-- Generated: 2026-04-07T14:30:22

BEGIN TRANSACTION;
GO

-- Create missing table: users
-- Issue: Table 'users' defined in log model but missing in database
CREATE TABLE users (
    id INT NOT NULL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

-- Add missing column to existing table: orders
-- Issue: Column 'status' is missing in table 'orders'
ALTER TABLE orders
ADD status VARCHAR(50) NOT NULL DEFAULT 'pending';
GO

-- Review the above statements, then uncomment to commit:
-- COMMIT TRANSACTION;
-- GO

-- Or rollback if issues found:
ROLLBACK TRANSACTION;
GO
```

**2. ALTER scripts (для Attribute Differences)**:
```sql
-- Auto-generated ALTER scripts for attribute differences
-- WARNING: These changes may affect existing data!
-- Generated: 2026-04-07T14:30:22

BEGIN TRANSACTION;
GO

-- Alter table: users
-- Issue: Column 'email' has type mismatch
-- Current: varchar(100)
-- Expected: varchar(255)
ALTER TABLE users
ALTER COLUMN email VARCHAR(255) NOT NULL;
GO

-- Issue: Column 'created_at' has nullable mismatch
-- Current: NULL allowed
-- Expected: NOT NULL
-- WARNING: Ensure no NULL values exist before running!
ALTER TABLE users
ALTER COLUMN created_at DATETIME2 NOT NULL;
GO

-- Review the above statements, then uncomment to commit:
-- COMMIT TRANSACTION;
-- GO

ROLLBACK TRANSACTION;
GO
```

**3. PRIMARY KEY scripts (для PK Differences)**:
```sql
-- Auto-generated PRIMARY KEY modification scripts
-- CRITICAL: These changes are risky and may affect foreign keys!
-- Generated: 2026-04-07T14:30:22

BEGIN TRANSACTION;
GO

-- Table: orders
-- Issue: Primary key mismatch in table 'orders'
-- Current: PK: ['id']
-- Expected: PK: ['id', 'order_date']

-- Step 1: Check for foreign key constraints
SELECT
    fk.name AS foreign_key_name,
    OBJECT_NAME(fk.parent_object_id) AS referencing_table
FROM sys.foreign_keys fk
WHERE OBJECT_NAME(fk.referenced_object_id) = 'orders';
GO

-- Step 2: Drop existing PK constraint
-- TODO: Replace 'PK_orders' with actual constraint name from above query
-- ALTER TABLE orders DROP CONSTRAINT PK_orders;
-- GO

-- Step 3: Add new PK constraint
-- ALTER TABLE orders ADD CONSTRAINT PK_orders PRIMARY KEY (id, order_date);
-- GO

ROLLBACK TRANSACTION;
GO
```

### 6.3 Naming Convention

`{YYYYMMDD}_{HHMMSS}_{check_type}.sql`

Пример: `20260407_143022_missing_in_db.sql`

### 6.4 File Encoding

UTF-8 with BOM для совместимости с SQL Server Management Studio.

---

## 7. Database Layer

### 7.1 Log Model Parser

**Input**: Excel файл с обязательными колонками:
- `table_name` (VARCHAR)
- `column_name` (VARCHAR)
- `data_type` (VARCHAR)
- `is_nullable` (BOOLEAN/VARCHAR)
- `default_value` (VARCHAR, nullable)
- `max_length` (INT, nullable)
- `is_primary_key` (BOOLEAN/VARCHAR)

**Boolean Parsing**:
- Поддерживаемые значения: `True/False`, `1/0`, `Yes/No`, `Y/N`
- Case-insensitive

**Data Type Normalization**:
- Lowercase: `VARCHAR` → `varchar`
- Remove size: `VARCHAR(50)` → `varchar`
- Trim whitespace

**Validation**:
- Проверка обязательных колонок
- Проверка на пустые значения в table_name/column_name
- Логирование warnings для неожиданных значений

### 7.2 Schema Reader

**Source**: MS SQL INFORMATION_SCHEMA views

**Queries**:

```sql
-- Get all tables
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
  AND TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME;

-- Get columns for table
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = ?
  AND TABLE_SCHEMA = 'dbo'
ORDER BY ORDINAL_POSITION;

-- Get primary key columns
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME), 'IsPrimaryKey') = 1
  AND TABLE_NAME = ?
  AND TABLE_SCHEMA = 'dbo';
```

**Schema**: По умолчанию `dbo`, но должно быть конфигурируемым.

### 7.3 Audit Logger

**Table Definition**:

```sql
CREATE TABLE [dbo].[peter_audit_log] (
    run_id VARCHAR(50) PRIMARY KEY,
    timestamp DATETIME2 NOT NULL,
    username VARCHAR(100) NOT NULL,
    check_types VARCHAR(500),           -- Comma-separated list
    total_issues INT NOT NULL,
    status VARCHAR(20) NOT NULL,        -- RUNNING, SUCCESS, FAILED
    error_message VARCHAR(MAX) NULL
);
```

**Operations**:
- `log_run_start()`: Записывает начало запуска
- `log_run_complete()`: Обновляет статус на SUCCESS
- `log_run_failure()`: Обновляет статус на FAILED с error message
- `get_run_history()`: Возвращает последние N записей

**Auto-Creation**: Таблица создаётся автоматически при первом запуске, если не существует.

### 7.4 Owner Mapping Table

**Table Definition**:

```sql
CREATE TABLE [dbo].[peter_owner_mapping] (
    table_name VARCHAR(255) PRIMARY KEY,
    owner_name VARCHAR(100) NOT NULL,
    jira_username VARCHAR(100) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

**Usage**:
- Detector использует эту таблицу для заполнения `assigned_to` в CheckResult
- При создании Jira задач используется `jira_username`

**Fallback**: Если table_name не найдено в mapping → используется default_owner из конфига.

---

## 8. Orchestrator & CLI

### 8.1 Orchestrator

**Responsibilities**:
- Координация всех трёх фаз (DETECT, REPORT, REMEDIATE)
- Управление транзакциями и error handling
- Audit logging
- Генерация run_id

**Main Method**: `run_checks(check_types: Optional[List[CheckType]]) -> RunReport`

**Flow**:
1. Генерация run_id и логирование старта
2. PHASE 1: DETECT
   - Загрузка log model
   - Загрузка db schema
   - Выполнение проверок
3. PHASE 2: REPORT
   - Генерация Excel отчёта
   - Создание Jira задач
4. PHASE 3: REMEDIATE
   - Генерация SQL скриптов
5. Логирование завершения
6. Возврат RunReport

**Error Handling**:
- Каждая фаза обёрнута в try-catch
- Ошибки в Report/Remediate не останавливают процесс
- Все ошибки логируются
- Критичные ошибки записываются в audit log

### 8.2 CLI Commands

**Framework**: Click

**Commands**:

```bash
peter run                           # Запуск всех проверок
peter run --checks missing_in_db    # Запуск конкретных проверок
peter run --config path/to/config   # Использование альтернативного конфига

peter history                       # Показать историю запусков
peter history --limit 20            # Последние 20 запусков

peter start-scheduler               # Запустить scheduled jobs

peter init-db                       # Инициализация БД (создание audit/mapping tables)
```

**Output Format**:
- Progress bars для длительных операций
- Цветовой вывод (✅ ❌ ⚠️ 🎫 🔧)
- Structured summary после завершения
- Exit codes: 0 = success, 1 = failure

### 8.3 Scheduler

**Framework**: APScheduler

**Trigger**: Cron expression из конфига

**Режим**: BlockingScheduler (для daemon mode)

**Timezone**: Конфигурируемый

**Job Function**: Вызывает `orchestrator.run_checks()` с полными проверками

**Logging**: Результаты scheduled runs логируются так же, как manual runs

---

## 9. Configuration & Error Handling

### 9.1 Configuration File

**Format**: YAML

**Location**: `config/config.yaml`

**Structure**:

```yaml
database:
  server: "localhost"
  database: "your_database"
  username: "db_user"
  password: "${DB_PASSWORD}"
  driver: "ODBC Driver 17 for SQL Server"

jira:
  url: "https://your-company.atlassian.net"
  username: "jira_user@company.com"
  api_token: "${JIRA_API_TOKEN}"
  project_key: "SCHEMA"
  issue_type: "Task"

paths:
  log_model_excel: "data/log_model.xlsx"
  output_reports: "output/reports"
  output_scripts: "output/scripts"

schedule:
  enabled: true
  cron: "0 2 * * *"
  timezone: "Europe/Moscow"

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

owner_mapping:
  default_owner: "schema_team"
  fallback_jira_user: "unassigned"
```

**Environment Variables**:
- Syntax: `${VAR_NAME}` или `${VAR_NAME:default_value}`
- Loaded via python-dotenv
- Stored in `.env` file (not in Git)

### 9.2 Logging Configuration

**Format**: YAML (logging.yaml)

**Handlers**:
- Console: INFO level, standard format
- File: DEBUG level, detailed format, rotating (10MB, 5 backups)
- Error File: ERROR level only, detailed format

**Log Files**:
- `logs/peter.log` - все логи
- `logs/peter_errors.log` - только ошибки

### 9.3 Custom Exceptions

```python
class PeterException(Exception):
    """Base exception"""

class ConfigurationError(PeterException):
    """Configuration issues"""

class DatabaseConnectionError(PeterException):
    """Database connectivity"""

class LogModelParseError(PeterException):
    """Log model parsing"""

class JiraIntegrationError(PeterException):
    """Jira API"""

class RemediationError(PeterException):
    """SQL script generation"""
```

**Usage**: Специфичные exceptions позволяют точнее обрабатывать ошибки и логировать контекст.

---

## 10. Testing Strategy

### 10.1 Test Pyramid

- **Unit Tests (80%)**: Тестируют отдельные компоненты изолированно
- **Integration Tests (15%)**: Тестируют взаимодействие компонентов
- **E2E Tests (5%)**: Полный flow с реальной тестовой БД

### 10.2 Unit Tests

**Coverage**:
- `test_log_model_parser.py`: Парсинг Excel, валидация, error handling
- `test_checks.py`: Каждая из 4 проверок
- `test_excel_writer.py`: Генерация отчётов, форматирование
- `test_remediation.py`: Генерация SQL скриптов
- `test_config.py`: Загрузка конфигов, env substitution

**Tools**:
- pytest
- pytest-cov (coverage)
- pytest-mock (mocking)

**Fixtures**: Переиспользуемые test data (sample Excel, mock DB schema)

### 10.3 Integration Tests

**Coverage**:
- `test_orchestrator.py`: Полный цикл DETECT→REPORT→REMEDIATE
- `test_database_integration.py`: Работа с реальной test БД
- `test_jira_integration.py`: Взаимодействие с Jira (mocked API)

**Test Database**:
- Docker container с MS SQL
- Автоматическое создание/удаление
- Seed data для тестирования различных сценариев

### 10.4 CI/CD

**Platform**: GitHub Actions

**Pipeline**:
1. Checkout code
2. Setup Python 3.10
3. Install dependencies
4. Start MS SQL container (Docker service)
5. Run unit tests
6. Run integration tests
7. Upload coverage to Codecov

**Coverage Target**: 80% minimum

---

## 11. Deployment & Installation

### 11.1 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-org/peter.git
cd peter

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup configuration
cp config/config.example.yaml config/config.yaml
cp .env.example .env
# Edit config.yaml and .env with your settings

# 5. Create directories
mkdir -p output/reports output/scripts logs data

# 6. Initialize database
peter init-db

# 7. Verify installation
peter --help
```

### 11.2 Deployment Options

**Option 1: Local Installation**
- Для разработки или single-user использования
- Запуск: `peter run`

**Option 2: Windows Service**
- Для production, scheduled runs
- Используем NSSM (Non-Sucking Service Manager)
- Запускает `peter start-scheduler` как сервис

**Option 3: Docker**
- Cross-platform, isolated
- Docker Compose для multi-container setup
- Volume mounts для config/output/logs

### 11.3 System Requirements

**Python**: 3.10+

**Database**: MS SQL Server 2016+

**ODBC Driver**: Microsoft ODBC Driver 17 for SQL Server

**Memory**: 512MB minimum, 1GB recommended

**Disk**: 1GB для приложения + space для reports/logs

---

## 12. Usage Examples & Workflow

### 12.1 Quick Start

```bash
# Первый запуск
peter run

# Запуск конкретных проверок
peter run --checks missing_in_db --checks pk_diff

# Альтернативный конфиг
peter run --config config/prod_config.yaml

# История запусков
peter history

# Запуск scheduler
peter start-scheduler
```

### 12.2 Typical Workflows

**Initial Setup (Day 1)**:
1. Установка Peter
2. Настройка config.yaml и .env
3. Создание log_model.xlsx (эталонная модель)
4. Заполнение peter_owner_mapping table
5. `peter init-db`
6. `peter run` (первый тестовый запуск)

**Regular Usage (Scheduled Mode)**:
1. `peter start-scheduler` (запускается как сервис)
2. Каждую ночь в 2 AM: автоматическая проверка
3. При находке проблем:
   - Excel отчёт → output/reports/
   - Jira задачи → автоматически созданы
   - SQL скрипты → output/scripts/
4. Команда получает Jira уведомления
5. Ответственные review SQL скрипты
6. Применение скриптов вручную после review

**Ad-Hoc Usage (Manual Run)**:
1. Разработчик меняет схему БД
2. `peter run` (проверка после изменений)
3. Review Excel отчёта
4. Обновление log_model.xlsx если нужно
5. `peter run` (повторная проверка)
6. Если всё ОК → продолжение работы

### 12.3 Example Output

```bash
$ peter run

🚀 Starting Peter - Schema Compliance Check
Config: config/config.yaml
Running all checks

Processing  [####################################]  100%

✅ Check completed successfully!
Run ID: peter_20260407_143022_a7f3c91b
Total issues found: 5

📊 Issues by severity:
  CRITICAL: 1
  HIGH: 2
  MEDIUM: 2

📄 Reports generated:
  Excel: output/reports/peter_20260407_143022_a7f3c91b.xlsx

🎫 Jira tasks created:
  SCHEMA-123: Schema compliance issues in table: users
  SCHEMA-124: Schema compliance issues in table: orders

🔧 Remediation scripts:
  output/scripts/20260407_143022_missing_in_db.sql
  output/scripts/20260407_143022_pk_diff.sql

⚠️  Review SQL scripts before applying to database!
```

### 12.4 Log Model Excel Format

```
| table_name | column_name | data_type | is_nullable | default_value | max_length | is_primary_key |
|------------|-------------|-----------|-------------|---------------|------------|----------------|
| users      | id          | int       | FALSE       | NULL          | NULL       | TRUE           |
| users      | email       | varchar   | FALSE       | NULL          | 255        | FALSE          |
| users      | created_at  | datetime2 | FALSE       | GETDATE()     | NULL       | FALSE          |
| orders     | id          | int       | FALSE       | NULL          | NULL       | TRUE           |
| orders     | user_id     | int       | FALSE       | NULL          | NULL       | FALSE          |
| orders     | total       | decimal   | FALSE       | 0.00          | NULL       | FALSE          |
```

### 12.5 Owner Mapping Table Example

```sql
INSERT INTO peter_owner_mapping (table_name, owner_name, jira_username)
VALUES
    ('users', 'Alice Smith', 'alice.smith'),
    ('orders', 'Bob Johnson', 'bob.johnson'),
    ('products', 'Charlie Davis', 'charlie.davis');
```

---

## Appendix A: Technology Stack

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.10+ | Runtime |
| pandas | 2.0.0+ | Excel parsing, data manipulation |
| openpyxl | 3.1.0+ | Excel writing |
| pydantic | 2.0.0+ | Configuration validation |
| PyYAML | 6.0+ | Config file parsing |
| pyodbc | 4.0.39+ | MS SQL connectivity |
| jira | 3.5.0+ | Jira API integration |
| APScheduler | 3.10.0+ | Job scheduling |
| click | 8.1.0+ | CLI framework |
| python-dotenv | 1.0.0+ | Environment variables |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 7.4.0+ | Testing framework |
| pytest-cov | 4.1.0+ | Coverage reporting |
| pytest-mock | 3.11.0+ | Mocking |
| black | 23.7.0+ | Code formatting |
| flake8 | 6.1.0+ | Linting |
| mypy | 1.5.0+ | Type checking |

---

## Appendix B: Glossary

- **Log Model**: Эталонная модель данных, описанная в Excel файле
- **Check Type**: Тип проверки (missing_in_db, missing_in_model, attr_diff, pk_diff)
- **Severity**: Уровень критичности проблемы (CRITICAL, HIGH, MEDIUM, LOW)
- **Run ID**: Уникальный идентификатор запуска проверок
- **Audit Log**: Таблица в БД, хранящая историю всех запусков
- **Owner Mapping**: Таблица, связывающая таблицы с ответственными
- **Remediation**: Процесс генерации SQL скриптов для исправления проблем
- **Orchestrator**: Главный координатор, управляющий всеми фазами процесса

---

## Appendix C: Future Enhancements

**Version 2.0 Potential Features**:
1. Web UI (dashboard для просмотра отчётов и истории)
2. Support для других СУБД (PostgreSQL, Oracle)
3. Автоматическое применение low-risk изменений
4. Slack/Teams notifications
5. Metric tracking и trends analysis
6. Git integration (version control для log model)
7. Rollback механизм для applied changes
8. Multi-database support (проверка нескольких БД)

---

**End of Specification**

---

_This specification was created on 2026-04-07 as part of the brainstorming and design process._
