# Food/cpi_training/clean_cpi.py
from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT
from pathlib import Path
from tkinter.tix import ROW
import pandas as pd
import io
import re

from Food.cpi_model.paths import DATA_DIR, MODELS_DIR, CPI_ROOT

OUT_STORES = DATA_DIR / "qc_food_purchased_from_stores_clean.csv"
OUT_RESTO  = DATA_DIR / "qc_food_purchased_from_restaurants_clean.csv"

def extract_csv_block(raw_text: str) -> str:
    """
    The StatCan export is a 'wide' table with a long preface and footnotes.
    We:
      - find the 'Geography' header row,
      - take the next two rows (months, units),
      - then keep only the two data rows we need.
    Return a minimal CSV string: header_line\nstores_line\nrestaurants_line
    """
    lines = raw_text.splitlines()
    # find the row that starts with "Geography"
    geo_idx = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith('"Geography"'):
            geo_idx = i
            break
    if geo_idx is None:
        raise RuntimeError("Could not find 'Geography' header row in file.")

    months_line = lines[geo_idx + 1]
    # normalize first header cell
    months_line = re.sub(r'^"[^"]+"', '"Products and product groups"', months_line)

    # find the two data rows anywhere after header block
    data_lines = lines[geo_idx + 3 : ]
    stores_line = None
    resto_line  = None
    for ln in data_lines:
        s = ln.strip()
        if s.startswith('"Food purchased from stores"'):
            stores_line = ln
        elif s.startswith('"Food purchased from restaurants"'):
            resto_line = ln
        elif s.startswith('"Food purchased from restaurants '):   # with footnote number
            resto_line = ln
        # stop early if both found
        if stores_line and resto_line:
            break

    if not stores_line or not resto_line:
        raise RuntimeError("Could not find both stores/restaurants lines in the file.")

    # build a tiny CSV with header + two rows
    tiny_csv = months_line + "\n" + stores_line + "\n" + resto_line + "\n"
    return tiny_csv

def main():
    # read as text; ignore weird encodings/HTML anchors
    raw_text = ROW.read_text(encoding="utf-8", errors="ignore")
    tiny = extract_csv_block(raw_text)

    # parse that tiny CSV safely
    df_wide = pd.read_csv(io.StringIO(tiny), header=0, engine="python")

    # melt to long
    df_long = df_wide.melt(
        id_vars=["Products and product groups"],
        var_name="Date",
        value_name="CPI_Food"
    )

    # clean
    df_long["Products and product groups"] = df_long["Products and product groups"].str.replace(r"\s*\d+$", "", regex=True)
    df_long["Date"] = pd.to_datetime(df_long["Date"], format="%B %Y", errors="coerce")
    df_long["CPI_Food"] = pd.to_numeric(df_long["CPI_Food"], errors="coerce")
    df_long = df_long.dropna(subset=["Date", "CPI_Food"]).sort_values("Date")

    # split and save
    stores = df_long[df_long["Products and product groups"]=="Food purchased from stores"][["Date","CPI_Food"]]
    resto  = df_long[df_long["Products and product groups"]=="Food purchased from restaurants"][["Date","CPI_Food"]]

    stores.to_csv(OUT_STORES, index=False)
    resto.to_csv(OUT_RESTO, index=False)

    print(f"✅ Saved Quebec groceries -> {OUT_STORES}")
    print(f"✅ Saved Quebec restaurants -> {OUT_RESTO}")

if __name__ == "__main__":
    main()
