import tkinter as tk
from src.views.login_view import LoginView

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginView(root)
    root.mainloop()