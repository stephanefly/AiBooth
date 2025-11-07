from pydantic import BaseModel

class Task(BaseModel):
    title: str
    prio: str
