import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Kết nối đến database phonebook_db"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="676767",
            database="phonebook_db",
            charset="utf8mb4",
            autocommit=False
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Lỗi kết nối Database: {e}")
        return None