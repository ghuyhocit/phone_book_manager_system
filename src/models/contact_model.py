from typing import Optional
from datetime import datetime
from src.models.db_connection import get_db_connection


class ContactModel:
    """Tầng Model xử lý SQL cho bảng contacts (UC 6-12)."""

    def _get_connection_and_cursor(self):
        conn = get_db_connection()
        if conn is None:
            raise ConnectionError("Không thể kết nối tới cơ sở dữ liệu phonebook_db.")
        return conn, conn.cursor(dictionary=True)

    def is_phone_duplicate(self, user_id: int, phone_number: str, exclude_contact_id: int = None) -> bool:
        """
        Kiểm tra trùng số điện thoại trong danh bạ của một user.
        - Trùng số điện thoại trong cùng user -> True (không cho phép).
        - Trùng tên nhưng khác số điện thoại -> xử lý ở tầng kiểm tra khác, ở đây check theo phone_number.
        """
        conn, cursor = self._get_connection_and_cursor()
        try:
            clean_phone = (phone_number or "").strip()
            if exclude_contact_id is not None:
                sql = """
                    SELECT contact_id
                    FROM contacts
                    WHERE user_id = %s AND phone_number = %s AND contact_id != %s
                    LIMIT 1
                """
                cursor.execute(sql, (user_id, clean_phone, exclude_contact_id))
            else:
                sql = """
                    SELECT contact_id
                    FROM contacts
                    WHERE user_id = %s AND phone_number = %s
                    LIMIT 1
                """
                cursor.execute(sql, (user_id, clean_phone))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def create_contact(self, user_id: int, full_name: str, phone_number: str,
                       email: str = "", address: str = "", note: str = "",
                       is_favorite: bool = False) -> int:
        """Thêm liên hệ mới (UC Add Contact). Trả về contact_id mới tạo."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            now = datetime.now()
            sql = """
                INSERT INTO contacts (
                    user_id, full_name, phone_number, email, address, note,
                    is_favorite, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id,
                (full_name or "").strip(),
                (phone_number or "").strip(),
                (email or "").strip() or None,
                (address or "").strip() or None,
                (note or "").strip() or None,
                1 if is_favorite else 0,
                now,
                now,
            )
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_contacts(self, user_id: int, favorites_only: bool = False,
                     order_by: str = "full_name ASC") -> list[dict]:
        """Lấy danh sách liên hệ của user (UC View List & Favorite filter)."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            allowed_orders = {
                "full_name ASC": "full_name ASC, contact_id ASC",
                "full_name DESC": "full_name DESC, contact_id DESC",
                "created_at DESC": "created_at DESC, contact_id DESC",
                "created_at ASC": "created_at ASC, contact_id ASC",
            }
            order_sql = allowed_orders.get(order_by, "full_name ASC, contact_id ASC")

            sql = f"""
                SELECT contact_id, user_id, full_name, phone_number, email,
                       address, note, is_favorite, created_at, updated_at
                FROM contacts
                WHERE user_id = %s
            """
            params = [user_id]
            if favorites_only:
                sql += " AND is_favorite = 1"

            sql += f" ORDER BY {order_sql}"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_contact_detail(self, user_id: int, contact_id: int) -> Optional[dict]:
        """Lấy chi tiết 1 liên hệ theo contact_id và user_id (UC View Details)."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            sql = """
                SELECT contact_id, user_id, full_name, phone_number, email,
                       address, note, is_favorite, created_at, updated_at
                FROM contacts
                WHERE user_id = %s AND contact_id = %s
                LIMIT 1
            """
            cursor.execute(sql, (user_id, contact_id))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def update_contact(self, user_id: int, contact_id: int, full_name: str,
                       phone_number: str, email: str = "", address: str = "",
                       note: str = "") -> bool:
        """Cập nhật thông tin liên hệ (UC Update Contact)."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            now = datetime.now()
            sql = """
                UPDATE contacts
                SET full_name = %s,
                    phone_number = %s,
                    email = %s,
                    address = %s,
                    note = %s,
                    updated_at = %s
                WHERE user_id = %s AND contact_id = %s
            """
            params = (
                (full_name or "").strip(),
                (phone_number or "").strip(),
                (email or "").strip() or None,
                (address or "").strip() or None,
                (note or "").strip() or None,
                now,
                user_id,
                contact_id,
            )
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_contact(self, user_id: int, contact_id: int) -> bool:
        """Xóa liên hệ (UC Delete Contact)."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            sql = "DELETE FROM contacts WHERE user_id = %s AND contact_id = %s"
            cursor.execute(sql, (user_id, contact_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def toggle_favorite(self, user_id: int, contact_id: int, is_favorite: bool) -> bool:
        """Đánh dấu / bỏ đánh dấu yêu thích (UC Mark/Unmark Favorite)."""
        conn, cursor = self._get_connection_and_cursor()
        try:
            now = datetime.now()
            sql = """
                UPDATE contacts
                SET is_favorite = %s, updated_at = %s
                WHERE user_id = %s AND contact_id = %s
            """
            cursor.execute(sql, (1 if is_favorite else 0, now, user_id, contact_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()