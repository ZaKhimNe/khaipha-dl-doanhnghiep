"""Đọc 14 bảng Datathon 2026, các phép nối dùng lại nhiều lần và biến mục tiêu.

Quy ước tuần: tuần bắt đầu Thứ Hai, kết thúc Chủ nhật (pandas "W-SUN"); `week_start` là ngày Thứ Hai.

Ba định nghĩa doanh thu (REVENUE_KINDS):
  gross_all            SUM(quantity*unit_price), gồm đơn cancelled  -> khớp tuyệt đối sales.Revenue
  gross_excl_cancelled SUM(quantity*unit_price), bỏ đơn cancelled
  net_excl_cancelled   SUM(quantity*unit_price - discount_amount), bỏ đơn cancelled
"""
import pandas as pd

from .paths import DATA_DIR

# Cột ngày của từng bảng, để parse_dates tự động khi load.
DATE_COLS = {
    "sales": ["Date"],
    "web_traffic": ["date"],
    "orders": ["order_date"],
    "customers": ["signup_date"],
    "promotions": ["start_date", "end_date"],
    "returns": ["return_date"],
    "reviews": ["review_date"],
    "shipments": ["ship_date", "delivery_date"],
    "inventory": ["snapshot_date"],
    "sample_submission": ["Date"],
}

TABLES = [
    "sales", "web_traffic", "orders", "order_items", "products", "customers", "geography",
    "payments", "shipments", "returns", "reviews", "promotions", "inventory", "sample_submission",
]

# (cột giá trị, có loại đơn cancelled không)
REVENUE_KINDS = {
    "gross_all": ("gross", False),
    "gross_excl_cancelled": ("gross", True),
    "net_excl_cancelled": ("net", True),
}

REVENUE_LABELS = {
    "gross_all": "Doanh thu gộp, gồm đơn huỷ, trước chiết khấu (= sales.Revenue)",
    "gross_excl_cancelled": "Doanh thu gộp, bỏ đơn huỷ, trước chiết khấu",
    "net_excl_cancelled": "Doanh thu net, bỏ đơn huỷ, sau chiết khấu",
}


def load(table: str, parse_dates: bool = True, **kwargs) -> pd.DataFrame:
    """Đọc một bảng theo tên (không cần đuôi .csv)."""
    if parse_dates and "usecols" not in kwargs:
        kwargs.setdefault("parse_dates", DATE_COLS.get(table, []))
    if table == "order_items":
        kwargs.setdefault("low_memory", False)
    return pd.read_csv(DATA_DIR / f"{table}.csv", **kwargs)


def load_many(*tables: str) -> dict:
    return {t: load(t) for t in tables}


def order_lines(order_items=None, orders=None, products=None) -> pd.DataFrame:
    """order_items nối orders (ngày, trạng thái) và products (danh mục, giá niêm yết, giá vốn).

    Thêm cột:
      gross        = quantity * unit_price      (cộng theo ngày khớp tuyệt đối sales.Revenue)
      net          = gross - discount_amount
      cogs_line    = quantity * products.cogs   (cộng theo ngày khớp tuyệt đối sales.COGS)
      is_cancelled = order_status == "cancelled"
    """
    oi = load("order_items") if order_items is None else order_items
    od = load("orders") if orders is None else orders
    pr = load("products") if products is None else products
    m = oi.merge(od[["order_id", "order_date", "order_status"]], on="order_id", how="left")
    m = m.merge(pr[["product_id", "category", "segment", "price", "cogs"]], on="product_id", how="left")
    m["gross"] = m["quantity"] * m["unit_price"]
    m["net"] = m["gross"] - m["discount_amount"]
    m["cogs_line"] = m["quantity"] * m["cogs"]
    m["is_cancelled"] = m["order_status"].eq("cancelled")
    return m


def _select(lines: pd.DataFrame, kind: str):
    if kind not in REVENUE_KINDS:
        raise ValueError(f"kind phải thuộc {list(REVENUE_KINDS)}")
    col, drop_cancelled = REVENUE_KINDS[kind]
    return (lines[~lines["is_cancelled"]] if drop_cancelled else lines), col


def revenue_daily(lines: pd.DataFrame, kind: str = "gross_all") -> pd.Series:
    """Doanh thu theo ngày đặt hàng (order_date) theo một trong REVENUE_KINDS."""
    sub, col = _select(lines, kind)
    return sub.groupby("order_date")[col].sum().rename(kind)


def weekly_category(lines: pd.DataFrame, kind: str = "gross_all", week: str = "W-SUN") -> pd.DataFrame:
    """Biến mục tiêu tuần x danh mục.

    Trả cột: week_start (Thứ Hai), category, revenue, cogs, units, n_orders, n_days, is_partial_week.
    Lưới đầy đủ mọi tuần x mọi danh mục, tuần không bán điền 0.
    n_days = số ngày của tuần nằm trong khoảng ngày có dữ liệu; is_partial_week = n_days < 7
    (chỉ xảy ra ở tuần đầu và tuần cuối).
    """
    sub, col = _select(lines, kind)
    sub = sub.assign(week_start=sub["order_date"].dt.to_period(week).dt.start_time)
    agg = sub.groupby(["week_start", "category"]).agg(
        revenue=(col, "sum"), cogs=("cogs_line", "sum"), units=("quantity", "sum"), n_orders=("order_id", "nunique"))

    first, last = lines["order_date"].min(), lines["order_date"].max()
    weeks = pd.period_range(first, last, freq=week).start_time
    cats = sorted(lines["category"].dropna().unique())
    grid = pd.MultiIndex.from_product([weeks, cats], names=["week_start", "category"])
    out = agg.reindex(grid, fill_value=0).reset_index()
    out[["units", "n_orders"]] = out[["units", "n_orders"]].astype(int)

    week_end = out["week_start"] + pd.Timedelta(days=6)
    out["n_days"] = ((week_end.clip(upper=last) - out["week_start"].clip(lower=first)).dt.days + 1).astype(int)
    out["is_partial_week"] = out["n_days"] < 7
    return out
