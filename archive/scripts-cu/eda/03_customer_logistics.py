"""EDA chi tiết: khách hàng/vùng/kênh và vận hành/trả hàng/khuyến mãi.

Nguồn: archive/engine-goc/customer_logistics_eda.py. Thay đổi so với bản gốc:
  - Đổi tên file đầu ra (bản gốc trùng tên eda_11/eda_12 với bản tiếng Việt nên bị ghi đè).
  - Mọi con số trong khung chú thích được TÍNH từ dữ liệu (bản gốc gõ cứng, nhiều số sai:
    tỷ lệ trả hàng, tiền hoàn theo danh mục, IQR, lift khuyến mãi).
  - Bỏ ylim cố định làm cắt cột (tỷ lệ trả ~3.4% > 2.0; Streetwear 406.7M > 350).

Đầu ra: outputs/eda/eda_15_customer_region_channel.png, outputs/eda/eda_16_ops_returns_promo.png
Chạy:   python scripts/eda/03_customer_logistics.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.stats as stats  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as ticker  # noqa: E402
import seaborn as sns  # noqa: E402

from ds317 import load_many, out_dir  # noqa: E402
from ds317.viz import save_fig, setup_style  # noqa: E402

BOX = dict(boxstyle="round,pad=0.5", alpha=0.95)


def promo_theme(name: str) -> str:
    for key, theme in [("Spring", "Spring Sale"), ("Mid-Year", "Mid-Year Sale"), ("Fall", "Fall Launch"),
                       ("Year-End", "Year-End Sale"), ("Urban", "Urban Blowout"), ("Rural", "Rural Special")]:
        if key in name:
            return theme
    return "Other"


def main():
    setup_style()
    out = out_dir("eda")
    t = load_many("customers", "geography", "orders", "order_items", "products", "shipments",
                  "returns", "reviews", "promotions", "sales")
    geo = t["geography"].drop_duplicates(subset=["zip"])[["zip", "region"]]
    oi = t["order_items"]
    oi["item_revenue"] = oi["quantity"] * oi["unit_price"] - oi["discount_amount"]

    # TODO(phuong-phap): doanh thu ở đây tính cả đơn cancelled; cân nhắc lọc theo order_status.
    orders_full = (t["orders"]
                   .merge(oi.groupby("order_id")["item_revenue"].sum().reset_index(), on="order_id", how="left")
                   .merge(t["customers"][["customer_id", "gender", "age_group", "acquisition_channel"]], on="customer_id", how="left")
                   .merge(geo, on="zip", how="left"))

    # ======================= eda_15: khách hàng, vùng, kênh =======================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    colors_reg = ["#3b82f6", "#10b981", "#f59e0b"]

    # (A) Doanh thu theo vùng
    reg = orders_full.groupby("region")["item_revenue"].agg(["sum", "count"]).reset_index()
    reg["pct"] = reg["sum"] / reg["sum"].sum() * 100
    bars = axes[0, 0].bar(reg["region"], reg["sum"] / 1e9, color=colors_reg, edgecolor="black", alpha=0.85, width=0.55)
    for bar, pct, cnt in zip(bars, reg["pct"], reg["count"]):
        axes[0, 0].annotate(f"{bar.get_height():.2f}B ({pct:.1f}%)\nN={cnt:,} orders",
                            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            ha="center", va="bottom", fontsize=9.5, fontweight="bold", xytext=(0, 4), textcoords="offset points")
    axes[0, 0].margins(y=0.2)
    top = reg.loc[reg["pct"].idxmax()]
    axes[0, 0].text(0.05, 0.88, f"{top['region']} chiếm {top['pct']:.1f}% doanh thu\nTổng: {reg['sum'].sum() / 1e9:.2f}B",
                    transform=axes[0, 0].transAxes, fontsize=9.5, bbox={**BOX, "facecolor": "#eff6ff", "edgecolor": "#93c5fd"})
    axes[0, 0].set_title("(A) Net Revenue by Region", fontsize=12, fontweight="bold")
    axes[0, 0].set_ylabel("Net Revenue (Billions)")

    # (B) Kênh thu hút khách
    chan = orders_full.groupby("acquisition_channel").agg(order_count=("order_id", "count"), total_rev=("item_revenue", "sum")) \
        .reset_index().sort_values("total_rev", ascending=False)
    x, w = np.arange(len(chan)), 0.38
    axes[0, 1].bar(x - w / 2, chan["total_rev"] / 1e9, w, label="Revenue (B)", color="#2563eb", alpha=0.85, edgecolor="black")
    ax2 = axes[0, 1].twinx()
    ax2.bar(x + w / 2, chan["order_count"] / 1e3, w, label="Orders (k)", color="#10b981", alpha=0.85, edgecolor="black")
    ax2.grid(False)
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels([c.replace("_", " ").title() for c in chan["acquisition_channel"]], rotation=25, ha="right")
    axes[0, 1].set_title("(B) Acquisition Channel: Revenue vs Order Volume", fontsize=12, fontweight="bold")
    axes[0, 1].set_ylabel("Revenue (Billions)", color="#2563eb")
    ax2.set_ylabel("Orders (Thousands)", color="#10b981")
    h1, l1 = axes[0, 1].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    axes[0, 1].legend(h1 + h2, l1 + l2, loc="upper right")

    # (C) Nhân khẩu học
    cust = t["customers"]
    age_gender = cust.groupby(["age_group", "gender"]).size().unstack(fill_value=0)
    pal_g = {"Female": "#ec4899", "Male": "#3b82f6", "Non-binary": "#8b5cf6"}
    age_gender.plot(kind="bar", ax=axes[1, 0], color=[pal_g.get(c, "#999") for c in age_gender.columns],
                    edgecolor="black", alpha=0.85, width=0.7)
    age_pct = cust["age_group"].value_counts(normalize=True) * 100
    g_pct = cust["gender"].value_counts(normalize=True) * 100
    chi_p = stats.chi2_contingency(age_gender)[1]
    axes[1, 0].text(0.04, 0.80,
                    f"Nhóm lớn nhất: {age_pct.index[0]} ({age_pct.iloc[0]:.1f}%), {age_pct.index[1]} ({age_pct.iloc[1]:.1f}%)\n"
                    + " | ".join(f"{k} {v:.1f}%" for k, v in g_pct.items())
                    + f"\nChi-square độc lập tuổi x giới: p = {chi_p:.3f}",
                    transform=axes[1, 0].transAxes, fontsize=9, bbox={**BOX, "facecolor": "#fdf2f8", "edgecolor": "#f472b6"})
    axes[1, 0].set_title(f"(C) Age Group by Gender (N={len(cust):,})", fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel("Age Group")
    axes[1, 0].set_ylabel("Customer Count")
    axes[1, 0].tick_params(axis="x", rotation=0)
    axes[1, 0].legend(title="Gender", loc="upper right")

    # (D) Giá trị đơn theo vùng
    sns.boxplot(data=orders_full, x="region", y="item_revenue", ax=axes[1, 1], palette=colors_reg, showmeans=True,
                showfliers=False, meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
    q = orders_full.groupby("region")["item_revenue"].describe()
    kw = stats.kruskal(*[g["item_revenue"].dropna() for _, g in orders_full.groupby("region")])
    axes[1, 1].text(0.05, 0.70,
                    "\n".join(f"• {r}: Median {row['50%']:,.0f} | Mean {row['mean']:,.0f} | IQR {row['75%'] - row['25%']:,.0f}"
                              for r, row in q.iterrows())
                    + f"\nKruskal-Wallis H = {kw.statistic:,.1f}, p = {kw.pvalue:.1e}",
                    transform=axes[1, 1].transAxes, fontsize=9, bbox={**BOX, "facecolor": "#fefce8", "edgecolor": "#fde047"})
    axes[1, 1].set_title("(D) Order Value by Region (ẩn điểm ngoài 1.5×IQR)", fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("Region")
    axes[1, 1].set_ylabel("Order Value")
    plt.suptitle("EDA 15: Customer Demographics, Regional Distribution & Acquisition Economics", fontsize=14, fontweight="bold", y=0.995)
    save_fig(fig, out / "eda_15_customer_region_channel.png")

    # ======================= eda_16: vận hành, trả hàng, khuyến mãi =======================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # (A) Thời gian giao vs điểm đánh giá
    ship = t["shipments"].copy()
    ship["lead_days"] = (ship["delivery_date"] - ship["ship_date"]).dt.days
    rs = t["reviews"].merge(ship[["order_id", "lead_days"]], on="order_id", how="inner")
    agg = rs.groupby("lead_days")["rating"].agg(mean_rating="mean", pct_5=lambda s: (s == 5).mean() * 100,
                                                pct_1=lambda s: (s == 1).mean() * 100).reset_index()
    ax, axb = axes[0, 0], axes[0, 0].twinx()
    ax.plot(agg["lead_days"], agg["mean_rating"], marker="o", lw=2.5, color="#dc2626", label="Mean Rating")
    axb.bar(agg["lead_days"] - 0.12, agg["pct_5"], width=0.24, alpha=0.35, color="#16a34a", label="5-Star %")
    axb.bar(agg["lead_days"] + 0.12, agg["pct_1"], width=0.24, alpha=0.35, color="#ea580c", label="1-Star %")
    axb.grid(False)
    r = stats.pearsonr(rs["lead_days"], rs["rating"])
    f = stats.f_oneway(*[g["rating"] for _, g in rs.groupby("lead_days")])
    best, worst = agg.loc[agg["mean_rating"].idxmax()], agg.loc[agg["mean_rating"].idxmin()]
    ax.text(0.05, 0.10,
            f"• Pearson r = {r.statistic:.4f} (p = {r.pvalue:.4f})\n• ANOVA F = {f.statistic:.3f} (p = {f.pvalue:.4f})\n"
            f"• Cao nhất: {best['lead_days']:.0f} ngày ({best['mean_rating']:.3f} sao)\n"
            f"• Thấp nhất: {worst['lead_days']:.0f} ngày ({worst['mean_rating']:.3f} sao)",
            transform=ax.transAxes, fontsize=9, bbox={**BOX, "facecolor": "#fff1f2", "edgecolor": "#fda4af"})
    ax.set_title(f"(A) Delivery Lead Time vs Review Rating (N={len(rs):,})", fontsize=12, fontweight="bold")
    ax.set_xlabel("Lead time (days)")
    ax.set_ylabel("Mean Rating", color="#dc2626")
    axb.set_ylabel("Rating share (%)", color="#16a34a")
    ax.legend(loc="upper right")

    # (B) Pareto lý do trả hàng
    rets = t["returns"]
    rr = rets["return_reason"].value_counts().rename_axis("reason").reset_index(name="count")
    rr["cum_pct"] = rr["count"].cumsum() / rr["count"].sum() * 100
    ax, axb = axes[0, 1], axes[0, 1].twinx()
    labels = [s.replace("_", " ").title() for s in rr["reason"]]
    bars = ax.bar(labels, rr["count"], color="#3b82f6", edgecolor="black", alpha=0.85, width=0.55)
    axb.plot(labels, rr["cum_pct"], color="#dc2626", marker="D", lw=2.5, label="Cumulative %")
    axb.axhline(80, color="#6b7280", linestyle="--", lw=1.5, label="80% Pareto")
    axb.set_ylim(0, 105)
    axb.grid(False)
    for bar, c in zip(bars, rr["count"]):
        ax.annotate(f"{c:,}\n({c / rr['count'].sum() * 100:.1f}%)", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", xytext=(0, 3), textcoords="offset points")
    ax.margins(y=0.15)
    ax.set_title("(B) Return Reasons Pareto", fontsize=12, fontweight="bold")
    ax.set_ylabel("Return count")
    ax.tick_params(axis="x", rotation=25)
    axb.legend(loc="lower right")

    # (C) Tỷ lệ trả & tiền hoàn theo danh mục
    prod = t["products"][["product_id", "category"]]
    cat = oi.merge(prod, on="product_id").groupby("category")["quantity"].sum().rename("units_sold").to_frame()
    cat = cat.join(rets.merge(prod, on="product_id").groupby("category")
                   .agg(units_returned=("return_quantity", "sum"), refund=("refund_amount", "sum")))
    cat["rate"] = cat["units_returned"] / cat["units_sold"] * 100
    x, w = np.arange(len(cat)), 0.35
    ax, axb = axes[1, 0], axes[1, 0].twinx()
    ax.bar(x - w / 2, cat["rate"], w, label="Unit Return Rate (%)", color="#f59e0b", edgecolor="black", alpha=0.85)
    axb.bar(x + w / 2, cat["refund"] / 1e6, w, label="Refund (M)", color="#ef4444", edgecolor="black", alpha=0.85)
    axb.grid(False)
    ax.set_xticks(x)
    ax.set_xticklabels(cat.index, rotation=15)
    ax.set_ylim(0, cat["rate"].max() * 1.6)
    axb.set_ylim(0, cat["refund"].max() / 1e6 * 1.6)
    top2 = cat["refund"].sort_values(ascending=False).head(2) / 1e6
    ax.text(0.30, 0.80,
            f"Hoàn tiền lớn nhất: {top2.index[0]} ({top2.iloc[0]:.1f}M), {top2.index[1]} ({top2.iloc[1]:.1f}M)\n"
            f"Tỷ lệ trả theo danh mục: {cat['rate'].min():.2f}% - {cat['rate'].max():.2f}%\n"
            f"Tổng: {len(rets):,} lượt trả | {rets['refund_amount'].sum() / 1e6:.1f}M hoàn tiền",
            transform=ax.transAxes, fontsize=8.5, bbox={**BOX, "facecolor": "#fef3c7", "edgecolor": "#fcd34d"})
    ax.set_title("(C) Return Rate & Refund by Category", fontsize=12, fontweight="bold")
    ax.set_ylabel("Unit Return Rate (%)", color="#f59e0b")
    axb.set_ylabel("Refunds (Millions)", color="#ef4444")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = axb.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left")

    # (D) Lift doanh thu theo chủ đề khuyến mãi (vs 30 ngày trước)
    # TODO(phuong-phap): so với 30 ngày trước lẫn hiệu ứng mùa vụ -> nên so cùng kỳ năm trước.
    si = t["sales"].set_index("Date").sort_index()
    lifts = []
    for _, row in t["promotions"].iterrows():
        before = si.loc[row["start_date"] - pd.Timedelta(days=30):row["start_date"] - pd.Timedelta(days=1), "Revenue"]
        during = si.loc[row["start_date"]:row["end_date"], "Revenue"]
        if len(before) and len(during):
            lifts.append({"theme": promo_theme(row["promo_name"]), "lift": (during.mean() / before.mean() - 1) * 100})
    lf = pd.DataFrame(lifts)
    th = lf.groupby("theme")["lift"].mean().sort_values(ascending=False)
    bars = axes[1, 1].barh(th.index, th.values, color=["#10b981" if v > 0 else "#ef4444" for v in th.values],
                           edgecolor="black", alpha=0.85, height=0.55)
    axes[1, 1].axvline(0, color="black", lw=1.2)
    axes[1, 1].bar_label(bars, labels=[f"{v:+.1f}%" for v in th.values], padding=4, fontsize=9.5, fontweight="bold")
    axes[1, 1].margins(x=0.2)
    rng = np.random.default_rng(42)
    boot = [rng.choice(lf["lift"], len(lf)).mean() for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    disc = oi.loc[oi["discount_amount"] > 0]
    axes[1, 1].text(0.04, 0.06,
                    f"• 95% bootstrap CI của lift trung bình: [{lo:+.1f}%, {hi:+.1f}%]\n"
                    f"• Dòng hàng có promo_id: {oi['promo_id'].notna().mean() * 100:.1f}%\n"
                    f"• Mức chiết khấu TB (dòng có giảm giá): {(disc['discount_amount'] / (disc['quantity'] * disc['unit_price'])).mean() * 100:.1f}%",
                    transform=axes[1, 1].transAxes, fontsize=8.8, bbox={**BOX, "facecolor": "#f0fdf4", "edgecolor": "#86efac"})
    axes[1, 1].set_title("(D) Mean Revenue Lift by Promo Theme (vs 30-day pre-window)", fontsize=12, fontweight="bold")
    axes[1, 1].xaxis.set_major_formatter(ticker.FormatStrFormatter("%+.0f%%"))
    plt.suptitle("EDA 16: Operations, Returns, Reviews & Promo Dynamics", fontsize=14, fontweight="bold", y=0.995)
    save_fig(fig, out / "eda_16_ops_returns_promo.png")


if __name__ == "__main__":
    main()
