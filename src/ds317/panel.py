"""Bảng tổng hợp theo ngày (master daily panel) từ các bảng giao dịch."""
import numpy as np
import pandas as pd

from .data import load

# Ngày không có bản ghi nghĩa là 0 thật (không có đơn / trả hàng / review / giao hàng).
COUNT_COLS = [
    "order_count", "unique_customers", "total_units_ordered", "total_discounts_applied",
    "return_count", "total_refund_amount", "shipments_dispatched", "review_count",
]
# web_traffic bắt đầu 2013-01-01 -> 181 ngày cuối 2012 không có dữ liệu (không phải 0).
TRAFFIC_COLS = ["total_sessions", "total_unique_visitors", "total_page_views", "avg_bounce_rate", "avg_session_duration"]
# Trung bình của ngày không có bản ghi là không xác định.
MEAN_COLS = ["avg_unit_price", "avg_shipping_fee", "avg_delivery_lead_days", "avg_rating"]


def build_daily_panel(t: dict | None = None, impute: str | None = None) -> pd.DataFrame:
    """Nối sales.csv với các chỉ số vận hành gộp theo ngày.

    t: dict bảng đã load sẵn (để không đọc lại file); thiếu bảng nào thì tự load.
    impute:
      None (mặc định) -> cột đếm/tổng (COUNT_COLS) điền 0 cho ngày không có bản ghi;
                         cột traffic (TRAFFIC_COLS) và cột trung bình (MEAN_COLS) giữ NaN.
      "median"        -> cách cũ: điền NaN mọi cột số bằng median toàn cột. KHÔNG nên dùng:
                         tạo số giả cho 181 ngày thiếu traffic và các ngày không có trả hàng/review.
    """
    t = dict(t or {})
    for name in ["sales", "web_traffic", "orders", "order_items", "returns", "shipments", "reviews"]:
        if name not in t:
            t[name] = load(name)

    sales = t["sales"].copy()
    sales["Gross_Profit"] = sales["Revenue"] - sales["COGS"]
    sales["Gross_Margin_Pct"] = sales["Gross_Profit"] / sales["Revenue"] * 100.0

    traffic_daily = t["web_traffic"].groupby("date").agg(
        total_sessions=("sessions", "sum"),
        total_unique_visitors=("unique_visitors", "sum"),
        total_page_views=("page_views", "sum"),
        avg_bounce_rate=("bounce_rate", "mean"),
        avg_session_duration=("avg_session_duration_sec", "mean"),
    ).rename_axis("Date")

    orders = t["orders"]
    orders_daily = orders.groupby("order_date").agg(
        order_count=("order_id", "count"),
        unique_customers=("customer_id", "nunique"),
    ).rename_axis("Date")

    oi = t["order_items"].merge(orders[["order_id", "order_date"]], on="order_id", how="left")
    oi_daily = oi.groupby("order_date").agg(
        total_units_ordered=("quantity", "sum"),
        total_discounts_applied=("discount_amount", "sum"),
        avg_unit_price=("unit_price", "mean"),
    ).rename_axis("Date")

    returns_daily = t["returns"].groupby("return_date").agg(
        return_count=("return_id", "count"),
        total_refund_amount=("refund_amount", "sum"),
    ).rename_axis("Date")

    ship = t["shipments"].copy()
    ship["delivery_lead_days"] = (ship["delivery_date"] - ship["ship_date"]).dt.days
    shipments_daily = ship.groupby("ship_date").agg(
        shipments_dispatched=("order_id", "count"),
        avg_shipping_fee=("shipping_fee", "mean"),
        avg_delivery_lead_days=("delivery_lead_days", "mean"),
    ).rename_axis("Date")

    reviews_daily = t["reviews"].groupby("review_date").agg(
        avg_rating=("rating", "mean"),
        review_count=("review_id", "count"),
    ).rename_axis("Date")

    master = sales.set_index("Date")
    for part in [traffic_daily, orders_daily, oi_daily, returns_daily, shipments_daily, reviews_daily]:
        master = master.join(part, how="left")
    master = master.reset_index()

    d = master["Date"].dt
    master["Year"], master["Month"], master["Day"] = d.year, d.month, d.day
    master["DayOfWeek"] = d.dayofweek
    master["IsWeekend"] = master["DayOfWeek"].isin([5, 6]).astype(int)
    master["DayOfYear"], master["Quarter"] = d.dayofyear, d.quarter

    if impute is None:
        master[COUNT_COLS] = master[COUNT_COLS].fillna(0)
    elif impute == "median":
        num_cols = master.select_dtypes(include=[np.number]).columns
        master[num_cols] = master[num_cols].fillna(master[num_cols].median())
    else:
        raise ValueError("impute phải là None hoặc 'median'")
    return master
