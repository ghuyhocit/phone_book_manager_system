import hashlib
from src.models.db_connection import get_db_connection

class UserModel:
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, full_name, email, phone, password, dob, address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email đã tồn tại!"

            hashed_pass = self.hash_password(password)
            sql = "INSERT INTO users (full_name, email, phone_number, password_hash, date_of_birth, address, role) VALUES (%s, %s, %s, %s, %s, %s, 'USER')"
            cursor.execute(sql, (full_name, email, phone, hashed_pass, dob, address))
            conn.commit()
            return True, "Đăng ký thành công!"
        except Exception as e:
            conn.rollback()
            return False, "Lỗi: " + str(e)
        finally:
            cursor.close()
            conn.close()

    def login(self, email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            hashed_pass = self.hash_password(password)
            sql = "SELECT user_id, full_name, role FROM users WHERE email = %s AND password_hash = %s"
            cursor.execute(sql, (email, hashed_pass))
            user = cursor.fetchone()
            return user
        except Exception as e:
            print("Lỗi login:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def update_profile(self, user_id, full_name, phone, dob, address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE users SET full_name=%s, phone_number=%s, date_of_birth=%s, address=%s WHERE user_id=%s"
            cursor.execute(sql, (full_name, phone, dob, address, user_id))
            conn.commit()
            return True, "Cập nhật hồ sơ thành công!"
        except Exception as e:
            conn.rollback()
            return False, "Lỗi: " + str(e)
        finally:
            cursor.close()
            conn.close()