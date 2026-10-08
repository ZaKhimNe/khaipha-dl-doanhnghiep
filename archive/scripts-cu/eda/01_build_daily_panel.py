"""Dựng master daily panel + thống kê mô tả/kiểm định cho sales.csv.

Nguồn: archive/engine-goc/merge_and_eda.py (Stage 1-3, 5). Các biểu đồ của file gốc
trùng với bản tiếng Việt nên đã chuyển hết sang 02_eda_charts_vi.py.

Đầu ra: outputs/data/master_daily_panel.csv, outputs/data/statistical_proof.json
Chạy:   python scripts/eda/01_build_daily_panel.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import scipy.stats as stats  # noqa: E402

from ds317 import out_dir  # noqa: E402
from ds317.panel import build_daily_panel  # noqa: E402


def main():
    out = out_dir("data")
    master = build_daily_panel()
    master.to_csv(out / "master_daily_panel.csv", index=False)
    print(f"master_daily_panel: {master.shape[0]} ngày x {master.shape[1]} cột")

    # TODO(phuong-phap): so Revenue với MA30 của chính nó (MA30 chứa cả ngày hiện tại) không
    # chứng minh được gì; bootstrap i.i.d. bỏ qua tự tương quan. Nên thay bằng so sánh
    # sai số mô hình vs baseline trên validation.
    actual = master["Revenue"]
    baseline = actual.rolling(30).mean().bfill()
    diff = actual - baseline
    t_stat, p_val = stats.ttest_rel(actual, baseline)
    w_stat, w_pval = stats.wilcoxon(diff)
    rng = np.random.default_rng(42)
    boot = [rng.choice(actual, size=len(actual), replace=True).mean() for _ in range(2000)]
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

    summary = {
        "dataset_rows": int(len(master)),
        "start_date": str(master["Date"].min().date()),
        "end_date": str(master["Date"].max().date()),
        "revenue_mean": float(actual.mean()),
        "revenue_median": float(actual.median()),
        "revenue_std": float(actual.std()),
        "revenue_skewness": float(stats.skew(actual)),
        "revenue_kurtosis": float(stats.kurtosis(actual)),
        "cogs_mean": float(master["COGS"].mean()),
        "cogs_median": float(master["COGS"].median()),
        "margin_mean_pct": float(master["Gross_Margin_Pct"].mean()),
        "paired_t_test": {"t_statistic": float(t_stat), "p_value": float(p_val), "significant": bool(p_val < 0.001)},
        "wilcoxon_test": {"statistic": float(w_stat), "p_value": float(w_pval), "significant": bool(w_pval < 0.001)},
        "cohens_d": float(diff.mean() / diff.std(ddof=1)),
        "bootstrap_95_ci": {"iterations": 2000, "ci_lower": float(ci_lo), "ci_upper": float(ci_hi)},
    }
    with open(out / "statistical_proof.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("  saved statistical_proof.json")


if __name__ == "__main__":
    main()
