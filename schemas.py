from pydantic import BaseModel
from datetime import date

class CompetitionCreate(BaseModel):
    name: str
    competition_type: str
    date: date
    organizer: str

class Competition(CompetitionCreate):
    id: int

    class Config:
        from_attributes = True