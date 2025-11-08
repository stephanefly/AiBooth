from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from modules.get_data.objectifs import criteria_to_prompt_block
from modules.get_data.profile_service import profile_to_prompt_block

# Charge .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)


def _sanitize_response(payload: str) -> dict[str, Any]:
    """Transforme la réponse brute du modèle en dictionnaire Python."""

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        # Tentative de récupération du premier bloc JSON valide.
        start = payload.find("{")
        end = payload.rfind("}") + 1
        if start == -1 or end <= start:
            raise
        data = json.loads(payload[start:end])

    if not isinstance(data, dict):
        # Le modèle doit renvoyer un objet JSON. Tout autre type est rejeté.
        return {"taches": []}

    # Harmonise les différentes clés possibles renvoyées par le modèle.
    if "actions" in data and "taches" not in data:
        data["taches"] = data.pop("actions")

    def _clean_field(value: Any) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            value = str(value)
        return value.strip()

    taches = []
    for item in data.get("taches", [])[:6]:
        if not isinstance(item, dict):
            continue
        cleaned = {
            "action": _clean_field(item.get("action", "")),
            "raison": _clean_field(item.get("raison", "")),
            "impact": _clean_field(item.get("impact", "")),
            "categorie": _clean_field(item.get("categorie", "")),
        }

        if not any(cleaned.values()):
            # Ignore les entrées totalement vides pour ne pas polluer l'UI.
            continue

        taches.append(cleaned)

    data["taches"] = taches
    return data


def generate_next_action(tasks: list[dict], prompt_template: str) -> dict[str, Any]:
    criteria_block = criteria_to_prompt_block()
    profile_block = profile_to_prompt_block()

    tasks_payload = json.dumps(tasks, ensure_ascii=False, indent=2)

    prompt = (
        prompt_template
        .replace("{{TASKS}}", tasks_payload)
        .replace("{{CRITERIA}}", criteria_block)
        .replace("{{PROFILE}}", profile_block)
    )

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Réponds UNIQUEMENT en JSON valide."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    raw_content = resp.choices[0].message.content
    return _sanitize_response(raw_content)
