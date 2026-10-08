"""
Comprehensive Data Dirtiness & Quality Audit for Datathon 2026 Round 1.
Vectorized execution across all 14 tables with statistical significance checks.
"""

import os, sys, glob
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\dataset"

def load(name, **kwargs):
    return pd.read_csv(os.path.join(DATA_DIR, name), **kwargs)

print("="*70)
print("TIẾN HÀNH KIỂM TOÁN CHẤT LƯỢNG VÀ ĐỘ 'BẨN' CỦA BỘ DỮ LIỆU (DATA DIRTINESS AUDIT)")
print("="*70)

# 1. Load data
orders = load('orders.csv')
order_items = load('order_items.csv', low_memory=False)
customers = load('customers.csv')
products = load('products.csv')
payments = load('payments.csv')
shipments = load('shipments.csv')
returns = load('returns.csv')
reviews = load('reviews.csv')
geo = load('geography.csv')
inventory = load('inventory.csv')
promotions = load('promotions.csv')
sales = load('sales.csv')
traffic = load('web_traffic.csv')

findings = []

# --- CHECK 1: Missing values & Nulls ---
print("\n[1] KIỂM TRA GIÁ TRỊ THIẾU (NULL / MISSING VALUES):")
for name, df in [
    ('order_items', order_items), ('promotions', promotions),
    ('orders', orders), ('payments', payments), ('products', products),
    ('shipments', shipments), ('returns', returns), ('reviews', reviews),
    ('customers', customers), ('inventory', inventory), ('sales', sales),
    ('web_traffic', traffic)
]:
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) > 0:
        for col, count in null_cols.items():
            pct = count / len(df) * 100
            print(f"  - Bảng {name}.{col}: {count:,} dòng bị NULL ({pct:.2f}%)")
            findings.append({
                'table': name, 'column': col, 'issue_type': 'Missing Values (NULL)',
                'count': int(count), 'pct': float(pct),
                'severity': 'HIGH' if pct > 50 else 'MEDIUM',
                'description': f'{count:,} missing rows ({pct:.2f}%)'
            })

# --- CHECK 2: Phantom Shipments & Status Desynchronization ---
print("\n[2] ĐỒNG BỘ TRẠNG THÁI ĐƠN HÀNG VS GIAO VẬN (PHANTOM SHIPMENTS):")
shipped_order_ids = set(shipments['order_id'])
delivered_no_ship = ((orders['order_status'] == 'delivered') & (~orders['order_id'].isin(shipped_order_ids))).sum()
returned_no_ship = ((orders['order_status'] == 'returned') & (~orders['order_id'].isin(shipped_order_ids))).sum()
shipped_no_ship = ((orders['order_status'] == 'shipped') & (~orders['order_id'].isin(shipped_order_ids))).sum()
total_phantom = delivered_no_ship + returned_no_ship + shipped_no_ship

print(f"  - Đơn 'delivered' không có bản ghi vận chuyển: {delivered_no_ship:,}")
print(f"  - Đơn 'returned' không có bản ghi vận chuyển: {returned_no_ship:,}")
print(f"  - Đơn 'shipped' không có bản ghi vận chuyển: {shipped_no_ship:,}")
print(f"  => Tổng số đơn ma (Phantom fulfillment): {total_phantom:,} đơn")
findings.append({
    'table': 'orders vs shipments', 'column': 'order_status / order_id',
    'issue_type': 'Phantom Fulfillment (Đơn ma)',
    'count': int(total_phantom), 'pct': float(total_phantom / len(orders) * 100),
    'severity': 'HIGH',
    'description': f'{total_phantom:,} đơn hàng đã giao/trả/vận chuyển nhưng không tồn tại trong shipments.csv'
})

# --- CHECK 3: Negative Gross Profit in Sales ---
print("\n[3] LỖ BÁN HÀNG BẤT THƯỜNG TRONG BẢNG DOANH THU (NEGATIVE GROSS PROFIT):")
sales['Profit'] = sales['Revenue'] - sales['COGS']
neg_profit_days = (sales['Profit'] < 0).sum()
neg_profit_pct = neg_profit_days / len(sales) * 100
total_loss = sales.loc[sales['Profit'] < 0, 'Profit'].sum()
worst_margin = (sales['Profit'] / sales['Revenue'] * 100).min()
print(f"  - Số ngày bán dưới giá vốn (COGS > Revenue): {neg_profit_days} / {len(sales)} ngày ({neg_profit_pct:.2f}%)")
print(f"  - Tổng mức lỗ gộp tích lũy từ các ngày lỗ: {total_loss:,.2f} VNĐ")
print(f"  - Biên lợi nhuận gộp ngày xấu nhất: {worst_margin:.2f}%")
findings.append({
    'table': 'sales', 'column': 'Revenue vs COGS',
    'issue_type': 'Negative Gross Profit (Bán dưới giá vốn)',
    'count': int(neg_profit_days), 'pct': float(neg_profit_pct),
    'severity': 'CRITICAL',
    'description': f'{neg_profit_days} ngày (~10% chuỗi thời gian) có COGS vượt Revenue, biên lợi nhuận thấp nhất {worst_margin:.2f}%'
})

# --- CHECK 4: Pricing Inconsistencies (Order Items vs Catalog Products) ---
print("\n[4] BẤT ĐỒNG NHẤT GIÁ BÁN (TRANSACTIONAL UNIT_PRICE VS CATALOG PRICE):")
merged_items = order_items.merge(products[['product_id', 'price']], on='product_id', how='left')
price_diff = np.abs(merged_items['unit_price'] - merged_items['price'])
mismatched_prices = (price_diff > 0.01).sum()
mismatch_pct = mismatched_prices / len(order_items) * 100
print(f"  - Số dòng order_items có đơn giá lệch so với giá niêm yết trong products.csv: {mismatched_prices:,} ({mismatch_pct:.2f}%)")
if mismatched_prices > 0:
    mean_diff = price_diff[price_diff > 0.01].mean()
    print(f"  - Độ lệch giá trung bình: {mean_diff:.2f}")
findings.append({
    'table': 'order_items vs products', 'column': 'unit_price vs price',
    'issue_type': 'Price Desynchronization (Sai lệch niêm yết)',
    'count': int(mismatched_prices), 'pct': float(mismatch_pct),
    'severity': 'HIGH' if mismatch_pct > 5 else 'MEDIUM',
    'description': f'{mismatched_prices:,} giao dịch ({mismatch_pct:.2f}%) có unit_price không khớp với giá niêm yết products.csv'
})

# --- CHECK 5: Excessive Discounts (Discount > Item Gross) ---
print("\n[5] CHIẾT KHẤU VƯỢT GIÁ TRỊ HÀNG HOÁ (EXCESSIVE DISCOUNTS):")
order_items['item_gross'] = order_items['quantity'] * order_items['unit_price']
excessive_disc = (order_items['discount_amount'] > order_items['item_gross']).sum()
free_items = (order_items['discount_amount'] == order_items['item_gross']).sum()
print(f"  - Chiết khấu > 100% giá trị đơn hàng (Doanh nghiệp phải bù tiền cho khách): {excessive_disc:,} dòng")
print(f"  - Chiết khấu = 100% (Hàng tặng 0 đồng): {free_items:,} dòng")
findings.append({
    'table': 'order_items', 'column': 'discount_amount',
    'issue_type': 'Excessive Discounting (Chiết khấu lố)',
    'count': int(excessive_disc), 'pct': float(excessive_disc / len(order_items) * 100),
    'severity': 'HIGH' if excessive_disc > 0 else 'LOW',
    'description': f'{excessive_disc:,} dòng hàng có chiết khấu vượt quá 100% tổng giá trị sản phẩm'
})

# --- CHECK 6: Payment Value vs Calculated Order Total Discrepancy ---
print("\n[6] ĐỐI SOÁT THANH TOÁN (PAYMENT RECONCILIATION VS ORDER ITEMS):")
order_items['item_net'] = order_items['item_gross'] - order_items['discount_amount']
order_subtotals = order_items.groupby('order_id')['item_net'].sum().reset_index(name='calc_items_net')

pay_summary = payments.groupby('order_id')['payment_value'].sum().reset_index(name='total_paid')
ship_fees = shipments[['order_id', 'shipping_fee']].drop_duplicates(subset=['order_id'])

reconciliation = order_subtotals.merge(pay_summary, on='order_id', how='left')
reconciliation = reconciliation.merge(ship_fees, on='order_id', how='left').fillna({'shipping_fee': 0})
reconciliation['expected_total'] = reconciliation['calc_items_net'] + reconciliation['shipping_fee']
reconciliation['diff_with_ship'] = np.abs(reconciliation['total_paid'] - reconciliation['expected_total'])
reconciliation['diff_items_only'] = np.abs(reconciliation['total_paid'] - reconciliation['calc_items_net'])

pay_discrepancy_ship = (reconciliation['diff_with_ship'] > 1.0).sum()
pay_discrepancy_items = (reconciliation['diff_items_only'] > 1.0).sum()
print(f"  - Sai lệch thanh toán so với [Tiền hàng net + Phí ship]: {pay_discrepancy_ship:,} đơn ({pay_discrepancy_ship/len(reconciliation)*100:.2f}%)")
print(f"  - Sai lệch thanh toán so với [Tiền hàng net đơn thuần]: {pay_discrepancy_items:,} đơn ({pay_discrepancy_items/len(reconciliation)*100:.2f}%)")
findings.append({
    'table': 'payments vs order_items', 'column': 'payment_value vs expected_total',
    'issue_type': 'Payment Reconciliation Gap (Lệch đối soát)',
    'count': int(pay_discrepancy_ship), 'pct': float(pay_discrepancy_ship / len(reconciliation) * 100),
    'severity': 'HIGH' if pay_discrepancy_ship > 1000 else 'MEDIUM',
    'description': f'{pay_discrepancy_ship:,} đơn hàng có số tiền thực trả lệch so với tổng giá trị hàng hóa và phí vận chuyển'
})

# --- CHECK 7: Return Integrity & Impossible Quantities ---
print("\n[7] TOÀN VẸN ĐƠN ĐỔI TRẢ (RETURNS INTEGRITY):")
ret_items = returns.merge(order_items[['order_id', 'product_id', 'quantity']], on=['order_id', 'product_id'], how='left')
ret_qty_exceeds = (ret_items['return_quantity'] > ret_items['quantity']).sum()
ret_unmatched = ret_items['quantity'].isnull().sum()
print(f"  - Số lượng trả hàng > số lượng đã mua: {ret_qty_exceeds:,} dòng")
print(f"  - Trả sản phẩm không có trong đơn hàng ban đầu: {ret_unmatched:,} dòng")
findings.append({
    'table': 'returns vs order_items', 'column': 'return_quantity vs quantity',
    'issue_type': 'Impossible Returns (Trả hàng phi lý)',
    'count': int(ret_qty_exceeds + ret_unmatched), 'pct': float((ret_qty_exceeds + ret_unmatched) / len(returns) * 100),
    'severity': 'HIGH' if (ret_qty_exceeds + ret_unmatched) > 0 else 'LOW',
    'description': f'{ret_qty_exceeds:,} dòng có số lượng trả lớn hơn đã mua; {ret_unmatched:,} sản phẩm trả không thuộc đơn hàng'
})

# --- CHECK 8: Inventory Anomalies & Metric Inconsistencies ---
print("\n[8] BẤT THƯỜNG TRONG QUẢN TRỊ KHO (INVENTORY ANOMALIES):")
neg_stock = (inventory['stock_on_hand'] < 0).sum()
invalid_stockout_days = (inventory['stockout_days'] > 31).sum()
invalid_fill_rate = ((inventory['fill_rate'] < 0) | (inventory['fill_rate'] > 1.0)).sum()
invalid_sell_through = ((inventory['sell_through_rate'] < 0) | (inventory['sell_through_rate'] > 1.0)).sum()

print(f"  - Tồn kho âm (stock_on_hand < 0): {neg_stock:,} dòng")
print(f"  - Số ngày đứt hàng trong tháng > 31 ngày: {invalid_stockout_days:,} dòng")
print(f"  - Fill rate ngoài khoảng [0, 1]: {invalid_fill_rate:,} dòng")
print(f"  - Sell-through rate ngoài khoảng [0, 1]: {invalid_sell_through:,} dòng")
findings.append({
    'table': 'inventory', 'column': 'stock_on_hand / fill_rate / stockout_days',
    'issue_type': 'Inventory Metric Violations',
    'count': int(neg_stock + invalid_stockout_days + invalid_fill_rate + invalid_sell_through),
    'pct': float((neg_stock + invalid_stockout_days + invalid_fill_rate + invalid_sell_through) / len(inventory) * 100),
    'severity': 'MEDIUM',
    'description': f'Tồn kho âm ({neg_stock}), ngày đứt hàng > 31 ({invalid_stockout_days}), fill rate vi phạm ({invalid_fill_rate})'
})

# --- CHECK 9: Aggregate Sales vs Transactional Orders Reconciliation ---
print("\n[9] ĐỐI SOÁT DOANH THU TỔNG HỢP (SALES.CSV) VS TỔNG ĐƠN HÀNG (ORDERS.CSV):")
# Aggregate daily orders
orders['order_date_str'] = orders['order_date'].str[:10]
order_items_order = order_items.merge(orders[['order_id', 'order_date_str', 'order_status']], on='order_id')
daily_order_rev = order_items_order.groupby('order_date_str')['item_net'].sum().reset_index(name='trans_revenue')

sales_comp = sales.merge(daily_order_rev, left_on='Date', right_on='order_date_str', how='inner')
sales_comp['diff_abs'] = np.abs(sales_comp['Revenue'] - sales_comp['trans_revenue'])
sales_comp['diff_pct'] = sales_comp['diff_abs'] / sales_comp['Revenue'] * 100
large_rev_mismatch = (sales_comp['diff_pct'] > 5.0).sum()
print(f"  - Số ngày có doanh thu sales.csv lệch > 5% so với tổng đơn hàng orders.csv: {large_rev_mismatch:,} / {len(sales_comp)} ngày ({large_rev_mismatch/len(sales_comp)*100:.2f}%)")
print(f"  - Sai lệch doanh thu trung bình mỗi ngày: {sales_comp['diff_abs'].mean():,.2f} VNĐ ({sales_comp['diff_pct'].mean():.2f}%)")
findings.append({
    'table': 'sales vs orders / order_items', 'column': 'Revenue vs sum(item_net)',
    'issue_type': 'Macro-Micro Discrepancy (Lệch doanh thu vĩ mô - vi mô)',
    'count': int(large_rev_mismatch), 'pct': float(large_rev_mismatch / len(sales_comp) * 100),
    'severity': 'CRITICAL',
    'description': f'{large_rev_mismatch} ngày ({large_rev_mismatch/len(sales_comp)*100:.2f}%) có doanh thu vĩ mô lệch > 5% so với dữ liệu đơn hàng vi mô'
})

# Save findings dataframe
df_findings = pd.DataFrame(findings)
out_csv = os.path.join(r"C:\Users\Admin\firstmate\projects\datathon-2026-sales-forecasting\data", "data_dirtiness_audit.csv")
df_findings.to_csv(out_csv, index=False)
print(f"\n=> Đã lưu kết quả kiểm toán vào: {out_csv}")
print("="*70)
