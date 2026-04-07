import pytest
from models.data_models import CheckType, Severity


class TestCheckType:
    def test_check_type_values(self):
        assert CheckType.MISSING_IN_DB.value == "missing_in_db"
        assert CheckType.MISSING_IN_MODEL.value == "missing_in_model"
        assert CheckType.ATTR_DIFF.value == "attribute_diff"
        assert CheckType.PK_DIFF.value == "pk_diff"

    def test_from_string(self):
        assert CheckType.from_string("missing_in_db") == CheckType.MISSING_IN_DB
        assert CheckType.from_string("pk_diff") == CheckType.PK_DIFF

    def test_all_method(self):
        all_checks = CheckType.all()
        assert len(all_checks) == 4
        assert CheckType.MISSING_IN_DB in all_checks


class TestSeverity:
    def test_severity_values(self):
        assert Severity.CRITICAL.value == "CRITICAL"
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
