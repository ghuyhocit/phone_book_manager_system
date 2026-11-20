"""Controller cho chức năng Admin (UC 21-25).

Kiểm tra quyền, kiểm tra dữ liệu, gọi Model và điều khiển View.
"""
import re
from datetime import date, datetime

from src.models.admin_model import AdminModel

DEFAULT_PAGE_SIZE = 20
MIN_BIRTH_YEAR = 1900
PHONE_PATTERN = re.compile(r"^\+?\d{8,15}$")


def normalize_user(user):
    """Chấp nhận user dạng dict hoặc dạng tuple (user_id, full_name, role)
    như UserModel.login trả về."""
    if isinstance(user, dict):
        return user
    return {"user_id": user[0], "full_name": user[1], "role": user[2]}


class AdminController:
    def __init__(self, admin_user, view, model=None):
        """admin_user: dict hoặc tuple (user_id, full_name, role) của người đang đăng nhập."""
        self.admin = normalize_user(admin_user)
        self.view = view
        self.model = model or AdminModel()
        self.page = 1
        self.page_size = DEFAULT_PAGE_SIZE
        self.keyword = ""
        self.view.set_controller(self)

    # ---------- Kiểm tra quyền ----------
    def _is_admin(self):
        if self.admin.get("role") != "ADMIN":
            self.view.show_error("Chỉ quản trị viên được dùng chức năng này.")
            return False
        return True

    def _db_error(self, exc):
        self.view.show_error(f"Lỗi cơ sở dữ liệu, thao tác chưa được thực hiện.\n({exc})")

    # ---------- UC 21: Xem danh sách người dùng ----------
    def load_users(self, page=None, keyword=None):
        if not self._is_admin():
            return
        if keyword is not None:
            self.keyword = keyword.strip()
            self.page = 1
        if page is not None:
            self.page = max(1, page)
        try:
            users, total = self.model.get_users(self.page, self.page_size, self.keyword)
        except Exception as exc:
            self._db_error(exc)
            return
        total_pages = max(1, -(-total // self.page_size))
        if self.page > total_pages:  # trang hiện tại không còn dữ liệu (vừa xóa)
            self.page = total_pages
            return self.load_users()
        self.view.show_users(users, self.page, total_pages, total)

    def set_page_size(self, page_size):
        """View báo số dòng vừa với cửa sổ; giữ nguyên dòng đầu đang xem."""
        if page_size < 1 or page_size == self.page_size:
            return
        first_index = (self.page - 1) * self.page_size
        self.page_size = page_size
        self.page = first_index // page_size + 1
        self.load_users()

    # ---------- UC 22: Cập nhật người dùng ----------
    def start_update(self, user_id):
        if not self._is_admin():
            return
        try:
            user = self.model.get_user(user_id)
        except Exception as exc:
            self._db_error(exc)
            return
        if user is None:
            self.view.show_error("Người dùng không tồn tại.")
            self.load_users()
            return
        self.view.show_update_form(user)

    def submit_update(self, user_id, full_name, phone_number, address, date_of_birth):
        if not self._is_admin():
            return False
        full_name, phone_number = full_name.strip(), phone_number.strip()
        address, date_of_birth = address.strip(), date_of_birth.strip()
        error = self._validate(full_name, phone_number, address, date_of_birth)
        if error:
            self.view.show_error(error)
            return False
        try:
            updated = self.model.update_user(
                user_id, full_name, phone_number, address, date_of_birth)
        except Exception as exc:
            self._db_error(exc)
            return False
        if not updated:
            self.view.show_error("Người dùng không tồn tại.")
            return False
        self.view.show_info("Cập nhật người dùng thành công.")
        self.load_users()
        return True

    @staticmethod
    def _validate(full_name, phone_number, address, date_of_birth):
        if not full_name or len(full_name) > 100:
            return "Họ tên không được để trống và tối đa 100 ký tự."
        if not PHONE_PATTERN.match(phone_number):
            return "Số điện thoại phải gồm 8-15 chữ số."
        if not address or len(address) > 255:
            return "Địa chỉ không được để trống và tối đa 255 ký tự."
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            return "Ngày sinh phải có dạng YYYY-MM-DD."
        if dob > date.today():
            return "Ngày sinh không được ở tương lai."
        if dob.year < MIN_BIRTH_YEAR:
            return f"Ngày sinh không hợp lệ (năm phải từ {MIN_BIRTH_YEAR} trở đi)."
        return None

    # ---------- UC 23: Xóa người dùng ----------
    def delete_user(self, user_id):
        if not self._is_admin():
            return
        if user_id == self.admin.get("user_id"):
            self.view.show_error("Không thể xóa chính tài khoản của bạn.")
            return
        if not self.view.confirm(
                "Xóa người dùng này cùng toàn bộ liên hệ và danh mục của họ?\n"
                "Thao tác không thể hoàn tác."):
            return
        try:
            deleted = self.model.delete_user(user_id)
        except Exception as exc:
            self._db_error(exc)
            return
        if deleted:
            self.view.show_info("Đã xóa người dùng.")
        else:
            self.view.show_error("Người dùng không tồn tại.")
        self.load_users()

    # ---------- UC 24, 25: Xem tổng số người dùng / liên hệ ----------
    def load_statistics(self):
        if not self._is_admin():
            return
        try:
            total_users = self.model.count_users()
            total_contacts = self.model.count_contacts()
        except Exception as exc:
            self._db_error(exc)
            return
        self.view.show_statistics(total_users, total_contacts)


def open_admin_screen(parent, admin_user):
    """Mở màn hình quản trị; gọi hàm này sau khi Admin đăng nhập thành công."""
    from src.views.admin_view import AdminView
    view = AdminView(parent)
    controller = AdminController(admin_user, view)
    controller.load_users()
    controller.load_statistics()
    return controller
