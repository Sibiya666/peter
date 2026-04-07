## Task 17: Remediation Engine (SQL Script Generator)

**Files:**
- Create: `src/core/remediation.py`
- Modify: `src/core/__init__.py`  
- Create: `tests/unit/test_remediation.py`

- [ ] **Step 1: Write test**

Create `tests/unit/test_remediation.py`:

```python
import pytest
from pathlib import Path
from core.remediation import SqlRemediationEngine
from models.data_models import CheckType, Severity, CheckResult


class TestSqlRemediationEngine:
    def test_generate_scripts_creates_files(self, tmp_path):
        results = [CheckResult(
            check_type=CheckType.MISSING_IN_DB,
            severity=Severity.CRITICAL,
            table_name="users",
            issue_description="Table missing",
            current_value=None,
            expected_value="Table",
            recommended_action="CREATE TABLE users",
            assigned_to="alice"
        )]

        engine = SqlRemediationEngine()
        scripts = engine.generate_scripts(results, str(tmp_path))

        assert len(scripts) > 0
        for filename, filepath in scripts.items():
            assert Path(filepath).exists()
```

- [ ] **Step 2: Run test**

```bash
pytest tests/unit/test_remediation.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement**

Create `src/core/remediation.py` - Full implementation with CREATE/ALTER/DROP script generation following the spec

- [ ] **Step 4: Run test**

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add SQL remediation engine"
```

---

