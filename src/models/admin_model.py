"""Model cho chức năng Admin (UC 21-25).

Model chỉ làm việc với database và trả dữ liệu, không biết gì về giao diện.
"""
from src.models.db_connection import get_db_connection


class AdminModel:
    def __init__(self, connection_factory=get_db_connection):
        self._connect = connection_factory

    def _open(self):
        conn = self._connect()
        if conn is None:
            raise ConnectionError("Không thể kết nối cơ sở dữ liệu.")
        return conn

    # ---------- UC 21: Xem danh sách người dùng ----------
    def get_users(self, page=1, page_size=20, keyword=""):
        """Trả về (danh sách người dùng của trang, tổng số bản ghi)."""
        offset = (page - 1) * page_size
        where, params = "", []
        if keyword:
            where = "WHERE full_name LIKE %s OR email LIKE %s OR phone_number LIKE %s"
            like = f"%{keyword}%"
            params = [like, like, like]
        conn = self._open()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(f"SELECT COUNT(*) AS total FROM users {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                "SELECT user_id, full_name, email, phone_number, role "
                f"FROM users {where} ORDER BY user_id LIMIT %s OFFSET %s",
                params + [page_size, offset],
            )
            return cur.fetchall(), total
        finally:
            conn.close()

    # ---------- UC 22: Cập nhật người dùng ----------
    def get_user(self, user_id):
        """Trả về thông tin một người dùng, hoặc None nếu không tồn tại."""
        conn = self._open()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT user_id, full_name, email, phone_number, date_of_birth, "
                "address, role FROM users WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def update_user(self, user_id, full_name, phone_number, address, date_of_birth):
        """Cập nhật thông tin người dùng (một giao dịch nguyên tử).

        Trả về True nếu có người dùng được cập nhật, False nếu không tồn tại.
        """
        conn = self._open()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
            if cur.fetchone() is None:
                return False
            cur.execute(
                "UPDATE users SET full_name = %s, phone_number = %s, "
                "address = %s, date_of_birth = %s WHERE user_id = %s",
                (full_name, phone_number, address, date_of_birth, user_id),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- UC 23: Xóa người dùng ----------
    def delete_user(self, user_id, current_admin_id=None):
        """Xóa tài khoản; liên hệ và nhóm bị xóa theo nhờ ON DELETE CASCADE.

        Admin không được tự xóa chính mình: nếu user_id trùng current_admin_id
        thì ném ValueError và không xóa gì.
        Trả về True nếu đã xóa, False nếu không tồn tại.
        """
        if current_admin_id is not None and user_id == current_admin_id:
            raise ValueError("Admin không được tự xóa tài khoản của mình.")
        conn = self._open()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- UC 24, 25: Thống kê ----------
    def count_users(self):
        return self._count("users")

    def count_contacts(self):
        return self._count("contacts")

    def _count(self, table):
        conn = self._open()
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table}")  # table do code truyền, không phải input người dùng
            return cur.fetchone()[0]
        finally:
            conn.close()
