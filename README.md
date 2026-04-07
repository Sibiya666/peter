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

```bash
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
```

## Usage

```bash
# Run all checks
peter run

# Run specific checks
peter run --checks missing_in_db

# View history
peter history

# Start scheduler
peter start-scheduler
```

## Documentation

See `docs/superpowers/specs/` for design specifications.
