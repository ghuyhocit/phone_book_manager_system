import tkinter as tk
from tkinter import messagebox
from src.controllers.auth_controller import AuthController

class ProfileView:
    def __init__(self, top_win, user_data, main_win):
        self.top_win = top_win
        self.main_win = main_win 
        self.user_data = user_data
        self.controller = AuthController()
        
        self.top_win.title("Sửa hồ sơ")
        self.top_win.geometry("300x350")

        tk.Label(top_win, text="Full Name:").pack()
        self.name_entry = tk.Entry(top_win)
        self.name_entry.insert(0, user_data[1]) 
        self.name_entry.pack()

        tk.Label(top_win, text="Email (Không được sửa):").pack()
        email_entry = tk.Entry(top_win, state='readonly') 
        email_entry.insert(0, user_data[2]) 
        email_entry.pack()

        tk.Label(top_win, text="Phone:").pack()
        self.phone_entry = tk.Entry(top_win)
        self.phone_entry.pack()

        tk.Label(top_win, text="DOB (YYYY-MM-DD):").pack()
        self.dob_entry = tk.Entry(top_win)
        self.dob_entry.pack()

        tk.Label(top_win, text="Address:").pack()
        self.addr_entry = tk.Entry(top_win)
        self.addr_entry.pack()

        tk.Button(top_win, text="Lưu thay đổi", command=self.save_profile).pack(pady=10)

    def save_profile(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        dob = self.dob_entry.get()
        addr = self.addr_entry.get()

        success, msg = self.controller.handle_update_profile(self.user_data[0], name, phone, dob, addr)
        if success:
            messagebox.showinfo("Thông báo", msg)
            self.top_win.destroy() 
        else:
            messagebox.showerror("Lỗi", msg)