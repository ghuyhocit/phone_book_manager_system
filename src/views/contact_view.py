import tkinter as tk
from tkinter import messagebox
from src.controllers.contact_controller import ContactController


class ContactView:
    """Tầng View giao diện quản lý danh bạ (tkinter thuần), kết nối ContactController."""

    def __init__(self, root: tk.Tk, user_id: int = 1, controller: ContactController = None):
        self.root = root
        self.user_id = user_id
        self.controller = controller or ContactController()

        self.root.title("Quản lý danh bạ - Contact Core")
        self.root.geometry("980x600")
        self.root.minsize(820, 520)

        self.contacts_cache: list[dict] = []
        self.selected_contact_id: int | None = None
        self.selected_is_favorite: bool = False

        self.fav_only_var = tk.BooleanVar(value=False)
        self.sort_var = tk.StringVar(value="name_asc")

        self._build_ui()
        self.load_contacts()

    def _build_ui(self):
        # Thanh công cụ phía trên
        top_bar = tk.Frame(self.root, padx=10, pady=8, bg="#f0f2f5")
        top_bar.pack(fill=tk.X)

        tk.Label(top_bar, text="DANH BẠ LIÊN HỆ", font=("Arial", 13, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        tk.Button(top_bar, text="+ Thêm liên hệ", command=self.open_add_dialog, bg="#2563eb", fg="white", padx=10, pady=4).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(top_bar, text="Làm mới", command=self.load_contacts, padx=8, pady=4).pack(side=tk.RIGHT, padx=(6, 0))

        # Thanh lọc & sắp xếp
        filter_bar = tk.Frame(self.root, padx=10, pady=6)
        filter_bar.pack(fill=tk.X)

        tk.Checkbutton(
            filter_bar,
            text="Chỉ xem yêu thích",
            variable=self.fav_only_var,
            command=self.load_contacts,
        ).pack(side=tk.LEFT)

        tk.Label(filter_bar, text="   Sắp xếp:").pack(side=tk.LEFT, padx=(10, 4))

        sort_options = [
            ("Tên A -> Z", "name_asc"),
            ("Tên Z -> A", "name_desc"),
            ("Mới nhất", "newest"),
            ("Cũ nhất", "oldest"),
        ]
        for label, val in sort_options:
            tk.Radiobutton(
                filter_bar,
                text=label,
                variable=self.sort_var,
                value=val,
                command=self.load_contacts,
            ).pack(side=tk.LEFT, padx=4)

        # Khung chính chia 2 cột: trái danh sách, phải chi tiết
        main_pane = tk.Frame(self.root, padx=10, pady=6)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Cột trái: Danh sách liên hệ
        left_frame = tk.LabelFrame(main_pane, text="Danh sách liên hệ", padx=8, pady=8)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        list_container = tk.Frame(left_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL)
        self.contact_listbox = tk.Listbox(
            list_container,
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            exportselection=False,
        )
        scrollbar.config(command=self.contact_listbox.yview)

        self.contact_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.contact_listbox.bind("<<ListboxSelect>>", self.on_select_contact)

        # Cột phải: Chi tiết liên hệ & thao tác
        right_frame = tk.LabelFrame(main_pane, text="Chi tiết liên hệ", width=360, padx=12, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)

        self.detail_vars = {
            "full_name": tk.StringVar(value="-"),
            "phone_number": tk.StringVar(value="-"),
            "email": tk.StringVar(value="-"),
            "address": tk.StringVar(value="-"),
            "favorite": tk.StringVar(value="-"),
        }

        fields = [
            ("Họ và tên:", "full_name"),
            ("Số điện thoại:", "phone_number"),
            ("Email:", "email"),
            ("Địa chỉ:", "address"),
            ("Yêu thích:", "favorite"),
        ]

        for label_text, key in fields:
            row = tk.Frame(right_frame, pady=4)
            row.pack(fill=tk.X)
            tk.Label(row, text=label_text, width=13, anchor="w", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(row, textvariable=self.detail_vars[key], anchor="w", justify=tk.LEFT, wraplength=200, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(right_frame, text="Ghi chú:", anchor="w", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(8, 2))
        self.note_text = tk.Text(right_frame, height=5, width=35, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 10), bg="#f8fafc")
        self.note_text.pack(fill=tk.BOTH, expand=True)

        # Các nút thao tác trên liên hệ đang chọn
        btn_frame = tk.Frame(right_frame, pady=10)
        btn_frame.pack(fill=tk.X)

        self.btn_edit = tk.Button(btn_frame, text="Sửa", command=self.open_edit_dialog, state=tk.DISABLED, width=8)
        self.btn_edit.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_delete = tk.Button(btn_frame, text="Xóa", command=self.on_delete_contact, state=tk.DISABLED, bg="#dc2626", fg="white", width=8)
        self.btn_delete.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_fav = tk.Button(btn_frame, text="Yêu thích", command=self.on_toggle_favorite, state=tk.DISABLED, width=12)
        self.btn_fav.pack(side=tk.RIGHT)

        # Thanh trạng thái dưới cùng
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w", padx=8, pady=4).pack(side=tk.BOTTOM, fill=tk.X)

    def load_contacts(self):
        ok, msg, rows = self.controller.list_contacts(
            user_id=self.user_id,
            favorites_only=self.fav_only_var.get(),
            sort_by=self.sort_var.get(),
        )
        if not ok:
            messagebox.showerror("Lỗi", msg)
            self.status_var.set(msg)
            return

        self.contacts_cache = rows
        self.contact_listbox.delete(0, tk.END)

        for item in self.contacts_cache:
            star = "[★] " if item.get("is_favorite") else "[ ] "
            name = item.get("full_name") or ""
            phone = item.get("phone_number") or ""
            self.contact_listbox.insert(tk.END, f"{star}{name:<24} | {phone}")

        self.selected_contact_id = None
        self.selected_is_favorite = False
        self._clear_detail_panel()
        self._set_action_buttons_state(False)
        self.status_var.set(f"Tổng số liên hệ hiển thị: {len(self.contacts_cache)}")

    def on_select_contact(self, event=None):
        selection = self.contact_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < 0 or idx >= len(self.contacts_cache):
            return

        contact_id = self.contacts_cache[idx].get("contact_id")
        ok, msg, detail = self.controller.get_contact_detail(user_id=self.user_id, contact_id=contact_id)
        if not ok or not detail:
            messagebox.showwarning("Thông báo", msg or "Không tải được chi tiết liên hệ.")
            return

        self.selected_contact_id = detail.get("contact_id")
        self.selected_is_favorite = bool(detail.get("is_favorite"))

        self.detail_vars["full_name"].set(detail.get("full_name") or "-")
        self.detail_vars["phone_number"].set(detail.get("phone_number") or "-")
        self.detail_vars["email"].set(detail.get("email") or "-")
        self.detail_vars["address"].set(detail.get("address") or "-")
        self.detail_vars["favorite"].set("Có (★)" if self.selected_is_favorite else "Không")

        self.note_text.config(state=tk.NORMAL)
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", detail.get("note") or "")
        self.note_text.config(state=tk.DISABLED)

        self._set_action_buttons_state(True)
        self.btn_fav.config(text="Bỏ yêu thích" if self.selected_is_favorite else "Đánh dấu ★")

    def _clear_detail_panel(self):
        for key in self.detail_vars:
            self.detail_vars[key].set("-")
        self.note_text.config(state=tk.NORMAL)
        self.note_text.delete("1.0", tk.END)
        self.note_text.config(state=tk.DISABLED)

    def _set_action_buttons_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.btn_edit.config(state=state)
        self.btn_delete.config(state=state)
        self.btn_fav.config(state=state)
        if not enabled:
            self.btn_fav.config(text="Yêu thích")

    def _open_contact_form(self, mode: str, initial_data: dict = None):
        is_edit = mode == "edit"
        win = tk.Toplevel(self.root)
        win.title("Cập nhật liên hệ" if is_edit else "Thêm liên hệ mới")
        win.geometry("420x360")
        win.transient(self.root)
        win.grab_set()

        name_var = tk.StringVar(value=(initial_data.get("full_name") if initial_data else "") or "")
        phone_var = tk.StringVar(value=(initial_data.get("phone_number") if initial_data else "") or "")
        email_var = tk.StringVar(value=(initial_data.get("email") if initial_data else "") or "")
        address_var = tk.StringVar(value=(initial_data.get("address") if initial_data else "") or "")
        fav_var = tk.BooleanVar(value=bool(initial_data.get("is_favorite")) if initial_data else False)

        form = tk.Frame(win, padx=14, pady=12)
        form.pack(fill=tk.BOTH, expand=True)

        rows = [
            ("Họ và tên (*):", name_var),
            ("Số điện thoại (*):", phone_var),
            ("Email:", email_var),
            ("Địa chỉ:", address_var),
        ]

        for label_txt, var in rows:
            r = tk.Frame(form, pady=4)
            r.pack(fill=tk.X)
            tk.Label(r, text=label_txt, width=16, anchor="w").pack(side=tk.LEFT)
            tk.Entry(r, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(form, text="Ghi chú:", anchor="w").pack(fill=tk.X, pady=(6, 2))
        note_entry = tk.Text(form, height=4, wrap=tk.WORD)
        note_entry.pack(fill=tk.BOTH, expand=True)
        if initial_data and initial_data.get("note"):
            note_entry.insert("1.0", initial_data["note"])

        if not is_edit:
            tk.Checkbutton(form, text="Đánh dấu là liên hệ yêu thích", variable=fav_var).pack(anchor="w", pady=(6, 0))

        def on_save():
            full_name = name_var.get()
            phone_number = phone_var.get()
            email = email_var.get()
            address = address_var.get()
            note = note_entry.get("1.0", tk.END).strip()

            if is_edit:
                ok, msg = self.controller.edit_contact(
                    user_id=self.user_id,
                    contact_id=self.selected_contact_id,
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email,
                    address=address,
                    note=note,
                )
            else:
                ok, msg, _ = self.controller.add_contact(
                    user_id=self.user_id,
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email,
                    address=address,
                    note=note,
                    is_favorite=fav_var.get(),
                )

            if not ok:
                messagebox.showerror("Không thể lưu", msg, parent=win)
                return

            messagebox.showinfo("Thành công", msg, parent=win)
            win.destroy()
            self.load_contacts()

        btns = tk.Frame(win, padx=14, pady=10)
        btns.pack(fill=tk.X)
        tk.Button(btns, text="Hủy", command=win.destroy, width=10).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(btns, text="Lưu", command=on_save, bg="#16a34a", fg="white", width=10).pack(side=tk.RIGHT)

    def open_add_dialog(self):
        self._open_contact_form(mode="add")

    def open_edit_dialog(self):
        if self.selected_contact_id is None:
            return
        ok, msg, detail = self.controller.get_contact_detail(user_id=self.user_id, contact_id=self.selected_contact_id)
        if not ok or not detail:
            messagebox.showerror("Lỗi", msg or "Không lấy được thông tin liên hệ để sửa.")
            return
        self._open_contact_form(mode="edit", initial_data=detail)

    def on_delete_contact(self):
        if self.selected_contact_id is None:
            return
        name = self.detail_vars["full_name"].get()
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa liên hệ '{name}' không?",
        )
        if not confirm:
            return

        ok, msg = self.controller.remove_contact(user_id=self.user_id, contact_id=self.selected_contact_id)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return

        messagebox.showinfo("Thành công", msg)
        self.load_contacts()

    def on_toggle_favorite(self):
        if self.selected_contact_id is None:
            return
        new_fav = not self.selected_is_favorite
        ok, msg = self.controller.set_favorite(
            user_id=self.user_id,
            contact_id=self.selected_contact_id,
            is_favorite=new_fav,
        )
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return

        self.status_var.set(msg)
        current_id = self.selected_contact_id
        self.load_contacts()

        # Giữ chọn lại đúng dòng vừa đổi trạng thái yêu thích
        for idx, item in enumerate(self.contacts_cache):
            if item.get("contact_id") == current_id:
                self.contact_listbox.selection_set(idx)
                self.on_select_contact()
                break


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactView(root=root, user_id=1)
    root.mainloop()