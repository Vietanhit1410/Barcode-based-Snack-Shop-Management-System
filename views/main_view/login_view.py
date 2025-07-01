import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from controllers.employee_controller import EmployeeController
from models.employe_model import EmployeeModel
from views.main_view.home import MainApp


class LoginView:
    def __init__(self, parent):
        self.model_employee = EmployeeModel()
        self.root = parent
        self.root.title("Milktea Store Management")
        self.root.state("zoomed")  # Toàn màn hình
        self.root.configure(bg="#daeaf6")  # màu nền nhẹ nhàng như sương mai

        # Tiêu đề lớn – uy nghi
        title = tk.Label(
            self.root, text="Milktea Store Management",
            font=("Segoe UI", 28, "bold"), bg="#daeaf6", fg="#0d3b66"
        )
        title.pack(pady=40)

        # Khung chính – như ngọc ấn giữa long đình
        frame = tk.Frame(self.root, bg="white", bd=0, relief="flat")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=360)

        # Bóng đổ bằng canvas (giả lập shadow)
        shadow = tk.Frame(self.root, bg="#b0c4de")
        shadow.place(relx=0.5 + 0.01, rely=0.5 + 0.01, anchor="center", width=500, height=360)

        # Nhúng frame lên trên bóng đổ
        frame.lift()

        # Nhãn – Tài khoản
        tk.Label(frame, text=" Tên đăng nhập", font=("Segoe UI", 13, "bold"),
                 bg="white", anchor="w").pack(fill="x", padx=30, pady=(25, 5))
        self.entry_username = ttk.Entry(frame, font=("Segoe UI", 12))
        self.entry_username.pack(fill="x", padx=30, pady=5, ipady=6)

        # Nhãn – Mật khẩu
        tk.Label(frame, text=" Mật khẩu", font=("Segoe UI", 13, "bold"),
                 bg="white", anchor="w").pack(fill="x", padx=30, pady=(20, 5))
        self.entry_password = ttk.Entry(frame, show="*", font=("Segoe UI", 12))
        self.entry_password.pack(fill="x", padx=30, pady=5, ipady=6)

        # Nút đăng nhập – vàng son
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Royal.TButton",
                        font=("Segoe UI", 12, "bold"),
                        padding=10,
                        background="#007acc",
                        foreground="white")
        style.map("Royal.TButton",
                  background=[("active", "#005f99")],
                  foreground=[("active", "white")])

        login_btn = ttk.Button(frame, text=" Đăng nhập", style="Royal.TButton", command=self.verify_account)
        login_btn.pack(pady=30, ipadx=10)

    def get_login_info(self):
        return self.entry_username.get(), self.entry_password.get()

    def verify_account(self):
        user = self.model_employee.login(*self.get_login_info())
        if user:
            with open(r"D:\BTL_Python_done1603\resource\user.txt", "w") as file:
                file.write(f"{user[1]},{user[2]},{user[8]}")
            self.root.destroy()
            root_main = tk.Tk()
            MainApp(root_main)
            root_main.mainloop()
        else:
            self.show_error("Sai thông tin", "Tên đăng nhập hoặc mật khẩu không chính xác!")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)
