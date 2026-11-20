from src.models.user_model import UserModel

class AuthController:
    def __init__(self):
        self.model = UserModel()

    def handle_register(self, full_name, email, phone, password, dob, address):
        if not full_name or not email or not phone or not password or not dob or not address:
            return False, "Vui lòng nhập đầy đủ thông tin!"
        
        return self.model.register(full_name, email, phone, password, dob, address)

    def handle_login(self, email, password):
        if not email or not password:
            return None, "Vui lòng nhập Email và Password!"
        
        user = self.model.login(email, password)
        if user:
            return user, "Đăng nhập thành công!"
        else:
            return None, "Invalid username or password."
        
    def handle_update_profile(self, user_id, full_name, phone, dob, address):
        if not full_name or not phone or not dob or not address:
            return False, "Vui lòng nhập đầy đủ thông tin!"
        
        return self.model.update_profile(user_id, full_name, phone, dob, address)