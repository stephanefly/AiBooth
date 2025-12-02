from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from modules.get_data.event_queries import fetch_min_events
from modules.get_data.db_crm import get_db
from modules.get_data.notion_service import fetch_tasks
from modules.get_data.objectifs import objectives_with_priority
from modules.ai_work.ai_service import generate_next_action
from modules.whatsapp.send_html import create_html, build_dashboard_context, send_whatsapp_text

app = FastAPI()

# Static & templates
BASE_DIR = Path(__file__).parent
app.mount("static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/")
def home():
    return {"message": "OK"}

@app.get("/tasks")
def read_tasks():
    return fetch_tasks()

@app.get("/events_min")
async def events_min(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await fetch_min_events(db, limit)


async def get_dashboard_context(request: Request, db: AsyncSession):
    """
    Construit le contexte complet du dashboard :
    - tasks (Notion)
    - objectives (CRM)
    - events (CRM)
    - actions (LLM)
    - top_by_domaine
    - message_a_envoyer
    """

    # 1) Notion → Tasks
    tasks = fetch_tasks()

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
    except Exception:
        crm_dict = []

    # 4) Prompt
    template_text = (BASE_DIR / "modules" / "ai_work" / "prompts" / "next_action.txt").read_text(
        encoding="utf-8"
    )

    # 5) Appel LLM
    result = generate_next_action(tasks, crm_dict, template_text) or {}

    actions = result.get("taches", []) or []
    message_a_envoyer = result.get("message", "") or ""

    # 6) Top 3 par domaine
    groups: dict[str, list[dict]] = {}
    for a in actions:
        dom = a.get("domaine", "Autre")
        groups.setdefault(dom, []).append(a)

    top_by_domaine = {dom: items[:3] for dom, items in groups.items()}

    # 7) Contexte unique (utilise la fonction utilitaire)
    ctx = build_dashboard_context(
        objectives_dict=objectives_dict,
        actions=actions,
        top_by_domaine=top_by_domaine,
        message_a_envoyer=message_a_envoyer,
        request=request,
    )

    return ctx

@app.get("/ui", response_class=HTMLResponse)
async def ui_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # Construire le contexte une seule fois
    ctx = await get_dashboard_context(request, db)

    # Générer le HTML pour WhatsApp / export
    create_html(ctx)

    # Retourner la page UI
    return templates.TemplateResponse("dashboard.html", ctx)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    dashboard_path = (
        BASE_DIR
        / "modules"
        / "whatsapp"
        / "dashboard"
        / "dashboard_today.html"
    )

    with open(dashboard_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.get("/whatsapp/send-text")
async def whatsapp_send_text():

    data = send_whatsapp_text()
    return JSONResponse({"api_response": data})
