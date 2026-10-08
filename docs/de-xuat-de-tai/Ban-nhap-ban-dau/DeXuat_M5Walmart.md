# BẢN ĐỀ XUẤT ĐỀ TÀI – MÔN DS317

> Ký hiệu: **[cần chạy]** = số liệu nhóm tự tính từ notebook; **[tự đếm lại]** = số đã biết, cần xác nhận lại trên tệp đã tải.

## Thông tin chung

| Mục | Nội dung |
|---|---|
| Tên đề tài dự kiến (tiếng Việt) | Dự báo số lượng bán theo ngày của từng mặt hàng tại từng cửa hàng trong 28 ngày tới trên dữ liệu M5 (Walmart), hỗ trợ lập kế hoạch bổ sung hàng |
| Tên đề tài dự kiến (tiếng Anh) | 28-Day Item–Store Daily Sales Forecasting on the M5 (Walmart) Dataset to Support Replenishment Planning |
| Tên nhóm, lớp | [..], DS317.R11 |
| Thành viên (họ tên, MSSV, email) | [..] |
| Nhóm trưởng (họ tên, MSSV, email, điện thoại) | [..] |
| Ngày nộp | [..] |

---

## Phần 1. Rà soát tài sản dữ liệu

### 1.1. Danh sách nguồn dữ liệu

| Nguồn | Mô tả ngắn | Đường dẫn / cách thu thập | Giấy phép | Ngày truy cập | Mỗi dòng là gì |
|---|---|---|---|---|---|
| sales_train_evaluation.csv | Số lượng bán theo ngày, dạng wide (d_1 … d_1941) | https://www.kaggle.com/competitions/m5-forecasting-accuracy | [ghi đúng điều khoản ở tab Rules/Data] | [..] | 1 cặp (item_id, store_id); mỗi cột d_i là 1 ngày |
| calendar.csv | Lịch, sự kiện, cờ SNAP theo bang | như trên | như trên | [..] | 1 ngày |
| sell_prices.csv | Giá bán theo tuần | như trên | như trên | [..] | 1 bộ (store_id, item_id, wm_yr_wk) |

Khóa nối: `sales.d` ↔ `calendar.d`; `calendar.wm_yr_wk` + `store_id` + `item_id` ↔ `sell_prices`.

### 1.2. Bảng kiểm kê

| Tiêu chí | Kết quả của nhóm | Đánh giá |
|---|---|---|
| Nguồn gốc | Dữ liệu công khai của cuộc thi Kaggle M5 (Walmart, tổ chức bởi ĐH Nicosia); giấy phép: [..] | Đạt (sau khi ghi điều khoản) |
| Quy mô | sales: 30.490 dòng × 1.947 cột; calendar: 1.969 × 14; sell_prices: ~6,84 triệu × 4 [tự đếm lại]. Chuyển sang dạng long: ~59 triệu dòng; dung lượng [..] MB | Cần lưu ý (vượt RAM Colab nếu dùng toàn bộ) |
| Cấu trúc | Có cấu trúc, CSV, 3 bảng nối qua khóa ở 1.1. Phân cấp: 3 bang → 10 cửa hàng; 3 ngành → 7 department → 3.049 mặt hàng | Đạt |
| Nhãn | Có sẵn cột `sales` (số nguyên ≥ 0). Không có dữ liệu tồn kho, nên không phân biệt được "không có nhu cầu" với "hết hàng" | Đạt cho dự báo; Không đạt cho bài toán hết hàng |
| Chất lượng | 68,2% giá trị bằng 0 (HOBBIES ~77%, HOUSEHOLD ~71%, FOODS ~62%); sell_price NaN ở giai đoạn mặt hàng chưa bán; ngày 25/12 đóng cửa, sales = 0 toàn hệ thống; tỷ lệ số 0 "trước ngày bán đầu tiên": [cần chạy]; số dòng trùng khóa: [cần chạy] | Cần lưu ý |
| Thời gian | 29/01/2011 → 22/05/2016, 1.941 ngày liên tục (~5,3 năm); đủ mùa vụ tuần và năm; tách được train/validation/test theo thời gian | Đạt |
| Tính riêng tư | Không có dữ liệu khách hàng; chỉ có số lượng tổng hợp theo mặt hàng–cửa hàng | Đạt |

### 1.3. Nhận định

- **Cho phép:** dự báo số lượng bán theo ngày ở mọi cấp phân cấp (item–store, store–department, bang); phân tích tác động của sự kiện, SNAP, giá; phân nhóm chuỗi theo mẫu nhu cầu.
- **Không cho phép:** phân tích khách hàng hoặc giỏ hàng (không có hóa đơn, nên không làm được luật kết hợp); phân tích lợi nhuận (không có giá vốn); dự đoán hết hàng (không có tồn kho).
- **Giới hạn 1:** một phần số 0 là số 0 cấu trúc (mặt hàng chưa ra mắt), phải cắt trước khi tính tỷ lệ gián đoạn thật.
- **Giới hạn 2:** quy mô ~59 triệu dòng, phải thu hẹp phạm vi, ví dụ 1 bang, hoặc 1 ngành kèm 2 năm gần nhất.
- **Giới hạn 3:** doanh số là nhu cầu đã bị cắt (censored) khi hết hàng; nhóm ghi rõ điểm này nằm ngoài phạm vi.

---

## Phần 2. Bối cảnh và nhu cầu của doanh nghiệp

### 2.1. Các yếu tố bối cảnh

| Yếu tố | Nội dung |
|---|---|
| Doanh nghiệp / lĩnh vực | **Bối cảnh giả định**, dựng theo dữ liệu: chuỗi siêu thị bán lẻ 10 cửa hàng tại California, Texas, Wisconsin; 3.049 mặt hàng thuộc FOODS, HOBBIES, HOUSEHOLD |
| Chủ thể ra quyết định | Bộ phận Kế hoạch bổ sung hàng (replenishment) cấp cửa hàng |
| Quyết định cần hỗ trợ | Đầu mỗi tuần, lập đơn đặt hàng cho từng mặt hàng tại từng cửa hàng dựa trên nhu cầu dự kiến 28 ngày tới |
| Hiện trạng | Giả định dùng quy tắc cố định: đặt theo lượng bán cùng kỳ tuần trước hoặc trung bình 28 ngày gần nhất. Quy tắc này không tính ngày SNAP, sự kiện, thay đổi giá. Đây là baseline |
| Chi phí của việc làm sai | Dự báo thấp dẫn đến hết hàng, mất doanh thu (nhất là FOODS vào ngày SNAP). Dự báo cao dẫn đến tồn dư: FOODS là hàng hỏng phải hủy; HOBBIES/HOUSEHOLD chiếm kệ và vốn. FOODS: dư thừa tốn kém hơn; mặt hàng bán chạy: thiếu hụt tốn kém hơn |
| Chỉ số nghiệp vụ (KPI) | Tỷ lệ đáp ứng nhu cầu (fill rate); số đơn vị thiếu ước tính × giá bán; số đơn vị dư ước tính × chi phí lưu kho giả định |

### 2.2. Câu phát biểu nhu cầu nghiệp vụ

> Bộ phận Kế hoạch bổ sung hàng của mỗi cửa hàng cần dự báo, vào đầu mỗi tuần, số lượng bán theo ngày của từng mặt hàng trong 28 ngày tới, để lập đơn đặt hàng sát nhu cầu, nhằm giảm lượng hàng thiếu và hàng tồn dư (đặc biệt ngành FOODS).

---

## Phần 3. Phát biểu bài toán khai phá dữ liệu

| Thành phần | Phương án 1 – Dự báo item–store | Phương án 2 – Dự báo store–department | Phương án 3 – Dự đoán hết hàng |
|---|---|---|---|
| Nhóm bài toán | Hồi quy / chuỗi thời gian (dữ liệu đếm), có giám sát | Chuỗi thời gian, có giám sát | Phân loại nhị phân, có giám sát |
| Đơn vị phân tích | 1 cặp (item, store) × 1 ngày dự báo | 1 cặp (store, dept) × 1 ngày | 1 cặp (item, store) × 1 ngày |
| Cho trước | Lịch sử bán đến mốc cắt, lịch, SNAP, giá; phạm vi [bang/ngành đã chọn] | Doanh số tổng hợp của 70 chuỗi (10 cửa hàng × 7 department) | Lịch sử bán, giá, lịch |
| Cần tìm | Số lượng bán mỗi ngày trong 28 ngày sau mốc cắt | Tổng số lượng bán mỗi ngày trong 28 ngày tới của từng department | Mặt hàng có hết hàng trong ngày tới hay không |
| Biến mục tiêu | `sales` tại ngày t+h, h = 1..28 | Tổng `sales` theo (store, dept, ngày) | Không định nghĩa được: không có dữ liệu tồn kho |
| Đầu vào | Lag, rolling mean/std tính đến mốc cắt; thứ, tháng; cờ event, SNAP theo bang; giá, mức thay đổi giá; mã store/dept/cat | Như PA1, tổng hợp theo department | – |
| Đầu ra | Số thực ≥ 0 (đơn vị sản phẩm) cho 28 ngày | Số thực ≥ 0 cho 28 ngày | Xác suất trong [0, 1] |
| Ràng buộc | Chạy trên Google Colab; xử lý được 62–77% giá trị 0; chỉ ra được yếu tố chính của dự báo | Như PA1 | – |
| Ngoài phạm vi | Tối ưu giá; khôi phục nhu cầu thật khi hết hàng; mặt hàng mới chưa có lịch sử (cold-start) | Như PA1 | – |
| Mức đáp ứng câu nhu cầu | Trực tiếp: ra số lượng cho từng đơn đặt hàng | Một phần: hỗ trợ ngân sách theo ngành, không ra đơn cho từng mặt hàng | Không đáp ứng được |

**Kiểm tra rò rỉ dữ liệu:**

- Mốc cắt là đầu tuần; mọi lag/rolling kết thúc tại mốc cắt. Dự báo trực tiếp 28 ngày thì lag ≥ 28; nếu dùng lag ngắn hơn phải dự báo đệ quy.
- Event, SNAP được biết trước từ lịch.
- Giá bán giả định là giá kế hoạch đã biết trước (ghi rõ giả định).

---

## Phần 4. Thẩm định tính khả thi

### 4.1. Kết quả kiểm chứng nhanh

| Kiểm chứng | PA1 | PA2 |
|---|---|---|
| (1) Tạo biến mục tiêu, phân bố | % số 0 sau khi cắt giai đoạn chưa ra mắt: [cần chạy] | Phân bố doanh số 70 chuỗi, % số 0: [cần chạy] |
| (2) Số mẫu sau lọc | Số chuỗi × số ngày trong phạm vi đã chọn, dung lượng RAM: [cần chạy] | 70 × 1.941 = 135.870 dòng |
| (3) Baseline | Seasonal-naive (tuần trước) và trung bình 28 ngày, RMSSE trên 28 ngày cuối; 1 mô hình cây đơn giản để kiểm tra có vượt baseline: [cần chạy] | Tương tự: [cần chạy] |

PA3 không chạy kiểm chứng vì không tạo được biến mục tiêu.

### 4.2. Bảng tổng hợp thẩm định

| Phương án | Dữ liệu | Kỹ thuật | Nguồn lực | Đạo đức – pháp lý | Kết luận |
|---|---|---|---|---|---|
| PA1 | Đạt: [số mẫu sau lọc]; nhãn có sẵn; chặn rò rỉ bằng mốc cắt | Đạt khi thu hẹp phạm vi: [thời gian chạy; RMSSE baseline vs mô hình] | [số thành viên, số tuần còn lại, kế hoạch sơ bộ] | Đạt: không có dữ liệu cá nhân; [trích giấy phép] | **Đề nghị chọn** |
| PA2 | Đạt: ít số 0, chuỗi mượt | Đạt: tính toán nhẹ | Đạt | Đạt | Khả thi nhưng chỉ đáp ứng một phần; giữ làm phân tích bổ trợ |
| PA3 | Không đạt: không có tồn kho, không tạo được nhãn đáng tin | Không xét | Không xét | Không xét | Loại |

### 4.3. Phương án đề nghị

Nhóm đề nghị PA1 vì đây là phương án duy nhất cho ra số lượng đến từng mặt hàng–cửa hàng, đúng với quyết định đặt hàng hằng tuần. PA2 được giữ làm phân tích bổ trợ để đối chiếu tổng dự báo theo department. Rủi ro lớn nhất là quy mô dữ liệu và tỷ lệ số 0 cao khiến mô hình dự báo lệch về 0. Nhóm giới hạn phạm vi ở [1 bang / 1 ngành, 2 năm gần nhất] và dùng hàm mất mát dành cho dữ liệu đếm. Nếu vẫn vượt tài nguyên, nhóm chuyển sang PA2.

---

## Phụ lục

- Notebook kiểm chứng nhanh: `<MãLớp>_<TênNhóm>_DeXuat_Code.ipynb`
- Bảng % số 0 theo ngành, theo cửa hàng; bảng số 0 cấu trúc
- Heatmap doanh số thứ × tháng; biểu đồ tác động SNAP lên FOODS

---

## Ghi chú nội bộ (xóa trước khi nộp)

- Bản thuyết minh ghi 1.913 ngày (file validation); file evaluation có 1.941 ngày. Chốt một file.
- 42.840 là tổng chuỗi của cả 12 cấp phân cấp; cấp item–store chỉ có 30.490 chuỗi.
- Tên đề tài cũ ("store – department") không khớp với Mục 3 (item–store).
- "Event không làm tăng doanh số do trùng ngày đóng cửa": chỉ 25/12 đóng cửa. Bỏ 25/12 rồi so sánh lại.
- "Top 50/50 đội dùng LightGBM": kiểm lại với bài báo M5 trước khi viết.
- Tài liệu tham khảo: [1] trích bài "Background, organization…" nhưng nội dung lấy từ bài "Results, findings and conclusions"; [2] Hobor ghi sai tác giả và tên bài.
