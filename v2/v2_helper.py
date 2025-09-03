import time

import pandas as pd

from core.config import LOGGER

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %X"


def format_date_series(s: pd.Series, default_date:bool=False) -> pd.Series:
    """
    Convert a Series of datetimes/strings to YYYY-MM-DD strings, preserving None for invalid values.
    """
    s_dt = pd.to_datetime(s, errors="coerce")
    out = s_dt.dt.strftime(DATE_FMT)
    # Preserve None for NaT
    return out.where(s_dt.notna(), None if not default_date else "1945-08-17")

def format_datetime_series(s: pd.Series) -> pd.Series:
    """
    Convert a Series of datetimes/strings to YYYY-MM-DD strings, preserving None for invalid values.
    """
    s_dt = pd.to_datetime(s, errors="coerce")
    out = s_dt.dt.strftime(DATETIME_FMT)
    # Preserve None for NaT
    return out.where(s_dt.notna(), None)

def log_duration(prefix: str, start_time: float) -> None:
    """Log a duration message with consistent formatting."""
    LOGGER.info(f"{prefix} in {time.time() - start_time:.2f}s")


def str_to_float(x: str) -> float:
    if x == "" or x is None or x == "-":
        return 0
    x = x.replace(",", ".")
    try:
        return float(x)
    except Exception as e:
        LOGGER.error(f"error converting {x} to float: {e}")
        return 0
