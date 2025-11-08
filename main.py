
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from modules.get_data.event_queries import fetch_min_events
from modules.get_data.db_crm import get_db
from modules.get_data.notion_service import fetch_tasks
from modules.get_data.objectifs import objectives_with_priority
from modules.ai_work.ai_service import generate_next_action
from pathlib import Path
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

# Static & templates
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/")
def home():
    return {"message": "OK"}


@app.get("/tasks")
def read_tasks():
    return fetch_tasks()

@app.get("/next_action")
def next_action():
    tasks = fetch_tasks()
    tasks_dict = [
        {
            "title": t.title,
            "prio": t.prio,
            "due_date": t.due_date,
            "days_remaining": t.days_remaining,
        }
        for t in tasks
    ]
    template = (BASE_DIR / "prompts" / "next_action.txt").read_text(encoding="utf-8")
    # -> generate_next_action DOIT retourner un dict {"action": "...", "raison": "..."}
    return generate_next_action(tasks_dict, template)

@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard(request: Request):
    tasks = fetch_tasks()
    tasks_dict = [
        {
            "title": t.title,
            "prio": t.prio,
            "due_date": t.due_date,
            "days_remaining": t.days_remaining,
        }
        for t in tasks
    ]
    objectives = objectives_with_priority()

    template_text = (BASE_DIR / "prompts" / "next_action.txt").read_text(encoding="utf-8")
    result = generate_next_action(tasks_dict, template_text)  # ex: {"actions":[{...}, ...]}
    print(result)

    actions = result.get("taches", [])

    # Top priorité = première action
    top = actions[0] if actions else {
        "action": "—",
        "raison": "—",
        "impact": "—",
        "categorie": "—"
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "tasks": tasks_dict,
            "objectives": [obj.dict() for obj in objectives],
            "top": top,
            "actions": actions
        }
    )


@app.get("/events-min")
async def events_min(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await fetch_min_events(db, limit)
