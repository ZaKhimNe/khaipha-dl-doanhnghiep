# Bài viết EDA

Mỗi notebook trong `notebooks/eda/` có 1 file bài viết ở thư mục này. Người phụ trách đọc notebook (output đã lưu sẵn),
rồi viết giải thích cho từng chart vào file của mình theo khung bên dưới.

| Notebook | File bài viết | Phụ trách |
|---|---|---|
| `notebooks/eda/00_tu_dien_du_lieu.ipynb` | `docs/eda/00_tu_dien_du_lieu.md` | |
| `notebooks/eda/01_bien_muc_tieu_tong_theo_ngay.ipynb` | `docs/eda/01_bien_muc_tieu_tong_theo_ngay.md` | |
| `notebooks/eda/02_bien_muc_tieu_tuan_danh_muc.ipynb` | `docs/eda/02_bien_muc_tieu_tuan_danh_muc.md` | |
| `notebooks/eda/03_gia_bien_loi_nhuan_khuyen_mai.ipynb` | `docs/eda/03_gia_bien_loi_nhuan_khuyen_mai.md` | |
| `notebooks/eda/04_van_hanh_va_traffic.ipynb` | `docs/eda/04_van_hanh_va_traffic.md` | |
| `notebooks/eda/05_ton_kho_tra_hang_khach_hang.ipynb` | `docs/eda/05_ton_kho_tra_hang_khach_hang.md` | |
| `notebooks/eda/06_chat_luong_du_lieu.ipynb` | `docs/eda/06_chat_luong_du_lieu.md` | |

Ảnh để chèn vào bài viết: `outputs/eda/<tên notebook>/<tên ảnh>.png`.

## Khung "Đọc chart" (dùng cho mỗi chart)

```markdown
### <Mã ảnh> – <câu hỏi của chart>

![](../../outputs/eda/<tên notebook>/<tên ảnh>.png)

> **Đọc chart:**
> 1. Kết luận 1 câu có số: …
> 2. Số kiểm tra lại từ data: …
> 3. Điều lạ / chưa giải thích được: …
> 4. Ảnh hưởng đến tiền xử lý hoặc mô hình: …
```

Với notebook 00 (từ điển dữ liệu): mỗi bảng viết mục "3 điều lạ" thay cho khung trên.
