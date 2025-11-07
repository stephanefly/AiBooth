from pathlib import Path
import json
from textwrap import shorten

# Par défaut, fichier au root du projet. Sinon mets le chemin en .env et lis via os.getenv.
PROFILE_PATH = Path(__file__).resolve().parents[2] / "stephane_faure_ai_profile.json"

def profile_to_prompt_block() -> str:
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    owner = data.get("owner", {})
    bio = data.get("user_bio", {})
    prefs = data.get("preferences", {})
    msc = data.get("model_set_context", [])

    # Bio : lignes utiles, compactées
    bio_lines = []
    for k in sorted(bio.keys(), key=lambda x: int(x)):
        v = str(bio[k]).strip()
        if v:
            bio_lines.append(f"- {v}")

    # Préférences clés
    fmt = prefs.get("format")
    code_no_emoji = prefs.get("code", {}).get("no_emojis_in_code")
    emails_no_emoji = prefs.get("emails_pro", {}).get("no_emojis")

    # Model Set Context : on limite pour éviter un prompt trop long
    msc_lines = []
    for item in msc[:20]:
        # On coupe à ~160 chars pour rester dense
        msc_lines.append(f"- {shorten(item, width=160, placeholder='…')}")

    lines = []
    lines.append("=== Owner ===")
    lines.append(f"- Nom: {owner.get('display_name','')}")
    lines.append(f"- Timezone: {owner.get('timezone','')}")
    lines.append("")
    lines.append("=== Bio (synthèse) ===")
    lines.extend(bio_lines)
    lines.append("")
    lines.append("=== Préférences ===")
    if fmt: lines.append(f"- Format: {fmt}")
    lines.append(f"- Pas d’emojis dans le code: {bool(code_no_emoji)}")
    lines.append(f"- Pas d’emojis dans emails pro: {bool(emails_no_emoji)}")
    lines.append("")
    lines.append("=== Contexte métier (extraits) ===")
    lines.extend(msc_lines)

    return "\n".join(lines)
