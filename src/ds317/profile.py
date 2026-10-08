"""Mô tả kỹ thuật từng bảng, phục vụ từ điển dữ liệu (notebook 00)."""
import pandas as pd

from .data import DATE_COLS


def _fmt(v):
    if pd.isna(v):
        return ""
    if isinstance(v, pd.Timestamp):
        return str(v.date())
    if isinstance(v, float):
        return f"{v:,.4g}"
    return str(v)


def profile_table(df: pd.DataFrame, name: str = "") -> pd.DataFrame:
    """1 dòng / cột: tên cột, kiểu, % trống, số giá trị khác nhau, min, max, 3 giá trị ví dụ."""
    rows = []
    for col in df.columns:
        s = df[col]
        nonnull = s.dropna()
        orderable = pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s)
        examples = nonnull.drop_duplicates().head(3)
        rows.append({
            "bang": name,
            "cot": col,
            "kieu": str(s.dtype),
            "pct_trong": round(s.isna().mean() * 100, 2),
            "so_gia_tri_khac_nhau": int(s.nunique()),
            "min": _fmt(nonnull.min()) if orderable and len(nonnull) else "",
            "max": _fmt(nonnull.max()) if orderable and len(nonnull) else "",
            "vi_du": " | ".join(_fmt(v) for v in examples),
        })
    return pd.DataFrame(rows)


def date_range(df: pd.DataFrame, name: str) -> tuple:
    """(ngày nhỏ nhất, ngày lớn nhất) trên các cột ngày của bảng; (None, None) nếu không có."""
    cols = [c for c in DATE_COLS.get(name, []) if c in df.columns]
    if not cols:
        return None, None
    return min(df[c].min() for c in cols), max(df[c].max() for c in cols)


def key_coverage(child: pd.DataFrame, parent: pd.DataFrame, key: str,
                 child_name: str = "", parent_name: str = "", parent_key: str | None = None) -> dict:
    """% giá trị khoá (khác nhau, khác NaN) của bảng con có trong bảng cha."""
    ck = child[key].dropna().unique()
    pk = set(parent[parent_key or key].dropna().unique())
    missing = sum(1 for v in ck if v not in pk)
    return {
        "bang_con": child_name, "bang_cha": parent_name, "khoa": key,
        "so_khoa_con": len(ck), "so_khoa_thieu_o_cha": missing,
        "pct_khop": round((1 - missing / len(ck)) * 100, 4) if len(ck) else float("nan"),
    }


def duplicate_keys(df: pd.DataFrame, key: str | list) -> int:
    """Số dòng có khoá chính bị trùng (không tính lần xuất hiện đầu tiên)."""
    return int(df.duplicated(subset=key).sum())
