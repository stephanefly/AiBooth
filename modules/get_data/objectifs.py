from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from models import Objective

EXCEL_PATH = Path(__file__).resolve().parents[2] / "Objectifs_Strategiques_MySelfieBooth.xlsx"
SHEET = "GLOBAL"

PRIO_WEIGHTS = {"CRITIQUE": 3, "HAUT": 2, "MOYEN": 1, "FAIBLE": 0, "CRITIQUE OPE": 4}


@lru_cache
def _load_objectives_frame() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET)
    df = df.rename(
        columns={
            "Domaine": "domaine",
            "Résumé": "resume",
            "Objectif": "objectif",
            "PRIORITE": "priorite",
        }
    )

    df = df[["domaine", "resume", "objectif", "priorite"]]
    df = df.dropna(subset=["domaine", "objectif", "priorite"])
    df["priorite"] = df["priorite"].astype(str).str.strip()
    df["resume"] = df["resume"].fillna("")
    df["poids"] = (
        df["priorite"].str.upper().map(PRIO_WEIGHTS).fillna(0).astype(int)
    )
    df = df.sort_values("poids", ascending=False)
    return df


def criteria_to_prompt_block() -> str:
    df = _load_objectives_frame()
    lines = [
        f"- {r.domaine} — {r.objectif} — PRIORITE={r.priorite} ({r.poids})"
        for _, r in df.iterrows()
    ]
    return "\n".join(lines)


def objectives_with_priority() -> List[Objective]:
    df = _load_objectives_frame()
    objectives: Iterable[Objective] = (
        Objective(
            domaine=row.domaine,
            resume=row.resume,
            objectif=row.objectif,
            priorite=row.priorite,
            poids=int(row.poids),
        )
        for _, row in df.iterrows()
    )
    return list(objectives)
