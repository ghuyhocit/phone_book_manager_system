import os
import mysql.connector

def get_db_connection():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "123456")
    database = os.getenv("DB_NAME", "phonebook_db")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            autocommit=False
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối Database: {err}")
        return None