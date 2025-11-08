from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData

metadata = MetaData()

Client = Table(
    "app_client",  # <-- CORRECTION (c'était "app_event")
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nom", String(100)),
    Column("mail", String(100)),
    Column("numero_telephone", String(15)),
    Column("how_find", String(255)),
    Column("raison_sociale", Boolean),
    Column("nb_relance_devis", Integer),
    Column("nb_relance_avis", Integer),
    Column("autorisation_mail", Boolean),
    Column("code_espace_client", String(6)),
    Column("mail_sondage", Boolean),
)

class Task(BaseModel):
    title: str
    prio: str
    due_date: Optional[str] = None
    days_remaining: Optional[int] = None


class Objective(BaseModel):
    domaine: str
    resume: str
    objectif: str
    priorite: str
    poids: int
