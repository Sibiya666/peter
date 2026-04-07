import pytest
from errors import (
    PeterException,
    ConfigurationError,
    DatabaseConnectionError,
    LogModelParseError,
    JiraIntegrationError,
    RemediationError
)


class TestExceptions:
    def test_peter_exception_is_base(self):
        with pytest.raises(PeterException):
            raise PeterException("Base error")

    def test_configuration_error_inheritance(self):
        with pytest.raises(PeterException):
            raise ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")

    def test_exception_message(self):
        error = DatabaseConnectionError("Connection failed")
        assert str(error) == "Connection failed"

    def test_all_exceptions_inherit_from_base(self):
        exceptions = [
            ConfigurationError,
            DatabaseConnectionError,
            LogModelParseError,
            JiraIntegrationError,
            RemediationError
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, PeterException)
