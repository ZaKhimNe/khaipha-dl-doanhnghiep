# BẢN ĐỀ XUẤT ĐỀ TÀI – MÔN DS317

> Ký hiệu: **[cần chạy]** = số liệu nhóm tự tính từ notebook; **[tự đếm lại]** = số đã có từ Lab 1–2, cần xác nhận lại trên tệp.

## Thông tin chung

| Mục | Nội dung |
|---|---|
| Tên đề tài dự kiến (tiếng Việt) | Dự báo doanh thu 4 tuần tới theo danh mục sản phẩm cho doanh nghiệp bán lẻ thời trang thương mại điện tử, hỗ trợ lập ngân sách nhập hàng và khuyến mãi |
| Tên đề tài dự kiến (tiếng Anh) | 4-Week Category-Level Revenue Forecasting for a Fashion E-commerce Retailer to Support Purchasing and Promotion Budgeting |
| Tên nhóm, lớp | [..], DS317.R11 |
| Thành viên (họ tên, MSSV, email) | [..] |
| Nhóm trưởng (họ tên, MSSV, email, điện thoại) | [..] |
| Ngày nộp | [..] |

---

## Phần 1. Rà soát tài sản dữ liệu

### 1.1. Danh sách nguồn dữ liệu

| Nguồn | Mô tả ngắn | Đường dẫn / cách thu thập | Giấy phép | Ngày truy cập | Mỗi dòng là gì |
|---|---|---|---|---|---|
| order_items | Chi tiết đơn hàng | Bộ dữ liệu BTC Datathon 2026 cung cấp | [ghi điều khoản sử dụng của BTC] | [..] | 1 SKU trong 1 đơn hàng |
| orders | Đơn hàng | như trên | như trên | [..] | 1 đơn hàng |
| products | Danh mục sản phẩm | như trên | như trên | [..] | 1 SKU |
| inventory | Ảnh chụp tồn kho | như trên | như trên | [..] | 1 sản phẩm tại 1 thời điểm snapshot |
| sales.csv | Doanh thu tổng hợp theo ngày | như trên | như trên | [..] | 1 ngày |
| traffic | Lượng truy cập web | như trên | như trên | [..] | [1 ngày – cần xác nhận] |
| customers, payments, shipments, reviews … | Các bảng còn lại (tổng 14 bảng) | như trên | như trên | [..] | [cần điền] |

Khóa nối chính: `order_items.order_id` ↔ `orders`; `order_items.product_id` ↔ `products` (lấy category); `inventory.product_id` ↔ `products`; ngày ↔ `sales`, `traffic`.

### 1.2. Bảng kiểm kê

| Tiêu chí | Kết quả của nhóm | Đánh giá |
|---|---|---|
| Nguồn gốc | Dữ liệu mô phỏng do BTC Datathon 2026 cung cấp; điều khoản: [..]; cần xác nhận được phép dùng cho môn học và công bố kết quả | Cần lưu ý (đến khi ghi được điều khoản) |
| Quy mô | order_items 714.669 dòng (646.945 đơn, 3.213.143 đơn vị); products 2.412 SKU; inventory 60.247 snapshot / 1.624 sản phẩm; sales ~3.650 ngày [tự đếm lại]; customers, traffic, reviews, payments, shipments: [cần chạy] | Đạt |
| Cấu trúc | Có cấu trúc, CSV, 14 bảng quan hệ; 4 danh mục: Streetwear, Outdoor, Casual, GenZ | Đạt |
| Nhãn | Có sẵn doanh thu ở 2 nguồn: sales.csv (vĩ mô) và tổng hợp từ order_items (vi mô), lệch trung bình +5,17%, có ngày tới ~20%. Chọn order_items làm ground truth vì truy vết được tới SKU/danh mục | Cần lưu ý |
| Chất lượng | Traffic thiếu 181 ngày đầu 2012 (4,7%); 73,8% đơn đặt trước ngày tạo tài khoản; 18,6% item bán dưới giá vốn; 10,0% ngày lãi gộp âm; 0,1% đơn không có mã vận đơn; 62,16% đơn lệch nếu cộng nhầm phí ship; 67,3% lần quan sát tồn kho ghi nhận hết hàng | Cần lưu ý |
| Thời gian | 2012–2022, theo ngày (~10 năm); tách được train/validation/test theo năm | Đạt |
| Tính riêng tư | Dữ liệu mô phỏng; bảng customers: [liệt kê cột có dạng định danh – tên, email, SĐT, địa chỉ – và cách xử lý] | [Đạt / Cần lưu ý – cần chạy] |

### 1.3. Nhận định

- **Cho phép:** dự báo doanh thu/số lượng theo ngày hoặc tuần ở cấp danh mục và SKU; phân tích mùa vụ (đỉnh Thứ 4–5, Tháng 4–6); phân cụm kịch bản vận hành theo ngày.
- **Không cho phép:** dùng thời gian gắn bó của khách hàng (signup_date mâu thuẫn ở 73,8% đơn); phân tích biên lợi nhuận đáng tin (18,6% item dưới giá vốn, 10% ngày lãi gộp âm).
- **Giới hạn 1:** doanh thu quan sát được là nhu cầu đã bị cắt khi hết hàng (67,3% lần quan sát hết hàng), nên mô hình có thể học thấp hơn nhu cầu thật.
- **Giới hạn 2:** ở cấp danh mục × tuần chỉ có 4 × ~520 = ~2.080 mẫu; nếu cần nhiều mẫu hơn phải xuống cấp ngày hoặc SKU.
- **Giới hạn 3:** dữ liệu mô phỏng, kết luận nghiệp vụ không tổng quát trực tiếp cho thị trường thật.

---

## Phần 2. Bối cảnh và nhu cầu của doanh nghiệp

### 2.1. Các yếu tố bối cảnh

| Yếu tố | Nội dung |
|---|---|
| Doanh nghiệp / lĩnh vực | **Bối cảnh giả định** theo dữ liệu Datathon 2026: sàn thương mại điện tử thời trang, 4 danh mục (Streetwear, Outdoor, Casual, GenZ), 2.412 SKU, ~646.945 đơn trong 2012–2022; doanh thu ngày trung bình 4,30 tỷ, đỉnh Tháng 4–6 |
| Chủ thể ra quyết định | Bộ phận Kế hoạch – Vận hành |
| Quyết định cần hỗ trợ | Đầu mỗi tuần, chốt ngân sách nhập hàng và ngân sách khuyến mãi cho từng danh mục trong 4 tuần tới |
| Hiện trạng | Lập kế hoạch theo kinh nghiệm, chưa có dự báo định lượng theo danh mục. Mô phỏng hiện trạng làm baseline: doanh thu cùng kỳ năm trước hoặc trung bình 4 tuần gần nhất |
| Chi phí của việc làm sai | Dự báo thấp dẫn đến nhập thiếu, hết hàng; dữ liệu cho thấy 8,36% nhu cầu bị mất, ~445 tỷ doanh thu tiềm năng [tự đếm lại]. Dự báo cao dẫn đến tồn dư phải xả hàng, biên lãi gộp rơi về khoảng -40% trong các đợt xả hằng năm. Hai loại sai đều tốn kém; cần ước lượng chi phí trên mỗi đồng sai lệch cho từng loại để chọn độ đo |
| Chỉ số nghiệp vụ (KPI) | Tỷ lệ nhu cầu bị mất do hết hàng; biên lãi gộp trong các đợt xả hàng; WMAPE doanh thu theo danh mục |

### 2.2. Câu phát biểu nhu cầu nghiệp vụ

> Bộ phận Kế hoạch – Vận hành cần dự báo, vào đầu mỗi tuần, doanh thu của từng danh mục sản phẩm trong 4 tuần tới, để phân bổ ngân sách nhập hàng và khuyến mãi theo danh mục, nhằm giảm tỷ lệ nhu cầu bị mất do hết hàng và giảm các đợt xả hàng lỗ.

---

## Phần 3. Phát biểu bài toán khai phá dữ liệu

| Thành phần | Phương án 1 – Dự báo doanh thu theo danh mục | Phương án 2 – Dự báo số lượng theo SKU | Phương án 3 – Phân cụm kịch bản vận hành |
|---|---|---|---|
| Nhóm bài toán | Chuỗi thời gian / hồi quy, có giám sát | Chuỗi thời gian / hồi quy (dữ liệu đếm), có giám sát | Gom cụm, không giám sát |
| Đơn vị phân tích | 1 danh mục × 1 tuần dự báo (có thể mô hình theo ngày rồi cộng lên tuần) | 1 SKU × 1 tuần | 1 ngày |
| Cho trước | Doanh thu, số đơn, số lượng, traffic, khuyến mãi, tồn kho theo danh mục đến mốc cắt | Lịch sử bán theo SKU, giá, khuyến mãi, tồn kho đến mốc cắt | Các chỉ số vận hành theo ngày (doanh thu, số đơn, chiết khấu, lãi gộp, tỷ lệ hết hàng) |
| Cần tìm | Doanh thu của từng danh mục trong mỗi tuần của 4 tuần sau mốc cắt | Số lượng bán của từng SKU trong 4 tuần tới | 3–5 nhóm ngày có kiểu vận hành khác nhau |
| Biến mục tiêu | Tổng `doanh thu` từ order_items (không gồm phí ship) theo (danh mục, tuần t+h), h = 1..4 | Tổng `quantity` theo (SKU, tuần t+h) | Không cần nhãn |
| Đầu vào | Lag/rolling của doanh thu, số đơn, số lượng (tính đến mốc cắt); tuần, tháng, mùa cao điểm; mức chiết khấu kế hoạch; tồn kho tại mốc cắt. Không dùng COGS, signup_date | Như PA1 ở cấp SKU, thêm thuộc tính sản phẩm | Chỉ số vận hành đã chuẩn hóa |
| Đầu ra | Doanh thu (VNĐ), số thực ≥ 0, cho 4 tuần × 4 danh mục | Số lượng ≥ 0 cho 4 tuần × mỗi SKU | Nhãn cụm cho mỗi ngày và hồ sơ từng cụm |
| Ràng buộc | Chạy trên Colab; chỉ ra được yếu tố chính của dự báo | Như PA1; phải xử lý nhiều SKU bán thưa | Cụm phải diễn giải được cho nghiệp vụ |
| Ngoài phạm vi | Dự báo cấp SKU; tối ưu giá; mặt hàng mới (cold-start) | Tối ưu giá; cold-start | Dự báo |
| Mức đáp ứng câu nhu cầu | Trực tiếp: ra doanh thu theo danh mục cho ngân sách | Một phần: phục vụ đơn nhập theo SKU, chi tiết hơn mức ngân sách cần; dữ liệu thưa hơn | Gián tiếp: mô tả bối cảnh, dùng làm đặc trưng cho PA1 |

**Kiểm tra rò rỉ dữ liệu:**

- Số đơn và số lượng bán tương quan rất cao với doanh thu (r = 0,938 và 0,922) nhưng là giá trị cùng kỳ; chỉ được dùng bản lag trước mốc cắt.
- Loại COGS (r = 0,976) vì được tính từ chính giao dịch cần dự báo.
- Mức chiết khấu chỉ dùng giá trị kế hoạch biết trước; nếu dữ liệu chỉ có chiết khấu thực tế thì chỉ dùng bản lag.
- Tồn kho chỉ dùng snapshot gần nhất trước mốc cắt.

---

## Phần 4. Thẩm định tính khả thi

### 4.1. Kết quả kiểm chứng nhanh

| Kiểm chứng | PA1 | PA2 | PA3 |
|---|---|---|---|
| (1) Tạo biến mục tiêu / bảng đặc trưng | Chuỗi doanh thu tuần của 4 danh mục; phân bố, % tuần bằng 0: [cần chạy] | % tuần bán = 0 theo SKU: [cần chạy] | Bảng chỉ số theo ngày; phân bố từng chỉ số: [cần chạy] |
| (2) Số mẫu sau lọc | Số tuần × 4 danh mục sau khi bỏ đơn không có mã vận đơn: [cần chạy] | Số SKU còn lịch sử đủ dài × số tuần: [cần chạy] | ~3.650 ngày (4 cụm từ PCA ở Lab 2: 42,7% / 21,4% / 20,5% / 15,3%) |
| (3) Baseline | Seasonal-naive (cùng kỳ năm trước) và trung bình 4 tuần; WMAPE, MAE trên 2021–2022; 1 mô hình cây đơn giản: [cần chạy] | Tương tự: [cần chạy] | Silhouette cho k = 3..6: [cần chạy] |

### 4.2. Bảng tổng hợp thẩm định

| Phương án | Dữ liệu | Kỹ thuật | Nguồn lực | Đạo đức – pháp lý | Kết luận |
|---|---|---|---|---|---|
| PA1 | Đạt: nhãn tạo được từ order_items; [số mẫu]; đã loại COGS, signup_date; chặn rò rỉ bằng mốc cắt | [Thời gian chạy; WMAPE baseline vs mô hình] | [số thành viên, số tuần còn lại] | [Trích điều khoản BTC; xử lý cột định danh trong customers] | **Đề nghị chọn** |
| PA2 | [Đạt / Cần lưu ý: tỷ lệ tuần bằng 0 ở SKU] | [cần chạy] | Nặng hơn PA1 | Như PA1 | Dự phòng nếu giảng viên yêu cầu mức chi tiết SKU |
| PA3 | Đạt: đã có kết quả PCA từ Lab 2 | Đạt | Đạt | Như PA1 | Giữ làm phân tích bổ trợ; nhãn cụm dùng làm đặc trưng cho PA1 |

### 4.3. Phương án đề nghị

Nhóm đề nghị PA1 vì trả lời trực tiếp quyết định phân bổ ngân sách nhập hàng và khuyến mãi theo danh mục mỗi tuần. PA3 được giữ làm phân tích bổ trợ, nhãn kịch bản vận hành dùng làm đặc trưng. Rủi ro lớn nhất là doanh thu bị cắt do hết hàng (67,3% lần quan sát hết hàng), khiến mô hình học thấp hơn nhu cầu thật; nhóm sẽ so sánh kết quả có và không điều chỉnh theo tỷ lệ ngày có hàng trên tập validation. Rủi ro thứ hai là số mẫu ở cấp danh mục × tuần ít; nếu mô hình không vượt baseline, nhóm chuyển sang mô hình ở cấp ngày rồi cộng lên tuần.

---

## Phụ lục

- Notebook kiểm chứng nhanh: `<MãLớp>_<TênNhóm>_DeXuat_Code.ipynb`
- Bảng đối soát doanh thu sales.csv vs order_items theo ngày
- Bảng % thiếu, % mâu thuẫn theo bảng
- Heatmap doanh thu thứ × tháng; biểu đồ PCA 4 kịch bản vận hành

---

## Ghi chú nội bộ (xóa trước khi nộp)

- Định nghĩa "67,3% lần quan sát hết hàng" cần ghi rõ (theo snapshot, theo sản phẩm hay theo ngày); tỷ lệ này rất cao, giảng viên dễ hỏi.
- Con số 445 tỷ và 8,36% nhu cầu mất cần có cách tính trong notebook.
- Quyết định "nhập hàng" thực tế cần số lượng theo SKU; PA1 chỉ phục vụ mức ngân sách. Câu nhu cầu đã viết theo ngân sách để khớp.
- Bản thuyết minh dự thảo ghi "Chuỗi doanh thu theo ngày/tuần": chốt một đơn vị.
- Bản thuyết minh dùng MAPE; khi doanh thu có ngày thấp, ưu tiên WMAPE/sMAPE.
- Log-transform và CatBoost Encoder cho `store_type`: kiểm tra dữ liệu có cột này không (bối cảnh là thương mại điện tử).
