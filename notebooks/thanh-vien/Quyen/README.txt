Bằng chứng công việc - Nguyễn Văn Quyền
Phạm vi: Phần 3 (phát biểu bài toán PA1) + Phần 4.1 (kiểm chứng nhanh PA1)
Gom thư mục lúc: 2026-09-29 16:22:36

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
  - Số mẫu PA1 (tuần x 4 danh mục): 2184
      train = 1772, validation = 208, test = 204
  - Baseline seasonal-naive (cùng kỳ năm trước) trên validation 2021: WMAPE = 0.189
  - Baseline trung bình 4 tuần gần nhất trên validation 2021: WMAPE = 0.3212
  - Ngưỡng cần vượt cho mô hình PA1: WMAPE < 0.189 (seasonal-naive)
  - Có bảng khuyến mãi lên lịch trước không: CÓ - promotions.csv là bảng khuyến mãi lên lịch trước, có start_date/end_date/discount_value.

SHA-256 để đối soát (đảm bảo file không bị chỉnh sửa sau khi nộp):
  quyen_pa1_kiem_chung.ipynb: fe9eb95c34dd26ff832388b9bcee6e88ee3e3e9c227820706e96118e948dd6d7
  pa1_validation_evidence.json: 31f7abdef2b57d05bd7520301d125e5e8989aedadda87edc4a6b4fa1363214c8
  bieu_do_1_chuoi_tuan_theo_danh_muc.png: b6700ea3a5783171e6ddf5ec5261d4b20b9e18cf2f17e878b3f93109fc02f92b
  bieu_do_2_ty_trong_danh_muc.png: 0ffc119b0b4ef74ecadf1bf797135732372430264b63e6ec308a8e256ac6e174
  bieu_do_3_so_sanh_baseline_wmape.png: b16cc6e22a4acc40fa973742f8c122e6771ec2b618758ae807e13450e9772d25
  bieu_do_4_wmape_theo_horizon.png: 7ee185d5a3a48c825bfb989740bac16d344c7253656ea3b6836bb9f47fbeda66
