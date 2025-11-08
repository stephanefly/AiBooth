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
        {"property": "Échéance", "date": {"after": yesterday}}
    ]
}

data = notion.databases.query(
    database_id=DATABASE_ID,
    filter=NOTION_TASK_FILTER,
    page_size=100
)


def _extract_due_date(properties: dict[str, dict]) -> Optional[str]:
    candidate_keys = [
        "Échéance",
        "Echéance",
        "Echeance",
        "Deadline",
        "Due Date",
    ]

    for key in candidate_keys:
        prop = properties.get(key)
        if not prop:
            continue
        date_payload = prop.get("date")
        if date_payload and date_payload.get("start"):
            return date_payload["start"]
    return None


def _days_until(date_str: str) -> Optional[int]:
    if not date_str:
        return None

    try:
        due = datetime.fromisoformat(date_str)
    except ValueError:
        try:
            due = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
        except ValueError:
            return None

    today = datetime.utcnow().date()
    return (due.date() - today).days


def fetch_tasks():
    tasks = []

    for row in data["results"]:
        title = row["properties"]["Nom"]["title"][0]["plain_text"]

        prio = (
            row["properties"]["Priorité"]["select"]["name"]
            if row["properties"]["Priorité"]["select"]
            else "Moyenne"
        )

        due_date = _extract_due_date(row["properties"])
        days_remaining = _days_until(due_date) if due_date else None

        tasks.append(
            Task(
                title=title,
                prio=prio,
                due_date=due_date,
                days_remaining=days_remaining,
            )
        )

    return tasks
