import json

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


@app.get("/ui", response_class=HTMLResponse)
async def ui_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # 1) Notion → Tasks
    tasks = fetch_tasks()  # déjà des dicts: title, prio, dommaine, due_date, days_remaining

    # 2) Objectifs
    objectives = objectives_with_priority()
    objectives_dict = [obj.dict() for obj in objectives]

    # 3) CRM → Events (async)
    try:
        events = await fetch_min_events(db, limit=500)
        crm_dict = [
            {
                "nom": e.get("nom"),
                "date": e.get("date"),
                "product": e.get("product"),
                "status": e.get("status"),
                "option": e.get("option"),
                "sent": e.get("sent"),
                "directory_name": e.get("directory_name"),
            }
            for e in events
        ]
    except:
        crm_dict = []
    print(crm_dict)

    # 4) Prompt
    template_text = (BASE_DIR / "modules" / "ai_work" / "prompts" / "next_action.txt").read_text(encoding="utf-8")

    # 5) Appel LLM (sans if)
    result = generate_next_action(tasks, crm_dict, template_text)

    actions = (result or {}).get("taches", [])

    # Top 3 par domaine (groupement + slicing)
    groups = {}
    for a in actions:
        dom = a.get("domaine", "Autre")
        if dom not in groups:
            groups[dom] = []
        groups[dom].append(a)

    # 2) On garde uniquement les 3 premiers de chaque domaine
    top_by_domaine = {}
    for dom, items in groups.items():
        top_by_domaine[dom] = items[:3]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "objectives": objectives_dict,
            "top": (actions or [{
                "action": "—", "impact": "—", "categorie": "—", "domaine": "—"
            }])[0],
            "top_by_domaine": top_by_domaine,  # <-- ajoute ceci
        }
    )

@app.get("/events_min")
async def events_min(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await fetch_min_events(db, limit)
