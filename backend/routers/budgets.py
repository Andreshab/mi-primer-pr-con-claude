import datetime as dt

from fastapi import APIRouter, HTTPException, Query
from models.budget import BudgetUpsert
from services import budgets as svc

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _current_month() -> str:
    t = dt.date.today()
    return f"{t.year}-{t.month:02d}"


@router.get("/")
def list_budgets(month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$")):
    month = month or _current_month()
    return [i for i in svc.list_budget_status(month) if i["budget_amount"] is not None]


@router.put("/{category_id}")
def upsert_budget(category_id: str, payload: BudgetUpsert):
    try:
        svc.upsert_budget(category_id, float(payload.amount))
    except LookupError:
        raise HTTPException(status_code=404, detail="Category not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Only expense categories can have a budget")
    return svc.get_budget_status(category_id, _current_month())


@router.delete("/{category_id}", status_code=204)
def delete_budget(category_id: str):
    svc.delete_budget(category_id)
