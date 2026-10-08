"""Đường dẫn chuẩn của project.

Mặc định đọc dữ liệu từ <repo>/data/raw/datathon-2026-round-1.
Chạy ở máy khác / Colab: đặt biến môi trường DS317_DATA_DIR trỏ tới thư mục chứa 14 file CSV.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("DS317_DATA_DIR", ROOT / "data" / "raw" / "datathon-2026-round-1"))
OUTPUT_DIR = Path(os.environ.get("DS317_OUTPUT_DIR", ROOT / "outputs"))


def out_dir(*parts: str) -> Path:
    """Trả về thư mục con trong outputs/ (tự tạo nếu chưa có)."""
    p = OUTPUT_DIR.joinpath(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return p
