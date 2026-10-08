"""Kiểm tra chất lượng dữ liệu (notebook 06).

audit_findings(t)     9 kiểm tra "độ bẩn" (chuyển từ scripts/audit/01_data_quality_audit.py)
dirtiness_metrics(t)  các chỉ số dùng cho chart độ bẩn / đối soát
dq_rules(t)           quy tắc theo 6 khía cạnh, mỗi dòng 1 quy tắc: số kiểm tra, số vi phạm, điểm
dq_scores(rules)      bảng điểm bảng x khía cạnh = 1 - tổng vi phạm / tổng kiểm tra

t: dict bảng đã load bằng ds317.load_many(...) (cột ngày đã parse).
"""
import numpy as np
import pandas as pd

from .data import order_lines

DIMENSIONS = ["Đầy đủ", "Hợp lệ", "Chính xác", "Nhất quán", "Duy nhất", "Kịp thời"]
ORDER_STATUSES = {"created", "paid", "shipped", "delivered", "returned", "cancelled"}
DQ_TABLES = ["sales", "web_traffic", "orders", "order_items", "products", "customers", "geography",
             "payments", "shipments", "returns", "reviews", "promotions", "inventory"]


def _lines(t):
    return order_lines(t["order_items"], t["orders"], t["products"])


def _payment_reconciliation(t, lines=None):
    lines = _lines(t) if lines is None else lines
    rec = lines.groupby("order_id")["net"].sum().to_frame("items_net")
    rec = rec.join(t["payments"].groupby("order_id")["payment_value"].sum())
    fee = t["shipments"].drop_duplicates("order_id").set_index("order_id")["shipping_fee"]
    return rec.join(fee).fillna({"shipping_fee": 0})


def _sales_vs_lines(t, lines=None):
    lines = _lines(t) if lines is None else lines
    daily = lines.groupby("order_date")[["gross", "net", "cogs_line"]].sum()
    return t["sales"].set_index("Date").join(daily, how="inner")


def dirtiness_metrics(t: dict) -> dict:
    """Các chỉ số độ bẩn chính (giá trị tính từ data)."""
    lines = _lines(t)
    orders = t["orders"]
    oc = orders[["order_id", "order_date", "customer_id"]].merge(
        t["customers"][["customer_id", "signup_date"]], on="customer_id")
    below = lines["unit_price"] < lines["cogs"]
    sales = t["sales"]
    phantom = orders["order_status"].isin(["delivered", "returned", "shipped"]) & ~orders["order_id"].isin(t["shipments"]["order_id"])
    rec = _payment_reconciliation(t, lines)
    comp = _sales_vs_lines(t, lines)
    return {
        "before_signup": oc["order_date"] < oc["signup_date"],
        "below_cogs": below,
        "below_cogs_by_year": below.groupby(lines["order_date"].dt.year).mean() * 100,
        "neg_profit_days": sales["Revenue"] < sales["COGS"],
        "days_without_traffic": ~sales["Date"].isin(t["web_traffic"]["date"]),
        "phantom_orders": phantom,
        "pay_match_items": (rec["payment_value"] - rec["items_net"]).abs() <= 1,
        "pay_gap_with_ship": (rec["payment_value"] - rec["items_net"] - rec["shipping_fee"]).abs() > 1,
        "discount_pct_of_revenue": (comp["Revenue"] - comp["net"]) / comp["Revenue"] * 100,
        "max_gap_gross_pct": float(((comp["Revenue"] - comp["gross"]).abs() / comp["Revenue"] * 100).max()),
        "max_gap_cogs_pct": float(((comp["COGS"] - comp["cogs_line"]).abs() / comp["COGS"] * 100).max()),
    }


def audit_findings(t: dict) -> pd.DataFrame:
    """9 kiểm tra độ bẩn; mỗi dòng: bảng, cột, loại lỗi, số dòng, %, mức độ, mô tả."""
    rows = []

    def add(table, column, issue, count, base, severity, desc):
        rows.append({"bang": table, "cot": column, "loai_loi": issue, "so_dong": int(count),
                     "pct": round(count / base * 100, 3) if base else 0.0, "muc_do": severity, "mo_ta": desc})

    lines = _lines(t)
    orders, sales = t["orders"], t["sales"]
    m = dirtiness_metrics(t)

    for name in DQ_TABLES:
        df = t[name]
        for col, n in df.isnull().sum()[lambda s: s > 0].items():
            pct = n / len(df) * 100
            add(name, col, "Giá trị trống (NULL)", n, len(df), "HIGH" if pct > 50 else "MEDIUM", f"{n:,} dòng trống")

    ph = m["phantom_orders"]
    add("orders vs shipments", "order_status / order_id", "Đơn đã giao nhưng không có shipment", ph.sum(), len(orders), "HIGH",
        "Đơn delivered/returned/shipped không có trong shipments.csv (đơn cancelled/paid/created không có shipment là bình thường)")

    neg = m["neg_profit_days"]
    worst = ((sales["Revenue"] - sales["COGS"]) / sales["Revenue"] * 100).min()
    add("sales", "Revenue vs COGS", "Ngày lỗ gộp (COGS > Revenue)", neg.sum(), len(sales), "CRITICAL",
        f"Biên gộp ngày thấp nhất {worst:.2f}%")

    mism = ((lines["unit_price"] - lines["price"]).abs() > 0.01).sum()
    add("order_items vs products", "unit_price vs price", "Giá bán khác giá niêm yết", mism, len(lines),
        "HIGH" if mism / len(lines) > 0.05 else "MEDIUM", "unit_price khác products.price quá 0.01")

    exc = (lines["discount_amount"] > lines["gross"]).sum()
    add("order_items", "discount_amount", "Chiết khấu > giá trị dòng hàng", exc, len(lines), "HIGH" if exc else "LOW",
        "discount_amount > quantity*unit_price")

    gap = m["pay_gap_with_ship"]
    add("payments vs order_items", "payment_value", "Lệch thanh toán nếu cộng phí ship", gap.sum(), len(gap),
        "INFO", f"payment_value khớp tiền hàng net ở {m['pay_match_items'].sum():,}/{len(gap):,} đơn -> payments không gồm phí ship")

    # cộng số lượng đã mua theo (order_id, product_id): order_items có 16 cặp bị tách 2 dòng
    bought = t["order_items"].groupby(["order_id", "product_id"])["quantity"].sum()
    ri = t["returns"].join(bought, on=["order_id", "product_id"])
    over, unmatched = (ri["return_quantity"] > ri["quantity"]).sum(), ri["quantity"].isna().sum()
    add("returns vs order_items", "return_quantity", "Trả hàng phi lý", over + unmatched, len(ri), "HIGH" if over + unmatched else "LOW",
        f"{over} dòng trả nhiều hơn đã mua; {unmatched} sản phẩm trả không thuộc đơn")

    inv = t["inventory"]
    bad = ((inv["stock_on_hand"] < 0) | (inv["stockout_days"] > 31) | ~inv["fill_rate"].between(0, 1)
           | ~inv["sell_through_rate"].between(0, 1)).sum()
    add("inventory", "stock_on_hand / stockout_days / fill_rate / sell_through_rate", "Chỉ số tồn kho ngoài miền hợp lệ",
        bad, len(inv), "MEDIUM", "tồn âm, stockout_days > 31, tỷ lệ ngoài [0, 1]")

    add("sales vs order_items", "Revenue", "Định nghĩa: Revenue = doanh thu gộp trước chiết khấu", 0, len(sales), "INFO",
        f"Revenue khớp SUM(quantity*unit_price) (lệch lớn nhất {m['max_gap_gross_pct']:.4f}%), gồm cả đơn cancelled; "
        f"cao hơn doanh thu net trung bình {m['discount_pct_of_revenue'].mean():.2f}% do chiết khấu")
    return pd.DataFrame(rows)


def dq_rules(t: dict) -> pd.DataFrame:
    """Quy tắc chất lượng theo 6 khía cạnh; điểm = 1 - số vi phạm / số kiểm tra."""
    rules = []

    def rule(table, column, dim, desc, violations, checked):
        v, n = int(np.sum(violations)), int(checked)
        rules.append({"bang": table, "cot": column, "khia_canh": dim, "quy_tac": desc,
                      "so_kiem_tra": n, "so_vi_pham": v, "diem": round(1 - v / n, 6) if n else np.nan})

    lines = _lines(t)
    oi, orders, sales = t["order_items"], t["orders"], t["sales"]
    od = orders.set_index("order_id")["order_date"]

    # Đầy đủ: % trống từng cột
    for name in DQ_TABLES:
        df = t[name]
        for col in df.columns:
            rule(name, col, "Đầy đủ", "giá trị không trống", df[col].isna(), len(df))

    # Hợp lệ: miền giá trị
    valid = [
        ("order_items", "quantity", "quantity > 0", oi["quantity"] <= 0),
        ("order_items", "unit_price", "unit_price > 0", oi["unit_price"] <= 0),
        ("order_items", "discount_amount", "0 <= discount_amount <= quantity*unit_price",
         (oi["discount_amount"] < 0) | (oi["discount_amount"] > oi["quantity"] * oi["unit_price"])),
        ("orders", "order_status", f"order_status thuộc {sorted(ORDER_STATUSES)}", ~orders["order_status"].isin(ORDER_STATUSES)),
        ("reviews", "rating", "rating thuộc [1, 5]", ~t["reviews"]["rating"].between(1, 5)),
        ("products", "price", "price > 0", t["products"]["price"] <= 0),
        ("products", "cogs", "cogs > 0", t["products"]["cogs"] <= 0),
        ("payments", "payment_value", "payment_value >= 0", t["payments"]["payment_value"] < 0),
        ("payments", "installments", "installments >= 1", t["payments"]["installments"] < 1),
        ("shipments", "shipping_fee", "shipping_fee >= 0", t["shipments"]["shipping_fee"] < 0),
        ("returns", "return_quantity", "return_quantity > 0", t["returns"]["return_quantity"] <= 0),
        ("returns", "refund_amount", "refund_amount >= 0", t["returns"]["refund_amount"] < 0),
        ("inventory", "stock_on_hand", "stock_on_hand >= 0", t["inventory"]["stock_on_hand"] < 0),
        ("inventory", "stockout_days", "stockout_days thuộc [0, 31]", ~t["inventory"]["stockout_days"].between(0, 31)),
        ("inventory", "fill_rate", "fill_rate thuộc [0, 1]", ~t["inventory"]["fill_rate"].between(0, 1)),
        ("inventory", "sell_through_rate", "sell_through_rate thuộc [0, 1]", ~t["inventory"]["sell_through_rate"].between(0, 1)),
        ("web_traffic", "sessions", "sessions >= 0", t["web_traffic"]["sessions"] < 0),
        ("web_traffic", "bounce_rate", "bounce_rate thuộc [0, 1]", ~t["web_traffic"]["bounce_rate"].between(0, 1)),
        ("sales", "Revenue", "Revenue > 0", sales["Revenue"] <= 0),
        ("sales", "COGS", "COGS > 0", sales["COGS"] <= 0),
        ("promotions", "discount_value", "discount_value > 0", t["promotions"]["discount_value"] <= 0),
        ("promotions", "end_date", "end_date >= start_date", t["promotions"]["end_date"] < t["promotions"]["start_date"]),
    ]
    for table, col, desc, viol in valid:
        rule(table, col, "Hợp lệ", desc, viol, len(viol))

    # Chính xác: so với nguồn đối chiếu
    rule("order_items", "unit_price", "Chính xác", "unit_price = products.price (±0.01)",
         (lines["unit_price"] - lines["price"]).abs() > 0.01, len(lines))
    comp = _sales_vs_lines(t, lines)
    rule("sales", "Revenue", "Chính xác", "Revenue = SUM(quantity*unit_price) theo ngày (±0.01%)",
         (comp["Revenue"] - comp["gross"]).abs() / comp["Revenue"] > 1e-4, len(comp))
    rule("sales", "COGS", "Chính xác", "COGS = SUM(quantity*products.cogs) theo ngày (±0.01%)",
         (comp["COGS"] - comp["cogs_line"]).abs() / comp["COGS"] > 1e-4, len(comp))
    rec = _payment_reconciliation(t, lines)
    rule("payments", "payment_value", "Chính xác", "payment_value = tiền hàng net của đơn (±1)",
         (rec["payment_value"] - rec["items_net"]).abs() > 1, len(rec))

    # Nhất quán: khoá nối + thứ tự thời gian
    fks = [
        ("order_items", "order_id", "orders", "order_id"), ("order_items", "product_id", "products", "product_id"),
        ("orders", "customer_id", "customers", "customer_id"), ("customers", "zip", "geography", "zip"),
        ("payments", "order_id", "orders", "order_id"), ("shipments", "order_id", "orders", "order_id"),
        ("returns", "order_id", "orders", "order_id"), ("reviews", "order_id", "orders", "order_id"),
        ("inventory", "product_id", "products", "product_id"),
    ]
    for child, ck, parent, pk in fks:
        s = t[child][ck]
        rule(child, ck, "Nhất quán", f"{ck} có trong {parent}.{pk}", ~s.isin(t[parent][pk]), len(s))
    ri = t["returns"].merge(oi[["order_id", "product_id"]].drop_duplicates(), on=["order_id", "product_id"], how="left", indicator=True)
    rule("returns", "order_id, product_id", "Nhất quán", "(order_id, product_id) có trong order_items", ri["_merge"] != "both", len(ri))
    bought = oi.groupby(["order_id", "product_id"])["quantity"].sum()
    rq = t["returns"].join(bought, on=["order_id", "product_id"])
    rule("returns", "return_quantity", "Nhất quán", "return_quantity <= số lượng đã mua trong đơn", rq["return_quantity"] > rq["quantity"], len(rq))

    sh = t["shipments"]
    sh_od = sh["order_id"].map(od)
    rule("shipments", "ship_date", "Nhất quán", "ship_date >= orders.order_date", sh["ship_date"] < sh_od, len(sh))
    rule("shipments", "delivery_date", "Nhất quán", "delivery_date >= ship_date", sh["delivery_date"] < sh["ship_date"], len(sh))
    for name, col in [("returns", "return_date"), ("reviews", "review_date")]:
        df = t[name]
        rule(name, col, "Nhất quán", f"{col} >= orders.order_date", df[col] < df["order_id"].map(od), len(df))
    sign = orders["customer_id"].map(t["customers"].set_index("customer_id")["signup_date"])
    rule("orders", "order_date", "Nhất quán", "order_date >= customers.signup_date", orders["order_date"] < sign, len(orders))
    need_ship = orders["order_status"].isin(["shipped", "delivered", "returned"])
    rule("orders", "order_status", "Nhất quán", "đơn shipped/delivered/returned có bản ghi shipments",
         need_ship & ~orders["order_id"].isin(sh["order_id"]), need_ship.sum())

    # Duy nhất: khoá chính
    pks = [("orders", ["order_id"]), ("products", ["product_id"]), ("customers", ["customer_id"]), ("sales", ["Date"]),
           ("geography", ["zip"]), ("payments", ["order_id"]), ("shipments", ["order_id"]), ("returns", ["return_id"]),
           ("reviews", ["review_id"]), ("promotions", ["promo_id"]), ("web_traffic", ["date"]),
           ("inventory", ["snapshot_date", "product_id"]), ("order_items", ["order_id", "product_id"])]
    for name, key in pks:
        rule(name, ", ".join(key), "Duy nhất", f"khoá {', '.join(key)} không trùng", t[name].duplicated(subset=key), len(t[name]))

    # Kịp thời: ngày nằm trong khoảng sales + độ phủ ngày
    lo, hi = sales["Date"].min(), sales["Date"].max()
    for name, col in [("orders", "order_date"), ("web_traffic", "date"), ("shipments", "delivery_date"),
                      ("returns", "return_date"), ("reviews", "review_date"), ("inventory", "snapshot_date"),
                      ("promotions", "start_date")]:
        s = t[name][col]
        rule(name, col, "Kịp thời", f"{col} nằm trong khoảng sales [{lo.date()}, {hi.date()}]", ~s.between(lo, hi), len(s))
    rule("web_traffic", "date", "Kịp thời", "mọi ngày của sales có dữ liệu traffic", ~sales["Date"].isin(t["web_traffic"]["date"]), len(sales))
    all_days = pd.date_range(lo, hi)
    rule("sales", "Date", "Kịp thời", "chuỗi ngày liên tục (không thiếu ngày)", ~all_days.isin(sales["Date"]), len(all_days))
    return pd.DataFrame(rules)


def dq_scores(rules: pd.DataFrame) -> pd.DataFrame:
    """Bảng 13 bảng x 6 khía cạnh; điểm = 1 - tổng vi phạm / tổng kiểm tra (NaN: không có quy tắc)."""
    g = rules.groupby(["bang", "khia_canh"])[["so_vi_pham", "so_kiem_tra"]].sum()
    score = (1 - g["so_vi_pham"] / g["so_kiem_tra"]).unstack()
    return score.reindex(index=DQ_TABLES, columns=DIMENSIONS)
