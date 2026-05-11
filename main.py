from fastapi import FastAPI
from database import supabase

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Orienteringsarrangören API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/competitions")
def create_competition(competition: dict):
    result = supabase.table("competitions").insert(competition).execute()
    return result.data

@app.get("/competitions")
def get_competitions():
    result = supabase.table("competitions").select("*").execute()
    return result.data