from datetime import datetime
from typing import Optional
from datetime import date, timedelta

from notion_client import Client as Notion
from models import Task
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

data = notion.databases.query(
    database_id=DATABASE_ID,
    filter=NOTION_TASK_FILTER,
    page_size=100
)


def _days_until(date_str: str) -> Optional[int]:
    if not date_str:
        return None

    due = datetime.fromisoformat(date_str).date()

    today = date.today()
    return (due - today).days



def fetch_tasks():
    tasks = []

    for row in data["results"]:

        title = row["properties"]["Nom"]["title"][0]["plain_text"]

        prio = (
            row["properties"]["Priorité"]["select"]["name"]
            if row["properties"]["Priorité"]["select"]
            else "Moyenne"
        )

        domaine = (
            row["properties"]["Domaine"]["select"]["name"]
            if row["properties"]["Priorité"]["select"]
            else ""
        )

        url = row["url"]

        due_date = (
            row["properties"]["Échéance"]["date"]
            if row["properties"]["Échéance"]["date"]
            else None)
        days_remaining = _days_until(due_date) if due_date else None

        tasks.append({
            "title": title,
            "prio": prio,
            "domaine": domaine,
            "due_date": due_date,
            "days_remaining": days_remaining,
            "url": url,
        })

    return tasks
