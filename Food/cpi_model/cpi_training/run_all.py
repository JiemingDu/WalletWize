# Food/cpi_training/run_all.py
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
steps = [
    ("Cleaning raw CSV",   f"python3 {HERE/'clean_cpi.py'}"),
    ("Training CPI models",f"python3 {HERE/'train_cpi.py'}"),
    ("Forecasting CPI",    f"python3 {HERE/'predict_cpi.py'}"),
]
print("🚀 Starting CPI pipeline...\n")
for label, cmd in steps:
    print(f"▶️ {label}")
    if subprocess.run(cmd, shell=True).returncode != 0:
        print(f"❌ {label} failed."); sys.exit(1)
print("\n✅ All CPI steps completed successfully!")
