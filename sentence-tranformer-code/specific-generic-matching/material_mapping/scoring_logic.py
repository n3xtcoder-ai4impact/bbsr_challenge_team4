import pandas as pd
import torch
from sentence_transformers import util


def name_sim(embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
    return util.cos_sim(embedding1, embedding2).item()


def cat_sim(embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
    return util.cos_sim(embedding1, embedding2).item()


def year_bucket_match(year1: int, year2: int) -> int:
    if pd.isna(year1) or pd.isna(year2):
        return 0
    return 1 if abs(int(year1) - int(year2)) <= 2 else 0


def unit_match(unit1: str, unit2: str) -> int:
    return 1 if unit1.strip().lower() == unit2.strip().lower() else 0
