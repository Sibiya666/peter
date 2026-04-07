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

