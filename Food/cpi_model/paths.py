# Food/cpi_model/paths.py
from pathlib import Path

# Root of the cpi_model package: .../Food/cpi_model
CPI_ROOT = Path(__file__).resolve().parent

# Data and models live INSIDE the cpi_model package
DATA_DIR   = CPI_ROOT / "data"
MODELS_DIR = CPI_ROOT / "models"