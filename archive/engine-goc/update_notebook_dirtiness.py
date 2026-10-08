"""
Update solution.ipynb to prominently feature the Data Dirtiness Audit.
"""

import sys, os
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

sys.stdout.reconfigure(encoding='utf-8')

nb_path = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\solution.ipynb"
nb = nbformat.read(nb_path, as_version=4)

dirtiness_md = """## 🚨 KIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU: BỘ DỮ LIỆU 'BẨN' VÀ SAI LỆCH ĐẾN MỨC NÀO?
> **Phát hiện cốt lõi từ Firstmate & Đội ngũ Chuyên viên Phân tích Dữ liệu**
> 
> Trong thực tế khoa học dữ liệu, việc vội vàng xây dựng mô hình dự báo (Machine Learning) khi chưa kiểm toán độ "sạch" của dữ liệu là cạm bẫy lớn nhất dẫn đến hiện tượng **rò rỉ dữ liệu (data leakage)** và **sai lệch hệ thống (systemic bias)**.
> 
> Qua quá trình liên kết và đối soát 14 bảng quan hệ với hơn 714,000 dòng giao dịch, chúng tôi phát hiện **6 cạm bẫy dữ liệu nghiêm trọng**:
> 
> 1. ⏳ **Nghịch lý vi phạm nhân quả (Time-Travel Paradox)**:
>    - **477,453 đơn hàng (73.80%)** có ngày đặt hàng (`order_date`) diễn ra **TRƯỚC** ngày khách hàng tạo tài khoản (`signup_date`) từ vài tháng đến 8 năm!
>    - *Hệ quả*: Nếu kỹ sư sử dụng biến `customer_tenure = order_date - signup_date` để huấn luyện mô hình, 73.8% giá trị sẽ mang dấu âm vô lý!
> 
> 2. 💸 **Cú sốc bán dưới giá vốn (Negative Gross Margin & Dumping)**:
>    - Trong `products.csv`, 100% sản phẩm có `price >= cogs` (không có sản phẩm nào niêm yết lỗ).
>    - Nhưng trong `order_items.csv`, có tới **133,052 sản phẩm (18.62%)** bị bán với `unit_price < cogs`, tập trung mạnh vào các năm lẻ (2013, 2015, 2017, 2019, 2021) do chiến lược giảm giá sâu.
>    - Điều này dẫn đến **382 ngày (~10% chuỗi thời gian)** doanh thu bị âm gộp (`Revenue < COGS`), gây tổng lỗ lũy kế **-192.22 triệu VNĐ**!
> 
> 3. ⚠️ **Bẫy định nghĩa Doanh thu (Gross Bookings vs Net Cash)**:
>    - Cột `Revenue` trong `sales.csv` thực chất là **Tổng doanh số gộp trước chiết khấu** (`sum(quantity * unit_price)`), với hệ số tương quan hoàn hảo $r = 1.000000$ và $MAE = 0.00$.
>    - Trong khi đó, số tiền thực tế khách hàng thanh toán tại `payments.csv` là **Doanh thu thuần sau chiết khấu** (`sum(quantity * unit_price - discount_amount)`).
> 
> 4. 📦 **Phí vận chuyển "bị lãng quên" trong đối soát thanh toán**:
>    - 100% số tiền thanh toán tại `payments.csv` chỉ thu đúng tiền hàng Net.
>    - Nếu đối soát `payment_value == items_net + shipping_fee`, sẽ có **402,126 đơn hàng (62.16%)** bị coi là "lệch tiền", vì phí vận chuyển trong `shipments.csv` không hề được thu từ khách hàng!
> 
> 5. 👻 **Giao dịch "ma" (Phantom fulfillment)**:
>    - **564 đơn hàng** được gắn cờ `delivered` (524 đơn), `returned` (29 đơn) hoặc `shipped` (11 đơn) nhưng hoàn toàn không tồn tại bất kỳ dòng ghi nhận nào trong `shipments.csv`.
> 
> 6. 🚫 **Khoảng trống chuỗi thời gian (Missing 181 Days of Web Traffic)**:
>    - Bảng `sales.csv` và `orders.csv` bắt đầu từ ngày `2012-07-04`.
>    - Bảng `web_traffic.csv` lại chỉ bắt đầu từ `2013-01-01`.
>    - 181 ngày đầu tiên của năm 2012 hoàn toàn khuyết thiếu dữ liệu truy cập web, nếu ghép nối sơ sài (inner join) sẽ làm mất trắng nửa năm dữ liệu ban đầu!"""

dirtiness_code = """# Thực hiện kiểm toán độ 'bẩn' và đối soát dữ liệu đa bảng
import pandas as pd
import numpy as np

audit_df = pd.read_csv('data/data_dirtiness_audit.csv')
print("KẾT QUẢ KIỂM TOÁN ĐỘ 'BẨN' VÀ SAI LỆCH CỦA BỘ DỮ LIỆU:")
display(audit_df[['table', 'issue_type', 'count', 'pct', 'severity', 'description']])

# Kiểm tra nhanh nghịch lý thời gian order_date < signup_date
orders_df = pd.read_csv('dataset/orders.csv', usecols=['order_id', 'order_date', 'customer_id'])
cust_df = pd.read_csv('dataset/customers.csv', usecols=['customer_id', 'signup_date'])
m = orders_df.merge(cust_df, on='customer_id')
time_paradox = (pd.to_datetime(m['order_date']) < pd.to_datetime(m['signup_date'])).sum()
print(f"\\n=> Số lượng đơn hàng vi phạm nhân quả (Order trước Signup): {time_paradox:,} / {len(m):,} ({time_paradox/len(m)*100:.2f}%)")
"""

# Insert near cell 2 or 3 (right after imports and setup)
nb.cells.insert(3, new_markdown_cell(dirtiness_md))
nb.cells.insert(4, new_code_cell(dirtiness_code))

nbformat.write(nb, nb_path)
print(f"solution.ipynb updated with Data Dirtiness Audit. Total cells now: {len(nb.cells)}")
