import tkinter as tk
from tkinter import messagebox
from src.views.profile_view import ProfileView

class DashboardView:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data 
        self.root.title("Dashboard - Phone Book")
        self.root.geometry("400x350")
        
        tk.Label(root, text=f"Xin chào, {user_data[1]}!", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(root, text=f"Role: {user_data[3]}").pack(pady=5)
        
        tk.Button(root, text="Sửa hồ sơ cá nhân", command=self.open_profile, width=25).pack(pady=8)
        tk.Button(root, text="Quản lý danh bạ", width=25, command=self.open_contact_manager).pack(pady=5)
        tk.Button(root, text="Tìm kiếm & Nhóm", width=25, command=self.open_search_group).pack(pady=5)
        
        if user_data[3] == "ADMIN":
            tk.Button(root, text="Quản trị hệ thống", width=25, command=self.open_admin_panel, 
                     bg="#FFD700", fg="black").pack(pady=8)
        
        tk.Button(root, text="Đăng xuất", command=self.logout, bg="red", fg="white", width=25).pack(pady=15)

    def open_profile(self):
        profile_win = tk.Toplevel(self.root)
        app = ProfileView(profile_win, self.user_data, self.root)

    def open_contact_manager(self):
        contact_win = tk.Toplevel(self.root)
        from src.views.contact_view import ContactView
        app = ContactView(root=contact_win, user_id=self.user_data[0])

    def open_search_group(self):
        search_win = tk.Toplevel(self.root)
        search_win.title("Tìm kiếm & Nhóm")
        search_win.geometry("900x600")
        
        from src.controllers.category_controller import SearchGroupController
        from src.views.search_view import SearchGroupView
        
        controller = SearchGroupController(user_id=self.user_data[0])
        app = SearchGroupView(search_win, controller)
        app.pack(fill="both", expand=True)
        
    def open_admin_panel(self):
        from src.views.admin_view import AdminView
        from src.controllers.admin_controller import open_admin_screen
        open_admin_screen(self.root, self.user_data)

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.root.destroy()
            import tkinter as tk
            from src.views.login_view import LoginView
            new_root = tk.Tk()
            LoginView(new_root)
            new_root.mainloop()