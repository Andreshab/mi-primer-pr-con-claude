from database import get_client
from models.goal import GoalCreate, GoalUpdate, ContributionCreate


def list_goals(status: str | None = None) -> list[dict]:
    db = get_client()
    q = db.table("savings_goals_with_progress").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data


def get_goal(goal_id: str) -> dict | None:
    db = get_client()
    result = db.table("savings_goals_with_progress").select("*").eq("id", goal_id).execute()
    return result.data[0] if result.data else None


def create_goal(payload: GoalCreate) -> dict:
    db = get_client()
    data = payload.model_dump()
    data["target_amount"] = float(data["target_amount"])
    if data["deadline"]:
        data["deadline"] = data["deadline"].isoformat()
    result = db.table("savings_goals").insert(data).execute()
    goal_id = result.data[0]["id"]
    return get_goal(goal_id)


def update_goal(goal_id: str, payload: GoalUpdate) -> dict | None:
    db = get_client()
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "target_amount" in data:
        data["target_amount"] = float(data["target_amount"])
    if "deadline" in data:
        data["deadline"] = data["deadline"].isoformat()
    if not data:
        return get_goal(goal_id)
    db.table("savings_goals").update(data).eq("id", goal_id).execute()
    return get_goal(goal_id)


def add_contribution(goal_id: str, payload: ContributionCreate) -> dict:
    db = get_client()
    data = payload.model_dump()
    data["goal_id"] = goal_id
    data["amount"] = float(data["amount"])
    data["date"] = data["date"].isoformat()
    db.table("goal_contributions").insert(data).execute()

    # Auto-complete goal if target reached
    goal = get_goal(goal_id)
    if goal and float(goal["current_amount"]) >= float(goal["target_amount"]):
        db.table("savings_goals").update({"status": "completed"}).eq("id", goal_id).execute()
        goal = get_goal(goal_id)
    return goal


def get_contributions(goal_id: str) -> list[dict]:
    db = get_client()
    return (
        db.table("goal_contributions")
        .select("*")
        .eq("goal_id", goal_id)
        .order("date", desc=True)
        .execute()
        .data
    )
