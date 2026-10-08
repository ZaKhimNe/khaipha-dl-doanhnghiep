"""Bộ biểu đồ EDA tiếng Việt (eda_01 ... eda_12 + eda_stratified_sample_fidelity).

Nguồn: archive/engine-goc/generate_vietnamese_charts.py. Thay đổi so với bản gốc:
  - Đơn vị: giá trị chia 1e6 là TRIỆU (bản gốc ghi nhầm "Tỷ VNĐ").
  - Tên cụm K-means: bản gốc gán tên/tỷ lệ cố định theo số thứ tự cụm (số thứ tự này
    ngẫu nhiên) -> nay ghi "Cụm i (x%)" với tỷ lệ tính từ dữ liệu.

Đầu ra: outputs/eda/*.png
Chạy:   python scripts/eda/02_eda_charts_vi.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.stats as stats  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from ds317 import load_many, out_dir  # noqa: E402
from ds317.panel import build_daily_panel  # noqa: E402
from ds317.viz import save_fig, setup_style  # noqa: E402

UNIT = "Triệu VNĐ"


def main():
    setup_style()
    out = out_dir("eda")
    t = load_many("sales", "web_traffic", "orders", "order_items", "products", "inventory",
                  "returns", "reviews", "shipments", "customers")
    master = build_daily_panel(t)
    products = t["products"].copy()

    # --- Lấy mẫu phân tầng 150k vs toàn bộ 714k ---------------------------------------------
    items = t["order_items"].merge(products[["product_id", "category"]], on="product_id", how="left")
    items = items.merge(t["orders"][["order_id", "order_date"]], on="order_id", how="left")
    items["Year"] = items["order_date"].dt.year
    items["Item_Revenue"] = items["quantity"] * items["unit_price"] - items["discount_amount"]
    sample = items.groupby(["Year", "category"], group_keys=False).sample(
        frac=150000 / len(items), random_state=42).reset_index(drop=True)
    ks_stat, _ = stats.ks_2samp(items["Item_Revenue"], sample["Item_Revenue"])

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    mix = pd.DataFrame({
        f"Toàn bộ dữ liệu ({len(items) / 1e3:.0f}k dòng)": items["category"].value_counts(normalize=True) * 100,
        f"Mẫu phân tầng ({len(sample) / 1e3:.0f}k dòng)": sample["category"].value_counts(normalize=True) * 100,
    })
    mix.plot(kind="bar", ax=axes[0], color=["#2563eb", "#10b981"], width=0.7)
    axes[0].set_title("Tỷ trọng danh mục sản phẩm: Mẫu phân tầng vs Dữ liệu gốc?", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Tỷ trọng (%)")
    axes[0].tick_params(axis="x", rotation=20)
    sns.kdeplot(items["Item_Revenue"].clip(upper=50000), ax=axes[1], color="#2563eb", lw=2, label="Toàn bộ dữ liệu")
    sns.kdeplot(sample["Item_Revenue"].clip(upper=50000), ax=axes[1], color="#10b981", lw=2, linestyle="--", label="Mẫu phân tầng")
    axes[1].set_title(f"Phân phối doanh thu: Dữ liệu mẫu vs Dữ liệu gốc có bị lệch không? (KS D={ks_stat:.5f})",
                      fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Doanh thu từng dòng sản phẩm (VNĐ)")
    axes[1].legend()
    plt.suptitle("Phương pháp lấy mẫu phân tầng có đảm bảo đại diện cho toàn bộ dữ liệu?", fontsize=14, fontweight="bold", y=1.02)
    save_fig(fig, out / "eda_stratified_sample_fidelity.png")

    # --- eda_01: Phân phối doanh thu, giá vốn, lợi nhuận, biên ---------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, col, color, label in [(axes[0, 0], "Revenue", "#2563eb", "Doanh thu"),
                                  (axes[0, 1], "COGS", "#ea580c", "Giá vốn COGS")]:
        s = master[col] / 1e6
        sns.histplot(s, kde=True, ax=ax, color=color, bins=40, stat="density")
        ax.axvline(s.mean(), color="#dc2626", linestyle="--", label=f"Trung bình: {s.mean():.2f} triệu")
        ax.axvline(s.median(), color="#16a34a", linestyle=":", label=f"Trung vị: {s.median():.2f} triệu")
        ax.set_xlabel(f"{label} ({UNIT})")
        ax.legend()
    axes[0, 0].set_title("Doanh thu hàng ngày phân phối như thế nào? (Trung bình vs Trung vị)", fontsize=12, fontweight="bold")
    axes[0, 1].set_title("Giá vốn hàng bán (COGS) chiếm bao nhiêu trong doanh thu?", fontsize=12, fontweight="bold")
    sns.boxplot(x=master["Gross_Profit"] / 1e6, ax=axes[1, 0], color="#10b981")
    axes[1, 0].set_title("Lợi nhuận gộp hàng ngày: Có xuất hiện điểm ngoại lai (Outliers) không?", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel(f"Lợi nhuận gộp ({UNIT})")
    sns.histplot(master["Gross_Margin_Pct"], kde=True, ax=axes[1, 1], color="#8b5cf6", bins=35)
    axes[1, 1].axvline(master["Gross_Margin_Pct"].mean(), color="#dc2626", linestyle="--",
                       label=f"Biên TB: {master['Gross_Margin_Pct'].mean():.1f}%")
    axes[1, 1].set_title("Tỷ suất lợi nhuận gộp (%) phân phối quanh mức nào?", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("Biên lợi nhuận gộp (%)")
    axes[1, 1].legend()
    plt.suptitle("Cấu trúc kinh tế hàng ngày: Doanh thu vs Giá vốn vs Biên lợi nhuận (2012–2022)?", fontsize=14, fontweight="bold", y=0.98)
    save_fig(fig, out / "eda_01_target_distributions.png")

    # --- eda_02: Xu hướng 10 năm ---------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(15, 9), sharex=True)
    specs = [
        ("Revenue", 1e6, "#2563eb", "#dc2626", "Doanh thu ngày", f"Doanh thu ({UNIT})",
         "Doanh thu thực tế vs Đường trung bình động 30 ngày qua 10 năm?"),
        ("COGS", 1e6, "#ea580c", "#b91c1c", "Giá vốn ngày", f"Giá vốn COGS ({UNIT})",
         "Giá vốn COGS tăng trưởng theo chu kỳ thế nào so với doanh thu?"),
        ("Gross_Margin_Pct", 1, "#10b981", "#047857", "Biên lợi nhuận (%)", "Biên lợi nhuận (%)",
         "Tỷ suất lợi nhuận gộp có duy trì ổn định qua các năm không?"),
    ]
    for ax, (col, scale, c1, c2, lab, ylab, title) in zip(axes, specs):
        ax.plot(master["Date"], master[col] / scale, color=c1, lw=0.8, label=lab)
        ax.plot(master["Date"], master[col].rolling(30).mean() / scale, color=c2, lw=2, label="Đường MA 30 ngày")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylab)
        ax.legend(loc="upper left")
    save_fig(fig, out / "eda_02_timeseries_stl_decomposition.png")

    # --- eda_03: Mùa vụ thứ x tháng ------------------------------------------------------------
    piv = master.pivot_table(index="DayOfWeek", columns="Month", values="Revenue", aggfunc="mean") / 1e6
    piv.index = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    piv.columns = [f"Tháng {m}" for m in range(1, 13)]
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.heatmap(piv, cmap="Blues", annot=True, fmt=".2f", cbar_kws={"label": f"Doanh thu trung bình ({UNIT})"}, ax=ax)
    ax.set_title("Thời điểm nào trong năm đạt đỉnh doanh thu: Thứ trong tuần vs Tháng trong năm?", fontsize=13, fontweight="bold")
    ax.set_xlabel("Tháng trong năm", fontsize=11, fontweight="bold")
    ax.set_ylabel("Thứ trong tuần", fontsize=11, fontweight="bold")
    save_fig(fig, out / "eda_03_seasonality_heatmap.png")

    # --- eda_04: Tương quan --------------------------------------------------------------------
    corr_names = {
        "Revenue": "Doanh thu", "COGS": "Giá vốn COGS", "Gross_Profit": "Lợi nhuận gộp",
        "total_sessions": "Lượng truy cập", "total_page_views": "Lượt xem trang", "order_count": "Số đơn hàng",
        "total_units_ordered": "Số lượng SP", "total_discounts_applied": "Chiết khấu",
        "return_count": "Số lượng trả", "avg_bounce_rate": "Tỷ lệ thoát",
    }
    corr = master[list(corr_names)].rename(columns=corr_names).corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, ax=ax)
    ax.set_title("Những chỉ số vận hành nào có tương quan mạnh nhất vs Doanh thu và Chi phí?", fontsize=13, fontweight="bold")
    save_fig(fig, out / "eda_04_correlation_matrix.png")

    # --- eda_05: Truy cập / đơn hàng vs doanh thu ----------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, col, c1, c2, xlab, title in [
        (axes[0], "total_sessions", "#3b82f6", "#dc2626", "Lượt truy cập hàng ngày (Sessions)",
         "Lượng truy cập (Sessions) vs Doanh thu: Liệu có tương quan thuận?"),
        (axes[1], "order_count", "#10b981", "#ea580c", "Số lượng đơn hàng hàng ngày",
         "Số lượng đơn hàng vs Doanh thu: Mức độ tác động mạnh đến đâu?"),
    ]:
        r, p = stats.pearsonr(master[col], master["Revenue"])
        sns.regplot(x=master[col], y=master["Revenue"] / 1e6, ax=ax,
                    scatter_kws={"alpha": 0.3, "color": c1}, line_kws={"color": c2, "lw": 2.5})
        ax.set_title(f"{title} (r = {r:.3f}, p = {p:.1e})", fontsize=12, fontweight="bold")
        ax.set_xlabel(xlab)
        ax.set_ylabel(f"Doanh thu ({UNIT})")
    plt.suptitle("Động lực tăng trưởng: Lượng truy cập website vs Số lượng đơn hàng đóng góp thế nào vào doanh thu?",
                 fontsize=14, fontweight="bold", y=1.02)
    save_fig(fig, out / "eda_05_bivariate_traffic_sales.png")

    # --- eda_06: Biên lợi nhuận theo danh mục, số SKU theo phân khúc ---------------------------
    products["unit_margin_pct"] = (products["price"] - products["cogs"]) / products["price"] * 100.0
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.boxplot(data=products, x="category", y="unit_margin_pct", ax=axes[0], palette="Set2")
    axes[0].set_title("Ngành hàng nào mang lại tỷ suất lợi nhuận cao nhất: Streetwear vs Outdoor vs Casual vs GenZ?",
                      fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Danh mục ngành hàng (Category)")
    axes[0].set_ylabel("Biên lợi nhuận đơn vị (%)")
    axes[0].tick_params(axis="x", rotation=20)
    sns.countplot(data=products, x="segment", ax=axes[1], palette="Pastel1")
    axes[1].set_title("Cơ cấu danh mục sản phẩm (SKU) phân bổ như thế nào giữa các phân khúc?", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Phân khúc sản phẩm (Segment)")
    axes[1].set_ylabel("Số lượng mã SKU")
    save_fig(fig, out / "eda_06_bivariate_order_economics.png")

    # --- eda_07: Truy cập x chiết khấu -> doanh thu --------------------------------------------
    t_q = pd.qcut(master["total_sessions"], q=10, duplicates="drop")
    d_q = pd.qcut(master["total_discounts_applied"], q=10, duplicates="drop")
    surf = master.pivot_table(index=t_q, columns=d_q, values="Revenue", aggfunc="mean", observed=False) / 1e6
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(surf, cmap="viridis", ax=ax, cbar_kws={"label": f"Doanh thu trung bình ({UNIT})"})
    ax.set_title("Lượng truy cập (Traffic) vs Mức giảm giá (Discounts): Đâu là điểm bão hòa doanh thu?", fontsize=12, fontweight="bold")
    ax.set_xlabel("Phân vị mức chiết khấu (VNĐ)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Phân vị lượng truy cập web (Sessions)", fontsize=11, fontweight="bold")
    save_fig(fig, out / "eda_07_multivariate_surface.png")

    # --- eda_08: PCA + K-means (k=4), cài bằng NumPy -------------------------------------------
    feat = ["total_sessions", "total_page_views", "order_count", "total_units_ordered", "total_discounts_applied", "return_count"]
    X = master[feat].values
    Xs = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    e_val, e_vec = np.linalg.eigh(np.cov(Xs, rowvar=False))
    order = np.argsort(e_val)[::-1]
    e_val, e_vec = e_val[order], e_vec[:, order]
    pca_2d = Xs @ e_vec[:, :2]
    var_exp = e_val[:2] / e_val.sum()

    rng = np.random.default_rng(42)
    k = 4
    centers = Xs[rng.choice(len(Xs), k, replace=False)].copy()
    for _ in range(30):
        labels = np.argmin(np.linalg.norm(Xs[:, None] - centers, axis=2), axis=1)
        new = np.array([Xs[labels == i].mean(axis=0) if (labels == i).any() else centers[i] for i in range(k)])
        if np.allclose(centers, new):
            break
        centers = new
    # TODO(phan-tich): đặt tên ý nghĩa cho từng cụm dựa trên profile tâm cụm (centers), không gán cứng.
    shares = np.bincount(labels, minlength=k) / len(labels) * 100

    fig, ax = plt.subplots(figsize=(12, 8))
    pal = ["#2563eb", "#dc2626", "#f59e0b", "#10b981"]
    for cid in range(k):
        sub = pca_2d[labels == cid]
        ax.scatter(sub[:, 0], sub[:, 1], c=pal[cid], label=f"Cụm {cid + 1} ({shares[cid]:.1f}%)", alpha=0.6, s=35)
    cp = centers @ e_vec[:, :2]
    ax.scatter(cp[:, 0], cp[:, 1], c="black", s=200, marker="X", edgecolor="white", lw=2, label="Tâm cụm")
    ax.set_title(f"Doanh nghiệp vận hành theo những trạng thái nào: 4 cụm (PCA giải thích {var_exp.sum() * 100:.1f}% phương sai)?",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel(f"Thành phần chính 1 - PC1 ({var_exp[0] * 100:.1f}% phương sai)")
    ax.set_ylabel(f"Thành phần chính 2 - PC2 ({var_exp[1] * 100:.1f}% phương sai)")
    ax.legend(frameon=True, loc="best")
    save_fig(fig, out / "eda_08_pca_regime_clusters.png")

    # --- eda_09: Giá & biên lợi nhuận trung bình theo danh mục ---------------------------------
    cat_fin = products.groupby("category").agg(price_mean=("price", "mean"), margin_mean=("unit_margin_pct", "mean")).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.barplot(data=cat_fin, x="category", y="price_mean", ax=axes[0], palette="Blues_d")
    axes[0].set_title("Giá bán trung bình giữa các ngành hàng: Streetwear vs Outdoor vs Casual vs GenZ?", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Giá bán niêm yết trung bình (VNĐ)")
    sns.barplot(data=cat_fin, x="category", y="margin_mean", ax=axes[1], palette="Greens_d")
    axes[1].set_title("Biên lợi nhuận gộp danh mục: Ngành hàng nào tối ưu hóa lợi nhuận nhất?", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Biên lợi nhuận trung bình (%)")
    for ax in axes:
        ax.tick_params(axis="x", rotation=20)
    save_fig(fig, out / "eda_09_category_margin_breakdown.png")

    # --- eda_10: Fill rate & đứt hàng ----------------------------------------------------------
    inv = t["inventory"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.histplot(inv["fill_rate"].dropna() * 100, bins=40, color="#10b981", kde=True, ax=axes[0])
    axes[0].set_title("Tỷ lệ đáp ứng đơn hàng (Fill Rate) của kho có đạt chuẩn 95% không?", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Tỷ lệ đáp ứng đơn hàng (%)")
    sns.barplot(data=inv.groupby("category")["stockout_days"].mean().reset_index(),
                x="category", y="stockout_days", ax=axes[1], palette="Reds_d")
    axes[1].set_title("Số ngày đứt hàng trung bình mỗi tháng: Ngành hàng nào chịu ảnh hưởng nặng nhất?", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Số ngày đứt hàng / tháng")
    axes[1].tick_params(axis="x", rotation=20)
    save_fig(fig, out / "eda_10_inventory_stockout_impact.png")

    # --- eda_11: Khách hàng & đánh giá ---------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.countplot(data=t["customers"], x="age_group", hue="gender", ax=axes[0], palette="magma",
                  order=sorted(t["customers"]["age_group"].unique()))
    axes[0].set_title("Cơ cấu độ tuổi vs Giới tính: Khách hàng mục tiêu của doanh nghiệp là ai?", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Nhóm độ tuổi")
    axes[0].set_ylabel("Số lượng khách hàng")
    axes[0].legend(title="Giới tính")
    sns.countplot(data=t["reviews"], x="rating", ax=axes[1], palette="coolwarm")
    axes[1].set_title("Mức độ hài lòng của khách hàng: Đánh giá 5 sao vs 1 sao chênh lệch ra sao?", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Số sao đánh giá (1 đến 5 sao)")
    axes[1].set_ylabel("Số lượng đánh giá")
    save_fig(fig, out / "eda_11_customer_geo_demographics.png")

    # --- eda_12: Lý do trả hàng & thời gian giao -----------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    t["returns"]["return_reason"].value_counts().plot(kind="bar", ax=axes[0], color="#ef4444")
    axes[0].set_title("Nguyên nhân trả hàng phổ biến nhất: Sai kích cỡ vs Lỗi sản phẩm?", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Lý do trả hàng")
    axes[0].set_ylabel("Số lượng đơn đổi trả")
    axes[0].tick_params(axis="x", rotation=30)
    lead = (t["shipments"]["delivery_date"] - t["shipments"]["ship_date"]).dt.days
    sns.countplot(x=lead, ax=axes[1], color="#3b82f6")
    axes[1].set_title("Thời gian giao hàng (Lead Time) thực tế mất bao nhiêu ngày?", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Số ngày vận chuyển (ngày)")
    axes[1].set_ylabel("Số đơn")
    save_fig(fig, out / "eda_12_operations_returns_reviews.png")


if __name__ == "__main__":
    main()
