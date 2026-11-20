from src.models.db_connection import get_db_connection

def main():
    print("=== Phone Book Management System ===")
    conn = get_db_connection()
    if conn:
        print("[OK] Kết nối Database thành công!")
        conn.close()
    else:
        print("[FAIL] Kết nối thất bại. Kiểm tra lại mật khẩu MySQL.")

if __name__ == "__main__":
    main()