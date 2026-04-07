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
