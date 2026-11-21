import tkinter as tk
from tkinter import messagebox
from src.views.profile_view import ProfileView

class DashboardView:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data  
        self.root.title("Dashboard - Phone Book")
        self.root.geometry("400x300")
        
        tk.Label(root, text=f"Xin chào, {user_data[1]}!", font=("Arial", 16, "bold")).pack(pady=30)
        tk.Label(root, text=f"Role: {user_data[3]}").pack()
        
        tk.Button(root, text="Sửa hồ sơ cá nhân", command=self.open_profile, width=25).pack(pady=10)
        
        tk.Button(root, text="Quản lý danh bạ", width=25, command=self.open_contact_manager).pack(pady=5) 
        
        tk.Button(root, text="Đăng xuất", command=self.logout, bg="red", fg="white", width=25).pack(pady=20)

    def open_profile(self):
        profile_win = tk.Toplevel(self.root)
        app = ProfileView(profile_win, self.user_data, self.root)

    def open_contact_manager(self):
        contact_win = tk.Toplevel(self.root)
        from src.views.contact_view import ContactView 
        app = ContactView(root=contact_win, user_id=self.user_data[0])

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.root.destroy() 
            import tkinter as tk
            from src.views.login_view import LoginView
            new_root = tk.Tk()
            LoginView(new_root)
            new_root.mainloop()