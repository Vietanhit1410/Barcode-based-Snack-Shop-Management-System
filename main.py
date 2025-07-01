import sys
import tkinter as tk

from views.main_view.admin_view import AdminDashboard
from views.main_view.home import MainApp
from views.main_view.login_view import LoginView

def run():
    root = tk.Tk()  # Tạo cửa sổ Tkinter
    with open(r"D:\BTL_Python_done1603\resource\user.txt", "r") as file:
        data = file.read().strip()
    if data == "None":
        app = LoginView(root)
        root.mainloop()
    else:
        MainApp(root)
        root.mainloop()


if __name__ == "__main__":
    run()




