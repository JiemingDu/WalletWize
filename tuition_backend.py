"""
Minimal tuition backend (full-time only, no predictions).

Expected CSV: montreal_tuition_annual_cad.csv
Columns: university, program, annual_tuition_cad

API:
- list_schools() -> list[str]
- list_programs(school: str) -> list[str]
- get_tuition(school: str, program: str) -> dict
"""

from __future__ import annotations
from pathlib import Path
import csv
from typing import Dict, List

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "montreal_tuition_annual_cad.csv"

class TuitionIndex:
    def __init__(self, csv_path: str | Path = CSV_PATH):
        self.csv_path = Path(csv_path)
        self._by_school: Dict[str, Dict[str, float]] = {}  # {school: {program: tuition}}
        self._load()

    @staticmethod
    def _norm(s: str) -> str:
        return (s or "").strip().lower()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")

        with self.csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                school = row["university"].strip()
                program = row["program"].strip()
                try:
                    tuition = float(row["annual_tuition_cad"])
                except Exception:
                    continue

                school_key = self._norm(school)
                self._by_school.setdefault(school_key, {})
                self._by_school[school_key][program] = tuition

    # Public API
    def list_schools(self) -> List[str]:
        """For your School dropdown."""
        # Return the original casing by title-casing the key
        return sorted({s.title() for s in self._by_school.keys()})

    def list_programs(self, school: str) -> List[str]:
        """For your Program dropdown (depends on selected school)."""
        skey = self._norm(school)
        if skey not in self._by_school:
            return []
        return sorted(self._by_school[skey].keys())

    def get_tuition(self, school: str, program: str) -> Dict:
        """Return annual tuition (CAD) for the exact program at the given school."""
        skey = self._norm(school)
        if skey not in self._by_school:
            raise ValueError(f"Unknown school: {school}")

        # exact program match first
        school_programs = self._by_school[skey]
        if program in school_programs:
            amount = school_programs[program]
        else:
            # fallback: case-insensitive scan
            matches = [p for p in school_programs.keys() if p.lower() == program.lower()]
            if matches:
                amount = school_programs[matches[0]]
                program = matches[0]  # normalize the label
            else:
                raise ValueError(
                    f"Program not found for {school}: '{program}'. "
                    f"Available: {sorted(school_programs.keys())}"
                )

        return {
            "school": school,
            "program": program,
            "annual_tuition_cad": round(amount, 2),
        }


INDEX = TuitionIndex(CSV_PATH)


def list_schools() -> List[str]:
    return INDEX.list_schools()


def list_programs(school: str) -> List[str]:
    return INDEX.list_programs(school)


def get_tuition(school: str, program: str) -> Dict:
    return INDEX.get_tuition(school, program)["annual_tuition_cad"]


# Local test
if __name__ == "__main__":
    print(get_tuition("McGill", "Bachelor of Science in Architecture (BSc(Arch))"))
#     print("Schools:", list_schools())
#     print("McGill programs (first 5):", list_programs("McGill")[:5])
#     print(get_tuition("McGill", "Bachelor of Engineering (BEng)"))