import logging
import os
import time
from functools import wraps

import pandas as pd
import pymysql.cursors
import pymysqlpool
from dotenv import load_dotenv

load_dotenv()

# Bug 2 & Optimasi 4: Environment Variable Validation & Logging Consistency
REQUIRED_ENV_VARS = [
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASS",
    "DB_NAME",
    "DB_NAME_KEPEGAWAIAN",
]


def validate_env():
    """Validate that all required environment variables are set."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please check your .env file."
        )


validate_env()

# Optimasi 4: Log level from environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    encoding="utf-8",
)
LOGGER = logging.getLogger(__name__)

# Cache for database configurations
DEFAULT_EO_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

DEFAULT_KEPEGAWAIAN_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME_KEPEGAWAIAN"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

# Bug 1 & Optimasi 1: Singleton Connection Pools
_smartoffice_pool = None
_kepegawaian_pool = None


def get_smartoffice_connection_pool() -> pymysqlpool.Connection:
    """Get a connection from the smartoffice connection pool (Singleton)."""
    global _smartoffice_pool
    if _smartoffice_pool is None:
        LOGGER.info("Initializing SmartOffice connection pool")
        _smartoffice_pool = pymysqlpool.ConnectionPool(
            name="smartoffice-pool",
            size=5,
            maxsize=10,
            pre_create_num=1,
            **DEFAULT_EO_DB_CONFIG,
        )
    return _smartoffice_pool.get_connection()


def get_kepegawaian_connection_pool(autocommit: bool = False) -> pymysqlpool.Connection:
    """Get a connection from the kepegawaian connection pool (Singleton)."""
    global _kepegawaian_pool
    # Since autocommit is a pool level setting in pymysqlpool,
    # we might need separate pools if both are used.
    # However, currently it's only used with autocommit=False (default).
    if _kepegawaian_pool is None:
        LOGGER.info("Initializing Kepegawaian connection pool")
        # Bug 6: Lowering maxsize from 1000 to 50
        _kepegawaian_pool = pymysqlpool.ConnectionPool(
            name="kepegawaian-pool",
            size=5,
            maxsize=50,
            pre_create_num=2,
            autocommit=autocommit,
            **DEFAULT_KEPEGAWAIAN_DB_CONFIG,
        )
    return _kepegawaian_pool.get_connection()


# Optimasi 2: Simple Retry Mechanism
def db_retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        LOGGER.error(f"Operation failed after {max_retries} attempts: {e}")
                        raise
                    LOGGER.warning(f"Database operation failed, retrying ({retries}/{max_retries}): {e}")
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


@db_retry()
def fetch_smartoffice(query: str, where: tuple = None) -> pd.DataFrame:
    with get_smartoffice_connection_pool() as conn:
        return _get_fetch_result(conn, query, where)


@db_retry()
def fetch_kepegawaian(query: str, where: tuple = None) -> pd.DataFrame:
    with get_kepegawaian_connection_pool() as conn:
        return _get_fetch_result(conn, query, where)


def _get_fetch_result(conn: pymysqlpool.Connection, query: str, where: tuple = None) -> pd.DataFrame:
    with conn.cursor() as cursor:
        # Bug 5: Pythonic None check (PEP 8)
        if where is not None:
            cursor.execute(query, where)
        else:
            cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else None
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)


@db_retry()
def save_update_smartoffice(query: str, data: list):
    with get_smartoffice_connection_pool() as connection:
        _do_save_update(connection, query, data)


@db_retry()
def save_update_kepegawaian(query: str, data: list):
    with get_kepegawaian_connection_pool() as connection:
        _do_save_update(connection, query, data)


def _do_save_update(connection: pymysqlpool.Connection, query: str, data: list):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.executemany(query, data)
            affected = cursor.rowcount
            LOGGER.info(f"{affected} row(s) affected")
            connection.commit()
        except Exception as e:
            LOGGER.error(f"Database error during save/update: {e}")
            connection.rollback()
            # Bug 3: Re-raise exception so caller knows it failed
            raise
        finally:
            # Bug 4: Always restore FOREIGN_KEY_CHECKS
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            except Exception as e:
                LOGGER.warning(f"Failed to restore FOREIGN_KEY_CHECKS: {e}")
