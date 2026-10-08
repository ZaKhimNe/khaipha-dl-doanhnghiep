# Hướng dẫn thành viên

## 1. Clone repo

```bash
git clone https://github.com/ZaKhimNe/khaipha-dl-doanhnghiep.git
cd khaipha-dl-doanhnghiep
```

## 2. Tải dữ liệu

Join competition **Datathon 2026** trên Kaggle, tải 14 file CSV, giải nén vào:

```
data/raw/datathon-2026-round-1/
```

(ví dụ phải có `data/raw/datathon-2026-round-1/sales.csv`). Dữ liệu không có trên GitHub.

## 3. Cài môi trường Python

```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Chạy thử

Mở và chạy hết `notebooks/eda/00_tu_dien_du_lieu.ipynb`. Đạt khi không lỗi và đọc đủ 14 file CSV.

## 5. Quy tắc làm việc

- `notebooks/eda/` là **bản chuẩn**, KHÔNG sửa trực tiếp. Muốn thử thì copy sang `notebooks/thanh-vien/<Tên>/`.
- Bài viết để ở `docs/eda/<file được giao>.md` (xem `docs/eda/README.md`).
- Làm trên nhánh `eda/<ten>`, mở Pull Request vào `main`, Khiêm review.
- KHÔNG commit file nào trong `data/`.
- KHÔNG đụng `notebooks/thanh-vien/Quyen/`.

```bash
git checkout -b eda/<ten>
# ... làm việc ...
git add docs/eda/<file>.md notebooks/thanh-vien/<Tên>/
git commit -m "EDA: <nội dung>"
git push -u origin eda/<ten>
# rồi mở Pull Request trên GitHub
```

## 6. Kẹt?

Nhắn Khiêm kèm ảnh chụp lỗi.
