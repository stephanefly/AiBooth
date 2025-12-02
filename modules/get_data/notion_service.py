from datetime import datetime
from typing import Optional, Any
from datetime import date, timedelta

from notion_client import Client as Notion
from dotenv import load_dotenv
import os

# Charge .env
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Notion(auth=NOTION_TOKEN)

yesterday = (date.today() - timedelta(days=1)).isoformat()

NOTION_TASK_FILTER = {
    "and": [
        {"property": "État", "status": {"does_not_equal": "Done"}},
        {"property": "Domaine", "select": {"does_not_equal": "RESERVATION"}},
    ]
}

def _days_until(date_value: Any) -> Optional[int]:
    """
    Prend soit :
    - une string ISO ("2025-11-15" ou "2025-11-15T10:00:00.000Z")
    - un dict Notion {"start": "...", "end": ...}
    - ou autre -> renvoie None
    """
    if not date_value:
        return None

    # Cas dict Notion {"start": "2025-11-15", "end": None}
    if isinstance(date_value, dict):
        date_value = date_value.get("start")

    # On veut absolument une string ici
    if not isinstance(date_value, str):
        return None

    # On coupe au cas où il y a l'heure dedans
    date_str = date_value.split("T")[0]

    try:
        due = datetime.fromisoformat(date_str).date()
    except ValueError:
        return None

    today = date.today()
    return (due - today).days


def fetch_tasks():
    tasks = []

    data = notion.databases.query(
        database_id=DATABASE_ID,
        filter=NOTION_TASK_FILTER,
        page_size=1000
    )

    for row in data["results"]:
        # Titre : on sécurise s'il n'y a pas de bloc
        title_prop = row["properties"]["Nom"]["title"]
        title = title_prop[0]["plain_text"] if title_prop else "(Sans titre)"

        # Priorité
        prio_prop = row["properties"]["Priorité"]["select"]
        prio = prio_prop["name"] if prio_prop else "Moyenne"

        # Domaine (tu avais une petite erreur ici : tu re-testais Priorité)
        domaine_prop = row["properties"]["Domaine"]["select"]
        domaine = domaine_prop["name"] if domaine_prop else ""

        # Etat (tu avais une petite erreur ici : tu re-testais Priorité)
        etat_prop = row["properties"]["État"]["status"]
        etat = etat_prop["name"] if etat_prop else ""

        url = row["url"]

        # Échéance Notion : c'est un dict {"start": "...", "end": "..."} ou None
        echeance_prop = row["properties"]["Échéance"]["date"]
        # due_date stockée comme string simple (ou None)
        due_date = echeance_prop["start"] if echeance_prop else None

        days_remaining = _days_until(echeance_prop) if echeance_prop else None

        tasks.append({
            "title": title,
            "prio": prio,
            "etat": etat,
            "domaine": domaine,
            "due_date": due_date,
            "days_remaining": days_remaining,
            "url": url,
        })

    return tasks
