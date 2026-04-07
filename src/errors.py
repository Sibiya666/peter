"""Custom exceptions for Peter application"""


class PeterException(Exception):
    """Base exception for all Peter errors"""
    pass


class ConfigurationError(PeterException):
    """Configuration file or environment errors"""
    pass


class DatabaseConnectionError(PeterException):
    """Database connectivity issues"""
    pass


class LogModelParseError(PeterException):
    """Log model Excel parsing errors"""
    pass


class JiraIntegrationError(PeterException):
    """Jira API integration errors"""
    pass


class RemediationError(PeterException):
    """SQL remediation script generation errors"""
    pass
