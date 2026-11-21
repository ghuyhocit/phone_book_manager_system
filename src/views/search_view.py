# search_view.py
# View (Tkinter): only the screen, no SQL here
# test alone (from the project root): python -m src.views.search_view
# needs the database, user_id = 1

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

PAGE_SIZE = 20
ALL_GROUPS = "All"
SORT_CHOICES = {
    "Name A-Z": "name_asc",
    "Name Z-A": "name_desc",
    "Newest first": "newest",
    "Oldest first": "oldest",
}


class SearchGroupView(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, padding=10)
        self.controller = controller
        self.page = 0
        self.groups = []

        self.build_screen()
        self.load_groups()
        self.load_contacts()

    def build_screen(self):
        # top: search, sort, filter
        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Label(top, text="Search:").pack(side="left")
        self.keyword_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.keyword_var, width=28)
        entry.pack(side="left", padx=5)
        entry.bind("<KeyRelease>", self.on_filter_changed)

        ttk.Label(top, text="Sort:").pack(side="left", padx=(10, 0))
        self.sort_var = tk.StringVar(value="Name A-Z")
        sort_box = ttk.Combobox(top, textvariable=self.sort_var, width=12,
                                values=list(SORT_CHOICES), state="readonly")
        sort_box.pack(side="left", padx=5)
        sort_box.bind("<<ComboboxSelected>>", self.on_filter_changed)

        ttk.Label(top, text="Group:").pack(side="left", padx=(10, 0))
        self.group_var = tk.StringVar(value=ALL_GROUPS)
        self.group_box = ttk.Combobox(top, textvariable=self.group_var, width=14,
                                      state="readonly")
        self.group_box.pack(side="left", padx=5)
        self.group_box.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # table
        self.table = ttk.Treeview(self, columns=("name", "phone", "email", "groups"),
                                  show="headings", height=14)
        self.table.heading("name", text="Full name")
        self.table.heading("phone", text="Phone")
        self.table.heading("email", text="Email")
        self.table.heading("groups", text="Groups")
        self.table.column("name", width=180)
        self.table.column("phone", width=120)
        self.table.column("email", width=180)
        self.table.column("groups", width=160)
        self.table.pack(fill="both", expand=True, pady=8)

        self.message_label = ttk.Label(self, text="", foreground="gray")
        self.message_label.pack()

        # bottom: buttons and paging
        bottom = ttk.Frame(self)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Manage groups", command=self.open_group_manager).pack(side="left")
        ttk.Button(bottom, text="Add to group", command=self.add_to_group).pack(side="left", padx=5)
        ttk.Button(bottom, text="Remove from group", command=self.remove_from_group).pack(side="left")

        self.next_button = ttk.Button(bottom, text="Next >", command=self.next_page)
        self.next_button.pack(side="right")
        self.page_label = ttk.Label(bottom, text="Page 1")
        self.page_label.pack(side="right", padx=8)
        self.prev_button = ttk.Button(bottom, text="< Previous", command=self.prev_page)
        self.prev_button.pack(side="right")

    # ----- events -----
    def on_filter_changed(self, event=None):
        self.page = 0
        self.load_contacts()

    def next_page(self):
        self.page += 1
        self.load_contacts()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_contacts()

    # ----- load data -----
    def get_selected_group_id(self):
        name = self.group_var.get()
        for group in self.groups:
            if group["group_name"] == name:
                return group["group_id"]
        return None  # "All"

    def load_groups(self):
        success, result = self.controller.get_groups()
        if not success:
            messagebox.showerror("Error", result)
            return
        self.groups = result
        names = [ALL_GROUPS]
        for group in self.groups:
            names.append(group["group_name"])
        self.group_box["values"] = names
        if self.group_var.get() not in names:
            self.group_var.set(ALL_GROUPS)

    def load_contacts(self):
        success, result = self.controller.search(
            self.keyword_var.get(),
            self.get_selected_group_id(),
            SORT_CHOICES[self.sort_var.get()],
            self.page,
            PAGE_SIZE,
        )
        if not success:
            messagebox.showerror("Error", result)
            return
        contacts, has_next = result

        # empty page (for example after deleting), go back one page
        if len(contacts) == 0 and self.page > 0:
            self.page -= 1
            self.load_contacts()
            return

        for row in self.table.get_children():
            self.table.delete(row)
        for contact in contacts:
            self.table.insert("", "end", iid=str(contact["contact_id"]), values=(
                contact["full_name"],
                contact["phone_number"],
                contact["email"] or "",
                contact["group_names"] or "",
            ))

        if len(contacts) == 0:
            if self.keyword_var.get().strip() != "":
                self.message_label.config(text="No contacts found")
            elif self.get_selected_group_id() is not None:
                self.message_label.config(text="No contacts in this category")
            else:
                self.message_label.config(text="No contacts yet")
        else:
            self.message_label.config(text="")

        self.page_label.config(text="Page " + str(self.page + 1))
        if self.page > 0:
            self.prev_button.state(["!disabled"])
        else:
            self.prev_button.state(["disabled"])
        if has_next:
            self.next_button.state(["!disabled"])
        else:
            self.next_button.state(["disabled"])

    def get_selected_contact_id(self):
        selected = self.table.selection()
        if len(selected) == 0:
            messagebox.showinfo("Info", "Please select a contact first.")
            return None
        return int(selected[0])

    # ----- add / remove group -----
    def choose_groups(self, title, groups, allow_many):
        # popup with a list of groups, returns the chosen group ids
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.grab_set()

        if allow_many:
            mode = "multiple"
        else:
            mode = "browse"
        listbox = tk.Listbox(popup, selectmode=mode, exportselection=False, height=8, width=30)
        for group in groups:
            listbox.insert("end", group["group_name"])
        listbox.pack(padx=10, pady=10)

        chosen = []

        def save():
            if len(listbox.curselection()) == 0:
                messagebox.showinfo("Info", "Please choose a group first.", parent=popup)
                return
            for index in listbox.curselection():
                chosen.append(groups[index]["group_id"])
            popup.destroy()

        buttons = ttk.Frame(popup)
        buttons.pack(pady=(0, 10))
        ttk.Button(buttons, text="Save", command=save).pack(side="left", padx=4)
        ttk.Button(buttons, text="Cancel", command=popup.destroy).pack(side="left", padx=4)

        self.wait_window(popup)
        return chosen

    def add_to_group(self):
        contact_id = self.get_selected_contact_id()
        if contact_id is None:
            return
        if len(self.groups) == 0:
            if messagebox.askyesno("No groups", "You have no groups yet. Create one now?"):
                self.open_group_manager()
            return

        group_ids = self.choose_groups("Add to group", self.groups, True)
        if len(group_ids) == 0:
            return
        success, message = self.controller.assign_to_groups(contact_id, group_ids)
        if success:
            messagebox.showinfo("Done", message)
        else:
            messagebox.showerror("Error", message)
        self.load_contacts()

    def remove_from_group(self):
        contact_id = self.get_selected_contact_id()
        if contact_id is None:
            return
        success, result = self.controller.get_groups_of_contact(contact_id)
        if not success:
            messagebox.showerror("Error", result)
            return
        if len(result) == 0:
            messagebox.showinfo("Info", "This contact is not in any group.")
            return

        group_ids = self.choose_groups("Remove from group", result, False)
        if len(group_ids) == 0:
            return
        success, message = self.controller.remove_from_group(contact_id, group_ids[0])
        if success:
            messagebox.showinfo("Done", message)
        else:
            messagebox.showerror("Error", message)
        self.load_contacts()

    # ----- manage groups (create / edit / delete) -----
    def open_group_manager(self):
        window = tk.Toplevel(self)
        window.title("Manage groups")
        window.grab_set()

        listbox = tk.Listbox(window, height=10, width=32, exportselection=False)
        listbox.pack(padx=10, pady=10)

        def fill_list():
            self.load_groups()
            listbox.delete(0, "end")
            for group in self.groups:
                listbox.insert("end", group["group_name"])

        def get_selected_group():
            selected = listbox.curselection()
            if len(selected) == 0:
                messagebox.showinfo("Info", "Please select a group.", parent=window)
                return None
            return self.groups[selected[0]]

        def create():
            name = simpledialog.askstring("Create group", "Group name:", parent=window)
            if name is None:
                return
            success, message = self.controller.create_group(name)
            if success:
                fill_list()
            else:
                messagebox.showerror("Error", message, parent=window)

        def edit():
            group = get_selected_group()
            if group is None:
                return
            name = simpledialog.askstring("Edit group", "New name:", parent=window,
                                          initialvalue=group["group_name"])
            if name is None:
                return
            success, message = self.controller.edit_group(group["group_id"], name)
            if success:
                fill_list()
                self.load_contacts()
            else:
                messagebox.showerror("Error", message, parent=window)

        def delete():
            group = get_selected_group()
            if group is None:
                return
            sure = messagebox.askyesno(
                "Confirm",
                "Delete group '" + group["group_name"] + "'?\n"
                "The contacts in this group will NOT be deleted.",
                parent=window)
            if not sure:
                return
            success, message = self.controller.delete_group(group["group_id"])
            if success:
                fill_list()
                self.load_contacts()
            else:
                messagebox.showerror("Error", message, parent=window)

        buttons = ttk.Frame(window)
        buttons.pack(pady=(0, 10))
        ttk.Button(buttons, text="Create", command=create).pack(side="left", padx=4)
        ttk.Button(buttons, text="Edit", command=edit).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete", command=delete).pack(side="left", padx=4)
        ttk.Button(buttons, text="Close", command=window.destroy).pack(side="left", padx=4)

        fill_list()


if __name__ == "__main__":
    from src.controllers.category_controller import SearchGroupController

    root = tk.Tk()
    root.title("Search + Group")
    view = SearchGroupView(root, SearchGroupController(user_id=1))
    view.pack(fill="both", expand=True)
    root.mainloop()
