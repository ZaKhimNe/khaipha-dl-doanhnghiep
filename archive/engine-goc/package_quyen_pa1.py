# -*- coding: utf-8 -*-
"""
Gom bằng chứng công việc của Nguyễn Văn Quyền (Phần 3 + Phần 4.1 PA1)
thành một thư mục duy nhất: submissions/quyen-pa-1/  (không nén zip).

Nội dung thư mục:
  - quyen_pa1_kiem_chung.ipynb        (notebook đã chạy, có output + biểu đồ)
  - pa1_validation_evidence.json      (bằng chứng dạng máy đọc được)
  - bieu_do_1_chuoi_tuan_theo_danh_muc.png
  - bieu_do_2_ty_trong_danh_muc.png
  - bieu_do_3_so_sanh_baseline_wmape.png
  - bieu_do_4_wmape_theo_horizon.png
  - README.txt                        (tóm tắt ngắn + sha256 từng file để đối soát)
"""
import os
import json
import shutil
import hashlib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV_DIR = os.path.join(ROOT, "artifacts", "vanquyen")
NB = os.path.join(ROOT, "engine", "quyen_pa1_kiem_chung.ipynb")
EVIDENCE = os.path.join(EV_DIR, "pa1_validation_evidence.json")
CHARTS = [
    os.path.join(EV_DIR, "bieu_do_1_chuoi_tuan_theo_danh_muc.png"),
    os.path.join(EV_DIR, "bieu_do_2_ty_trong_danh_muc.png"),
    os.path.join(EV_DIR, "bieu_do_3_so_sanh_baseline_wmape.png"),
    os.path.join(EV_DIR, "bieu_do_4_wmape_theo_horizon.png"),
]

OUT_DIR = os.path.join(ROOT, "submissions", "quyen-pa-1")
os.makedirs(OUT_DIR, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


for p in [NB, EVIDENCE] + CHARTS:
    if not os.path.exists(p):
        raise FileNotFoundError(f"Thiếu file bắt buộc: {p}")

with open(EVIDENCE, encoding="utf-8") as f:
    ev = json.load(f)

# Sao chép toàn bộ file vào thư mục nộp
files_to_copy = [NB, EVIDENCE] + CHARTS
for src in files_to_copy:
    dst = os.path.join(OUT_DIR, os.path.basename(src))
    shutil.copy2(src, dst)

vc = ev["viec_3_chuoi_tuan"]
bl = ev["viec_3_baseline_validation_2021"]

readme = f"""Bằng chứng công việc - Nguyễn Văn Quyền
Phạm vi: Phần 3 (phát biểu bài toán PA1) + Phần 4.1 (kiểm chứng nhanh PA1)
Gom thư mục lúc: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Danh sách file trong thư mục này:
  - quyen_pa1_kiem_chung.ipynb            : notebook đã chạy từ đầu đến cuối, không lỗi,
                                             có kèm 4 biểu đồ minh họa ngay trong notebook.
  - pa1_validation_evidence.json          : toàn bộ kết quả dạng JSON, dùng để điền vào
                                             bảng 4.1 và sửa Phần 3 của bản đề xuất.
  - bieu_do_1_chuoi_tuan_theo_danh_muc.png: chuỗi doanh thu tuần 2012-2022 theo 4 danh mục,
                                             có đánh dấu ranh giới train / validation / test.
  - bieu_do_2_ty_trong_danh_muc.png       : tỷ trọng doanh thu theo danh mục.
  - bieu_do_3_so_sanh_baseline_wmape.png  : so sánh WMAPE của 2 baseline, theo từng danh mục.
  - bieu_do_4_wmape_theo_horizon.png      : WMAPE thay đổi thế nào theo horizon h=1..4 tuần.

Kết luận chính (xem chi tiết đầy đủ trong file JSON):
  - Số mẫu PA1 (tuần x 4 danh mục): {vc["so_mau_tong"]}
      train = {vc["chia_du_lieu"]["train"]["so_mau"]}, \
validation = {vc["chia_du_lieu"]["validation"]["so_mau"]}, \
test = {vc["chia_du_lieu"]["test"]["so_mau"]}
  - Baseline seasonal-naive (cùng kỳ năm trước) trên validation 2021: \
WMAPE = {bl["tong_the"]["seasonal_naive"]["WMAPE"]}
  - Baseline trung bình 4 tuần gần nhất trên validation 2021: \
WMAPE = {bl["tong_the"]["trung_binh_4_tuan"]["WMAPE"]}
  - Ngưỡng cần vượt cho mô hình PA1: WMAPE < {bl["tong_the"]["seasonal_naive"]["WMAPE"]} (seasonal-naive)
  - Có bảng khuyến mãi lên lịch trước không: {ev["viec_2_bang_khuyen_mai"]["ket_luan"]}

SHA-256 để đối soát (đảm bảo file không bị chỉnh sửa sau khi nộp):
"""
for src in files_to_copy:
    readme += f"  {os.path.basename(src)}: {sha256(src)}\n"

with open(os.path.join(OUT_DIR, "README.txt"), "w", encoding="utf-8") as f:
    f.write(readme)

print("Đã tạo thư mục nộp bài tại:", OUT_DIR)
print("Danh sách file:")
for name in sorted(os.listdir(OUT_DIR)):
    full = os.path.join(OUT_DIR, name)
    print(f"  - {name} ({os.path.getsize(full):,} bytes)")
