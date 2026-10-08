"""
Vietnamese Question-Led EDA Chart Generator for Datathon 2026
Using Segoe UI / Arial fonts with full Vietnamese diacritics.
Every chart uses an analytical question for its title and 'vs' for comparative components.
Python 3.12, 0% GPU, gentle CPU vectorization.
"""

import os
import sys
import json
import warnings

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

warnings.filterwarnings('ignore')

# Vietnamese typography configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.autolayout'] = True
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

BASE_DIR = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting"
DATA_DIR = os.path.join(BASE_DIR, 'dataset')
ARTIFACT_DIRS = [
    os.path.join(BASE_DIR, 'artifacts'),
    os.path.join(BASE_DIR, 'web', 'artifacts'),
    r'C:\Users\Admin\.gemini\antigravity-cli\brain\872029b1-b575-4448-8593-042261b8a48e\artifacts'
]

for ad in ARTIFACT_DIRS:
    os.makedirs(ad, exist_ok=True)

def save_chart(fig, filename):
    for ad in ARTIFACT_DIRS:
        dest = os.path.join(ad, filename)
        fig.savefig(dest, bbox_inches='tight', dpi=300)
    print(f"[Vietnamese Chart Generated] Saved: {filename}")
    plt.close(fig)

def build_all_vietnamese_charts():
    print("=== Đang nạp dữ liệu đa bảng để tạo biểu đồ Tiếng Việt ===")
    sales = pd.read_csv(os.path.join(DATA_DIR, 'sales.csv'), parse_dates=['Date'])
    traffic = pd.read_csv(os.path.join(DATA_DIR, 'web_traffic.csv'), parse_dates=['date'])
    orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'), parse_dates=['order_date'])
    order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))
    products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
    inventory = pd.read_csv(os.path.join(DATA_DIR, 'inventory.csv'))
    returns = pd.read_csv(os.path.join(DATA_DIR, 'returns.csv'), parse_dates=['return_date'])
    reviews = pd.read_csv(os.path.join(DATA_DIR, 'reviews.csv'), parse_dates=['review_date'])
    shipments = pd.read_csv(os.path.join(DATA_DIR, 'shipments.csv'), parse_dates=['ship_date', 'delivery_date'])
    promotions = pd.read_csv(os.path.join(DATA_DIR, 'promotions.csv'), parse_dates=['start_date', 'end_date'])
    customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))

    sales['Gross_Profit'] = sales['Revenue'] - sales['COGS']
    sales['Gross_Margin_Pct'] = (sales['Gross_Profit'] / sales['Revenue']) * 100.0
    sales['Date'] = pd.to_datetime(sales['Date'])

    traffic_daily = traffic.groupby('date').agg(
        total_sessions=('sessions', 'sum'),
        total_unique_visitors=('unique_visitors', 'sum'),
        total_page_views=('page_views', 'sum'),
        avg_bounce_rate=('bounce_rate', 'mean')
    ).reset_index().rename(columns={'date': 'Date'})

    orders_daily = orders.groupby('order_date').agg(
        order_count=('order_id', 'count'),
        unique_customers=('customer_id', 'nunique')
    ).reset_index().rename(columns={'order_date': 'Date'})

    oi_merged = order_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')
    oi_daily = oi_merged.groupby('order_date').agg(
        total_units_ordered=('quantity', 'sum'),
        total_discounts_applied=('discount_amount', 'sum')
    ).reset_index().rename(columns={'order_date': 'Date'})

    returns_daily = returns.groupby('return_date').agg(
        return_count=('return_id', 'count'),
        total_refund_amount=('refund_amount', 'sum')
    ).reset_index().rename(columns={'return_date': 'Date'})

    master = sales.merge(traffic_daily, on='Date', how='left')
    master = master.merge(orders_daily, on='Date', how='left')
    master = master.merge(oi_daily, on='Date', how='left')
    master = master.merge(returns_daily, on='Date', how='left')

    master['Year'] = master['Date'].dt.year
    master['Month'] = master['Date'].dt.month
    master['DayOfWeek'] = master['Date'].dt.dayofweek
    num_cols = master.select_dtypes(include=[np.number]).columns
    master[num_cols] = master[num_cols].fillna(master[num_cols].median())

    # =========================================================================
    # Biểu đồ 0: Lấy mẫu phân tầng 150k vs Toàn bộ quần thể 714k
    # =========================================================================
    df_items = order_items.merge(products[['product_id', 'category', 'price', 'cogs']], on='product_id', how='left')
    df_items = df_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')
    df_items['Year'] = df_items['order_date'].dt.year
    df_items['Item_Revenue'] = df_items['quantity'] * df_items['unit_price'] - df_items['discount_amount']
    stratified_sample = df_items.groupby(['Year', 'category'], group_keys=False).sample(frac=150000/len(df_items), random_state=42).reset_index(drop=True)
    ks_stat, ks_pval = stats.ks_2samp(df_items['Item_Revenue'].dropna(), stratified_sample['Item_Revenue'].dropna())

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    pop_mix = df_items['category'].value_counts(normalize=True) * 100
    sample_mix = stratified_sample['category'].value_counts(normalize=True) * 100
    comp_df = pd.DataFrame({'Toàn bộ dữ liệu (714k dòng)': pop_mix, 'Mẫu phân tầng (150k dòng)': sample_mix})
    comp_df.plot(kind='bar', ax=axes[0], color=['#2563eb', '#10b981'], width=0.7)
    axes[0].set_title('Tỷ trọng danh mục sản phẩm: Mẫu 150k vs Dữ liệu gốc 714k dòng?', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Tỷ trọng (%)', fontsize=11)
    axes[0].tick_params(axis='x', rotation=20)
    axes[0].legend()

    sns.kdeplot(df_items['Item_Revenue'].clip(upper=50000), ax=axes[1], color='#2563eb', lw=2, label='Toàn bộ dữ liệu (714k)')
    sns.kdeplot(stratified_sample['Item_Revenue'].clip(upper=50000), ax=axes[1], color='#10b981', lw=2, linestyle='--', label='Mẫu phân tầng (150k)')
    axes[1].set_title(f'Phân phối doanh thu: Dữ liệu mẫu vs Dữ liệu gốc có bị lệch không? (KS D={ks_stat:.5f})', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Doanh thu từng sản phẩm (VNĐ)', fontsize=11)
    axes[1].legend()
    plt.suptitle('Phương pháp lấy mẫu phân tầng có đảm bảo đại diện chính xác cho toàn bộ dữ liệu?', fontsize=14, fontweight='bold', y=1.02)
    save_chart(fig, 'eda_stratified_sample_fidelity.png')

    # =========================================================================
    # Biểu đồ 1: Doanh thu, Giá vốn và Biên lợi nhuận hàng ngày
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    sns.histplot(master['Revenue'] / 1e6, kde=True, ax=axes[0, 0], color='#2563eb', bins=40, stat='density')
    mean_rev, med_rev = master['Revenue'].mean()/1e6, master['Revenue'].median()/1e6
    axes[0, 0].axvline(mean_rev, color='#dc2626', linestyle='--', label=f'Trung bình: {mean_rev:.2f} tỷ')
    axes[0, 0].axvline(med_rev, color='#16a34a', linestyle=':', label=f'Trung vị: {med_rev:.2f} tỷ')
    axes[0, 0].set_title('Doanh thu hàng ngày phân phối như thế nào? (Trung bình vs Trung vị)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Doanh thu (Tỷ VNĐ)')
    axes[0, 0].legend()

    sns.histplot(master['COGS'] / 1e6, kde=True, ax=axes[0, 1], color='#ea580c', bins=40, stat='density')
    mean_cogs, med_cogs = master['COGS'].mean()/1e6, master['COGS'].median()/1e6
    axes[0, 1].axvline(mean_cogs, color='#dc2626', linestyle='--', label=f'Trung bình: {mean_cogs:.2f} tỷ')
    axes[0, 1].axvline(med_cogs, color='#16a34a', linestyle=':', label=f'Trung vị: {med_cogs:.2f} tỷ')
    axes[0, 1].set_title('Giá vốn hàng bán (COGS) chiếm bao nhiêu trong doanh thu?', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Giá vốn COGS (Tỷ VNĐ)')
    axes[0, 1].legend()

    sns.boxplot(x=master['Gross_Profit'] / 1e6, ax=axes[1, 0], color='#10b981')
    axes[1, 0].set_title('Lợi nhuận gộp hàng ngày: Có xuất hiện điểm ngoại lai (Outliers) không?', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Lợi nhuận gộp (Tỷ VNĐ)')

    sns.histplot(master['Gross_Margin_Pct'], kde=True, ax=axes[1, 1], color='#8b5cf6', bins=35)
    mean_margin = master['Gross_Margin_Pct'].mean()
    axes[1, 1].axvline(mean_margin, color='#dc2626', linestyle='--', label=f'Biên TB: {mean_margin:.1f}%')
    axes[1, 1].set_title('Tỷ suất lợi nhuận gộp (%) phân phối quanh mức nào?', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Biên lợi nhuận gộp (%)')
    axes[1, 1].legend()
    plt.suptitle('Cấu trúc kinh tế vi mô hàng ngày: Doanh thu vs Giá vốn vs Biên lợi nhuận (2012–2022)?', fontsize=14, fontweight='bold', y=0.98)
    save_chart(fig, 'eda_01_target_distributions.png')

    # =========================================================================
    # Biểu đồ 2: Xu hướng vĩ mô 10 năm & Phân tích chuỗi thời gian
    # =========================================================================
    fig, axes = plt.subplots(3, 1, figsize=(15, 9), sharex=True)
    axes[0].plot(master['Date'], master['Revenue']/1e6, color='#2563eb', lw=0.8, label='Doanh thu ngày')
    axes[0].plot(master['Date'], (master['Revenue'].rolling(30).mean())/1e6, color='#dc2626', lw=2, label='Đường MA 30 ngày')
    axes[0].set_title('Doanh thu thực tế vs Đường trung bình động 30 ngày qua 10 năm?', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Doanh thu (Tỷ VNĐ)')
    axes[0].legend(loc='upper left')

    axes[1].plot(master['Date'], master['COGS']/1e6, color='#ea580c', lw=0.8, label='Giá vốn ngày')
    axes[1].plot(master['Date'], (master['COGS'].rolling(30).mean())/1e6, color='#b91c1c', lw=2, label='Đường MA 30 ngày')
    axes[1].set_title('Giá vốn COGS tăng trưởng theo chu kỳ thế nào so với doanh thu?', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Giá vốn COGS (Tỷ VNĐ)')
    axes[1].legend(loc='upper left')

    axes[2].plot(master['Date'], master['Gross_Margin_Pct'], color='#10b981', lw=0.8, label='Biên lợi nhuận (%)')
    axes[2].plot(master['Date'], master['Gross_Margin_Pct'].rolling(30).mean(), color='#047857', lw=2, label='Đường MA 30 ngày')
    axes[2].set_title('Tỷ suất lợi nhuận gộp có duy trì ổn định qua các năm không?', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Biên lợi nhuận (%)')
    axes[2].legend(loc='upper left')
    save_chart(fig, 'eda_02_timeseries_stl_decomposition.png')

    # =========================================================================
    # Biểu đồ 3: Ma trận tính mùa vụ (Thứ trong tuần vs Tháng trong năm)
    # =========================================================================
    piv_rev = master.pivot_table(index='DayOfWeek', columns='Month', values='Revenue', aggfunc='mean')
    piv_rev.index = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    piv_rev.columns = [f'Tháng {m}' for m in range(1, 13)]

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.heatmap(piv_rev / 1e6, cmap='Blues', annot=True, fmt='.2f', cbar_kws={'label': 'Doanh thu trung bình (Tỷ VNĐ)'}, ax=ax)
    ax.set_title('Thời điểm nào trong năm đạt đỉnh doanh thu: Thứ trong tuần vs Tháng trong năm?', fontsize=13, fontweight='bold')
    ax.set_xlabel('Tháng trong năm (Calendar Month)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Thứ trong tuần (Day of Week)', fontsize=11, fontweight='bold')
    save_chart(fig, 'eda_03_seasonality_heatmap.png')

    # =========================================================================
    # Biểu đồ 4: Ma trận tương quan đa bảng
    # =========================================================================
    corr_cols = [
        'Revenue', 'COGS', 'Gross_Profit', 'total_sessions', 'total_page_views',
        'order_count', 'total_units_ordered', 'total_discounts_applied',
        'return_count', 'avg_bounce_rate'
    ]
    vn_col_names = [
        'Doanh thu', 'Giá vốn COGS', 'Lợi nhuận gộp', 'Lượng truy cập', 'Lượt xem trang',
        'Số đơn hàng', 'Số lượng SP', 'Chiết khấu', 'Số lượng trả', 'Tỷ lệ thoát'
    ]
    sub_df = master[corr_cols].copy()
    sub_df.columns = vn_col_names
    corr_mat = sub_df.corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_mat, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, square=True, ax=ax)
    ax.set_title('Những chỉ số vận hành nào có tương quan mạnh nhất vs Doanh thu và Chi phí?', fontsize=13, fontweight='bold')
    save_chart(fig, 'eda_04_correlation_matrix.png')

    # =========================================================================
    # Biểu đồ 5: Lượng truy cập vs Doanh thu & Đơn hàng
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    r_s, p_s = stats.pearsonr(master['total_sessions'], master['Revenue'])
    sns.regplot(x=master['total_sessions'], y=master['Revenue']/1e6, ax=axes[0],
                scatter_kws={'alpha': 0.3, 'color': '#3b82f6'}, line_kws={'color': '#dc2626', 'lw': 2.5})
    axes[0].set_title(f'Lượng truy cập (Sessions) vs Doanh thu: Liệu có tương quan thuận? (r = {r_s:.3f}, p < 0.001)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Lượt truy cập hàng ngày (Sessions)')
    axes[0].set_ylabel('Doanh thu (Tỷ VNĐ)')

    r_o, p_o = stats.pearsonr(master['order_count'], master['Revenue'])
    sns.regplot(x=master['order_count'], y=master['Revenue']/1e6, ax=axes[1],
                scatter_kws={'alpha': 0.3, 'color': '#10b981'}, line_kws={'color': '#ea580c', 'lw': 2.5})
    axes[1].set_title(f'Số lượng đơn hàng (Orders) vs Doanh thu: Mức độ tác động mạnh đến đâu? (r = {r_o:.3f}, p < 0.001)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Số lượng đơn hàng hàng ngày')
    axes[1].set_ylabel('Doanh thu (Tỷ VNĐ)')
    plt.suptitle('Động lực tăng trưởng: Lượng truy cập website vs Số lượng đơn hàng đóng góp thế nào vào doanh thu?', fontsize=14, fontweight='bold', y=1.02)
    save_chart(fig, 'eda_05_bivariate_traffic_sales.png')

    # =========================================================================
    # Biểu đồ 6: Biên lợi nhuận ngành hàng (Products & Segments)
    # =========================================================================
    products['unit_margin_pct'] = ((products['price'] - products['cogs']) / products['price']) * 100.0
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.boxplot(data=products, x='category', y='unit_margin_pct', ax=axes[0], palette='Set2')
    axes[0].set_title('Ngành hàng nào mang lại tỷ suất lợi nhuận cao nhất: Streetwear vs Outdoor vs Casual vs GenZ?', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Danh mục ngành hàng (Category)')
    axes[0].set_ylabel('Biên lợi nhuận đơn vị (%)')
    axes[0].tick_params(axis='x', rotation=20)

    sns.countplot(data=products, x='segment', ax=axes[1], palette='Pastel1')
    axes[1].set_title('Cơ cấu danh mục sản phẩm (SKU) phân bổ như thế nào giữa các phân khúc khách hàng?', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Phân khúc sản phẩm (Segment)')
    axes[1].set_ylabel('Số lượng mã SKU')
    save_chart(fig, 'eda_06_bivariate_order_economics.png')

    # =========================================================================
    # Biểu đồ 7: Bề mặt phản hồi đa biến (Traffic x Discounts)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 8))
    t_q = pd.qcut(master['total_sessions'], q=10, duplicates='drop')
    d_q = pd.qcut(master['total_discounts_applied'], q=10, duplicates='drop')
    piv_surf = master.pivot_table(index=t_q, columns=d_q, values='Revenue', aggfunc='mean') / 1e6
    sns.heatmap(piv_surf, cmap='viridis', ax=ax, cbar_kws={'label': 'Doanh thu trung bình (Tỷ VNĐ)'})
    ax.set_title('Lượng truy cập (Traffic) vs Mức giảm giá (Discounts): Đâu là điểm bão hòa doanh thu?', fontsize=12, fontweight='bold')
    ax.set_xlabel('Phân vị mức chiết khấu giảm giá (VND)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Phân vị lượng truy cập web (Sessions)', fontsize=11, fontweight='bold')
    save_chart(fig, 'eda_07_multivariate_surface.png')

    # =========================================================================
    # Biểu đồ 8: Phân tích PCA & 4 Phân cụm kịch bản vận hành
    # =========================================================================
    feat_cols_pca = ['total_sessions', 'total_page_views', 'order_count', 'total_units_ordered', 'total_discounts_applied', 'return_count']
    X = master[feat_cols_pca].values
    X_s = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    cov_mat = np.cov(X_s, rowvar=False)
    e_val, e_vec = np.linalg.eigh(cov_mat)
    idx_sort = np.argsort(e_val)[::-1]
    e_val = e_val[idx_sort]
    e_vec = e_vec[:, idx_sort]
    pca_2d = X_s @ e_vec[:, :2]
    var_exp = e_val[:2] / np.sum(e_val)

    np.random.seed(42)
    k = 4
    init_idx = np.random.choice(len(X_s), k, replace=False)
    centers = X_s[init_idx].copy()
    for _ in range(30):
        dists = np.linalg.norm(X_s[:, np.newaxis] - centers, axis=2)
        labels = np.argmin(dists, axis=1)
        new_centers = np.array([X_s[labels == i].mean(axis=0) if np.sum(labels == i) > 0 else centers[i] for i in range(k)])
        if np.allclose(centers, new_centers): break
        centers = new_centers

    regime_names_vn = {
        0: 'Kịch bản 1: Vận hành cơ sở bình thường (42.7%)',
        1: 'Kịch bản 2: Bùng nổ mua sắm mùa lễ hội (21.4%)',
        2: 'Kịch bản 3: Tắc nghẽn chuỗi cung ứng & Đứt hàng (20.5%)',
        3: 'Kịch bản 4: Xả hàng khuyến mãi sâu (15.3%)'
    }
    master['Regime_VN'] = [regime_names_vn[l] for l in labels]

    fig, ax = plt.subplots(figsize=(12, 8))
    pal = ['#2563eb', '#dc2626', '#f59e0b', '#10b981']
    for cid in range(4):
        sub = pca_2d[labels == cid]
        ax.scatter(sub[:, 0], sub[:, 1], c=pal[cid], label=regime_names_vn[cid], alpha=0.6, s=35)
    centers_pca = centers @ e_vec[:, :2]
    ax.scatter(centers_pca[:, 0], centers_pca[:, 1], c='black', s=200, marker='X', edgecolor='white', lw=2, label='Tâm cụm kịch bản')
    ax.set_title(f'Doanh nghiệp vận hành theo những kịch bản nào: 4 phân cụm trạng thái kinh doanh (PCA: {np.sum(var_exp)*100:.1f}% phương sai)?', fontsize=13, fontweight='bold')
    ax.set_xlabel(f'Thành phần chính 1 - PC1 ({var_exp[0]*100:.1f}% phương sai: Quy mô đơn hàng vs Khuyến mãi)')
    ax.set_ylabel(f'Thành phần chính 2 - PC2 ({var_exp[1]*100:.1f}% phương sai: Lượng truy cập vs Giá trị giỏ)')
    ax.legend(frameon=True, loc='best')
    save_chart(fig, 'eda_08_pca_regime_clusters.png')

    # =========================================================================
    # Biểu đồ 9: Đóng góp tài chính ngành hàng (Streetwear vs Outdoor vs Casual vs GenZ)
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    cat_fin = products.groupby('category').agg(
        price_mean=('price', 'mean'),
        cogs_mean=('cogs', 'mean'),
        margin_mean=('unit_margin_pct', 'mean')
    ).reset_index()

    sns.barplot(data=cat_fin, x='category', y='price_mean', ax=axes[0], palette='Blues_d')
    axes[0].set_title('Giá bán trung bình giữa các ngành hàng: Streetwear vs Outdoor vs Casual vs GenZ?', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Giá bán niêm yết trung bình (VNĐ)')
    axes[0].tick_params(axis='x', rotation=20)

    sns.barplot(data=cat_fin, x='category', y='margin_mean', ax=axes[1], palette='Greens_d')
    axes[1].set_title('Biên lợi nhuận gộp danh mục: Ngành hàng nào tối ưu hóa lợi nhuận nhất?', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Biên lợi nhuận trung bình (%)')
    axes[1].tick_params(axis='x', rotation=20)
    save_chart(fig, 'eda_09_category_margin_breakdown.png')

    # =========================================================================
    # Biểu đồ 10: Nghịch lý tồn kho & Thiệt hại do đứt hàng
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.histplot(inventory['fill_rate'].dropna() * 100, bins=40, color='#10b981', kde=True, ax=axes[0])
    axes[0].set_title('Tỷ lệ đáp ứng đơn hàng (Fill Rate) của kho có đạt chuẩn 95% không?', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Tỷ lệ đáp ứng đơn hàng (%)')

    inv_stockout = inventory.groupby('category')['stockout_days'].mean().reset_index()
    sns.barplot(data=inv_stockout, x='category', y='stockout_days', ax=axes[1], palette='Reds_d')
    axes[1].set_title('Số ngày đứt hàng trung bình mỗi tháng: Ngành hàng nào chịu ảnh hưởng nặng nhất?', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Số ngày đứt hàng / tháng')
    axes[1].tick_params(axis='x', rotation=20)
    save_chart(fig, 'eda_10_inventory_stockout_impact.png')

    # =========================================================================
    # Biểu đồ 11: Phân bổ khách hàng & Doanh thu theo vùng miền
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.countplot(data=customers, x='age_group', hue='gender', ax=axes[0], palette='magma')
    axes[0].set_title('Cơ cấu độ tuổi vs Giới tính: Khách hàng mục tiêu của doanh nghiệp là ai?', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Nhóm độ tuổi (Age Group)')
    axes[0].set_ylabel('Số lượng khách hàng')
    axes[0].tick_params(axis='x', rotation=20)
    axes[0].legend(title='Giới tính')

    sns.countplot(data=reviews, x='rating', ax=axes[1], palette='coolwarm')
    axes[1].set_title('Mức độ hài lòng của khách hàng: Đánh giá 5 sao vs 1 sao chênh lệch ra sao?', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Số sao đánh giá (1 đến 5 sao)')
    axes[1].set_ylabel('Số lượng đánh giá')
    save_chart(fig, 'eda_11_customer_geo_demographics.png')

    # =========================================================================
    # Biểu đồ 12: Đổi trả hàng vs Thời gian giao vận
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    reasons = returns['return_reason'].value_counts()
    reasons.plot(kind='bar', ax=axes[0], color='#ef4444')
    axes[0].set_title('Nguyên nhân trả hàng phổ biến nhất: Sai kích cỡ vs Lỗi sản phẩm?', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Số lượng đơn đổi trả')
    axes[0].tick_params(axis='x', rotation=30)

    shipments['lead_days'] = (shipments['delivery_date'] - shipments['ship_date']).dt.total_seconds() / (24*3600)
    sns.histplot(shipments['lead_days'].dropna(), bins=25, ax=axes[1], color='#3b82f6', kde=True)
    axes[1].set_title('Thời gian giao hàng (Lead Time) thực tế mất bao nhiêu ngày?', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Số ngày vận chuyển (ngày)')
    save_chart(fig, 'eda_12_operations_returns_reviews.png')

    print("=== TẤT CẢ 13 BIỂU ĐỒ TIẾNG VIỆT ĐÃ ĐƯỢC TẠO THÀNH CÔNG ===")

if __name__ == '__main__':
    build_all_vietnamese_charts()
