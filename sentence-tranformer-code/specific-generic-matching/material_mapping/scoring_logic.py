import pandas as pd


def year_bucket_match(year1: int, year2: int) -> int:
    if pd.isna(year1) or pd.isna(year2):
        return 0
    return 1 if abs(int(year1) - int(year2)) <= 2 else 0


def unit_match(unit1: str, unit2: str) -> int:
    return 1 if unit1.strip().lower() == unit2.strip().lower() else 0
