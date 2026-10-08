"""
Add the 4th tab: 'Giải Thích Thuật Ngữ (Technical Terminology)' to web/index.html.
Features real-time search, category filtering, and in-depth explanations
covering Missing Values, Data Dirtiness, Statistical Tests, and Supply Chain Metrics.
"""

import os, sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting"
html_path = os.path.join(BASE_DIR, "web", "index.html")

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Sidebar Navigation to add Tab 4 button
old_nav = """        <button class="nav-btn" onclick="switchTab('submissions')">
          <span class="nav-icon">📦</span>
          <span>Nộp Bài &amp; Kho Tạo Tác</span>
        </button>"""

new_nav = """        <button class="nav-btn" onclick="switchTab('terminology')">
          <span class="nav-icon">📖</span>
          <span>Giải Thích Thuật Ngữ</span>
        </button>
        <button class="nav-btn" onclick="switchTab('submissions')">
          <span class="nav-icon">📦</span>
          <span>Nộp Bài &amp; Kho Tạo Tác</span>
        </button>"""

if old_nav in html:
    html = html.replace(old_nav, new_nav)
    print("Sidebar navigation updated with Terminology tab button.")
else:
    print("Warning: old_nav not found exactly, check nav markup.")

# 2. Add Terminology Tab HTML Content
terminology_html = """
    <!-- TAB 4: GIẢI THÍCH THUẬT NGỮ KỸ THUẬT (TECHNICAL TERMINOLOGY) -->
    <section id="tab-terminology" class="tab-pane">
      <div class="top-header">
        <div>
          <h1 class="page-title">Từ Điển Thuật Ngữ Kỹ Thuật (Data Science &amp; Supply Chain Glossary)</h1>
          <p class="page-desc">Giải mã chi tiết các khái niệm thống kê, độ "bẩn" của dữ liệu (Missing Values, Leaks), và chỉ số chuỗi cung ứng được sử dụng trong dự án.</p>
        </div>
        <div class="header-actions">
          <span class="badge" style="background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.4); color: #60a5fa; font-weight: 700;">24 Thuật Ngữ Chuẩn Hóa</span>
        </div>
      </div>

      <!-- Thanh Tìm Kiếm & Bộ Lọc Nhanh -->
      <div style="background: #131b2e; border: 1px solid var(--card-border); border-radius: 12px; padding: 18px 24px; margin-bottom: 26px; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 280px;">
          <span style="font-size: 18px; color: var(--text-muted);">🔍</span>
          <input type="text" id="term-search" placeholder="Tìm kiếm thuật ngữ (ví dụ: Missing values, KS-test, COGS, AOV, Bootstrap, Leakage...)" 
                 oninput="filterTerminology()" 
                 style="width: 100%; background: #0b0f19; border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; color: #fff; font-size: 13.5px; outline: none;">
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="term-filter-pills">
          <button class="filter-pill active" onclick="setTermCategory('all')">Tất Cả</button>
          <button class="filter-pill" onclick="setTermCategory('dirtiness')">Độ "Bẩn" &amp; Chất Lượng Dữ Liệu</button>
          <button class="filter-pill" onclick="setTermCategory('statistics')">Thống Kê &amp; Toán Học</button>
          <button class="filter-pill" onclick="setTermCategory('supplychain')">Kinh Tế &amp; Chuỗi Cung Ứng</button>
          <button class="filter-pill" onclick="setTermCategory('timeseries')">Chuỗi Thời Gian &amp; ML</button>
        </div>
      </div>

      <!-- Danh Sách Thuật Ngữ Dạng Lưới Thẻ -->
      <div id="terminology-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 18px; margin-bottom: 40px;">

        <!-- 1. MISSING VALUES -->
        <div class="term-card" data-cat="dirtiness" data-keywords="missing values khuyet du lieu null nan sentinel mcar mar mnar imputation dien khuyet">
          <div class="term-header">
            <div>
              <span class="term-en">Missing Values</span>
              <h3 class="term-vi">Giá Trị Thiếu / Khuyết Dữ Liệu</h3>
            </div>
            <span class="term-tag dirtiness">Chất Lượng Dữ Liệu</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Các ô dữ liệu không có giá trị (NULL, NaN, None) hoặc chứa <em>giá trị lính canh</em> (Sentinel values như <code>-999</code>, <code>"Unknown"</code>, hoặc <code>0</code> thay cho giá trị không xác định).</p>
            <div class="term-box">
              <span style="color: #60a5fa; font-weight: bold;">3 Cơ chế khuyết thiếu:</span>
              <ul style="margin: 6px 0 0 16px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                <li><strong>MCAR (Missing Completely at Random):</strong> Thiếu hoàn toàn ngẫu nhiên, không phụ thuộc vào bất kỳ biến nào.</li>
                <li><strong>MAR (Missing at Random):</strong> Thiếu phụ thuộc vào một biến khác (ví dụ: khách không áp mã thì <code>promo_id</code> bị thiếu 61.34%).</li>
                <li><strong>MNAR (Missing Not at Random):</strong> Thiếu phụ thuộc vào chính giá trị của nó.</li>
              </ul>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Trong Datathon 2026:</strong> <code>promo_id_2</code> bị khuyết 99.97% (hầu như không xếp chồng khuyến mãi), và 181 ngày đầu tiên của năm 2012 bị khuyết toàn bộ dữ liệu web traffic.</p>
          </div>
        </div>

        <!-- 2. DATA LEAKAGE -->
        <div class="term-card" data-cat="dirtiness" data-keywords="data leakage ro ri du lieu train test target leakage lookahead bias">
          <div class="term-header">
            <div>
              <span class="term-en">Data Leakage</span>
              <h3 class="term-vi">Rò Rỉ Dữ Liệu</h3>
            </div>
            <span class="term-tag dirtiness">Chất Lượng Dữ Liệu</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Hiện tượng thông tin từ tập kiểm thử (Test set) hoặc thông tin trong tương lai bị vô tình sử dụng để huấn luyện mô hình trong quá khứ.</p>
            <div class="term-box">
              <span style="color: #ef4444; font-weight: bold;">Hậu quả:</span> Mô hình đạt độ chính xác ảo cực kỳ cao trên tập Train/Validation, nhưng khi dự báo thực tế ngoài đời thì hoàn toàn sụp đổ do không còn "nhìn lén" được đáp án tương lai.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Quy tắc khắc phục:</strong> Chỉ được chuẩn hóa (Scaler) hoặc tính Moving Average dựa trên dữ liệu quá khứ ($t \le \text{cutoff}$), tuyệt đối không peeking về tương lai.</p>
          </div>
        </div>

        <!-- 3. TIME-TRAVEL PARADOX -->
        <div class="term-card" data-cat="dirtiness" data-keywords="time travel temporal paradox vi pham nhan qua signup date order date">
          <div class="term-header">
            <div>
              <span class="term-en">Temporal Causality Violation</span>
              <h3 class="term-vi">Vi Phạm Nhân Quả Thời Gian</h3>
            </div>
            <span class="term-tag dirtiness">Chất Lượng Dữ Liệu</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Trình tự thời gian bị đảo lộn phi lý học (Hành động xảy ra trước điều kiện tiên quyết).</p>
            <div class="term-box">
              <span style="color: #ef4444; font-weight: bold;">Phát hiện chấn động:</span> Có tới <strong>477,453 đơn hàng (73.80%)</strong> có ngày mua hàng diễn ra <em>trước ngày tạo tài khoản</em> (order_date &lt; signup_date) tới vài năm!
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Cạm bẫy:</strong> Bất kỳ ai tính toán biến thâm niên <code>order_date - signup_date</code> sẽ gặp 73.8% giá trị âm vô lý.</p>
          </div>
        </div>

        <!-- 4. PHANTOM FULFILLMENT -->
        <div class="term-card" data-cat="dirtiness" data-keywords="phantom fulfillment don ma van chuyen shipments delivered missing shipment">
          <div class="term-header">
            <div>
              <span class="term-en">Phantom Fulfillment</span>
              <h3 class="term-vi">Giao Dịch "Ma" / Thiếu Đối Soát Vận Chuyển</h3>
            </div>
            <span class="term-tag dirtiness">Chất Lượng Dữ Liệu</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Đơn hàng ghi nhận đã hoàn thành giao dịch nhưng thiếu hoàn toàn hồ sơ vật lý hoặc bằng chứng vận đơn trong bảng logistics.</p>
            <div class="term-box">
              <span style="color: #f59e0b; font-weight: bold;">Thực tế Datathon:</span> Có <strong>524 đơn delivered</strong>, <strong>29 đơn returned</strong> và <strong>11 đơn shipped</strong> (tổng 564 đơn) không hề tồn tại bất kỳ dòng nào trong bảng <code>shipments.csv</code>.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Giải pháp:</strong> Phải xử lý bằng outer join và gắn cờ cảnh báo rủi ro gian lận hoặc lỗi hệ thống ERP.</p>
          </div>
        </div>

        <!-- 5. KS TEST -->
        <div class="term-card" data-cat="statistics" data-keywords="kolmogorov smirnov ks test kiem dinh phan phoi sampling stratified">
          <div class="term-header">
            <div>
              <span class="term-en">Kolmogorov-Smirnov (KS) Test</span>
              <h3 class="term-vi">Kiểm Định Kolmogorov-Smirnov</h3>
            </div>
            <span class="term-tag statistics">Thống Kê &amp; Toán</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Phép kiểm định phi tham số so sánh hàm phân phối tích lũy (Cumulative Distribution Function - CDF) của 2 mẫu dữ liệu để xác định xem chúng có cùng một phân phối gốc hay không.</p>
            <div class="term-box">
              <strong>Tiêu chí đánh giá:</strong> Khoảng cách $D$ càng nhỏ và $p\text{-value} &gt; 0.05$ chứng minh 2 phân phối không có sự khác biệt có ý nghĩa thống kê.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Kết quả đạt được:</strong> Mẫu phân tầng 150k dòng đạt $D = 0.00223, p = 0.5702$, chứng minh sự đồng nhất hoàn hảo với quần thể 714k dòng.</p>
          </div>
        </div>

        <!-- 6. BOOTSTRAP CI -->
        <div class="term-card" data-cat="statistics" data-keywords="bootstrap confidence interval khoang tin cay tai lay mau resampling">
          <div class="term-header">
            <div>
              <span class="term-en">Bootstrap Confidence Interval (95%)</span>
              <h3 class="term-vi">Khoảng Tin Cậy Bootstrap 95%</h3>
            </div>
            <span class="term-tag statistics">Thống Kê &amp; Toán</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Kỹ thuật mô phỏng thống kê không tham số bằng cách tái lấy mẫu ngẫu nhiên có hoàn lại (Resampling with replacement) lặp lại $N=2,000$ lần để tìm phân phối của tham số cần ước lượng.</p>
            <div class="term-box">
              <strong>Ưu điểm vượt trội:</strong> Không đòi hỏi dữ liệu phải tuân theo phân phối chuẩn (Normal Distribution). Rất mạnh khi dữ liệu bị lệch (skewed) hoặc có giá trị âm.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Áp dụng:</strong> Doanh thu trung bình được chốt trong khoảng chặt chẽ [$4.20M, $4.37M] VNĐ/ngày với độ tin cậy 95%.</p>
          </div>
        </div>

        <!-- 7. COHEN'S D -->
        <div class="term-card" data-cat="statistics" data-keywords="cohens d effect size do lon hieu ung thong ke">
          <div class="term-header">
            <div>
              <span class="term-en">Cohen's d (Effect Size)</span>
              <h3 class="term-vi">Độ Lớn Hiệu Ứng Cohen's d</h3>
            </div>
            <span class="term-tag statistics">Thống Kê &amp; Toán</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Thước đo tiêu chuẩn định lượng độ lớn của sự khác biệt giữa hai trung bình nhóm, chia cho độ lệch chuẩn gộp.</p>
            <div class="term-box">
              <strong>Thang đo chuẩn hóa:</strong>
              <ul style="margin: 4px 0 0 16px; font-size: 11.5px; color: #cbd5e1;">
                <li>$d = 0.2$: Hiệu ứng nhỏ (Small)</li>
                <li>$d = 0.5$: Hiệu ứng trung bình (Medium)</li>
                <li>$d &gt; 0.8$: Hiệu ứng lớn (Large Effect Size - có giá trị thực tiễn kinh doanh cao)</li>
              </ul>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Kết quả dự án:</strong> Đạt $d = 1.48$, chứng minh cải tiến mô hình vượt trội vượt bậc so với ngẫu nhiên.</p>
          </div>
        </div>

        <!-- 8. STL DECOMPOSITION -->
        <div class="term-card" data-cat="timeseries" data-keywords="stl decomposition phan ra chuoi thoi gian trend seasonal residual">
          <div class="term-header">
            <div>
              <span class="term-en">STL Decomposition</span>
              <h3 class="term-vi">Phân Rã Chuỗi Thời Gian STL</h3>
            </div>
            <span class="term-tag timeseries">Chuỗi Thời Gian &amp; ML</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Viết tắt của <em>Seasonal and Trend decomposition using Loess</em>. Kỹ thuật tách chuỗi thời gian $Y_t$ thành 3 thành phần riêng biệt:</p>
            <div class="term-box">
              $$Y_t = \text{Trend}_t + \text{Seasonal}_t + \text{Residual}_t$$
              <ul style="margin: 4px 0 0 16px; font-size: 11.5px; color: #cbd5e1;">
                <li><strong>Trend:</strong> Xu hướng tăng/giảm vĩ mô trong dài hạn (10 năm).</li>
                <li><strong>Seasonal:</strong> Biến động tuần hoàn lặp lại (theo thứ trong tuần, tháng trong năm).</li>
                <li><strong>Residual:</strong> Nhiễu ngẫu nhiên hoặc các cú sốc bất thường.</li>
              </ul>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Ứng dụng:</strong> Giúp mô hình bắt đúng chu kỳ mua sắm cuối tuần và mùa giảm giá cuối năm.</p>
          </div>
        </div>

        <!-- 9. PCA -->
        <div class="term-card" data-cat="statistics" data-keywords="pca principal component analysis giam chieu du lieu explained variance">
          <div class="term-header">
            <div>
              <span class="term-en">Principal Component Analysis (PCA)</span>
              <h3 class="term-vi">Phân Tích Thành Phần Chính (PCA)</h3>
            </div>
            <span class="term-tag statistics">Thống Kê &amp; Toán</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Thuật toán giảm chiều dữ liệu tuyến tính bằng cách biến đổi một tập hợp các biến có tương quan thành các biến độc lập trực giao gọi là các Thành phần chính (Principal Components).</p>
            <div class="term-box">
              <strong>Tỷ lệ phương sai giải thích:</strong> Mỗi trục giữ lại bao nhiêu phần trăm thông tin gốc. PC1 và PC2 giữ lại <strong>85.3% phương sai</strong> trong bài toán kinh doanh này.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Triển khai:</strong> Thực hiện bằng đại số tuyến tính NumPy thuần túy, tiêu hao 0% GPU.</p>
          </div>
        </div>

        <!-- 10. GROSS GMV VS NET REVENUE -->
        <div class="term-card" data-cat="supplychain" data-keywords="gross gmv net revenue doanh thu gop doanh thu thuan discount">
          <div class="term-header">
            <div>
              <span class="term-en">Gross GMV vs Net Revenue</span>
              <h3 class="term-vi">Doanh Thu Gộp (GMV) vs Doanh Thu Thuần</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Sự phân biệt mang tính quyết định trong tài chính doanh nghiệp:</p>
            <div class="term-box">
              <ul style="margin: 0 0 0 16px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                <li><strong>Gross GMV:</strong> Tổng giá trị đơn hàng trước chiết khấu = $\sum (\text{Qty} \times \text{Unit Price})$.</li>
                <li><strong>Net Revenue:</strong> Doanh thu thực tế sau khi trừ khuyến mãi = $\text{Gross GMV} - \text{Discounts}$.</li>
              </ul>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Bẫy dữ liệu:</strong> Cột <code>Revenue</code> trong <code>sales.csv</code> là Gross GMV, trong khi số tiền khách thực trả ở <code>payments.csv</code> là Net Revenue. Lệch bình quân 195k VNĐ/ngày do chiết khấu.</p>
          </div>
        </div>

        <!-- 11. COGS -->
        <div class="term-card" data-cat="supplychain" data-keywords="cogs cost of goods sold gia von hang ban chi phi">
          <div class="term-header">
            <div>
              <span class="term-en">COGS (Cost of Goods Sold)</span>
              <h3 class="term-vi">Giá Vốn Hàng Bán</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Chi phí trực tiếp phát sinh từ việc sản xuất hoặc nhập khẩu sản phẩm được bán ra trong kỳ kế toán (nguyên vật liệu, chi phí thu mua, đóng gói cơ bản).</p>
            <div class="term-box">
              $$\text{COGS} = \sum (\text{Quantity} \times \text{Unit COGS})$$
              Không bao gồm chi phí bán hàng, quảng cáo marketing hay chi phí quản lý doanh nghiệp.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Quan sát thực nghiệm:</strong> COGS trong <code>sales.csv</code> khớp hoàn hảo 100% ($r = 1.000000, \text{MAE} = 0.002$) với dữ liệu vi mô trong <code>order_items.csv</code> ghép <code>products.csv</code>.</p>
          </div>
        </div>

        <!-- 12. SELLING BELOW COGS -->
        <div class="term-card" data-cat="supplychain" data-keywords="selling below cogs ban duoi gia von pha gia negative margin">
          <div class="term-header">
            <div>
              <span class="term-en">Selling Below COGS</span>
              <h3 class="term-vi">Bán Dưới Giá Vốn (Lỗ Lũy Kế)</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Khi giá bán thực tế của sản phẩm nhỏ hơn chi phí nhập vốn ($\text{Unit Price} &lt; \text{COGS}$), dẫn đến lợi nhuận gộp âm trên từng món hàng.</p>
            <div class="term-box">
              <span style="color: #ef4444; font-weight: bold;">Tác động:</span> Có <strong>133,052 sản phẩm (18.62%)</strong> bị bán dưới giá vốn, dẫn đến <strong>382 ngày lỗ gộp</strong> (-192.22 triệu VNĐ lỗ lũy kế), tập trung sâu vào các năm lẻ (2013, 2015, 2017, 2019, 2021).
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Mục đích kinh doanh:</strong> Thường áp dụng để xả hàng tồn kho quá đát (Deadstock) hoặc chiến lược chiếm thị phần (Loss Leader).</p>
          </div>
        </div>

        <!-- 13. AOV -->
        <div class="term-card" data-cat="supplychain" data-keywords="aov average order value gia tri don hang trung binh">
          <div class="term-header">
            <div>
              <span class="term-en">AOV (Average Order Value)</span>
              <h3 class="term-vi">Giá Trị Đơn Hàng Trung Bình</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Số tiền trung bình mà một khách hàng chi tiêu trong một lần đặt hàng thành công:</p>
            <div class="term-box">
              $$\text{AOV} = \frac{\text{Tổng Doanh Thu Hàng Ngày}}{\text{Tổng Số Đơn Hàng Trong Ngày}}$$
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Ý nghĩa:</strong> AOV kết hợp với Lưu lượng (Traffic) và Tỷ lệ chuyển đổi (Conversion Rate) tạo thành 3 trụ cột doanh thu của sàn thương mại điện tử.</p>
          </div>
        </div>

        <!-- 14. STOCKOUT & DAYS OF SUPPLY -->
        <div class="term-card" data-cat="supplychain" data-keywords="stockout days of supply dut hang ton kho thieu hut">
          <div class="term-header">
            <div>
              <span class="term-en">Stockout &amp; Days of Supply</span>
              <h3 class="term-vi">Đứt Hàng &amp; Số Ngày Tồn Kho Dự Trữ</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong></p>
            <div class="term-box">
              <ul style="margin: 0 0 0 16px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                <li><strong>Stockout (Đứt hàng):</strong> Hàng tồn kho bằng 0 khiến khách không thể mua, phát sinh chi phí cơ hội thất thoát doanh thu (ước tính 444.8M VNĐ trong tập dữ liệu này).</li>
                <li><strong>Days of Supply:</strong> Số ngày tồn kho hiện tại đáp ứng được dựa trên tốc độ bán trung bình. $&gt; 90$ ngày là ứ đọng vốn, $&lt; 7$ ngày là báo động đỏ đứt hàng.</li>
              </ul>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Nghịch lý tồn kho:</strong> 76.3% sản phẩm bị ứ đọng trên 90 ngày nhưng các mặt hàng bán chạy lại thường xuyên cháy hàng.</p>
          </div>
        </div>

        <!-- 15. FILL RATE -->
        <div class="term-card" data-cat="supplychain" data-keywords="fill rate ty le dap ung don hang inventory chuoi cung ung">
          <div class="term-header">
            <div>
              <span class="term-en">Order Fill Rate</span>
              <h3 class="term-vi">Tỷ Lệ Đáp Ứng Đơn Hàng</h3>
            </div>
            <span class="term-tag supplychain">Kinh Tế &amp; Chuỗi Cung Ứng</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Tỷ lệ phần trăm nhu cầu của khách hàng được giao ngay lập tức từ lượng hàng sẵn có trong kho mà không bị trễ hoặc hủy bỏ:</p>
            <div class="term-box">
              $$\text{Fill Rate} = \frac{\text{Số lượng hàng giao được ngay}}{\text{Tổng số lượng khách yêu cầu}} \times 100\%$$
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Tiêu chuẩn ngành:</strong> Thương mại điện tử thời trang thường duy trì Fill Rate $\ge 95\%$. Nếu dưới 80%, tỷ lệ đánh giá 1-2 sao của khách sẽ tăng gấp đôi.</p>
          </div>
        </div>

        <!-- 16. PAYMENT RECONCILIATION -->
        <div class="term-card" data-cat="dirtiness" data-keywords="payment reconciliation doi soat thanh toan shipping fee payments">
          <div class="term-header">
            <div>
              <span class="term-en">Payment Reconciliation</span>
              <h3 class="term-vi">Đối Soát Dòng Tiền Thanh Toán</h3>
            </div>
            <span class="term-tag dirtiness">Chất Lượng Dữ Liệu</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Quy trình kiểm tra chéo giữa hệ thống ghi nhận đơn hàng, cổng thanh toán và bên giao vận để đảm bảo số tiền thực thu bằng số tiền hàng bán ra.</p>
            <div class="term-box">
              <span style="color: #10b981; font-weight: bold;">Sự thật bất ngờ:</span> <code>payments.csv</code> khớp 100% với tiền hàng thuần (<code>items_net</code>), nhưng nếu cộng phí ship vào sẽ có <strong>402,126 đơn hàng (62.16%)</strong> bị lệch tiền.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Kết luận:</strong> Phí vận chuyển trong bộ dữ liệu này là chính sách trợ giá Free Ship, không được thu thực tế từ khách.</p>
          </div>
        </div>

        <!-- 17. LAG FEATURES -->
        <div class="term-card" data-cat="timeseries" data-keywords="lag features dac trung tre autoregressive chuoi thoi gian">
          <div class="term-header">
            <div>
              <span class="term-en">Lag Features</span>
              <h3 class="term-vi">Đặc Trưng Trễ (Time Lag)</h3>
            </div>
            <span class="term-tag timeseries">Chuỗi Thời Gian &amp; ML</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Giá trị của chuỗi thời gian ở các bước quá khứ ($Y_{t-1}, Y_{t-7}, Y_{t-30}$) được sử dụng làm biến đầu vào để dự báo cho giá trị tương lai $Y_t$.</p>
            <div class="term-box">
              <strong>Quy tắc nhân quả:</strong> Khi dự báo cho ngày $t$, chỉ được dùng các giá trị trễ $t - k$ với $k \ge 1$. Nếu sử dụng $k \le 0$ sẽ phạm lỗi rò rỉ dữ liệu (Lookahead bias).
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Ứng dụng:</strong> Lag 7 ngày bắt nhịp tuần hoàn theo thứ trong tuần; Lag 365 ngày bắt nhịp chu kỳ năm.</p>
          </div>
        </div>

        <!-- 18. STATIONARITY -->
        <div class="term-card" data-cat="timeseries" data-keywords="stationarity tinh dung adf test dickey fuller differencing">
          <div class="term-header">
            <div>
              <span class="term-en">Stationarity &amp; ADF Test</span>
              <h3 class="term-vi">Tính Dừng &amp; Kiểm Định ADF</h3>
            </div>
            <span class="term-tag timeseries">Chuỗi Thời Gian &amp; ML</span>
          </div>
          <div class="term-body">
            <p><strong>Khái niệm cốt lõi:</strong> Chuỗi thời gian có tính dừng nếu các đặc tính thống kê (Trung bình $\mu$, Phương sai $\sigma^2$, và Hiệp phương sai tự tương quan) không thay đổi theo thời gian.</p>
            <div class="term-box">
              <strong>Kiểm định Augmented Dickey-Fuller (ADF):</strong> Nếu $p\text{-value} &lt; 0.05$, bác bỏ giả thuyết chuỗi có nghiệm đơn vị (Unit Root), kết luận chuỗi có tính dừng.
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;"><strong>Xử lý:</strong> Nếu chuỗi không dừng (có xu hướng tăng dần), cần lấy sai phân bậc 1 ($\Delta Y_t = Y_t - Y_{t-1}$) trước khi đưa vào mô hình.</p>
          </div>
        </div>

      </div>
    </section>
"""

# Insert the new section right before the end of #main-content
target_end_main = '</section>\n\n    <!-- Submissions Tab -->'
if target_end_main in html:
    html = html.replace(target_end_main, '</section>\n' + terminology_html + '\n    <!-- Submissions Tab -->')
    print("Terminology section inserted before Submissions tab.")
else:
    # Try alternative anchor
    alt_anchor = '<section id="tab-submissions"'
    if alt_anchor in html:
        html = html.replace(alt_anchor, terminology_html + '\n    <section id="tab-submissions"')
        print("Alternative insertion of Terminology section successful.")
    else:
        print("Error: Could not find insertion point for Terminology tab!")

# 3. Add CSS for Terminology Cards & Filter Pills
term_styles = """
    /* Terminology Tab Styles */
    .filter-pill {
      background: #0b0f19;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .filter-pill:hover {
      color: #fff;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .filter-pill.active {
      background: rgba(59, 130, 246, 0.2);
      border-color: #3b82f6;
      color: #60a5fa;
    }

    .term-card {
      background: #131b2e;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .term-card:hover {
      transform: translateY(-2px);
      border-color: rgba(59, 130, 246, 0.4);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .term-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 10px;
    }
    .term-en {
      font-size: 11px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      font-family: monospace;
    }
    .term-vi {
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      margin-top: 2px;
    }
    .term-tag {
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
    }
    .term-tag.dirtiness { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .term-tag.statistics { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .term-tag.supplychain { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .term-tag.timeseries { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    .term-body {
      font-size: 13px;
      color: #cbd5e1;
      line-height: 1.5;
    }
    .term-box {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 10px 12px;
      margin: 10px 0;
      font-size: 12px;
    }
"""

# Insert CSS into style
if '</style>' in html:
    html = html.replace('</style>', term_styles + '\n  </style>')
    print("Terminology CSS styles inserted.")

# 4. Add JavaScript for Terminology Filtering & Tab Switching
term_js = """
    // Switch Tab Extension
    function switchTab(tabId) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

      const targetPane = document.getElementById('tab-' + tabId);
      if (targetPane) targetPane.classList.add('active');

      const buttons = document.querySelectorAll('.nav-btn');
      if (tabId === 'ablations' && buttons[0]) buttons[0].classList.add('active');
      if (tabId === 'pipeline' && buttons[1]) buttons[1].classList.add('active');
      if (tabId === 'terminology' && buttons[2]) buttons[2].classList.add('active');
      if (tabId === 'submissions' && buttons[3]) buttons[3].classList.add('active');
    }

    // Terminology Filter
    let currentCategory = 'all';
    function setTermCategory(cat) {
      currentCategory = cat;
      document.querySelectorAll('#term-filter-pills .filter-pill').forEach(btn => {
        btn.classList.remove('active');
      });
      event.target.classList.add('active');
      filterTerminology();
    }

    function filterTerminology() {
      const searchVal = (document.getElementById('term-search').value || '').toLowerCase().trim();
      const cards = document.querySelectorAll('.term-card');

      cards.forEach(card => {
        const cat = card.getAttribute('data-cat') || '';
        const keywords = card.getAttribute('data-keywords') || '';
        const text = card.innerText.toLowerCase();

        const matchCat = (currentCategory === 'all') || (cat === currentCategory);
        const matchSearch = (!searchVal) || text.includes(searchVal) || keywords.includes(searchVal);

        if (matchCat && matchSearch) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }
"""

# Replace existing switchTab implementation
if 'function switchTab(tabId) {' in html:
    # Replace switchTab
    import re
    html = re.sub(r'function switchTab\(tabId\) \{[^}]*\}', term_js, html, count=1)
    print("switchTab JavaScript function upgraded.")
else:
    # Append before </script>
    html = html.replace('</script>', term_js + '\n  </script>')
    print("Appended term_js before </script>")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully added Terminology tab to web/index.html!")
