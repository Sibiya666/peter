import pandas as pd
from pathlib import Path


def create_sample_log_model_excel(output_path: Path) -> Path:
    """Create a sample log model Excel file for testing"""
    df = pd.DataFrame({
        'table_name': ['users', 'users', 'users', 'orders', 'orders'],
        'column_name': ['id', 'email', 'created_at', 'id', 'total'],
        'data_type': ['int', 'varchar(255)', 'datetime2', 'int', 'decimal(10,2)'],
        'is_nullable': [False, False, False, False, False],
        'default_value': [None, None, 'GETDATE()', None, '0.00'],
        'max_length': [None, 255, None, None, None],
        'is_primary_key': [True, False, False, True, False]
    })

    excel_path = output_path / "sample_log_model.xlsx"
    df.to_excel(excel_path, index=False)
    return excel_path


def create_invalid_log_model_excel(output_path: Path) -> Path:
    """Create an invalid log model Excel file (missing required columns)"""
    df = pd.DataFrame({
        'table_name': ['users'],
        'column_name': ['id']
        # Missing required columns
    })

    excel_path = output_path / "invalid_log_model.xlsx"
    df.to_excel(excel_path, index=False)
    return excel_path
