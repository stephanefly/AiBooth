from openai import OpenAI
import json
from modules.get_data.objectifs import criteria_to_prompt_block
from dotenv import load_dotenv
import os

from modules.get_data.profile_service import profile_to_prompt_block

# Charge .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_next_action(tasks: list[dict], prompt_template: str) -> dict:
    criteria_block = criteria_to_prompt_block()
    profile_block  = profile_to_prompt_block()

    prompt = (
        prompt_template
        .replace("{{TASKS}}", str(tasks))
        .replace("{{CRITERIA}}", criteria_block)
        .replace("{{PROFILE}}", profile_block)
    )

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Réponds UNIQUEMENT en JSON valide."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
    )
    return json.loads(resp.choices[0].message.content)  # <-- retourne un dict