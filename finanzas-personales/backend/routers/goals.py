from fastapi import APIRouter, HTTPException, Query
from models.goal import GoalCreate, GoalUpdate, ContributionCreate
from services import goals as svc

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/")
def list_goals(
    status: str | None = Query(None, pattern="^(active|completed|cancelled)$")
):
    return svc.list_goals(status=status)


@router.post("/", status_code=201)
def create_goal(payload: GoalCreate):
    return svc.create_goal(payload)


@router.put("/{goal_id}")
def update_goal(goal_id: str, payload: GoalUpdate):
    result = svc.update_goal(goal_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: str):
    if not svc.delete_goal(goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")


@router.post("/{goal_id}/contribute", status_code=201)
def add_contribution(goal_id: str, payload: ContributionCreate):
    goal = svc.get_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal["status"] != "active":
        raise HTTPException(status_code=409, detail="Cannot contribute to a non-active goal")
    return svc.add_contribution(goal_id, payload)


@router.get("/{goal_id}/history")
def get_contributions(goal_id: str):
    goal = svc.get_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return svc.get_contributions(goal_id)
