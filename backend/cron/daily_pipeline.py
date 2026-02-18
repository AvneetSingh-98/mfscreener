import subprocess
import sys
from datetime import datetime
from pathlib import Path

# =========================
# PROJECT ROOT
# =========================
ROOT = Path(__file__).resolve().parents[1]

# =========================
# SCRIPT PATHS (EXACT)
# =========================
SCRIPTS = [
    # 🔴 Benchmarks (NSE first, then BSE)
    ROOT / "data_ingestion" / "benchmarks" / "store_nav_daily_benchmark_nse.py",
    ROOT / "data_ingestion" / "benchmarks" / "store_nav_daily_benchmark_bse.py",

    # 🔴 Fund NAV
    ROOT / "data_ingestion" / "amfi" / "store_nav.py",

    # 🔴 Phase-3A
    ROOT / "scoring" / "large_cap_score_phase3a.py",

    # 🔴 Phase-3B
    ROOT / "scoring" / "large_cap_score_phase3b.py",

    # 🔴 Phase-3C
    ROOT / "scoring" / "large_cap_score_phase3c.py",
]


# =========================
# LOGGER
# =========================
def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts} UTC] {msg}")


def run(script_path: Path):
    log(f"▶ Running {script_path.name}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Script failed: {script_path.name}")

    log(f"✅ Completed {script_path.name}")


# =========================
# PIPELINE
# =========================
def main():
    log("🚀 DAILY PIPELINE STARTED")

    for script in SCRIPTS:
        if not script.exists():
            raise FileNotFoundError(f"Missing script: {script}")
        run(script)

    log("🏁 DAILY PIPELINE FINISHED SUCCESSFULLY")


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    main()
