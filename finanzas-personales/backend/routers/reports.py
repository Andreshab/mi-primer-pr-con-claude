from fastapi import APIRouter, Query
from services import reports as svc
from datetime import date

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
def monthly_summary(
    month: str = Query(default=None, pattern=r"^\d{4}-\d{2}$")
):
    if not month:
        today = date.today()
        month = f"{today.year}-{today.month:02d}"
    return svc.monthly_summary(month)


@router.get("/by-category")
def by_category(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    type: str | None = Query(default=None, pattern="^(income|expense)$"),
):
    return svc.by_category(month=month, type_filter=type)


@router.get("/trend")
def monthly_trend(months: int = Query(default=6, ge=2, le=24)):
    return svc.monthly_trend(months=months)


@router.get("/goals")
def goals_progress():
    return svc.goals_progress()
