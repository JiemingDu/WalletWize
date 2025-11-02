# Food/model.py
"""
Read wide CPI CSV like:
    Month and Year, July 1980, August 1980, ...
    CPI,            52.0,      53.0,        ...

Steps:
  1) Parse monthly cells, group -> yearly average CPI (raw).
  2) Normalize so BASE_YEAR = 100 (index).
  3) Forecast to `end_year` with a CAGR estimated from recent history.

Output dict is {year: index}, e.g. {2025: 100.0, 2026: 102.7, ...}
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import csv
import io
import re

BASE_YEAR = 2025
MONTHS = (
    "january","february","march","april","may","june",
    "july","august","september","october","november","december"
)

def _open_sniff(csv_path: str) -> Tuple[List[str], List[str]]:
    """
    Return (headers, values) for the first two CSV rows with delimiter sniffing + BOM handling.
    Assumes row 1 = header of month-year, row 2 starts with "CPI".
    """
    with open(csv_path, "rb") as f:
        raw = f.read()
    # handle UTF-8 BOM
    text = raw.decode("utf-8-sig", errors="replace")
    sample = text.splitlines()[0] if text else ""
    try:
        dialect = csv.Sniffer().sniff(sample)
        delim = dialect.delimiter
    except Exception:
        delim = ","  # default
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if len(rows) < 2:
        raise ValueError("CSV must have at least two rows (header + CPI row).")
    headers = [h.strip() for h in rows[0]]
    values  = [v.strip() for v in rows[1]]
    return headers, values

def _parse_month_year_headers(headers: List[str]) -> List[Tuple[int, str]]:
    """
    From headers like ["Month and Year","July 1980","August 1980",...]
    produce [(1980,'July'),(1980,'August'),...]
    Non-matching headers are ignored.
    """
    out: List[Tuple[int, str]] = []
    pat = re.compile(r"([A-Za-z]+)\s+((?:19|20)\d{2})")
    for h in headers[1:]:  # skip first ("Month and Year")
        m = pat.search(h)
        if not m: 
            continue
        month, year = m.group(1), int(m.group(2))
        if month.lower() not in MONTHS:
            continue
        out.append((year, month))
    return out

def _yearly_averages(headers: List[str], values: List[str]) -> Dict[int, float]:
    """
    Build {year: average_raw_cpi} using the second row values.
    values[0] should be "CPI"; values[1:] align with headers[1:].
    """
    ym = _parse_month_year_headers(headers)
    if not ym:
        raise ValueError("No month-year headers recognized.")
    if len(values) < 2:
        raise ValueError("Second row lacks CPI values.")
    nums: List[float] = []
    for v in values[1:]:
        try:
            nums.append(float(v))
        except Exception:
            nums.append(float("nan"))

    # group by year
    year_to_vals: Dict[int, List[float]] = {}
    for (year, _month), val in zip(ym, nums):
        if val == val:  # not NaN
            year_to_vals.setdefault(year, []).append(val)

    # average
    year_to_avg = {y: sum(vs)/len(vs) for y, vs in year_to_vals.items() if vs}
    if not year_to_avg:
        raise ValueError("No numeric CPI values parsed.")
    return dict(sorted(year_to_avg.items()))

def _normalize_to_base(year_to_avg: Dict[int, float], base_year: int = BASE_YEAR) -> Dict[int, float]:
    if base_year in year_to_avg and year_to_avg[base_year] != 0:
        base = year_to_avg[base_year]
    else:
        # if base missing, use last available year
        last_year = sorted(year_to_avg)[-1]
        base = year_to_avg[last_year] or 1.0
    return {y: (v / base) * 100.0 for y, v in year_to_avg.items()}

def _estimate_cagr(year_to_idx: Dict[int, float], window: int = 5) -> float:
    """
    Estimate compound annual growth from the last `window` years (min 2).
    Returns decimal rate, e.g., 0.025 for 2.5%.
    """
    years = sorted(year_to_idx)
    if len(years) < 2:
        return 0.0
    use = years[-window:] if len(years) >= window else years
    first, last = use[0], use[-1]
    v0, v1 = year_to_idx[first], year_to_idx[last]
    if v0 <= 0 or last == first:
        return 0.0
    return (v1 / v0) ** (1.0 / (last - first)) - 1.0

def build_food_cpi_model(csv_path: str, *, end_year: int = 2035, fallback_cagr: float = 0.025) -> Dict[int, float]:
    """
    Build CPI index {year: index} from the wide CSV and forecast to `end_year`.
    - Normalized so BASE_YEAR = 100.
    """
    headers, values = _open_sniff(csv_path)
    year_to_avg = _yearly_averages(headers, values)
    year_to_idx = _normalize_to_base(year_to_avg, BASE_YEAR)

    # forecast
    cagr = _estimate_cagr(year_to_idx, window=5)
    if cagr == 0.0:
        cagr = float(fallback_cagr)

    last_year = max(year_to_idx)
    last_val  = year_to_idx[last_year]
    for y in range(last_year + 1, end_year + 1):
        last_val *= (1.0 + cagr)
        year_to_idx[y] = last_val

    # re-normalize to ensure exact BASE_YEAR = 100
    if BASE_YEAR in year_to_idx and year_to_idx[BASE_YEAR] != 0:
        base = year_to_idx[BASE_YEAR]
        for y in list(year_to_idx.keys()):
            year_to_idx[y] = round(year_to_idx[y] / base * 100.0, 2)

    return dict(sorted(year_to_idx.items()))
