from mysql.connector import connect
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
load_dotenv()

db_url = f"mariadb+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}?charset=utf8mb4"
db_url_kepegawaian = f"mariadb+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB_KEPEGAWAIAN')}?charset=utf8mb4"

engine = create_engine(db_url)
engine_kepegawaian = create_engine(
    db_url_kepegawaian, pool_size=10, max_overflow=20)

koneksi = connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB"),
    port=int(os.getenv("MYSQL_PORT"))
)
