"""Lấy mẫu phân tầng ~150k dòng order_items theo (Năm, Danh mục) + kiểm định KS.

Nguồn: archive/engine-goc/stratified_eda_sampler.py. Biểu đồ so sánh mẫu/gốc đã có trong
02_eda_charts_vi.py nên không vẽ lại. Kết luận in ra giờ phụ thuộc kết quả KS
(bản gốc luôn in "ZERO LEAKAGE").

Đầu ra: outputs/data/order_items_stratified_150k.csv, outputs/data/stratified_sample_metrics.json
Chạy:   python scripts/eda/04_stratified_sample.py [so_dong]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import scipy.stats as stats  # noqa: E402

from ds317 import order_lines, out_dir  # noqa: E402

KS_THRESHOLD = 0.02


def main(target: int = 150_000):
    out = out_dir("data")
    df = order_lines()
    df["Year"] = df["order_date"].dt.year
    df["Gross_Item_Revenue"] = df["net"]  # giữ tên cột như bản gốc
    df["Gross_Item_COGS"] = df["quantity"] * df["cogs"]

    frac = min(1.0, target / len(df))
    sample = df.groupby(["Year", "category"], group_keys=False).sample(frac=frac, random_state=42).reset_index(drop=True)
    ks = stats.ks_2samp(df["Gross_Item_Revenue"], sample["Gross_Item_Revenue"])
    ok = ks.statistic < KS_THRESHOLD
    print(f"Tổng thể {len(df):,} dòng -> mẫu {len(sample):,} dòng (frac={frac:.4f})")
    print(f"KS D={ks.statistic:.5f}, p={ks.pvalue:.4f} -> "
          + ("phân phối được bảo toàn" if ok else f"CẢNH BÁO: D >= {KS_THRESHOLD}, mẫu lệch phân phối"))

    metrics = {
        "population_rows": int(len(df)),
        "stratified_sample_rows": int(len(sample)),
        "sampling_ratio": float(len(sample) / len(df)),
        "strata_dimensions": ["Year", "category"],
        "revenue_mean": float(sample["Gross_Item_Revenue"].mean()),
        "revenue_median": float(sample["Gross_Item_Revenue"].median()),
        "revenue_std": float(sample["Gross_Item_Revenue"].std()),
        "cogs_mean": float(sample["Gross_Item_COGS"].mean()),
        "ks_test_divergence": {"statistic": float(ks.statistic), "p_value": float(ks.pvalue),
                               "threshold": KS_THRESHOLD, "distribution_preserved": bool(ok)},
    }
    with open(out / "stratified_sample_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    sample.to_csv(out / "order_items_stratified_150k.csv", index=False)
    print("  saved stratified_sample_metrics.json, order_items_stratified_150k.csv")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 150_000)
