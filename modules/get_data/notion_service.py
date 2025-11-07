from notion_client import Client as Notion
from models import Task
from dotenv import load_dotenv
import os

# Charge .env
load_dotenv()


NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Notion(auth=NOTION_TOKEN)


NOTION_TASK_FILTER = {
    "and": [
        {"property": "Domaine", "select": {"does_not_equal": "RESERVATION"}},
        {"property": "Domaine", "select": {"does_not_equal": "PERSO"}},
        {"property": "État", "status": {"does_not_equal": "Done"}}
    ]
}

data = notion.databases.query(
    database_id=DATABASE_ID,
    filter=NOTION_TASK_FILTER,
    page_size=100
)


def fetch_tasks():

    tasks = []
    for row in data["results"]:
        title = row["properties"]["Nom"]["title"][0]["plain_text"]

        prio = (
            row["properties"]["Priorité"]["select"]["name"]
            if row["properties"]["Priorité"]["select"]
            else "Moyenne"
        )

        tasks.append(Task(title=title, prio=prio))

    return tasks
