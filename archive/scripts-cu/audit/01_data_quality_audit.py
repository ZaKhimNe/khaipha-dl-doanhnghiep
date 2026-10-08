"""Kiểm toán chất lượng dữ liệu ("độ bẩn") trên các bảng Datathon 2026.

Nguồn: archive/engine-goc/audit_data_dirtiness.py. Thay đổi so với bản gốc:
  - Check 9: sales.Revenue khớp tuyệt đối SUM(quantity*unit_price) (gộp, trước chiết khấu,
    gồm cả đơn cancelled). Độ lệch ~5% so với doanh thu net chỉ là chiết khấu -> đây là
    ĐỊNH NGHĨA cột, không phải lỗi CRITICAL như bản gốc kết luận.

Đầu ra: outputs/data/data_dirtiness_audit.csv
Chạy:   python scripts/audit/01_data_quality_audit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ds317 import load_many, out_dir  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def main():
    t = load_many("orders", "order_items", "customers", "products", "payments", "shipments",
                  "returns", "reviews", "geography", "inventory", "promotions", "sales", "web_traffic")
    orders, oi, sales = t["orders"], t["order_items"].copy(), t["sales"].copy()
    findings = []

    def add(table, column, issue, count, base, severity, desc):
        pct = count / base * 100 if base else 0.0
        findings.append({"table": table, "column": column, "issue_type": issue, "count": int(count),
                         "pct": float(pct), "severity": severity, "description": desc})
        print(f"  -> {issue}: {count:,} ({pct:.2f}%) [{severity}]")

    print("=" * 70 + "\nKIỂM TOÁN CHẤT LƯỢNG DỮ LIỆU\n" + "=" * 70)

    print("\n[1] Giá trị thiếu (NULL)")
    for name, df in t.items():
        for col, n in df.isnull().sum()[lambda s: s > 0].items():
            pct = n / len(df) * 100
            add(name, col, "Missing Values (NULL)", n, len(df), "HIGH" if pct > 50 else "MEDIUM",
                f"{n:,} dòng thiếu ({pct:.2f}%)")

    print("\n[2] Đơn đã giao/trả/đang giao nhưng không có bản ghi shipments")
    shipped = orders["order_id"].isin(t["shipments"]["order_id"])
    phantom = orders["order_status"].isin(["delivered", "returned", "shipped"]) & ~shipped
    add("orders vs shipments", "order_status / order_id", "Phantom Fulfillment (Đơn ma)", phantom.sum(), len(orders), "HIGH",
        f"{phantom.sum():,} đơn delivered/returned/shipped không có trong shipments.csv "
        f"(các đơn cancelled/paid/created không có shipment là bình thường)")

    print("\n[3] Ngày có COGS > Revenue")
    profit = sales["Revenue"] - sales["COGS"]
    neg = profit < 0
    worst = (profit / sales["Revenue"] * 100).min()
    add("sales", "Revenue vs COGS", "Negative Gross Profit (Bán dưới giá vốn)", neg.sum(), len(sales), "CRITICAL",
        f"{neg.sum()} ngày có COGS vượt Revenue, biên thấp nhất {worst:.2f}%")

    print("\n[4] unit_price lệch giá niêm yết products.price")
    m = oi.merge(t["products"][["product_id", "price"]], on="product_id", how="left")
    mism = (np.abs(m["unit_price"] - m["price"]) > 0.01).sum()
    add("order_items vs products", "unit_price vs price", "Price Desynchronization (Sai lệch niêm yết)", mism, len(oi),
        "HIGH" if mism / len(oi) > 0.05 else "MEDIUM", f"{mism:,} dòng có unit_price khác giá niêm yết")

    print("\n[5] Chiết khấu vượt giá trị dòng hàng")
    oi["gross"] = oi["quantity"] * oi["unit_price"]
    oi["net"] = oi["gross"] - oi["discount_amount"]
    exc = (oi["discount_amount"] > oi["gross"]).sum()
    add("order_items", "discount_amount", "Excessive Discounting (Chiết khấu lố)", exc, len(oi),
        "HIGH" if exc else "LOW", f"{exc:,} dòng chiết khấu > 100% giá trị dòng hàng")

    print("\n[6] Đối soát payments vs tiền hàng (+ phí ship)")
    rec = oi.groupby("order_id")["net"].sum().to_frame("items_net")
    rec = rec.join(t["payments"].groupby("order_id")["payment_value"].sum())
    rec = rec.join(t["shipments"].drop_duplicates("order_id").set_index("order_id")["shipping_fee"]).fillna({"shipping_fee": 0})
    gap_ship = (np.abs(rec["payment_value"] - rec["items_net"] - rec["shipping_fee"]) > 1).sum()
    gap_items = (np.abs(rec["payment_value"] - rec["items_net"]) > 1).sum()
    print(f"  payment != items_net: {gap_items:,} đơn | payment != items_net + ship: {gap_ship:,} đơn")
    add("payments vs order_items", "payment_value vs items_net + shipping_fee", "Payment Reconciliation Gap (Lệch đối soát)",
        gap_ship, len(rec), "HIGH" if gap_ship > 1000 else "MEDIUM",
        f"payment_value khớp tiền hàng net ở {len(rec) - gap_items:,}/{len(rec):,} đơn; "
        f"{gap_ship:,} đơn lệch nếu cộng phí ship -> payments KHÔNG gồm phí ship")

    print("\n[7] Trả hàng phi lý")
    ri = t["returns"].merge(oi[["order_id", "product_id", "quantity"]], on=["order_id", "product_id"], how="left")
    over = (ri["return_quantity"] > ri["quantity"]).sum()
    unmatched = ri["quantity"].isnull().sum()
    add("returns vs order_items", "return_quantity vs quantity", "Impossible Returns (Trả hàng phi lý)", over + unmatched,
        len(t["returns"]), "HIGH" if over + unmatched else "LOW",
        f"{over:,} dòng trả nhiều hơn đã mua; {unmatched:,} sản phẩm trả không thuộc đơn")

    print("\n[8] Chỉ số tồn kho ngoài miền hợp lệ")
    inv = t["inventory"]
    neg_stock = (inv["stock_on_hand"] < 0).sum()
    bad_days = (inv["stockout_days"] > 31).sum()
    bad_fill = (~inv["fill_rate"].between(0, 1)).sum()
    bad_st = (~inv["sell_through_rate"].between(0, 1)).sum()
    add("inventory", "stock_on_hand / fill_rate / stockout_days / sell_through_rate", "Inventory Metric Violations",
        neg_stock + bad_days + bad_fill + bad_st, len(inv), "MEDIUM",
        f"tồn âm {neg_stock}, stockout_days > 31: {bad_days}, fill_rate ngoài [0,1]: {bad_fill}, sell_through ngoài [0,1]: {bad_st}")

    print("\n[9] Định nghĩa sales.Revenue / COGS so với order_items")
    lines = oi.merge(orders[["order_id", "order_date"]], on="order_id").merge(t["products"][["product_id", "cogs"]], on="product_id")
    lines["line_cogs"] = lines["quantity"] * lines["cogs"]
    daily = lines.groupby("order_date")[["gross", "net", "line_cogs"]].sum()
    comp = sales.set_index("Date").join(daily, how="inner")
    d_gross = ((comp["Revenue"] - comp["gross"]).abs() / comp["Revenue"] * 100)
    d_net = ((comp["Revenue"] - comp["net"]) / comp["Revenue"] * 100)
    d_cogs = ((comp["COGS"] - comp["line_cogs"]).abs() / comp["COGS"] * 100)
    print(f"  |Revenue - SUM(gross)| lớn nhất: {d_gross.max():.4f}% | Revenue - SUM(net) trung bình: {d_net.mean():.2f}% "
          f"| |COGS - SUM(qty*cogs)| lớn nhất: {d_cogs.max():.4f}%")
    add("sales vs order_items", "Revenue vs SUM(quantity*unit_price)", "Định nghĩa: Revenue = doanh thu gộp trước chiết khấu",
        int((d_gross > 0.01).sum()), len(comp), "INFO",
        f"Revenue khớp SUM(quantity*unit_price) (lệch lớn nhất {d_gross.max():.4f}%), gồm cả đơn cancelled; "
        f"cao hơn doanh thu net trung bình {d_net.mean():.2f}% do chiết khấu. COGS = SUM(quantity*products.cogs).")

    out = out_dir("data") / "data_dirtiness_audit.csv"
    pd.DataFrame(findings).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n=> Đã lưu: {out}")


if __name__ == "__main__":
    main()
