import re
from typing import Optional
from src.models.contact_model import ContactModel


class ContactController:
    """Tầng Controller xử lý nghiệp vụ & validate cho Contact Core (UC 6-12)."""

    def __init__(self, model: Optional[ContactModel] = None):
        self.model = model or ContactModel()

    def validate_contact_input(
        self,
        full_name: str,
        phone_number: str,
        email: str = "",
        address: str = "",
        note: str = "",
    ) -> tuple[bool, str]:
        """Kiểm tra dữ liệu đầu vào trước khi ghi xuống DB."""
        name = (full_name or "").strip()
        phone = (phone_number or "").strip()
        mail = (email or "").strip()

        if not name:
            return False, "Họ và tên không được để trống."

        if not phone:
            return False, "Số điện thoại không được để trống."

        cleaned_phone = re.sub(r"[\s\-\.]", "", phone)
        if not re.fullmatch(r"(\+?\d){9,15}", cleaned_phone):
            return False, "Số điện thoại không hợp lệ (chỉ gồm chữ số, độ dài 9-15 số)."

        if mail and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
            return False, "Định dạng email không hợp lệ."

        if len(name) > 100:
            return False, "Họ và tên tối đa 100 ký tự."

        if len(phone) > 20:
            return False, "Số điện thoại tối đa 20 ký tự."

        if address and len(address.strip()) > 255:
            return False, "Địa chỉ tối đa 255 ký tự."

        if note and len(note.strip()) > 500:
            return False, "Ghi chú tối đa 500 ký tự."

        return True, ""

    def add_contact(
        self,
        user_id: int,
        full_name: str,
        phone_number: str,
        email: str = "",
        address: str = "",
        note: str = "",
        is_favorite: bool = False,
    ) -> tuple[bool, str, Optional[int]]:
        """Thêm liên hệ mới; chặn trùng SĐT trong cùng user, cho phép trùng tên khác SĐT."""
        if not user_id:
            return False, "Thiếu thông tin người dùng (user_id).", None

        is_valid, err_msg = self.validate_contact_input(
            full_name, phone_number, email, address, note
        )
        if not is_valid:
            return False, err_msg, None

        clean_phone = re.sub(r"[\s\-\.]", "", (phone_number or "").strip())

        try:
            if self.model.is_phone_duplicate(user_id=user_id, phone_number=clean_phone):
                return False, "Số điện thoại này đã tồn tại trong danh bạ của bạn.", None

            contact_id = self.model.create_contact(
                user_id=user_id,
                full_name=full_name,
                phone_number=clean_phone,
                email=email,
                address=address,
                note=note,
                is_favorite=is_favorite,
            )
            return True, "Thêm liên hệ thành công.", contact_id
        except ConnectionError as err:
            return False, str(err), None
        except Exception as err:
            return False, f"Lỗi hệ thống khi thêm liên hệ: {err}", None

    def list_contacts(
        self,
        user_id: int,
        favorites_only: bool = False,
        sort_by: str = "name_asc",
    ) -> tuple[bool, str, list[dict]]:
        """Lấy danh sách liên hệ (hỗ trợ lọc yêu thích và sắp xếp)."""
        if not user_id:
            return False, "Thiếu thông tin người dùng (user_id).", []

        sort_map = {
            "name_asc": "full_name ASC",
            "name_desc": "full_name DESC",
            "newest": "created_at DESC",
            "oldest": "created_at ASC",
        }
        order_by = sort_map.get(sort_by, "full_name ASC")

        try:
            contacts = self.model.get_contacts(
                user_id=user_id,
                favorites_only=favorites_only,
                order_by=order_by,
            )
            return True, "", contacts
        except ConnectionError as err:
            return False, str(err), []
        except Exception as err:
            return False, f"Lỗi hệ thống khi tải danh bạ: {err}", []

    def get_contact_detail(
        self, user_id: int, contact_id: int
    ) -> tuple[bool, str, Optional[dict]]:
        """Lấy thông tin chi tiết của một liên hệ."""
        if not user_id or not contact_id:
            return False, "Thiếu thông tin liên hệ.", None

        try:
            contact = self.model.get_contact_detail(
                user_id=user_id, contact_id=contact_id
            )
            if not contact:
                return False, "Không tìm thấy liên hệ này.", None
            return True, "", contact
        except ConnectionError as err:
            return False, str(err), None
        except Exception as err:
            return False, f"Lỗi hệ thống khi xem chi tiết liên hệ: {err}", None

    def edit_contact(
        self,
        user_id: int,
        contact_id: int,
        full_name: str,
        phone_number: str,
        email: str = "",
        address: str = "",
        note: str = "",
    ) -> tuple[bool, str]:
        """Cập nhật thông tin liên hệ; chặn trùng SĐT với liên hệ khác của cùng user."""
        if not user_id or not contact_id:
            return False, "Thiếu thông tin liên hệ cần cập nhật."

        is_valid, err_msg = self.validate_contact_input(
            full_name, phone_number, email, address, note
        )
        if not is_valid:
            return False, err_msg

        clean_phone = re.sub(r"[\s\-\.]", "", (phone_number or "").strip())

        try:
            existing = self.model.get_contact_detail(
                user_id=user_id, contact_id=contact_id
            )
            if not existing:
                return False, "Liên hệ không tồn tại hoặc đã bị xóa."

            if self.model.is_phone_duplicate(
                user_id=user_id,
                phone_number=clean_phone,
                exclude_contact_id=contact_id,
            ):
                return False, "Số điện thoại này đã được dùng bởi một liên hệ khác."

            updated = self.model.update_contact(
                user_id=user_id,
                contact_id=contact_id,
                full_name=full_name,
                phone_number=clean_phone,
                email=email,
                address=address,
                note=note,
            )
            if updated:
                return True, "Cập nhật liên hệ thành công."
            return False, "Không có thay đổi nào được lưu."
        except ConnectionError as err:
            return False, str(err)
        except Exception as err:
            return False, f"Lỗi hệ thống khi cập nhật liên hệ: {err}"

    def remove_contact(self, user_id: int, contact_id: int) -> tuple[bool, str]:
        """Xóa liên hệ khỏi danh bạ."""
        if not user_id or not contact_id:
            return False, "Thiếu thông tin liên hệ cần xóa."

        try:
            deleted = self.model.delete_contact(user_id=user_id, contact_id=contact_id)
            if deleted:
                return True, "Đã xóa liên hệ khỏi danh bạ."
            return False, "Không tìm thấy liên hệ để xóa."
        except ConnectionError as err:
            return False, str(err)
        except Exception as err:
            return False, f"Lỗi hệ thống khi xóa liên hệ: {err}"

    def set_favorite(
        self, user_id: int, contact_id: int, is_favorite: bool
    ) -> tuple[bool, str]:
        """Bật / tắt trạng thái yêu thích cho liên hệ."""
        if not user_id or not contact_id:
            return False, "Thiếu thông tin liên hệ."

        try:
            updated = self.model.toggle_favorite(
                user_id=user_id,
                contact_id=contact_id,
                is_favorite=is_favorite,
            )
            if updated:
                msg = (
                    "Đã thêm vào danh sách yêu thích."
                    if is_favorite
                    else "Đã bỏ khỏi danh sách yêu thích."
                )
                return True, msg
            return False, "Không thể cập nhật trạng thái yêu thích."
        except ConnectionError as err:
            return False, str(err)
        except Exception as err:
            return False, f"Lỗi hệ thống khi cập nhật yêu thích: {err}"