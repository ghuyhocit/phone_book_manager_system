import tkinter as tk
from tkinter import messagebox
from src.controllers.auth_controller import AuthController

class LoginView:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")
        self.controller = AuthController()

        # Giao diện Login
        tk.Label(root, text="Email:").pack()
        self.email_entry = tk.Entry(root)
        self.email_entry.pack()

        tk.Label(root, text="Password:").pack()
        self.pass_entry = tk.Entry(root, show="*")
        self.pass_entry.pack()

        tk.Button(root, text="Login", command=self.on_login).pack(pady=5)
        tk.Button(root, text="Register", command=self.open_register).pack()

    def on_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        
        user, msg = self.controller.handle_login(email, password)
        if user:
            messagebox.showinfo("Thông báo", msg)
            print("Đăng nhập OK. Tên:", user[1], "- Role:", user[2])
        else:
            messagebox.showerror("Lỗi", msg)

    def open_register(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Register")
        reg_win.geometry("300x350")

        tk.Label(reg_win, text="Full Name:").pack()
        name_entry = tk.Entry(reg_win)
        name_entry.pack()

        tk.Label(reg_win, text="Email:").pack()
        email_entry = tk.Entry(reg_win)
        email_entry.pack()

        tk.Label(reg_win, text="Phone:").pack()
        phone_entry = tk.Entry(reg_win)
        phone_entry.pack()

        tk.Label(reg_win, text="Password:").pack()
        pass_entry = tk.Entry(reg_win, show="*")
        pass_entry.pack()

        tk.Label(reg_win, text="DOB (YYYY-MM-DD):").pack()
        dob_entry = tk.Entry(reg_win)
        dob_entry.pack()

        tk.Label(reg_win, text="Address:").pack()
        addr_entry = tk.Entry(reg_win)
        addr_entry.pack()

        def do_register():
            name = name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            password = pass_entry.get()
            dob = dob_entry.get()
            addr = addr_entry.get()

            success, msg = self.controller.handle_register(name, email, phone, password, dob, addr)
            if success:
                messagebox.showinfo("Thông báo", msg)
                reg_win.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        tk.Button(reg_win, text="Submit", command=do_register).pack(pady=10)