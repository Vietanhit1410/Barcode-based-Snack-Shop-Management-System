import json
import tkinter as tk
from datetime import datetime
from time import sleep
from tkinter import ttk, messagebox
import threading


from Entity.Invoice import Invoice
from config.config import *
from controllers.customer_controller import CustomerController
from controllers.invoice_controller import InvoiceController
from controllers.invoice_detail_controller import InvoiceDetailController
from controllers.product_controller import ProductController
from controllers.thread import ThreadController
from models.product_model import ProductModel


def take_info_cart():
    try:
        with open(PATH_CART, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Lỗi đọc giỏ hàng từ file trong VIEW: {e}")
        return []



class InvoiceOrderView:
    def __init__(self, parent):
        self.info_customer = None
        self.point_entry = None
        self.customer_name = "Khách lẻ"
        self.customer_info_label = ""
        self.root = parent  # Đối tượng Tk chính
        self.root.title("Invoice Management System")
        self.root.state("zoomed")
        self.invoice_detail_controller = InvoiceDetailController()
        self.invoice_controller = InvoiceController()
        self.cart = []  # Giỏ hàng (danh sách các sản phẩm đã chọn)
        self.create_widgets()
        self.product_list.bind("<ButtonRelease-1>", self.on_row_selected)
        self.point = 0
        self.thread = ThreadController()
        self.thread.start_scanning()


        thread = threading.Thread(target=self.confim_change, daemon=True)
        thread.start()

    def confim_change(self):
        while True:
            with open(PATH_RECOGNIZE, "r") as file:
                if file.read() == "True" :
                    self.cart = take_info_cart()
                    for i in self.cart:
                        self.add_product_to_cart(i[INVOICE_DETAIL_PRODUCT_NAME],
                                                 i[INVOICE_DETAIL_QUANTITY],
                                                 i[INVOICE_DETAIL_PRICE])
            sleep(0.3)

    def create_widgets(self):
        # Chia giao diện thành 2 cột (có tỉ lệ bằng nhau)
        self.root.grid_columnconfigure(0, weight=1, uniform="equal")
        self.root.grid_columnconfigure(1, weight=1, uniform="equal")
        self.root.grid_rowconfigure(0, weight=1)

        # Left Frame (Giỏ hàng)
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Right Frame (Hóa đơn)
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Label quét mã sản phẩm
        self.scan_label = ttk.Label(self.left_frame, text="Giỏ hàng", font=("Arial", 14))
        self.scan_label.grid(row=0, column=0, pady=10)



        # Danh sách sản phẩm
        self.product_list = ttk.Treeview(self.left_frame, columns=("Tên sản phẩm", "Số lượng", "Giá"), show="headings", height=10)
        self.product_list.heading("Tên sản phẩm", text="Tên sản phẩm")
        self.product_list.heading("Số lượng", text="Số lượng")
        self.product_list.heading("Giá", text="Giá")
        self.product_list.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")

        # Ô nhập số điện thoại và nút tìm kiếm trên cùng một hàng
        self.phone_label = ttk.Label(self.left_frame, text="Số điện thoại:", font=("Arial", 12))
        self.phone_label.grid(row=3, column=0, sticky="w", padx=5, pady=(10, 0))

        self.search_frame = ttk.Frame(self.left_frame)
        self.search_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 0))

        self.phone_entry = ttk.Entry(self.search_frame, font=("Arial", 12), width=15)
        self.phone_entry.pack(side="left", padx=(0, 5))  # Khoảng cách nhỏ giữa Entry và Button

        self.search_customer_button = ttk.Button(self.search_frame, text="Tìm kiếm", command=self.search_customer_num)
        self.search_customer_button.pack(side="left")




        # Nút Xác nhận để hiển thị hóa đơn
        self.confirm_button = ttk.Button(self.left_frame, text="Xác nhận", command=self.show_invoice)
        self.confirm_button.grid(row=7, column=0, padx=5, pady=10)

        # Cấu hình để các cột và hàng có thể co giãn
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=0)
        self.left_frame.grid_rowconfigure(2, weight=1)  # Bảng sản phẩm có thể giãn ra
        self.left_frame.grid_rowconfigure(3, weight=0)

        # Cấu hình co giãn
        self.left_frame.grid_rowconfigure(4, weight=0)
        self.left_frame.grid_rowconfigure(6, weight=0)



        # Bên phải (hiển thị hóa đơn)
        self.invoice_label = ttk.Label(self.right_frame, text="Hóa đơn", font=("Arial", 14))
        self.invoice_label.grid(row=0, column=0, pady=10)

        self.invoice_text = tk.Text(self.right_frame, width=40, height=15, wrap=tk.WORD, font=("Arial", 12))
        self.invoice_text.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)  # Căn giữa theo chiều ngang
        self.right_frame.grid_rowconfigure(1, weight=1)  # Căn giữa theo chiều dọc
        # Nút "Xuất Bill"

        # Thay đổi trong create_widgets()
        self.print_button = ttk.Button(self.right_frame, text="Xuất Bill",
                                       command=lambda: threading.Thread(target=self.export_bill, daemon=True).start())
        self.print_button.grid(row=2, column=0, pady=10)

        # Cấu hình để các cột và hàng có thể co giãn
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)  # Hóa đơn có thể giãn ra
        self.right_frame.grid_rowconfigure(2, weight=0)

        # Cấu hình cột cho các frame
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)


    def search_customer_num(self):
        # Label hiển thị kết quả tìm kiếm
        if self.phone_entry.get() is not None :
            self.customer_controller = CustomerController()
            result = self.customer_controller.search_customer(self.phone_entry.get())[1]
            if result:
                self.info_customer = list(result[0])

            if self.info_customer:
                self.customer_name = self.info_customer[1]
                string_info = f"Customer name : {self.info_customer[1]}\nRoyality points: {self.info_customer[4]}"
                self.customer_info_label = ttk.Label(self.left_frame, text=f"{string_info}", font=("Arial", 12, "bold"),
                                                     foreground="blue", anchor="w")
                self.customer_info_label.grid(row=5, column=0, padx=5, pady=(5, 10), sticky="w")

                self.use_point_frame = ttk.Frame(self.left_frame)
                self.use_point_frame.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 0))

                self.label_point_use = ttk.Label(self.use_point_frame, text="Points want use", font=("Arial", 12),
                                                 width=15)
                self.label_point_use.pack(side="left", padx=(0, 5))

                self.point_entry = ttk.Entry(self.use_point_frame, font=("Arial", 12), width=15)
                self.point_entry.pack(side="left", padx=(0, 5))

            else:
                string_info = f"Cant found customer"
                self.customer_info_label = ttk.Label(self.left_frame, text=f"{string_info}", font=("Arial", 12, "bold"),
                                                     foreground="blue", anchor="w")
                self.customer_info_label.grid(row=5, column=0, padx=5, pady=(5, 10), sticky="w")



    def add_product_to_cart(self, product_name, quantity, price):

        for item in self.cart:
            if item[INVOICE_DETAIL_PRODUCT_NAME] == product_name:
                item[INVOICE_DETAIL_QUANTITY] = quantity
                item[INVOICE_DETAIL_PRICE] = item[INVOICE_DETAIL_QUANTITY] * price
                self.update_product_list()
                return
        self.update_product_list()

    def update_product_list(self):
        # Xóa toàn bộ dữ liệu cũ trong `Treeview`
        for item2 in self.product_list.get_children():
            self.product_list.delete(item2)

        # Thêm dữ liệu mới từ `self.cart`
        for item in self.cart:
            self.product_list.insert("", "end", values=(item["product_name"], item["quantity"], item["price"]))

    def show_invoice(self):
        try:
            if self.point_entry is not None:
                self.point = int(self.point_entry.get().strip())
        except ValueError:
            self.point = 0

        """Hiển thị hóa đơn và căn giữa trong Frame."""
        self.invoice_text.delete(1.0, tk.END)  # Xóa nội dung cũ

        if not self.cart:
            self.invoice_text.insert(tk.END, "Giỏ hàng trống!\n")
            return

        total_price = 0
        width = 40  # Chiều rộng nội dung hóa đơn

        invoice_content = " HÓA ĐƠN ".center(width, "=") + "\n"
        invoice_content += "{:<20} {:<8} {:<12}\n".format("Tên sản phẩm", "SL", "Thành tiền").center(width)
        invoice_content += "-" * width + "\n"

        for item in self.cart:
            name = item[INVOICE_DETAIL_PRODUCT_NAME]
            quantity = item[INVOICE_DETAIL_QUANTITY]
            price = item[INVOICE_DETAIL_PRICE]
            total_price += price  # Cộng dồn tổng tiền

            invoice_content += "{:<20} {:<8} {:<12,}\n".format(name, quantity, price).center(width)
        if self.point > 0:
            invoice_content += f"{'Tiền gốc:':<20} {total_price:,} VND".center(width) + "\n"
            invoice_content += f"{'Điểm thưởng:':<20} {self.point} ".center(width) + "\n"
            total_price -= (self.point *1000)

        invoice_content += "-" * width + "\n"
        invoice_content += f"{'Tổng tiền:':<20} {total_price:,} VND".center(width) + "\n"

        self.invoice_text.insert(tk.END, invoice_content)  # Hiển thị hóa đơn

        self.save_bill_in_db()

    def export_bill(self):
        """Lưu hóa đơn vào file .txt và làm mới giao diện"""
        content = self.invoice_text.get("1.0", "end-1c")
        now = datetime.now().strftime("%Y%m%d_%H%M%S")  # Tạo mã thời gian
        folder_path = r"D:\BTL_Python_done1603\resource\Invoice"  # Đường dẫn thư mục
        file_name = f"{now}.txt"
        file_path = os.path.join(folder_path, file_name)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            # Hiển thị thông báo trên luồng chính (Tránh lỗi giao diện bị đứng)
            self.root.after(0, lambda: messagebox.showinfo("Thành công", f"Hóa đơn đã được lưu: {file_path}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi lưu hóa đơn: {str(e)}"))

        # Làm mới giao diện trên luồng chính
        self.root.after(0, self.reset_invoice_ui)

    def reset_invoice_ui(self):
            # Dừng và khởi động lại quá trình quét
            self.thread.stop_scanning()

            self.root.destroy()  # Đóng cửa sổ hiện tại
            new_root = tk.Tk()  # Tạo cửa sổ mới
            InvoiceOrderView(new_root)  # Khởi tạo lại ứng dụng
            new_root.mainloop()  # Chạy lại vòng lặp

    def save_bill_in_db(self):
        if self.info_customer :
            self.info_customer[4] = self.info_customer[4] - self.point
            for item in self.cart:
                self.product_model = ProductModel()
                result = self.product_model.search_product(item[INVOICE_DETAIL_PRODUCT_NAME])[0]
                point = int(result[6]) * item[INVOICE_DETAIL_QUANTITY]
                self.info_customer[4] += point
                print(*self.info_customer[:5])
            self.customer_controller.update_customer(*self.info_customer[:5])

        food_quantity = 0
        drink_quantity = 0
        total_price_food = 0
        total_price_drink = 0
        invoice_code = ""
        for item in self.cart:
            invoice_code = item[INVOICE_DETAIL_INVOICE_CODE]
            print(item)
            item[INVOICE_DETAIL_CUSTOMER_NAME] = self.customer_name
            self.invoice_detail_controller.add_invoice_detail(invoice_code,item[INVOICE_DETAIL_PRODUCT_NAME],item[INVOICE_DETAIL_PRODUCT_TYPE],
                                                              item[INVOICE_DETAIL_PRODUCT_NAME],item[INVOICE_DETAIL_PRICE],item[INVOICE_DETAIL_SUBTOTAL],
                                                              self.customer_name,item[INVOICE_DETAIL_PRODUCT_ID_BARCODE])
            if item[INVOICE_DETAIL_PRODUCT_TYPE] == "drink":
                drink_quantity += item[INVOICE_DETAIL_QUANTITY]
                total_price_drink +=item[INVOICE_DETAIL_PRICE]
            if item[INVOICE_DETAIL_PRODUCT_TYPE] == "food":
                food_quantity+= item[INVOICE_DETAIL_QUANTITY]
                total_price_food+=item[INVOICE_DETAIL_PRICE]
        total_price = int(total_price_food) + int(total_price_drink)
        with open(r"D:\BTL_Python_done1603\resource\user.txt", "r") as file:
            employee_code = file.read().strip(",")[0]
        invoice = Invoice(employee_code, self.customer_name,drink_quantity,
                          food_quantity,total_price_drink,total_price_food,total_price - (self.point * 1000),invoice_code)
        self.invoice_controller.update_invoice_scan(invoice)


#     đây là hàm khi án vào có quyền sửa
    def on_row_selected(self, event):
        selected_item = self.product_list.focus()  # Lấy ID của hàng được chọn
        values = self.product_list.item(selected_item, 'values')  # Lấy dữ liệu hàng
        if not values:
            return

        # Mở cửa sổ popup chỉnh sửa
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Chỉnh sửa sản phẩm")
        edit_window.geometry("300x200")

        ttk.Label(edit_window, text="Tên sản phẩm:").pack(pady=5)
        name_label = ttk.Label(edit_window, text=values[0])  # Hiển thị tên sản phẩm
        name_label.pack()

        ttk.Label(edit_window, text="Số lượng mới:").pack(pady=5)
        quantity_entry = ttk.Entry(edit_window)
        quantity_entry.insert(0, values[1])  # Điền số lượng cũ vào
        quantity_entry.pack()

        def update_product():
            new_quantity = quantity_entry.get()
            if not new_quantity.isdigit() or int(new_quantity) < 0:
                messagebox.showerror("Lỗi", "Số lượng không hợp lệ!")
                return

            new_quantity = int(new_quantity)
            if new_quantity == 0:
                self.remove_product(values[0])  # Xóa sản phẩm nếu số lượng = 0
            else:
                self.update_quantity(values[0], new_quantity)

            edit_window.destroy()  # Đóng cửa sổ chỉnh sửa


        def delete_product():
            self.remove_product(values[0])
            edit_window.destroy()

        ttk.Button(edit_window, text="Cập nhật", command=update_product).pack(pady=5)
        ttk.Button(edit_window, text="Xóa", command=delete_product).pack(pady=5)
        ttk.Button(edit_window, text="Hủy", command=edit_window.destroy).pack(pady=5)

    def update_quantity(self, product_name, new_quantity):
        for item in self.cart:
            if item[INVOICE_DETAIL_PRODUCT_NAME] == product_name:
                item[INVOICE_DETAIL_QUANTITY] = new_quantity
                item[INVOICE_DETAIL_PRICE] = new_quantity * (
                            item[INVOICE_DETAIL_PRICE] / int(self.product_list.item(self.product_list.focus(), 'values')[1]))
                break
        self.update_product_list()

    def remove_product(self, product_name):
        self.cart = [item for item in self.cart if item[INVOICE_DETAIL_PRODUCT_NAME] != product_name]
        self.update_product_list()

#
# root = tk.Tk()
# InvoiceOrderView(root)
# root.mainloop()