# Giao việc cho Claude Code: đưa repo lên GitHub để cả nhóm EDA

Repo đích: https://github.com/ZaKhimNe/khaipha-dl-doanhnghiep
Thư mục làm việc: thư mục gốc `ds317-doanhnghiep` (hiện CHƯA có `.git`).

## 0. Ràng buộc (bắt buộc)

- KHÔNG sửa, xoá, di chuyển bất kỳ file nào trong `data/raw/`. KHÔNG đưa file nào trong `data/` lên GitHub.
- KHÔNG xoá file nào trên máy. Việc "không đẩy lên" chỉ làm bằng `.gitignore`.
- KHÔNG đụng `notebooks/thanh-vien/Quyen/` (có SHA-256 đối soát). Nó vẫn được commit nguyên trạng.
- KHÔNG sửa nội dung notebook hay code trong đợt này. Chỉ thêm/sửa `.gitignore`, `README.md` (mục 3) và tạo file hướng dẫn (mục 4).
- KHÔNG dùng `git push --force`. KHÔNG `git reset --hard`, `git clean`.
- Dừng lại và báo Khiêm nếu gặp một trong các tình huống ở mục 1.3.

## 1. Kiểm tra trước khi làm

1.1. Chạy `git --version`. Không có git thì dừng và báo.

1.2. Xem repo GitHub đang có gì: `git ls-remote https://github.com/ZaKhimNe/khaipha-dl-doanhnghiep`.

1.3. Dừng và báo Khiêm (không tự xử lý) nếu:
- Không truy cập được repo (chưa đăng nhập, thiếu quyền).
- Repo đã có commit với nội dung khác ngoài README/LICENSE/.gitignore mặc định của GitHub.

Nếu repo trống hoặc chỉ có file mặc định, đi tiếp mục 2.

1.4. Ghi lại SHA-256 của mọi file trong `notebooks/thanh-vien/Quyen/` và tổng số file trong `data/raw/`. Cuối đợt so lại phải giống hệt.

## 2. Cập nhật `.gitignore`

Giữ nguyên các dòng đang có. Thêm (nếu chưa có):

```
# Tài liệu PDF có bản quyền, nặng -> để trên Drive nhóm
docs/tai-lieu-tham-khao/
docs/tai-lieu-mon-hoc/

# Dữ liệu: chặn mọi thứ dưới data/ nhưng giữ cấu trúc thư mục
data/**
!data/README.md

# Môi trường / hệ điều hành
.env
.DS_Store
Thumbs.db
```

Tạo `data/README.md` (1 đoạn): data không có trên GitHub, tải từ Kaggle, giải nén vào `data/raw/datathon-2026-round-1/`, hoặc đặt biến `DS317_DATA_DIR`.

## 3. Khởi tạo và commit

3.1. `git init`, đặt nhánh `main`, thêm remote `origin` là repo đích.
Nếu repo GitHub có file mặc định (mục 1.3): `git pull origin main --allow-unrelated-histories` trước khi commit; có conflict ở README thì giữ README của máy và báo lại.

3.2. `git add -A` rồi CHƯA commit. Kiểm tra danh sách file sẽ vào commit (`git status`, `git ls-files --cached`):
- Không có file nào bắt đầu bằng `data/` ngoài `data/README.md`.
- Không có `.venv/`, `__pycache__/`, file `.pdf` trong `docs/tai-lieu-*`.
- Không file nào > 50 MB (liệt kê 10 file lớn nhất kèm dung lượng).
- Tổng dung lượng dự kiến (báo con số).
Sai bất kỳ điểm nào: sửa `.gitignore`, `git add -A` lại, kiểm tra lại. Không commit khi chưa đạt.

3.3. Phải có trong commit:
- `src/ds317/`, `scripts/`, `requirements.txt`, `README.md`
- `notebooks/eda/` (7 notebook, GIỮ output để xem chart trên GitHub)
- `outputs/eda/` (25 ảnh + bảng)
- `notebooks/thanh-vien/` (cả `Quyen/`), `notebooks/00_baseline_cuoc_thi.ipynb`, `notebooks/01_DS317.R11_DeXuat_Code_tong_hop.ipynb`
- `docs/ke-hoach/`, `docs/quan-ly/`, `docs/de-xuat-de-tai/`, `docs/eda-m5-screenshots/`
- `archive/` trừ `archive/outputs-cu/data/`

3.4. Commit với message: `Khởi tạo repo: thư viện ds317, 7 notebook EDA, outputs/eda, kế hoạch`.
Push: `git push -u origin main`.

## 4. Chuẩn bị chỗ làm cho thành viên

4.1. Tạo `docs/eda/README.md` gồm:
- Bảng: notebook nào → file bài viết nào → ai phụ trách (để trống cột "ai", Khiêm điền).
  Tên file bài viết: `docs/eda/00_tu_dien_du_lieu.md` … `docs/eda/06_chat_luong_du_lieu.md`.
- Khung "Đọc chart" 4 ý (kết luận có số / số kiểm tra / điều lạ / ảnh hưởng), copy từ file giao việc EDA trước.
- KHÔNG tự viết phân tích.

4.2. Tạo `docs/HUONG-DAN-THANH-VIEN.md` (ngắn, đọc trên điện thoại được):
1. Clone repo.
2. Join competition Datathon 2026 trên Kaggle, tải data, giải nén vào `data/raw/datathon-2026-round-1/`.
3. Tạo môi trường Python, cài `requirements.txt`.
4. Chạy `notebooks/eda/00_tu_dien_du_lieu.ipynb`: phải đọc đủ 14 file CSV, không lỗi.
5. Quy tắc làm việc:
   - `notebooks/eda/` là bản chuẩn, KHÔNG sửa trực tiếp. Muốn thử thì copy sang `notebooks/thanh-vien/<Tên>/`.
   - Bài viết để ở `docs/eda/<file được giao>.md`.
   - Làm trên nhánh `eda/<ten>`, mở Pull Request vào `main`, Khiêm review.
   - Không commit file trong `data/`.
   - Không đụng `notebooks/thanh-vien/Quyen/`.
6. Kẹt thì nhắn Khiêm kèm ảnh lỗi.

Tạo thư mục trống cho người chưa có: `notebooks/thanh-vien/<Tên>/.gitkeep` cho Khiem, TuongVan (giữ nguyên các thư mục đã có).

4.3. Thêm vào `README.md` một dòng trỏ tới `docs/HUONG-DAN-THANH-VIEN.md`.

Commit: `Thêm hướng dẫn thành viên và chỗ làm EDA`. Push.

## 5. Kiểm tra cuối (báo lại đủ từng dòng)

- [ ] `git ls-files | grep "^data/"` chỉ ra `data/README.md`.
- [ ] `git ls-files | wc -l` và tổng dung lượng repo (`git count-objects -vH`).
- [ ] Clone thử repo vào một thư mục tạm NGOÀI dự án, xác nhận có đủ `src/`, `notebooks/eda/`, `outputs/eda/`, không có data. Báo xong thì để nguyên thư mục tạm đó, KHÔNG xoá, ghi đường dẫn để Khiêm tự xoá.
- [ ] SHA-256 `notebooks/thanh-vien/Quyen/` và số file `data/raw/` giống mục 1.4.
- [ ] Link 2 commit trên GitHub.

## 6. Khiêm tự làm sau khi Claude Code xong (không giao Claude Code)

- Trên GitHub: Settings → Collaborators, mời 5 người quyền Write.
- Settings → Branches: bảo vệ `main`, bắt buộc Pull Request.
- Điền cột "ai phụ trách" trong `docs/eda/README.md`.
