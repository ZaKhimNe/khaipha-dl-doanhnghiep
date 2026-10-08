# DS317.R11 – Dự báo doanh thu (Datathon 2026)

Đồ án môn DS317 – Khai phá dữ liệu trong doanh nghiệp, nhóm 8. Đề tài: dự báo doanh thu **tuần × danh mục**
(Casual, GenZ, Outdoor, Streetwear) cho doanh nghiệp thời trang thương mại điện tử, dữ liệu Datathon 2026 Round 1.

## Đọc EDA theo thứ tự

Mở các notebook trong `notebooks/eda/` (output đã lưu sẵn, không cần chạy lại để đọc):

| # | Notebook | Trả lời câu hỏi |
|---|---|---|
| 00 | `00_tu_dien_du_lieu` | 13 bảng: mỗi dòng là gì, ý nghĩa cột, kiểu, % trống, khoá nối có khớp không |
| 01 | `01_bien_muc_tieu_tong_theo_ngay` | `sales.csv` theo ngày: phân phối, xu hướng 10 năm, mùa vụ thứ × tháng, phân rã STL |
| 02 | `02_bien_muc_tieu_tuan_danh_muc` | **Biến mục tiêu** tuần × danh mục: đối soát với `sales`, so sánh định nghĩa doanh thu |
| 03 | `03_gia_bien_loi_nhuan_khuyen_mai` | Biên niêm yết vs biên thực tế, giá bán lệch giá niêm yết, sụt biên vs khuyến mãi |
| 04 | `04_van_hanh_va_traffic` | Traffic / đơn / chiết khấu vs doanh thu, tương quan gốc vs diff 7 ngày, cụm trạng thái |
| 05 | `05_ton_kho_tra_hang_khach_hang` | Tồn kho, khách hàng, đánh giá, trả hàng, thời gian giao, vùng/kênh, khuyến mãi |
| 06 | `06_chat_luong_du_lieu` | Lỗi dữ liệu, đối soát thanh toán, điểm 6 khía cạnh × 13 bảng (trước tiền xử lý) |

Dưới mỗi chart có khối **"Số liệu chính"** (tính từ data) và ô **"Đọc chart (nhóm điền)"** để nhóm viết giải thích.
Ảnh và bảng số của mỗi notebook nằm ở `outputs/eda/<tên notebook>/` và `outputs/eda/<tên notebook>/tables/`.

## Quy ước

- **Tuần:** Thứ Hai → Chủ nhật (pandas `W-SUN`), `week_start` = ngày Thứ Hai. Tuần đầu (từ 2012-07-04) và tuần cuối
  (đến 2022-12-31) không đủ 7 ngày → `is_partial_week = True`.
- **Tiền:** đơn vị gốc là đồng; chart hiển thị **Triệu VNĐ** (chia 1e6).
- **Ba định nghĩa doanh thu** (`ds317.REVENUE_KINDS`):

| kind | Công thức | Đơn huỷ | Ghi chú |
|---|---|---|---|
| `gross_all` | SUM(`quantity × unit_price`) | gồm | = `sales.Revenue`, khớp tuyệt đối từng ngày |
| `gross_excl_cancelled` | SUM(`quantity × unit_price`) | bỏ | thấp hơn `sales` TB 9.2%/ngày |
| `net_excl_cancelled` | SUM(`quantity × unit_price − discount_amount`) | bỏ | thấp hơn `sales` TB 13.9%/ngày |

  `sales.COGS` = SUM(`quantity × products.cogs`). Định nghĩa chính thức của biến mục tiêu: nhóm quyết ở Giai đoạn 3.
- **Panel theo ngày** (`ds317.panel.build_daily_panel`): ngày không có đơn / trả hàng / review → cột đếm = 0;
  traffic thiếu 181 ngày cuối 2012 và các cột trung bình → giữ trống (không điền trung vị).

## Cấu trúc thư mục

```
data/raw/                      Dữ liệu gốc (không chỉnh sửa, không chia sẻ ra ngoài)
src/ds317/                     Thư viện dùng chung – notebook chỉ gọi hàm ở đây
  paths.py                     ROOT, DATA_DIR, OUTPUT_DIR, out_dir()
  data.py                      load(), load_many(), order_lines(), revenue_daily(), weekly_category()
  panel.py                     build_daily_panel()
  profile.py                   profile_table(), key_coverage(), duplicate_keys(), date_range()
  dictionary.py                TABLE_DESC, COLUMN_DESC – ý nghĩa bảng/cột (sửa tại đây)
  quality.py                   audit_findings(), dirtiness_metrics(), dq_rules(), dq_scores()
  viz.py                       setup_style(), nb_out(), save_fig(), source_note(), key_numbers()
notebooks/
  eda/00 … 06                  EDA (xem bảng trên)
  00_baseline_cuoc_thi.ipynb   baseline mẫu của BTC
  01_DS317.R11_DeXuat_Code_tong_hop.ipynb   notebook cho Bản đề xuất (Giai đoạn 1)
  thanh-vien/<Tên>/            notebook từng thành viên (Quyen/ giữ nguyên bản đã nộp, có SHA-256)
scripts/pa1/pa1_validation.py  kiểm chứng nhanh PA1 (bản chạy lại được của Quyền)
outputs/eda/<notebook>/        ảnh + tables/ do notebook EDA sinh ra
outputs/pa1/                   kết quả PA1
docs/                          đề xuất, phân công, tài liệu môn học, tài liệu tham khảo, kế hoạch
archive/                       chỉ để tham khảo: engine-goc/, scripts-cu/, outputs-cu/, notebooks-phien-ban-cu/
```

## Cài đặt và chạy

```bash
py -3 -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# chạy lại 1 notebook và lưu output vào file
jupyter nbconvert --to notebook --execute --inplace notebooks/eda/02_bien_muc_tieu_tuan_danh_muc.ipynb
python scripts/pa1/pa1_validation.py
```

Notebook tự tìm thư mục gốc repo (chứa `src/ds317`). Chạy trên Colab/máy khác: đặt biến môi trường
`DS317_DATA_DIR` trỏ tới thư mục chứa 14 file CSV.

## Ánh xạ ảnh EDA cũ → mới

Ảnh cũ nằm trong `archive/outputs-cu/`.

| Ảnh cũ | Ảnh mới |
|---|---|
| eda_01_target_distributions | 01a_phan_phoi_doanh_thu |
| eda_02_timeseries_stl_decomposition (không có STL) | 01b_xu_huong_MA30 + **01d_phan_ra_STL** (STL thật) |
| eda_03_seasonality_heatmap | 01c_mua_vu_thu_thang |
| eda_04_correlation_matrix | 04a_tuong_quan_goc_vs_diff |
| eda_05_bivariate_traffic_sales | 04b_traffic_don_hang_vs_doanh_thu |
| eda_06_bivariate_order_economics | 03a_bien_niem_yet_vs_thuc_te (biên) + 03d_so_sku_phan_khuc (SKU) |
| eda_07_multivariate_surface | 04c_traffic_x_chiet_khau |
| eda_08_pca_regime_clusters | 04d_cum_trang_thai_van_hanh (+ tables/cluster_profile.csv) |
| eda_09_category_margin_breakdown | 03a_bien_niem_yet_vs_thuc_te |
| eda_10_inventory_stockout_impact | 05a_ton_kho_dut_hang |
| eda_11_customer_geo_demographics | 05b_khach_hang_tuoi_gioi_tinh + 05c_danh_gia_sao |
| eda_12_operations_returns_reviews | 05d_ly_do_tra_hang + 05e_thoi_gian_giao |
| eda_13_data_dirtiness_audit | 06a_do_ban_du_lieu |
| eda_14_reconciliation_pitfalls | 06b_doi_soat_thanh_toan_doanh_thu |
| eda_15_customer_region_channel | 05f_khach_hang_vung_kenh (phần tuổi × giới chuyển sang 05b) |
| eda_16_ops_returns_promo | 05e (giao hàng vs số sao), 05d (Pareto lý do trả), 05g_van_hanh_tra_hang_khuyen_mai |
| eda_stratified_sample_fidelity | bỏ (không phục vụ hiểu dữ liệu; code ở archive/scripts-cu/eda/04_stratified_sample.py) |
| – | **Mới:** 02a_doi_soat_sales, 02b_doanh_thu_tuan_danh_muc, 02c_ty_trong_danh_muc_theo_nam, 03b_lech_gia_ban_vs_niem_yet, 03c_khuyen_mai_vs_bien_loi_nhuan, 06c_diem_6_khia_canh |

## Lưu ý về dữ liệu

- `payments.payment_value` = tiền hàng net (sau chiết khấu), **không** gồm `shipping_fee`.
- 99.99% dòng `order_items` có `unit_price` khác `products.price`; biên niêm yết (~26.6% TB SKU) khác xa biên thực tế (~13.8%).
- `order_items` có 16 dòng trùng cặp `(order_id, product_id)`.
- 73.8% đơn có `order_date` trước `customers.signup_date`.
