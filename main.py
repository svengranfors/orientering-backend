from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import supabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Orienteringsarrangören API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/competitions")
@app.post("/competitions")
def create_competition(competition: dict):
    # 1. Skapa tävlingen
    result = supabase.table("competitions").insert(competition).execute()
    new_competition = result.data[0]
    competition_id = new_competition["id"]
    competition_type = new_competition["competition_type"]

    # 2. Hämta alla process_templates för tävlingstypen
    process_templates = supabase.table("process_templates")\
        .select("*")\
        .eq("competition_type", competition_type)\
        .order("sort_order")\
        .execute().data

    # 3. Skapa competition_processes och activities
    for process_template in process_templates:
        # Skapa competition_process
        competition_process = supabase.table("competition_processes").insert({
            "competition_id": competition_id,
            "process_template_id": process_template["id"],
            "status": "not_started",
            "progress": 0
        }).execute().data[0]

        # 4. Hämta activity_templates för processen
        activity_templates = supabase.table("activity_templates")\
            .select("*")\
            .eq("process_template_id", process_template["id"])\
            .order("sort_order")\
            .execute().data

        # 5. Skapa activities
        for activity_template in activity_templates:
            due_date = None
            if activity_template["default_due_offset_days"] and competition.get("date"):
                from datetime import datetime, timedelta
                competition_date = datetime.strptime(competition["date"], "%Y-%m-%d")
                due_date = (competition_date - timedelta(days=activity_template["default_due_offset_days"])).strftime("%Y-%m-%d")

            supabase.table("activities").insert({
                "competition_process_id": competition_process["id"],
                "activity_template_id": activity_template["id"],
                "assignment_id": None,
                "status": "not_started",
                "priority": "normal",
                "due_date": due_date
            }).execute()

    return new_competition

@app.get("/competitions")
def get_competitions():
    result = supabase.table("competitions").select("*").execute()
    return result.data

@app.post("/roles")
def create_role(role: dict):
    result = supabase.table("roles").insert(role).execute()
    return result.data

@app.get("/roles")
def get_roles():
    result = supabase.table("roles").select("*").execute()
    return result.data

@app.post("/assignments")
def create_assignment(assignment: dict):
    result = supabase.table("assignments").insert(assignment).execute()
    return result.data

@app.get("/competitions/{competition_id}/assignments")
def get_assignments(competition_id: int):
    result = supabase.table("assignments")\
        .select("*, roles(name, description)")\
        .eq("competition_id", competition_id)\
        .execute()
    return result.data

@app.get("/competitions/{competition_id}/processes")
def get_processes(competition_id: int):
    result = supabase.table("competition_processes")\
        .select("*, process_templates(name, description, sort_order)")\
        .eq("competition_id", competition_id)\
        .order("process_templates(sort_order)")\
        .execute()
    return result.data

@app.get("/competition_processes/{process_id}/activities")
def get_activities(process_id: int):
    result = supabase.table("activities")\
        .select("*, activity_templates(name, description, role_id, sort_order, is_required)")\
        .eq("competition_process_id", process_id)\
        .order("activity_templates(sort_order)")\
        .execute()
    return result.data

@app.patch("/activities/{activity_id}")
def update_activity(activity_id: int, updates: dict):
    result = supabase.table("activities")\
        .update(updates)\
        .eq("id", activity_id)\
        .execute()
    return result.data

@app.post("/assignments")
def create_assignment(assignment: dict):
    # Skapa tillsättningen
    result = supabase.table("assignments").insert(assignment).execute()
    new_assignment = result.data[0]

    # Matcha aktiviteter med samma role_id och sätt assignment_id
    role_id = assignment["role_id"]
    competition_id = assignment["competition_id"]

    processes = supabase.table("competition_processes")\
        .select("id")\
        .eq("competition_id", competition_id)\
        .execute().data

    process_ids = [p["id"] for p in processes]

    for process_id in process_ids:
        activities = supabase.table("activities")\
            .select("id, activity_templates(role_id)")\
            .eq("competition_process_id", process_id)\
            .is_("assignment_id", "null")\
            .execute().data

        for activity in activities:
            if activity["activity_templates"]["role_id"] == role_id:
                supabase.table("activities")\
                    .update({
                        "assignment_id": new_assignment["id"],
                        "status": "assigned"
                    })\
                    .eq("id", activity["id"])\
                    .execute()

    return new_assignment

@app.post("/competition_processes/{process_id}/recalculate")
def recalculate_progress(process_id: int):
    activities = supabase.table("activities")\
        .select("status")\
        .eq("competition_process_id", process_id)\
        .execute().data

    total = len(activities)
    if total == 0:
        progress = 0
    else:
        done = sum(1 for a in activities if a["status"] == "done")
        progress = round((done / total) * 100)

    # Räkna ut processtatus
    statuses = [a["status"] for a in activities]
    if all(s == "done" for s in statuses):
        status = "done"
    elif any(s == "blocked" for s in statuses):
        status = "blocked"
    elif any(s in ["in_progress", "assigned"] for s in statuses):
        status = "in_progress"
    else:
        status = "not_started"

    result = supabase.table("competition_processes")\
        .update({"progress": progress, "status": status})\
        .eq("id", process_id)\
        .execute()

    return result.data