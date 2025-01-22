import os
from dotenv import load_dotenv
import pymysql
import pymysqlpool

load_dotenv()

DEFAULT_EO_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": "smartoffice",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_smartoffice_connection_pool() -> pymysqlpool.ConnectionPool:
    """Get a connection pool to the smartoffice database."""

    return pymysqlpool.ConnectionPool(
        name="smartoffice-pool",
        size=5,
        maxsize=10,
        pre_create_num=1,
        **DEFAULT_EO_DB_CONFIG,
    )


DEFAULT_KEPEGAWAIAN_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": "kepegawaian",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_kepegawaian_connection_pool(autocommit: bool = False) -> pymysqlpool.ConnectionPool:
    """Get a connection pool to kepegawaian database."""

    return pymysqlpool.ConnectionPool(
        name="kepegawaian-pool",
        size=5,
        maxsize=1000,
        pre_create_num=2,
        autocommit=autocommit,
        **DEFAULT_KEPEGAWAIAN_DB_CONFIG,
    )
