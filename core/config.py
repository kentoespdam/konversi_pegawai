import logging
import os

import pandas as pd
import pymysql.cursors
import pymysqlpool
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level="DEBUG",  # os.getenv('LOG_LEVEL', 'INFO'),
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
    encoding="utf-8",
)
LOGGER = logging.getLogger(__name__)

DEFAULT_EO_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_smartoffice_connection_pool() -> pymysqlpool.Connection:
    """Get a connection pool to the smartoffice database."""

    return pymysqlpool.ConnectionPool(
        name="smartoffice-pool",
        size=5,
        maxsize=10,
        pre_create_num=1,
        **DEFAULT_EO_DB_CONFIG,
    ).get_connection()


DEFAULT_KEPEGAWAIAN_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME_KEPEGAWAIAN"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_kepegawaian_connection_pool(autocommit: bool = False) -> pymysqlpool.Connection:
    """Get a connection pool to kepegawaian database."""

    return pymysqlpool.ConnectionPool(
        name="kepegawaian-pool",
        size=5,
        maxsize=1000,
        pre_create_num=2,
        autocommit=autocommit,
        **DEFAULT_KEPEGAWAIAN_DB_CONFIG,
    ).get_connection()


def fetch_smartoffice(query: str, where: tuple = None) -> pd.DataFrame:
    with get_smartoffice_connection_pool() as conn:
        return _get_fetch_result(conn, query, where)


def fetch_kepegawaian(query: str, where: tuple = None) -> pd.DataFrame:
    with get_kepegawaian_connection_pool() as conn:
        return _get_fetch_result(conn, query, where)


def _get_fetch_result(conn: pymysqlpool.Connection, query: str, where: tuple = None) -> pd.DataFrame:
    with conn.cursor() as cursor:
        if not where is None:
            cursor.execute(query, where)
        else:
            cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else None
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)


def save_update_smartoffice(query: str, data: list):
    with get_smartoffice_connection_pool() as connection:
        _do_save_update(connection, query, data)


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
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        except Exception as e:
            LOGGER.error(e)
            connection.rollback()
