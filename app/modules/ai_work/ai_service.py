from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.modules.get_data.objectifs import criteria_to_prompt_block
from app.modules.get_data.profile_service import profile_to_prompt_block

# Charge .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)

def _sanitize_response(payload: str):
    # payload est déjà du JSON valide grâce à response_format={"type": "json_object"}
    data = json.loads(payload)

    # Récupération des tâches (taches ou actions)
    raw_tasks = data.get("taches") or data.get("actions") or []
    raw_tasks = raw_tasks[:20]  # on limite à 20

    cleaned = []
    for t in raw_tasks:
        cleaned.append({
            "action": str(t.get("action", "")).strip(),
            "raison": str(t.get("raison", "")).strip(),
            "impact": str(t.get("impact", "")).strip(),
            "categorie": str(t.get("categorie", "")).strip(),
            "domaine": str(t.get("domaine", "")).strip(),
            "color_domaine": str(t.get("color_domaine", "")).strip(),
            "url": str(t.get("url", "")).strip(),
        })

    # Nouveau : on récupère aussi le message prêt à envoyer
    message = str(data.get("message", "")).strip()

    return {
        "taches": cleaned,
        "message": message,
    }



def generate_next_action(tasks: list[dict], crm_dict, prompt_template: str) -> dict[str, Any]:
    criteria_block = criteria_to_prompt_block()
    profile_block = profile_to_prompt_block()

    prompt = prompt_template
    prompt = prompt.replace("{{TASKS}}", json.dumps(tasks, ensure_ascii=False))
    prompt = prompt.replace("{{CRM_EVENTS}}", json.dumps(crm_dict, ensure_ascii=False))
    prompt = prompt.replace("{{PROFILE}}", json.dumps(profile_block or {}, ensure_ascii=False))
    prompt = prompt.replace("{{CRITERIA}}", json.dumps(criteria_block or [], ensure_ascii=False))

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant qui propose des prochaines actions prioritaires. "
                    "Réponds UNIQUEMENT en JSON valide de la forme : "
                    "{\"taches\": [...], \"message\": \"...\"}."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    raw_content = resp.choices[0].message.content
    print(raw_content)
    return _sanitize_response(raw_content)
