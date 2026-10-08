"""Biểu đồ kiểm toán chất lượng dữ liệu (eda_13, eda_14), nền tối, tiếng Việt.

Nguồn: archive/engine-goc/generate_dirtiness_charts.py. Thay đổi so với bản gốc:
  - Mọi con số (73.80%, 18.62%, 382 ngày, 181 ngày, 564 đơn, 62.16%...) được TÍNH từ dữ liệu.
  - eda_14 phải: chênh lệch sales.Revenue vs doanh thu net chính là chiết khấu
    (Revenue = doanh thu gộp trước chiết khấu), không phải "lệch đối soát".

Đầu ra: outputs/eda/eda_13_data_dirtiness_audit.png, outputs/eda/eda_14_reconciliation_pitfalls.png
Chạy:   python scripts/audit/02_data_quality_charts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from ds317 import load_many, out_dir  # noqa: E402
from ds317.viz import save_fig, setup_style  # noqa: E402

BG, PANEL, FG, MUTED = "#0f172a", "#1e293b", "#f8fafc", "#94a3b8"


def dark(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, linestyle=":", alpha=0.2, color=MUTED)


def legend(ax, **kw):
    ax.legend(facecolor=PANEL, edgecolor="#334155", labelcolor=FG, **kw)


def main():
    setup_style()
    out = out_dir("eda")
    t = load_many("orders", "customers", "order_items", "products", "sales", "shipments", "payments", "web_traffic")
    orders, oi, sales = t["orders"], t["order_items"].copy(), t["sales"].copy()
    oi["gross"] = oi["quantity"] * oi["unit_price"]
    oi["net"] = oi["gross"] - oi["discount_amount"]

    # ---- các chỉ số ----
    oc = orders[["order_id", "order_date", "customer_id"]].merge(t["customers"][["customer_id", "signup_date"]], on="customer_id")
    before_signup = oc["order_date"] < oc["signup_date"]

    items = oi.merge(orders[["order_id", "order_date"]], on="order_id").merge(t["products"][["product_id", "cogs"]], on="product_id")
    items["below_cogs"] = items["unit_price"] < items["cogs"]
    below_rate = items["below_cogs"].mean() * 100
    yearly_below = items.groupby(items["order_date"].dt.year)["below_cogs"].mean() * 100

    neg_days = (sales["Revenue"] < sales["COGS"])
    no_traffic = ~sales["Date"].isin(t["web_traffic"]["date"])
    phantom = orders["order_status"].isin(["delivered", "returned", "shipped"]) & ~orders["order_id"].isin(t["shipments"]["order_id"])

    rec = oi.groupby("order_id")["net"].sum().to_frame("items_net").join(t["payments"].set_index("order_id")["payment_value"])
    rec = rec.join(t["shipments"].drop_duplicates("order_id").set_index("order_id")["shipping_fee"]).fillna({"shipping_fee": 0})
    match_items = (np.abs(rec["payment_value"] - rec["items_net"]) <= 1)
    gap_ship = (np.abs(rec["payment_value"] - rec["items_net"] - rec["shipping_fee"]) > 1)

    # ======================= eda_13 =======================
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
    fig.patch.set_facecolor(BG)

    ax = axes[0, 0]
    dark(ax)
    n_b, n_a = before_signup.sum(), (~before_signup).sum()
    _, _, autot = ax.pie([n_b, n_a],
                         labels=[f"Đặt trước ngày tạo tài khoản\n({n_b:,} đơn - {n_b / len(oc) * 100:.2f}%)",
                                 f"Đặt sau khi tạo tài khoản\n({n_a:,} đơn - {n_a / len(oc) * 100:.2f}%)"],
                         colors=["#ef4444", "#10b981"], autopct="%1.1f%%", startangle=140, explode=(0.08, 0),
                         textprops=dict(color=FG, fontsize=11, fontweight="bold"))
    for a in autot:
        a.set_fontsize(13)
    ax.set_title("Nghịch lý thời gian: Đặt hàng trước vs Sau ngày tạo tài khoản?", color=FG, fontsize=12, fontweight="bold", pad=12)

    ax = axes[0, 1]
    dark(ax)
    colors = ["#ef4444" if p > 20 else "#f59e0b" if p > 10 else "#3b82f6" for p in yearly_below.values]
    bars = ax.bar(yearly_below.index.astype(str), yearly_below.values, color=colors, edgecolor="white", alpha=0.9, width=0.6)
    ax.axhline(below_rate, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Trung bình toàn bộ: {below_rate:.2f}%")
    ax.bar_label(bars, fmt="%.1f%%", color=FG, fontsize=8, fontweight="bold", padding=2)
    ax.set_title("Bán dưới giá vốn: Năm chẵn vs Năm lẻ biến động ra sao?", color=FG, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Tỷ lệ dòng hàng có unit_price < COGS (%)", color=MUTED, fontsize=10)
    legend(ax, fontsize=9)

    ax = axes[1, 0]
    dark(ax)
    issues = [
        ("Order trước Signup\n(Vi phạm nhân quả)", before_signup.mean() * 100, f"{n_b / 1e3:.0f}k đơn"),
        ("Hàng bán < COGS\n(Bán dưới giá vốn)", below_rate, f"{items['below_cogs'].sum() / 1e3:.0f}k dòng"),
        (f"Ngày lỗ gộp\n({neg_days.sum()} ngày COGS > Revenue)", neg_days.mean() * 100, f"{neg_days.sum()} ngày"),
        (f"Thiếu dữ liệu Traffic\n({no_traffic.sum()} ngày, 2012)", no_traffic.mean() * 100, f"{no_traffic.sum()} ngày"),
        ('Đơn hàng "ma"\n(Đã giao nhưng không có shipment)', phantom.mean() * 100, f"{phantom.sum()} đơn"),
    ]
    y = np.arange(len(issues))
    bars = ax.barh(y, [i[1] for i in issues], color=["#ef4444", "#f59e0b", "#ec4899", "#8b5cf6", "#06b6d4"],
                   edgecolor="white", alpha=0.85, height=0.55)
    ax.bar_label(bars, labels=[f"{i[1]:.2f}% ({i[2]})" for i in issues], color=FG, fontsize=8, fontweight="bold", padding=4)
    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in issues], color=FG, fontsize=9, fontweight="bold")
    ax.set_xlim(0, max(i[1] for i in issues) * 1.25)
    ax.set_xlabel("Tỷ lệ dữ liệu bị ảnh hưởng (%)", color=MUTED, fontsize=10)
    ax.set_title("Mức độ nghiêm trọng: Lỗi dữ liệu nào chiếm tỷ trọng lớn nhất?", color=FG, fontsize=12, fontweight="bold", pad=12)

    ax = axes[1, 1]
    dark(ax)
    for col, color, lab, ls in [("Revenue", "#3b82f6", "Doanh thu gộp (trước chiết khấu)", "-"),
                                ("COGS", "#ef4444", "Giá vốn hàng bán (COGS)", "-")]:
        ax.plot(sales["Date"], sales[col].rolling(30).mean() / 1e6, label=lab, color=color, linewidth=2, linestyle=ls)
    ax.plot(sales["Date"], (sales["Revenue"] - sales["COGS"]).rolling(30).mean() / 1e6,
            label="Lợi nhuận gộp (Revenue - COGS)", color="#10b981", linewidth=1.5, linestyle="--")
    ax.axhline(0, color="white", linestyle=":", alpha=0.6)
    ax.set_title("Doanh thu gộp (sales.csv) vs Giá vốn: lợi nhuận gộp có lúc âm?", color=FG, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Triệu VNĐ / ngày (MA 30 ngày)", color=MUTED, fontsize=10)
    legend(ax, fontsize=8, loc="upper right")

    plt.suptitle("KIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU: BỘ DỮ LIỆU 'BẨN' VÀ SAI LỆCH ĐẾN MỨC NÀO?\nKỳ vọng vs Thực tế (Datathon 2026)",
                 fontsize=14, fontweight="bold", color=FG, y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    save_fig(fig, out / "eda_13_data_dirtiness_audit.png", facecolor=BG, edgecolor="none", bbox_inches=None)

    # ======================= eda_14 =======================
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), dpi=300)
    fig.patch.set_facecolor(BG)

    ax = axes[0]
    dark(ax)
    vals = [match_items.mean() * 100, gap_ship.mean() * 100]
    bars = ax.bar(["Khớp\n(chỉ tính tiền hàng net)", "Bị lệch khi cộng phí ship"], vals,
                  color=["#10b981", "#ef4444"], width=0.45, edgecolor="white", alpha=0.9)
    ax.bar_label(bars, fmt="%.2f%%", color=FG, fontsize=11, fontweight="bold", padding=3)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Tỷ lệ đơn hàng (%)", color=MUTED, fontsize=10)
    ax.set_title("Cạm bẫy phí ship: payment_value có gồm phí vận chuyển không?", color=FG, fontsize=12, fontweight="bold", pad=12)
    ax.text(0.5, 0.45, "LƯU Ý CHO ML/BI:\npayments.csv chỉ thu tiền hàng net (sau chiết khấu),\n"
                       f"không gồm shipping_fee. Cộng phí ship vào sẽ lệch {gap_ship.sum():,} đơn.",
            transform=ax.transAxes, color="#fbbf24", fontsize=9, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.6", facecolor=BG, edgecolor="#f59e0b", alpha=0.95))

    ax = axes[1]
    dark(ax)
    daily = oi.merge(orders[["order_id", "order_date"]], on="order_id").groupby("order_date")[["gross", "net"]].sum()
    comp = sales.set_index("Date").join(daily, how="inner")
    disc_pct = (comp["Revenue"] - comp["net"]) / comp["Revenue"] * 100
    max_gross_gap = ((comp["Revenue"] - comp["gross"]).abs() / comp["Revenue"] * 100).max()
    sns.histplot(disc_pct, kde=True, ax=ax, color="#3b82f6", edgecolor="white", bins=40)
    ax.axvline(disc_pct.mean(), color="#ef4444", linestyle="--", linewidth=2, label=f"Trung bình: {disc_pct.mean():.2f}%")
    ax.set_title("sales.Revenue vs doanh thu net từ order_items: chênh lệch = chiết khấu", color=FG, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("(Revenue - SUM(net)) / Revenue (%)", color=MUTED, fontsize=10)
    ax.set_ylabel("Số ngày", color=MUTED, fontsize=10)
    ax.text(0.97, 0.80, f"Revenue = SUM(quantity × unit_price)\n(lệch lớn nhất {max_gross_gap:.4f}%)\n→ doanh thu GỘP trước chiết khấu",
            transform=ax.transAxes, color="#fbbf24", fontsize=9, ha="right",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=BG, edgecolor="#f59e0b"))
    legend(ax, fontsize=9, loc="upper left")

    plt.suptitle("CẠM BẪY ĐỐI SOÁT & ĐỊNH NGHĨA DOANH THU\nCác sai lệch ngầm giữa các bảng quan hệ",
                 fontsize=14, fontweight="bold", color=FG, y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    save_fig(fig, out / "eda_14_reconciliation_pitfalls.png", facecolor=BG, edgecolor="none", bbox_inches=None)


if __name__ == "__main__":
    main()
