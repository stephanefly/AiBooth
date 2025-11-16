import os
import json
import base64
from pathlib import Path
import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
import json
import http.client

from modules.whatsapp.admin_whatsapp import days_until_expiration

router = APIRouter()
templates = Jinja2Templates(directory="templates")

BASE_DIR = Path(__file__).resolve().parent  # dossier du fichier actuel

# Charge .env
load_dotenv()
DESTINATION = os.getenv("DESTINATION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
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
        "token_days_left": days_until_expiration(),  # <-- ajouté ici
    }

    # Pour TemplateResponse il faut 'request'
    if request is not None:
        ctx["request"] = request

    return ctx


def create_html(ctx):
    """
    Rend le template `dashboard.html` avec le contexte `ctx`
    et l'exporte dans un fichier HTML dans:
    modules/whatsapp/dashboard/dashboard_today.html
    sans aucun chemin en dur.
    """

    # 1) Rendu du template
    html_content = templates.get_template("dashboard.html").render(ctx)

    # 2) Dossier dynamique : modules/whatsapp/dashboard/
    export_dir = BASE_DIR / "modules" / "whatsapp" / "dashboard"
    export_dir.mkdir(parents=True, exist_ok=True)

    # 3) Fichier final
    export_path = export_dir / "dashboard_today.html"
    export_path.write_text(html_content, encoding="utf-8")

    return export_path



def send_whatsapp_text():
    conn = http.client.HTTPSConnection("graph.facebook.com")

    # dashboard = "http://localhost:8000/dashboard"

    payload = {
        "messaging_product": "whatsapp",
        "to": f"+{DESTINATION}",
        "type": "text",
        "text": {"body": "http://notion.myselfiebooth-paris.fr/dashboard" }
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    conn.request(
        "POST",
        f"/v20.0/{PHONE_NUMBER_ID}/messages",
        body=json.dumps(payload),
        headers=headers
    )

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    print(res.status, res.reason)
    print(data)
    return data

