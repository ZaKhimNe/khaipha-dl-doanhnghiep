"""Cấu hình biểu đồ, thư mục đầu ra và hàm lưu hình dùng chung."""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from .paths import out_dir

MILLION = 1e6
UNIT = "Triệu VNĐ"
NOTE_SALES = "Nguồn: sales.csv. sales.Revenue = doanh thu gộp, gồm đơn huỷ, trước chiết khấu."
NOTE_TRAFFIC = "Chỉ dùng dữ liệu từ 2013-01-01 (web_traffic không có 181 ngày cuối 2012)."


def _in_notebook() -> bool:
    try:
        from IPython import get_ipython
        return get_ipython() is not None and "IPKernelApp" in get_ipython().config
    except Exception:
        return False


def setup_style(dpi: int = 110, savefig_dpi: int = 200) -> None:
    if not _in_notebook():
        matplotlib.use("Agg")
    style = "seaborn-v0_8-whitegrid"
    plt.style.use(style if style in plt.style.available else "default")
    # Segoe UI / Arial hiển thị đủ dấu tiếng Việt trên Windows; DejaVu Sans là dự phòng.
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Tahoma", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = dpi
    plt.rcParams["savefig.dpi"] = savefig_dpi


def nb_out(name: str) -> tuple[Path, Path]:
    """(thư mục ảnh, thư mục bảng) = outputs/eda/<name>/ và outputs/eda/<name>/tables/."""
    return out_dir("eda", name), out_dir("eda", name, "tables")


def source_note(fig, text: str) -> None:
    """Ghi chú nguồn số liệu / định nghĩa doanh thu ở góc dưới trái chart."""
    fig.text(0.01, -0.01, text, ha="left", va="top", fontsize=9, color="#555555", style="italic")


def key_numbers(items: dict) -> None:
    """In khối 'Số liệu chính' (3–5 con số tính từ data) dưới mỗi chart."""
    print("Số liệu chính:")
    for k, v in items.items():
        print(f"  - {k}: {v}")


def save_fig(fig, path: Path, show: bool = True, **kwargs) -> None:
    """Lưu hình; trong notebook thì hiển thị luôn rồi đóng để không vẽ trùng."""
    kwargs.setdefault("bbox_inches", "tight")
    fig.savefig(path, **kwargs)
    if show and _in_notebook():
        from IPython.display import display
        display(fig)
    plt.close(fig)
    print(f"  đã lưu {path.name}")
