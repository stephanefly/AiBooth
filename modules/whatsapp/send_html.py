import os
import json
import base64
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = Path(__file__).resolve().parent  # dossier du fichier actuel

# Charge .env
load_dotenv()
DESTINATION = os.getenv("DESTINATION")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


def build_dashboard_context(
    objectives_dict,
    actions,
    top_by_domaine,
    message_a_envoyer,
    request=None,
):
    """
    Construit le contexte utilisé à la fois pour :
    - le TemplateResponse (UI)
    - la génération du HTML statique (WhatsApp)
    """

    top = (actions or [{
        "action": "—", "impact": "—", "categorie": "—", "domaine": "—"
    }])[0]

    ctx = {
        "objectives": objectives_dict,
        "top": top,
        "top_by_domaine": top_by_domaine,
        "message_a_envoyer": message_a_envoyer,
    }

    # Pour TemplateResponse il faut 'request'
    if request is not None:
        ctx["request"] = request

    return ctx


def create_html(ctx):
    """
    Rend le template `dashboard.html` avec le contexte `ctx`
    et l'exporte dans un fichier HTML.
    """

    html_content = templates.get_template("dashboard.html").render(ctx)

    # Exemple de chemin : modules/whatsapp/dashboard/dashboard_today.html
    export_dir = BASE_DIR / "dashboard"
    export_dir.mkdir(parents=True, exist_ok=True)

    export_path = export_dir / "dashboard_today.html"
    export_path.write_text(html_content, encoding="utf-8")

    return export_path
