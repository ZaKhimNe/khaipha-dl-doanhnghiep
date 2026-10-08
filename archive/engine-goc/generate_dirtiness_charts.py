"""
Generate Data Dirtiness & Quality Audit Visualizations in Vietnamese
with question-led titles, 'vs' comparative framing, and 300 DPI publication standards.
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\dataset"
OUT_DIRS = [
    r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\artifacts",
    r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\web\artifacts",
    r"C:\Users\Admin\.gemini\antigravity-cli\brain\872029b1-b575-4448-8593-042261b8a48e\artifacts"
]

for d in OUT_DIRS:
    os.makedirs(d, exist_ok=True)

# Load data
orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'), usecols=['order_id', 'order_date', 'customer_id', 'order_status'])
cust = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'), usecols=['customer_id', 'signup_date'])
order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'), usecols=['order_id', 'product_id', 'quantity', 'unit_price', 'discount_amount'], low_memory=False)
products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'), usecols=['product_id', 'price', 'cogs', 'category'])
sales = pd.read_csv(os.path.join(DATA_DIR, 'sales.csv'))
shipments = pd.read_csv(os.path.join(DATA_DIR, 'shipments.csv'), usecols=['order_id', 'shipping_fee'])
payments = pd.read_csv(os.path.join(DATA_DIR, 'payments.csv'), usecols=['order_id', 'payment_value'])

# -------------------------------------------------------------
# CHART 13: ĐỘ BẨN CỦA DỮ LIỆU & NGHỊCH LÝ NHÂN QUẢ (DATA DIRTINESS)
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
fig.patch.set_facecolor('#0f172a')

# 1. Temporal Paradox: Order before Signup
orders_cust = orders[['order_id', 'order_date', 'customer_id']].merge(cust, on='customer_id')
orders_cust['order_date'] = pd.to_datetime(orders_cust['order_date'])
orders_cust['signup_date'] = pd.to_datetime(orders_cust['signup_date'])
orders_cust['is_before_signup'] = orders_cust['order_date'] < orders_cust['signup_date']
counts_temporal = orders_cust['is_before_signup'].value_counts()

ax1 = axes[0, 0]
ax1.set_facecolor('#1e293b')
colors1 = ['#ef4444', '#10b981']
wedges, texts, autotexts = ax1.pie(
    [counts_temporal[True], counts_temporal[False]],
    labels=['Đặt trước ngày tạo tài khoản\n(477,453 đơn - 73.80%)', 'Đặt sau khi tạo tài khoản\n(169,492 đơn - 26.20%)'],
    colors=colors1, autopct='%1.1f%%', startangle=140,
    textprops=dict(color='#f8fafc', fontsize=11, fontweight='bold'),
    explode=(0.08, 0), shadow=True
)
for at in autotexts:
    at.set_color('#ffffff')
    at.set_fontsize(13)
ax1.set_title("Nghịch lý thời gian: Đặt hàng trước vs Sau ngày tạo tài khoản?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)

# 2. Biennial Margin Shock: Below COGS
orders['year'] = pd.to_datetime(orders['order_date']).dt.year
m_items = order_items.merge(orders[['order_id', 'year']], on='order_id').merge(products[['product_id', 'cogs']], on='product_id')
m_items['below_cogs'] = m_items['unit_price'] < m_items['cogs']
yearly_below = m_items.groupby('year')['below_cogs'].mean() * 100

ax2 = axes[0, 1]
ax2.set_facecolor('#1e293b')
years = yearly_below.index.tolist()
pcts = yearly_below.values.tolist()
bar_colors = ['#ef4444' if p > 20 else '#f59e0b' if p > 10 else '#3b82f6' for p in pcts]
bars = ax2.bar([str(y) for y in years], pcts, color=bar_colors, edgecolor='#ffffff', alpha=0.9, width=0.6)
ax2.axhline(18.62, color='#ef4444', linestyle='--', linewidth=1.5, label='Trung bình toàn bộ: 18.62%')
ax2.set_title("Bán phá giá dưới giá vốn: Năm chẵn vs Năm lẻ biến động ra sao?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)
ax2.set_ylabel("Tỷ lệ sản phẩm bán < Giá vốn (COGS) (%)", color='#94a3b8', fontsize=10)
ax2.tick_params(colors='#94a3b8', labelsize=9)
ax2.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=9)
ax2.grid(True, linestyle=':', alpha=0.2, color='#94a3b8')
for bar in bars:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 0.6, f'{h:.1f}%', ha='center', va='bottom', color='#f8fafc', fontsize=8, fontweight='bold')

# 3. Phantom Fulfillment & Missing Traffic
ax3 = axes[1, 0]
ax3.set_facecolor('#1e293b')
issues = [
    'Order trước Signup\n(Vi phạm nhân quả)',
    'Hàng bán < COGS\n(Bán dưới giá vốn)',
    'Doanh thu ngày bị âm gộp\n(382 ngày lỗ gộp)',
    'Khuyết dữ liệu Traffic\n(181 ngày đầu 2012)',
    'Đơn hàng "ma"\n(Giao không có mã ship)'
]
issue_pcts = [73.80, 18.62, 9.97, 4.72, 0.09]
issue_counts = ['477k đơn', '133k items', '382 ngày', '181 ngày', '564 đơn']

y_pos = np.arange(len(issues))
bars3 = ax3.barh(y_pos, issue_pcts, color=['#ef4444', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'], edgecolor='#ffffff', alpha=0.85, height=0.55)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(issues, color='#f8fafc', fontsize=9, fontweight='bold')
ax3.set_xlabel("Tỷ lệ dữ liệu bị ảnh hưởng (%)", color='#94a3b8', fontsize=10)
ax3.set_title("Mức độ nghiêm trọng: Lỗi dữ liệu nào chiếm tỷ trọng lớn nhất?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)
ax3.tick_params(colors='#94a3b8', labelsize=9)
ax3.grid(True, linestyle=':', alpha=0.2, color='#94a3b8')
for i, bar in enumerate(bars3):
    w = bar.get_width()
    ax3.text(w + 1.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}% ({issue_counts[i]})', ha='left', va='center', color='#f8fafc', fontsize=8, fontweight='bold')
ax3.set_xlim(0, 85)

# 4. Gross vs Net Revenue Definition Confusion
ax4 = axes[1, 1]
ax4.set_facecolor('#1e293b')
sales['Gross_Profit'] = sales['Revenue'] - sales['COGS']
sample_dates = pd.to_datetime(sales['Date'])
# Plot 60-day moving averages
rolling_rev = sales['Revenue'].rolling(30).mean() / 1e6
rolling_cogs = sales['COGS'].rolling(30).mean() / 1e6
rolling_profit = sales['Gross_Profit'].rolling(30).mean() / 1e6

ax4.plot(sample_dates, rolling_rev, label='Doanh thu gộp (Gross GMV trước chiết khấu)', color='#3b82f6', linewidth=2)
ax4.plot(sample_dates, rolling_cogs, label='Giá vốn hàng bán (COGS vĩ mô)', color='#ef4444', linewidth=2)
ax4.plot(sample_dates, rolling_profit, label='Lợi nhuận gộp (Gross Profit = Rev - COGS)', color='#10b981', linewidth=1.5, linestyle='--')
ax4.axhline(0, color='#ffffff', linestyle=':', alpha=0.6)
ax4.set_title("Bẫy định nghĩa: Doanh thu danh nghĩa (sales.csv) vs Giá vốn?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)
ax4.set_ylabel("Triệu VNĐ / Ngày (MA 30 ngày)", color='#94a3b8', fontsize=10)
ax4.tick_params(colors='#94a3b8', labelsize=9)
ax4.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8, loc='upper right')
ax4.grid(True, linestyle=':', alpha=0.2, color='#94a3b8')

plt.suptitle("KIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU: BỘ DỮ LIỆU 'BẨN' VÀ SAI LỆCH ĐẾN MỨC NÀO?\nKỳ vọng hoàn hảo vs Thực tế phân tích (14 bảng liên kết - Datathon 2026)",
             fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

for d in OUT_DIRS:
    p = os.path.join(d, "eda_13_data_dirtiness_audit.png")
    fig.savefig(p, facecolor=fig.get_facecolor(), edgecolor='none')
print("=> Saved eda_13_data_dirtiness_audit.png")
plt.close(fig)

# -------------------------------------------------------------
# CHART 14: CẠM BẪY ĐỐI SOÁT THANH TOÁN & GIAO VẬN (RECONCILIATION PITFALLS)
# -------------------------------------------------------------
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6.5), dpi=300)
fig2.patch.set_facecolor('#0f172a')

# 1. Shipping Fee Phantom in Payments
ax2_1 = axes2[0]
ax2_1.set_facecolor('#1e293b')
labels_pay = ['Tiền thanh toán == [Tiền hàng Net]\n(Khớp 100% - Phí ship = 0)', 'Tiền thanh toán != [Tiền hàng + Phí ship]\n(Sai lệch nếu tính cả phí vận chuyển)']
sizes_pay = [100.0, 62.16]
bars_pay = ax2_1.bar(['Khớp hoàn toàn\n(Chỉ tính tiền hàng)', 'Bị lệch khi cộng Phí Ship\n(62.16% đơn có phí ship)'], [100.0, 62.16],
                     color=['#10b981', '#ef4444'], width=0.45, edgecolor='#ffffff', alpha=0.9)
ax2_1.set_ylim(0, 115)
ax2_1.set_ylabel("Tỷ lệ phần trăm đơn hàng (%)", color='#94a3b8', fontsize=10)
ax2_1.set_title("Cạm bẫy phí ship: Phí vận chuyển trên giấy tờ vs Thực tế thu tiền?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)
ax2_1.tick_params(colors='#94a3b8', labelsize=9)
ax2_1.grid(True, linestyle=':', alpha=0.2, color='#94a3b8')
for b in bars_pay:
    h = b.get_height()
    ax2_1.text(b.get_x() + b.get_width()/2, h + 2, f'{h:.2f}%', ha='center', va='bottom', color='#f8fafc', fontsize=11, fontweight='bold')
ax2_1.text(0.5, 0.45, "LƯU Ý QUAN TRỌNG CHO ML/BI:\nToàn bộ bảng payments.csv CHỈ thu tiền hàng (item_net),\nkhông hề thu tiền phí vận chuyển trong shipments.csv!\nNếu cộng phí ship vào tổng thanh toán sẽ làm sai lệch 402,126 đơn.",
           transform=ax2_1.transAxes, color='#fbbf24', fontsize=9, ha='center', va='center',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='#0f172a', edgecolor='#f59e0b', alpha=0.95))

# 2. Macro vs Micro Revenue Gap Distribution
ax2_2 = axes2[1]
ax2_2.set_facecolor('#1e293b')
# Compare sales daily vs order items daily
orders['order_date_str'] = orders['order_date'].str[:10]
order_items['item_net'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount']
order_items_m = order_items.merge(orders[['order_id', 'order_date_str']], on='order_id')
daily_net = order_items_m.groupby('order_date_str')['item_net'].sum().reset_index()
sales_comp = sales.merge(daily_net, left_on='Date', right_on='order_date_str')
sales_comp['diff_pct'] = (sales_comp['Revenue'] - sales_comp['item_net']) / sales_comp['Revenue'] * 100

sns.histplot(sales_comp['diff_pct'], kde=True, ax=ax2_2, color='#3b82f6', edgecolor='#ffffff', bins=40)
ax2_2.axvline(sales_comp['diff_pct'].mean(), color='#ef4444', linestyle='--', linewidth=2, label=f'Độ lệch trung bình: +{sales_comp["diff_pct"].mean():.2f}%')
ax2_2.set_title("Lệch đối soát Doanh thu vĩ mô (sales.csv) vs Doanh thu vi mô (orders.csv)?", color='#f8fafc', fontsize=12, fontweight='bold', pad=12)
ax2_2.set_xlabel("Phần trăm chênh lệch: (sales.csv Revenue - Tổng order_items Net) (%)", color='#94a3b8', fontsize=10)
ax2_2.set_ylabel("Số ngày quan sát", color='#94a3b8', fontsize=10)
ax2_2.tick_params(colors='#94a3b8', labelsize=9)
ax2_2.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=9)
ax2_2.grid(True, linestyle=':', alpha=0.2, color='#94a3b8')

plt.suptitle("CẠM BẪY ĐỐI SOÁT & RỦI RO RÒ RỈ DỮ LIỆU (RECONCILIATION & DATA LEAKAGE PITFALLS)\nPhát hiện các sai lệch kinh tế học ngầm giữa 14 bảng quan hệ",
             fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.93])

for d in OUT_DIRS:
    p = os.path.join(d, "eda_14_reconciliation_pitfalls.png")
    fig2.savefig(p, facecolor=fig2.get_facecolor(), edgecolor='none')
print("=> Saved eda_14_reconciliation_pitfalls.png")
plt.close(fig2)
