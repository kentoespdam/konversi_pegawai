import time
from typing import Union

import pandas as pd
import numpy as np

from core.config import LOGGER

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %X"

def format_date_series(s: pd.Series, default_date: bool = False) -> pd.Series:
    """
    Convert a Series of datetimes/strings to YYYY-MM-DD strings, preserving None for invalid values.
    Returns None for NaT values to ensure compatibility with SQL insertion (pymysql).
    """
    if s.empty:
        return s
    
    # Coerce to datetime, letting pandas handle multiple formats if possible
    s_dt = pd.to_datetime(s, errors="coerce", format="mixed")
    
    # Format to string
    out = s_dt.dt.strftime(DATE_FMT)
    
    # Replace NaT with None (or default date if specified)
    # Using where(notna()) ensures the result is an object Series with None instead of NaT
    default_val = "1945-08-17" if default_date else None
    return out.where(s_dt.notna(), default_val)

def format_datetime_series(s: pd.Series) -> pd.Series:
    """
    Convert a Series of datetimes/strings to YYYY-MM-DD HH:MM:SS strings, preserving None for invalid values.
    Returns None for NaT values to ensure compatibility with SQL insertion (pymysql).
    """
    if s.empty:
        return s
        
    s_dt = pd.to_datetime(s, errors="coerce", format="mixed")
    out = s_dt.dt.strftime(DATETIME_FMT)
    
    return out.where(s_dt.notna(), None)

def log_duration(prefix: str, start_time: float) -> None:
    """Log a duration message with consistent formatting."""
    duration = time.time() - start_time
    LOGGER.info(f"{prefix} in {duration:.2f}s")

def str_to_float_series(s: pd.Series) -> pd.Series:
    """
    Vectorized conversion of a Series of strings to float64.
    Handles European formatting (dot as thousands, comma as decimal) and placeholders like '-' or ''.
    """
    if s.empty:
        return s

    # Ensure we are working with string representation
    s_str = s.astype(str)

    # Clean the string path:
    # 1. Remove thousands separator (dot)
    # 2. Replace decimal separator (comma) with dot
    # 3. Handle common empty placeholders by replacing with NaN
    s_cleaned = (
        s_str.str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"-": np.nan, "": np.nan, "None": np.nan, "nan": np.nan, "NaN": np.nan})
    )

    # Convert to numeric, errors='coerce' will turn non-parsable strings to NaN
    s_float = pd.to_numeric(s_cleaned, errors="coerce")

    # Fill NaN with 0 as per requirement
    return s_float.fillna(0).astype(float)

def str_to_float(x: Union[str, float, int, None]) -> float:
    """
    Scalar version of str_to_float_series for convenience.
    """
    if x is None or x == "" or x == "-":
        return 0.0
    
    if isinstance(x, (int, float)):
        return float(x)
        
    # Use the logic from the series version for consistency
    s = pd.Series([x])
    return float(str_to_float_series(s).iloc[0])
