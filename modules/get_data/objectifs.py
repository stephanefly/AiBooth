from pathlib import Path
import pandas as pd

EXCEL_PATH = Path(__file__).resolve().parents[2] / "Objectifs_Strategiques_MySelfieBooth.xlsx"
SHEET = "GLOBAL"

PRIO_WEIGHTS = {"CRITIQUE": 3, "HAUT": 2, "MOYEN": 1, "FAIBLE": 0}

def criteria_to_prompt_block():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET)
    df = df.rename(columns={
        "Domaine": "domaine",
        "Résumé": "resume",
        "Objectif": "objectif",
        "PRIORITE": "priorite",
    })[["domaine", "resume", "objectif", "priorite"]].dropna(subset=["domaine","objectif","priorite"])
    df["poids"] = df["priorite"].astype(str).str.upper().map(PRIO_WEIGHTS).fillna(0).astype(int)
    lines = [f"- {r.domaine} — {r.objectif} — PRIORITE={r.priorite} ({r.poids})" for _, r in df.iterrows()]
    return "\n".join(lines)
