"""
Update web/index.html to feature the Data Dirtiness Audit prominently,
with interactive inspection cards, metric summary banners, and the 2 new charts.
"""

import os, sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting"
html_path = os.path.join(BASE_DIR, "web", "index.html")

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect where experiments section starts and add the Data Dirtiness Section
# We can inject a new prominent section right inside tab-experiments
dirtiness_banner = """
      <!-- BANNER CẢNH BÁO ĐỘ BẨN CỦA DỮ LIỆU (DATA DIRTINESS AUDIT) -->
      <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 20px; margin-bottom: 28px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="background: #ef4444; color: #fff; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase;">Phát Hiện Cốt Lõi</span>
            <h2 style="font-size: 18px; color: #f8fafc; font-weight: 800;">Kiểm Toán Độ "Bẩn" & Cạm Bẫy Trong Bộ Dữ Liệu: Kỳ Vọng Lý Thuyết vs Thực Tế?</h2>
          </div>
          <span style="font-size: 12px; color: #fca5a5; font-family: monospace;">14 Bảng Liên Kết | 714k Dòng Hàng | 646k Đơn</span>
        </div>
        <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6; margin-bottom: 16px;">
          Thay vì vội vàng xây dựng mô hình học máy (Machine Learning) dựa trên các giả định sai lầm, quy trình phân tích chuyên sâu đã phát hiện <strong>6 cạm bẫy chất lượng dữ liệu nghiêm trọng</strong>. Nếu không làm sạch và chuẩn hóa trước, bất kỳ mô hình dự báo nào cũng sẽ bị sai lệch (data leakage & bias).
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px;">
            <div style="color: #ef4444; font-size: 11px; font-weight: 700; text-transform: uppercase;">1. Vi Phạm Nhân Quả (Time Paradox)</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">73.80% Đơn Hàng</div>
            <div style="font-size: 11px; color: #94a3b8;">477,453 đơn đặt <em>trước</em> ngày khách tạo tài khoản (signup_date) tới nhiều năm!</div>
          </div>
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 12px;">
            <div style="color: #f59e0b; font-size: 11px; font-weight: 700; text-transform: uppercase;">2. Bán Phá Giá Dưới Giá Vốn</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">18.62% Sản Phẩm</div>
            <div style="font-size: 11px; color: #94a3b8;">133,052 giao dịch bán dưới giá vốn (COGS). 382 ngày doanh thu bị âm gộp (-192M VNĐ).</div>
          </div>
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 8px; padding: 12px;">
            <div style="color: #a78bfa; font-size: 11px; font-weight: 700; text-transform: uppercase;">3. Bẫy Khái Niệm Doanh Thu</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">Gross vs Net GMV</div>
            <div style="font-size: 11px; color: #94a3b8;">Cột Revenue trong sales.csv là GMV <em>trước chiết khấu</em>, khác xa số tiền thực nhận ở payments.csv!</div>
          </div>
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px;">
            <div style="color: #10b981; font-size: 11px; font-weight: 700; text-transform: uppercase;">4. Lệch Đối Soát Phí Vận Chuyển</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 4px 0;">62.16% Bị Lệch Tiền</div>
            <div style="font-size: 11px; color: #94a3b8;">Bảng payments chỉ thu đúng tiền hàng Net (khớp 100%), hoàn toàn bỏ qua phí ship trong shipments.</div>
          </div>
        </div>
      </div>
"""

# New cards for eda_13 and eda_14
dirtiness_cards = """
        <!-- THẺ KIỂM TOÁN ĐỘ BẨN DỮ LIỆU EDA 13 -->
        <div class="eda-card" style="border: 1px solid rgba(239, 68, 68, 0.4); background: #131b2e;">
          <div class="card-img-wrap" onclick="openModal('artifacts/eda_13_data_dirtiness_audit.png', 'Kiểm toán chất lượng dữ liệu: Bộ dữ liệu Datathon 2026 \\'bẩn\\' và sai lệch đến mức nào?', 'Phát hiện 477,453 đơn hàng (73.8%) có ngày đặt hàng trước ngày tạo tài khoản của khách hàng (vi phạm quan hệ nhân quả). Đồng thời, 133,052 sản phẩm (18.62%) bị bán dưới giá vốn (COGS), tập trung vào các năm lẻ do chiến lược giảm giá sâu. 564 đơn hàng được ghi nhận đã giao hoặc đã trả nhưng hoàn toàn không có bản ghi vận chuyển (shipments.csv), và 181 ngày đầu tiên của năm 2012 bị khuyết hoàn toàn dữ liệu web traffic.')">
            <img src="artifacts/eda_13_data_dirtiness_audit.png" alt="Kiểm toán độ bẩn của bộ dữ liệu" loading="lazy">
            <span class="card-badge" style="background: #ef4444; color: #fff;">Kiểm Toán Độ Bẩn</span>
          </div>
          <div class="card-body">
            <div class="card-title">Bộ dữ liệu Datathon 2026 "bẩn" và sai lệch đến mức nào: Kỳ vọng lý thuyết vs Thực tế dữ liệu?</div>
            <div class="card-desc">Phát hiện 477k đơn đặt hàng trước ngày đăng ký, 133k mặt hàng bán dưới giá vốn, 382 ngày lỗ gộp và 564 đơn hàng "ma" không mã vận đơn.</div>
            <div class="card-stats">
              <span class="stat-tag" style="background: rgba(239,68,68,0.2); color: #f87171;">Order &lt; Signup: 73.8%</span>
              <span class="stat-tag" style="background: rgba(245,158,11,0.2); color: #fbbf24;">Bán &lt; COGS: 18.62%</span>
              <span class="stat-tag" style="background: rgba(59,130,246,0.2); color: #60a5fa;">Đơn ma: 564 đơn</span>
            </div>
          </div>
        </div>

        <!-- THẺ CẠM BẪY ĐỐI SOÁT & THANH TOÁN EDA 14 -->
        <div class="eda-card" style="border: 1px solid rgba(245, 158, 11, 0.4); background: #131b2e;">
          <div class="card-img-wrap" onclick="openModal('artifacts/eda_14_reconciliation_pitfalls.png', 'Cạm bẫy đối soát thanh toán & chuỗi cung ứng: Phí vận chuyển trên giấy tờ vs Thực tế thu tiền?', 'Kiểm toán đối soát giữa bảng payments.csv và order_items.csv cho thấy: Số tiền thanh toán thực tế khớp 100.0% với [Tiền hàng Net], nhưng lại lệch ở 62.16% đơn hàng nếu cộng thêm Phí vận chuyển (shipping_fee) trong bảng shipments.csv! Điều này chứng minh phí vận chuyển là số liệu ghi nhận nội bộ/miễn phí cho khách, không được thu tiền thực tế. Ngoài ra, doanh thu vĩ mô sales.csv lệch trung bình 5.17% so với đơn hàng vi mô do phản ánh GMV trước chiết khấu.')">
            <img src="artifacts/eda_14_reconciliation_pitfalls.png" alt="Cạm bẫy đối soát thanh toán" loading="lazy">
            <span class="card-badge" style="background: #f59e0b; color: #fff;">Cạm Bẫy Đối Soát</span>
          </div>
          <div class="card-body">
            <div class="card-title">Cạm bẫy đối soát thanh toán & chuỗi cung ứng: Phí vận chuyển trên giấy tờ vs Thực tế thu tiền?</div>
            <div class="card-desc">Bảng payments.csv chỉ thu tiền hàng thực tế (khớp 100%), hoàn toàn bỏ qua phí ship. Doanh thu vĩ mô sales.csv thực chất là GMV trước chiết khấu.</div>
            <div class="card-stats">
              <span class="stat-tag" style="background: rgba(16,185,129,0.2); color: #34d399;">Khớp tiền hàng: 100%</span>
              <span class="stat-tag" style="background: rgba(239,68,68,0.2); color: #f87171;">Lệch khi cộng ship: 62.2%</span>
              <span class="stat-tag" style="background: rgba(59,130,246,0.2); color: #60a5fa;">Độ lệch Gross GMV: 5.17%</span>
            </div>
          </div>
        </div>
"""

# Let's insert the banner after the search box
target_search = '</div>\n\n      <div class="eda-grid">'
if target_search in content:
    content = content.replace(target_search, '</div>\n\n' + dirtiness_banner + '      <div class="eda-grid">\n' + dirtiness_cards)
    print("Injected banner and dirtiness cards into web/index.html")
else:
    # Alternative insertion point
    content = content.replace('<div class="eda-grid">', dirtiness_banner + '<div class="eda-grid">\n' + dirtiness_cards)
    print("Alternative injection completed")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("web/index.html successfully updated with Data Dirtiness Audit section!")
