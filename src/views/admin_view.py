"""View cho chức năng Admin (UC 21-25).

View chỉ vẽ giao diện và chuyển thao tác của người dùng cho Controller,
không gọi SQL trực tiếp.
"""
import tkinter as tk
from tkinter import messagebox, ttk


class AdminView(tk.Toplevel):
    COLUMNS = (("user_id", "ID", 60), ("full_name", "Họ tên", 200),
               ("email", "Email", 240), ("phone_number", "Số điện thoại", 130),
               ("role", "Vai trò", 80))

    ROW_HEIGHT = 25
    HEADER_HEIGHT = 27
    MIN_ROWS = 20  # tối thiểu 20 dòng mỗi trang; cửa sổ nhỏ hơn thì dùng thanh cuộn

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Quản trị hệ thống - Phone Book")
        self.geometry("820x520")
        self.minsize(640, 420)
        self.controller = None
        self._build()

    def set_controller(self, controller):
        self.controller = controller

    # ---------- Dựng giao diện ----------
    def _build(self):
        stats = ttk.LabelFrame(self, text="Thống kê hệ thống")
        stats.pack(fill="x", padx=10, pady=(10, 5))
        self.lbl_users = ttk.Label(stats, text="Tổng số người dùng: -")
        self.lbl_users.pack(side="left", padx=15, pady=6)
        self.lbl_contacts = ttk.Label(stats, text="Tổng số liên hệ: -")
        self.lbl_contacts.pack(side="left", padx=15, pady=6)
        ttk.Button(stats, text="Làm mới",
                   command=lambda: self.controller.load_statistics()).pack(side="right", padx=10)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=5)
        ttk.Label(bar, text="Tìm:").pack(side="left")
        self.var_keyword = tk.StringVar()
        entry = ttk.Entry(bar, textvariable=self.var_keyword, width=30)
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda e: self.controller.load_users(keyword=self.var_keyword.get()))
        ttk.Button(bar, text="Tìm", command=lambda: self.controller.load_users(
            keyword=self.var_keyword.get())).pack(side="left")
        ttk.Button(bar, text="Xóa người dùng", command=self._on_delete).pack(side="right")
        ttk.Button(bar, text="Cập nhật", command=self._on_update).pack(side="right", padx=5)

        style = ttk.Style(self)
        style.configure("Admin.Treeview", rowheight=self.ROW_HEIGHT)  # style riêng, không ảnh hưởng màn hình khác
        table = ttk.Frame(self)
        table.pack(fill="both", expand=True, padx=10, pady=5)
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, columns=[c[0] for c in self.COLUMNS],
                                 show="headings", selectmode="browse",
                                 style="Admin.Treeview", height=5)
        for key, title, width in self.COLUMNS:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="w")
        self.scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self._on_scroll)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Configure>", self._on_tree_resize)
        self._resize_job = None

        nav = ttk.Frame(self)
        nav.pack(fill="x", padx=10, pady=(0, 10))
        self.btn_prev = ttk.Button(nav, text="< Trước", command=lambda: self.controller.load_users(
            page=self._page - 1))
        self.btn_prev.pack(side="left")
        self.lbl_page = ttk.Label(nav, text="Trang 1/1")
        self.lbl_page.pack(side="left", padx=10)
        self.btn_next = ttk.Button(nav, text="Sau >", command=lambda: self.controller.load_users(
            page=self._page + 1))
        self.btn_next.pack(side="left")
        self._page, self._total_pages = 1, 1

    def _on_scroll(self, first, last):
        """Cập nhật thanh cuộn (luôn hiển thị bên phải bảng)."""
        self.scroll.set(first, last)

    # ---------- Số dòng mỗi trang tự co giãn theo chiều cao cửa sổ ----------
    def _on_tree_resize(self, _event):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(150, self._apply_page_size)

    def _apply_page_size(self):
        self._resize_job = None
        height = self.tree.winfo_height()
        if self.controller is None or height < 60:
            return
        header, row_h = self.HEADER_HEIGHT, self.ROW_HEIGHT
        children = self.tree.get_children()
        if children:  # đo chiều cao thật nếu đã có dòng
            box = self.tree.bbox(children[0])
            if box:
                header, row_h = box[1], box[3]
        rows = max(self.MIN_ROWS, (height - header - 2) // row_h)
        self.controller.set_page_size(rows)

    def _selected_user_id(self):
        sel = self.tree.selection()
        if not sel:
            self.show_error("Hãy chọn một người dùng trong danh sách.")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _on_update(self):
        user_id = self._selected_user_id()
        if user_id is not None:
            self.controller.start_update(user_id)

    def _on_delete(self):
        user_id = self._selected_user_id()
        if user_id is not None:
            self.controller.delete_user(user_id)

    # ---------- Controller gọi các hàm hiển thị dưới đây ----------
    def show_users(self, users, page, total_pages, total):
        self.tree.delete(*self.tree.get_children())
        for u in users:
            self.tree.insert("", "end", values=(
                u["user_id"], u["full_name"], u["email"], u["phone_number"], u["role"]))
        self._page, self._total_pages = page, total_pages
        self.lbl_page.config(text=f"Trang {page}/{total_pages} ({total} người dùng)")
        self.btn_prev.state(["!disabled"] if page > 1 else ["disabled"])
        self.btn_next.state(["!disabled"] if page < total_pages else ["disabled"])
        if total == 0:
            self.lbl_page.config(text="Không có người dùng nào")

    def show_statistics(self, total_users, total_contacts):
        self.lbl_users.config(text=f"Tổng số người dùng: {total_users}")
        self.lbl_contacts.config(text=f"Tổng số liên hệ: {total_contacts}")

    def show_update_form(self, user):
        win = tk.Toplevel(self)
        win.title("Cập nhật người dùng")
        win.transient(self)
        win.grab_set()
        fields = [("Email (không sửa)", None), ("Họ tên", "full_name"),
                  ("Số điện thoại", "phone_number"),
                  ("Ngày sinh (YYYY-MM-DD)", "date_of_birth"), ("Địa chỉ", "address")]
        vars_ = {}
        win._vars = []  # giữ tham chiếu tới mọi biến, nếu không Tkinter sẽ làm ô nhập bị trống
        for row, (label, key) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            var = tk.StringVar(value=user["email"] if key is None else str(user[key]))
            win._vars.append(var)
            entry = ttk.Entry(win, textvariable=var, width=40,
                              state="readonly" if key is None else "normal")
            entry.grid(row=row, column=1, padx=10, pady=5)
            if key:
                vars_[key] = var

        def save():
            ok = self.controller.submit_update(
                user["user_id"], vars_["full_name"].get(), vars_["phone_number"].get(),
                vars_["address"].get(), vars_["date_of_birth"].get())
            if ok:
                win.destroy()

        btns = ttk.Frame(win)
        btns.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Cập nhật", command=save).pack(side="left", padx=5)
        ttk.Button(btns, text="Hủy", command=win.destroy).pack(side="left", padx=5)

    def show_error(self, message):
        messagebox.showerror("Lỗi", message, parent=self)

    def show_info(self, message):
        messagebox.showinfo("Thông báo", message, parent=self)

    def confirm(self, message):
        return messagebox.askyesno("Xác nhận", message, parent=self)