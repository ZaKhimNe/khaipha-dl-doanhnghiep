# Giao việc cho Claude Code: sửa code EDA và gộp thành notebook

> Dán nguyên file này cho Claude Code, chạy ở thư mục gốc repo `ds317-doanhnghiep`.

## 0. Bối cảnh (đọc trước)

- Đồ án DS317, nhóm 8: dự báo doanh thu **tuần × danh mục** (4 danh mục: Casual, GenZ, Outdoor, Streetwear) cho TMĐT thời trang, data Datathon 2026 Round 1 ở `data/raw/datathon-2026-round-1/`.
- Giai đoạn hiện tại: **EDA để cả nhóm hiểu dữ liệu**. Mỗi thành viên phụ trách vài bảng và viết "từ điển dữ liệu" + giải thích chart. Notebook phải giúp người đọc hiểu, không phải chỉ sinh ảnh đẹp.
- Code hiện có: thư viện chung `src/ds317/` (paths, data, panel, viz) và các script trong `scripts/eda`, `scripts/audit`. Đọc `README.md` trước.

## 1. Ràng buộc bắt buộc

1. KHÔNG sửa hay xoá gì trong `data/raw/`. KHÔNG xoá file nào: file cũ chuyển vào `archive/` bằng `mv -n`.
2. KHÔNG đụng `notebooks/thanh-vien/Quyen/` (có SHA-256 đối soát).
3. Logic dùng chung đặt trong `src/ds317/`, notebook chỉ gọi hàm. Không chép trùng code giữa các notebook.
4. Nhãn, tiêu đề chart bằng tiếng Việt. Đơn vị tiền: **Triệu VNĐ** (giá trị gốc là đồng, chia 1e6).
5. Mỗi notebook chạy được từ đầu đến cuối bằng `.venv` của repo: `jupyter nbconvert --to notebook --execute --inplace <file>`. Lưu output (ảnh, bảng) ngay trong notebook để người không chạy code vẫn đọc được.
6. Ảnh lưu vào `outputs/eda/<tên notebook>/`, bảng số vào `outputs/eda/<tên notebook>/tables/`.
7. KHÔNG tự viết kết luận phân tích thay nhóm. Ô giải thích để dạng mẫu có chỗ trống (xem mục 3). Chỉ được in số liệu tính từ data.
8. Commit chỉ khi được yêu cầu.

## 2. Sửa thư viện chung trước (`src/ds317/`)

| # | File | Sửa gì | Vì sao |
|---|---|---|---|
| A | `panel.py` | Bỏ `impute="median"` mặc định. Cột **đếm/tổng** (return_count, total_refund_amount, review_count, shipments_dispatched, order_count, total_units_ordered, total_discounts_applied) ngày không có dữ liệu → điền **0**. Cột **traffic** (181 ngày cuối 2012 không có) → giữ **NaN**. Cột **trung bình** (avg_rating, avg_shipping_fee, avg_delivery_lead_days, avg_unit_price) → giữ NaN. Thêm tham số `impute=None` mặc định, ghi rõ docstring. | Điền trung vị cho ngày không có trả hàng (27 ngày) / review (8 ngày) / traffic (181 ngày) tạo ra số giả, làm sai eda_04/05/07/08 |
| B | `data.py` | Trong `order_lines()` thêm cột: `cogs_line = quantity * products.cogs`, `is_cancelled = order_status == "cancelled"`. Giữ `gross`, `net`. | Cần tính biên lợi nhuận **thực tế** và tách đơn huỷ |
| C | `data.py` (hàm mới) | `revenue_daily(lines, kind)` với `kind ∈ {"gross_all", "gross_excl_cancelled", "net_excl_cancelled"}`; `weekly_category(lines, kind, week="W-SUN")` trả bảng `week_start, category, revenue, cogs, units, n_orders`, **điền 0** cho tuần × danh mục không bán, cột `is_partial_week` cho tuần đầu/cuối thiếu ngày. | Biến mục tiêu của đồ án, chưa có ở đâu |
| D | `profile.py` (mới) | `profile_table(df, name)` trả 1 dòng/cột: tên cột, kiểu, % trống, số giá trị khác nhau, min, max, 3 giá trị ví dụ. `key_coverage(child, parent, key)` trả % giá trị khoá của bảng con có trong bảng cha. | Phục vụ từ điển dữ liệu |

Quy ước tuần: tuần bắt đầu **Thứ Hai** (dùng `W-SUN` của pandas = tuần kết thúc Chủ nhật). Ghi quy ước này vào docstring và README.

## 3. Khuôn mẫu cho MỌI notebook

```
# <Số>. <Tên notebook>
**Mục tiêu:** <1 câu>
**Bảng dữ liệu dùng:** <danh sách>
**Người phụ trách viết giải thích:** <để trống>

## <Câu hỏi 1, viết dạng câu hỏi>
[code: tính + vẽ, lưu ảnh]
[code: in "Số liệu chính" – 3–5 con số tính từ data mà người đọc cần để kết luận]
> **Đọc chart (người phụ trách điền):**
> 1. Kết luận 1 câu có số: …
> 2. Số kiểm tra lại từ data: …
> 3. Điều lạ / chưa giải thích được: …
> 4. Ảnh hưởng đến tiền xử lý hoặc mô hình: …
```

Mỗi chart phải có: tiêu đề dạng câu hỏi, tên trục + đơn vị, ghi chú nguồn số liệu dưới chart nếu dùng định nghĩa doanh thu nào (ví dụ "doanh thu gộp, gồm đơn huỷ, trước chiết khấu").

## 4. Danh sách notebook (thư mục `notebooks/eda/`)

### 00_tu_dien_du_lieu.ipynb — mọi thành viên dùng
- Với 13 bảng (bỏ `sample_submission`): số dòng, số cột, khoảng ngày (nếu có cột ngày), bảng `profile_table`.
- Bảng khoá nối dùng `key_coverage`: order_items→orders (order_id), order_items→products (product_id), orders→customers (customer_id), customers→geography (zip), payments/shipments/returns/reviews→orders, inventory→products.
- Kiểm tra khoá chính trùng: orders.order_id, products.product_id, customers.customer_id, sales.Date.
- Xuất mỗi bảng 1 file `tables/profile_<bảng>.csv` + 1 file tổng `tables/overview.csv`.
- Cuối notebook: 1 ô markdown mẫu "Từ điển bảng <tên>" (1 dòng là gì / ý nghĩa cột / khoá / 3 điều lạ) để mỗi người copy dùng.

### 01_bien_muc_tieu_tong_theo_ngay.ipynb — thay eda_01, eda_02, eda_03
- Giữ nội dung eda_01 (phân phối), eda_02 (xu hướng + MA30), eda_03 (heatmap thứ × tháng), dùng `sales.csv`.
- Đổi tên ảnh: `01a_phan_phoi_doanh_thu.png`, `01b_xu_huong_MA30.png`, `01c_mua_vu_thu_thang.png`.
- eda_02 cũ tên "stl_decomposition" nhưng không có STL: thêm 1 chart STL thật (`statsmodels` STL, period=365 trên doanh thu ngày hoặc period=52 trên doanh thu tuần) → `01d_phan_ra_STL.png`. Nếu thiếu statsmodels thì thêm vào requirements.txt.
- Ghi chú dưới mọi chart: `sales.Revenue` là doanh thu gộp, gồm đơn huỷ, trước chiết khấu.

### 02_bien_muc_tieu_tuan_danh_muc.ipynb — MỚI, quan trọng nhất
- Dựng `order_lines` → `revenue_daily` 3 phiên bản → **đối soát** với `sales.Revenue` theo ngày: in sai lệch tuyệt đối max/mean cho từng phiên bản (kỳ vọng `gross_all` khớp tuyệt đối). Chart `02a_doi_soat_sales.png`.
- `weekly_category(kind="gross_all")` và `kind="net_excl_cancelled"`: chart chuỗi tuần 4 danh mục `02b_doanh_thu_tuan_danh_muc.png`; tỷ trọng danh mục theo năm `02c_ty_trong_danh_muc_theo_nam.png`; số tuần × danh mục bằng 0 `02d_tuan_khong_ban.png` (bảng nếu ít).
- Lưu bảng `tables/weekly_category_gross_all.csv`, `tables/weekly_category_net_excl_cancelled.csv`.
- KHÔNG chọn phiên bản nào làm biến mục tiêu chính thức: in cả hai, để nhóm quyết ở Giai đoạn 3.

### 03_gia_bien_loi_nhuan_khuyen_mai.ipynb — thay eda_06, eda_09
- Tách rõ 2 loại biên: **biên niêm yết** (products, mỗi SKU) và **biên thực tế** = (gross − cogs_line) / gross tính trên order_lines, theo danh mục × năm. Chart so sánh `03a_bien_niem_yet_vs_thuc_te.png`. (Lý do: chart cũ ra 24–28% còn biên thực tế trung bình ~12,5% — notebook phải cho thấy chênh lệch này đến từ đâu.)
- Phân phối độ lệch `unit_price / products.price − 1` theo danh mục `03b_lech_gia_ban_vs_niem_yet.png` (audit đã thấy 99,99% dòng lệch).
- Dòng thời gian khuyến mãi (`promotions` start–end) chồng lên biên lợi nhuận theo ngày/tuần `03c_khuyen_mai_vs_bien_loi_nhuan.png`: để nhóm trả lời "các cú sụt biên −40% vào tháng 8–9 các năm lẻ có trùng khuyến mãi không".
- Số SKU theo phân khúc (phần còn lại của eda_06) `03d_so_sku_phan_khuc.png`.

### 04_van_hanh_va_traffic.ipynb — thay eda_04, 05, 07, 08
- Dùng panel đã sửa (mục A). Mọi phân tích có traffic chỉ dùng **từ 2013-01-01** (ghi rõ trong chart).
- eda_04 tương quan: vẽ 2 bản — trên giá trị gốc và trên **chênh lệch so với tuần trước** (`diff(7)`), để thấy tương quan nào chỉ do xu hướng chung `04a_tuong_quan_goc_vs_diff.png`.
- eda_05, eda_07 giữ ý, đổi tên `04b_traffic_don_hang_vs_doanh_thu.png`, `04c_traffic_x_chiet_khau.png`.
- eda_08 (PCA + K-means): giữ, đổi tên `04d_cum_trang_thai_van_hanh.png`, in bảng profile tâm cụm (giá trị trung bình mỗi đặc trưng theo cụm) để nhóm tự đặt tên cụm.

### 05_ton_kho_tra_hang_khach_hang.ipynb — thay eda_10, 11, 12, 15, 16
- Chuyển nguyên logic từ `02_eda_charts_vi.py` (eda_10/11/12) và `03_customer_logistics.py` (eda_15/16).
- Đổi tên cho khớp nội dung: `05a_ton_kho_dut_hang.png`, `05b_khach_hang_tuoi_gioi_tinh.png`, `05c_danh_gia_sao.png`, `05d_ly_do_tra_hang.png`, `05e_thoi_gian_giao.png`, `05f_khach_hang_vung_kenh.png`, `05g_van_hanh_tra_hang_khuyen_mai.png`.
- Tách eda_11/12 cũ (mỗi ảnh 2 chủ đề không liên quan) thành ảnh riêng.
- Giữ các `TODO(phuong-phap)` hiện có dưới dạng ô markdown "Vấn đề phương pháp cần nhóm quyết".

### 06_chat_luong_du_lieu.ipynb — thay eda_13, 14 (dùng tiếp ở Giai đoạn 2)
- Chuyển logic `scripts/audit/01_data_quality_audit.py` + `02_data_quality_charts.py`.
- Thêm bảng điểm **6 khía cạnh** (Đầy đủ, Hợp lệ, Chính xác, Nhất quán, Duy nhất, Kịp thời) × 13 bảng, công thức `1 − số vi phạm / tổng`, mỗi quy tắc ghi rõ trong 1 bảng `tables/dq_rules.csv` (bảng, cột, khía cạnh, quy tắc, số vi phạm, điểm). Heatmap `06c_diem_6_khia_canh.png`. Đây là điểm "trước tiền xử lý".
- Quy tắc tối thiểu: % trống mỗi cột (Đầy đủ); quantity>0, unit_price>0, rating∈[1,5], order_status thuộc tập trạng thái (Hợp lệ); unit_price vs price, tổng tự dựng vs sales (Chính xác); khoá nối có trong bảng cha, delivery_date ≥ ship_date ≥ order_date, return_date ≥ order_date (Nhất quán); khoá chính không trùng (Duy nhất); khoảng ngày mỗi bảng so với sales (Kịp thời).

## 5. Dọn dẹp sau khi notebook chạy xong

- `mv -n` các script đã được thay vào `archive/scripts-cu/` (02_eda_charts_vi.py, 03_customer_logistics.py, audit/*, 01_build_daily_panel.py, 04_stratified_sample.py). Giữ `scripts/pa1/`.
- Ảnh cũ `outputs/eda/eda_*.png` → `archive/outputs-cu/`.
- Các file không rõ nguồn trong `outputs/eda` (`eda_*_matrix.csv`, `eda_regression_summary.csv`, `eda_distribution_summary.csv`, `eda_stats_summary.json`) → `archive/outputs-cu/khong-ro-nguon/`.
- Phần lấy mẫu phân tầng và `statistical_proof.json`: không đưa vào notebook mới (không phục vụ hiểu dữ liệu), để trong archive.
- Cập nhật `README.md`: thứ tự đọc notebook 00 → 06, quy ước tuần, 3 định nghĩa doanh thu, bảng ánh xạ ảnh cũ → ảnh mới.

## 6. Tiêu chí hoàn thành (Claude Code tự kiểm trước khi báo xong)

- [ ] 7 notebook chạy `nbconvert --execute` không lỗi, output lưu trong file.
- [ ] Notebook 02: `gross_all` khớp `sales.Revenue` từng ngày (sai lệch ≈ 0); in rõ sai lệch 2 phiên bản còn lại.
- [ ] Notebook 03: in được biên niêm yết và biên thực tế theo danh mục, thấy rõ chênh lệch.
- [ ] Panel không còn giá trị trung vị điền vào ngày không có trả hàng/review/traffic.
- [ ] Không còn tên ảnh lệch nội dung; README có bảng ánh xạ cũ → mới.
- [ ] Không file nào trong `data/raw/` và `notebooks/thanh-vien/Quyen/` bị thay đổi.
- [ ] Báo cáo cuối: danh sách file tạo/sửa/di chuyển, các số liệu chính in ra từ notebook 02 và 03, mọi chỗ còn `TODO`.
