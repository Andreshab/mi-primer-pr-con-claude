from __future__ import annotations
from decimal import Decimal
import datetime as dt
import json

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.category import CategoryCreate
from models.goal import ContributionCreate, GoalCreate
from models.settings import SettingsUpdate
from models.transaction import TransactionCreate
from services import budgets as budget_svc
from services import categories as cat_svc
from services import goals as goal_svc
from services import reports as rep_svc
from services import settings as settings_svc
from services import transactions as tx_svc

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def _ctx(request: Request, **kwargs) -> dict:
    return {
        "request": request,
        "settings": settings_svc.get_settings(),
        "all_categories": cat_svc.list_categories(),
        **kwargs,
    }


def _current_month() -> str:
    t = dt.date.today()
    return f"{t.year}-{t.month:02d}"


# ─── Full pages ───────────────────────────────────────────────────────────────

def _dashboard_ctx(request: Request) -> dict:
    month = _current_month()
    return _ctx(
        request,
        summary=rep_svc.monthly_summary(month),
        recent=tx_svc.list_transactions(month=month, limit=5)["data"],
        goals=rep_svc.goals_progress(),
        budget=budget_svc.budget_summary(month),
        month=month,
    )


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", _dashboard_ctx(request))


@router.get("/transactions", response_class=HTMLResponse)
def transactions_page(request: Request, month: str | None = None):
    month = month or _current_month()
    data = tx_svc.list_transactions(month=month)["data"]
    categories = cat_svc.list_categories()
    return templates.TemplateResponse(
        "transactions.html",
        _ctx(request, transactions=data, categories=categories, month=month),
    )


@router.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request):
    cats = cat_svc.list_categories()
    return templates.TemplateResponse("categories.html", _ctx(request, categories=cats))


@router.get("/goals", response_class=HTMLResponse)
def goals_page(request: Request):
    goals = goal_svc.list_goals()
    return templates.TemplateResponse("goals.html", _ctx(request, goals=goals))


@router.get("/budgets", response_class=HTMLResponse)
def budgets_page(request: Request, month: str | None = None):
    month = month or _current_month()
    items = budget_svc.list_budget_status(month)
    return templates.TemplateResponse(
        "budgets.html", _ctx(request, budget_items=items, month=month)
    )


@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, month: str | None = None):
    month = month or _current_month()
    by_cat = rep_svc.by_category(month=month, type_filter="expense")
    trend = rep_svc.monthly_trend(months=6)
    summary = rep_svc.monthly_summary(month)
    pie_data = json.dumps({
        "labels": [x["category_name"] for x in by_cat],
        "values": [x["total"] for x in by_cat],
        "colors": [x["category_color"] for x in by_cat],
    })
    trend_data = json.dumps({
        "months": [x["month"] for x in trend],
        "income": [x["income"] for x in trend],
        "expense": [x["expense"] for x in trend],
    })
    return templates.TemplateResponse(
        "reports.html",
        _ctx(request, month=month, summary=summary, pie_data=pie_data, trend_data=trend_data),
    )


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", _ctx(request))


# ─── HTMX partials ───────────────────────────────────────────────────────────

@router.get("/partials/dashboard", response_class=HTMLResponse)
def partial_dashboard(request: Request):
    return templates.TemplateResponse(
        "partials/dashboard_content.html", _dashboard_ctx(request)
    )


@router.get("/partials/budgets", response_class=HTMLResponse)
def partial_budget_list(request: Request, month: str | None = None):
    month = month or _current_month()
    items = budget_svc.list_budget_status(month)
    return templates.TemplateResponse(
        "partials/budget_rows.html", _ctx(request, budget_items=items, month=month)
    )


@router.put("/partials/budgets/{category_id}", response_class=HTMLResponse)
async def partial_upsert_budget(
    request: Request,
    category_id: str,
    amount: float = Form(...),
    month: str = Form(None),
):
    month = month or _current_month()
    if amount <= 0:
        return HTMLResponse("El monto debe ser mayor a 0", status_code=400)
    try:
        budget_svc.upsert_budget(category_id, amount)
    except (LookupError, ValueError) as e:
        return HTMLResponse(str(e), status_code=400)
    item = budget_svc.get_budget_status(category_id, month)
    return templates.TemplateResponse(
        "partials/budget_row.html", _ctx(request, item=item, month=month)
    )


@router.delete("/partials/budgets/{category_id}", response_class=HTMLResponse)
def partial_delete_budget(request: Request, category_id: str, month: str | None = None):
    month = month or _current_month()
    budget_svc.delete_budget(category_id)
    item = budget_svc.get_budget_status(category_id, month)
    return templates.TemplateResponse(
        "partials/budget_row.html", _ctx(request, item=item, month=month)
    )


@router.get("/partials/transactions", response_class=HTMLResponse)
def partial_tx_list(
    request: Request,
    month: str | None = None,
    type: str | None = None,
    category_id: str | None = None,
):
    month = month or _current_month()
    data = tx_svc.list_transactions(month=month, type_filter=type, category_id=category_id)["data"]
    return templates.TemplateResponse(
        "partials/transaction_rows.html", _ctx(request, transactions=data)
    )


@router.post("/partials/transactions", response_class=HTMLResponse)
async def partial_create_tx(
    request: Request,
    amount: float = Form(...),
    type: str = Form(...),
    category_id: str = Form(...),
    description: str = Form(""),
    tx_date: str = Form(...),
):
    payload = TransactionCreate(
        amount=Decimal(str(amount)),
        type=type,
        category_id=category_id,
        description=description or None,
        date=dt.date.fromisoformat(tx_date),
    )
    tx = tx_svc.create_transaction(payload)
    tx = tx_svc.get_transaction(tx["id"])
    response = templates.TemplateResponse("partials/transaction_row.html", _ctx(request, tx=tx))
    response.headers["HX-Trigger"] = "transactionCreated"
    return response


@router.delete("/partials/transactions/{tx_id}", response_class=HTMLResponse)
def partial_delete_tx(tx_id: str):
    tx_svc.delete_transaction(tx_id)
    return HTMLResponse("")


@router.post("/partials/categories", response_class=HTMLResponse)
async def partial_create_category(
    request: Request,
    name: str = Form(...),
    icon: str = Form("📦"),
    type: str = Form(...),
    color: str = Form("#6366f1"),
):
    cat = cat_svc.create_category(CategoryCreate(name=name, icon=icon, type=type, color=color))
    return templates.TemplateResponse("partials/category_card.html", _ctx(request, cat=cat))


@router.delete("/partials/categories/{cat_id}", response_class=HTMLResponse)
def partial_delete_category(cat_id: str):
    ok = cat_svc.delete_category(cat_id)
    if not ok:
        return HTMLResponse(
            '<p id="cat-error" class="text-rose-600 text-sm col-span-full">'
            "No se puede eliminar: tiene transacciones asociadas.</p>",
            status_code=409,
        )
    return HTMLResponse("")


@router.post("/partials/goals", response_class=HTMLResponse)
async def partial_create_goal(
    request: Request,
    name: str = Form(...),
    target_amount: float = Form(...),
    goal_date: str = Form(""),
):
    payload = GoalCreate(
        name=name,
        target_amount=Decimal(str(target_amount)),
        deadline=dt.date.fromisoformat(goal_date) if goal_date else None,
    )
    goal = goal_svc.create_goal(payload)
    return templates.TemplateResponse("partials/goal_card.html", _ctx(request, goal=goal))


@router.post("/partials/goals/{goal_id}/contribute", response_class=HTMLResponse)
async def partial_contribute(
    request: Request,
    goal_id: str,
    amount: float = Form(...),
    contrib_date: str = Form(...),
    note: str = Form(""),
):
    payload = ContributionCreate(
        amount=Decimal(str(amount)),
        date=dt.date.fromisoformat(contrib_date),
        note=note or None,
    )
    goal = goal_svc.add_contribution(goal_id, payload)
    return templates.TemplateResponse("partials/goal_card.html", _ctx(request, goal=goal))


@router.post("/partials/settings", response_class=HTMLResponse)
async def partial_update_settings(
    currency: str = Form(...),
    currency_symbol: str = Form(...),
    currency_locale: str = Form(...),
):
    settings_svc.update_settings(
        SettingsUpdate(currency=currency, currency_symbol=currency_symbol, currency_locale=currency_locale)
    )
    return HTMLResponse('<p class="text-green-600 font-medium text-sm">✓ Configuración guardada</p>')
