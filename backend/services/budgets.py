from database import get_client


def _month_range(month: str) -> tuple[str, str]:
    """month: YYYY-MM -> (start, end) ISO dates covering that month."""
    year, m = month.split("-")
    start = f"{month}-01"
    next_m = int(m) % 12 + 1
    next_y = int(year) + (1 if int(m) == 12 else 0)
    end = f"{next_y}-{next_m:02d}-01"
    return start, end


def list_budget_status(month: str) -> list[dict]:
    """Every expense category with its budget (if any) and month consumption."""
    db = get_client()
    cats = (
        db.table("categories")
        .select("id, name, icon, color")
        .eq("type", "expense")
        .order("name")
        .execute()
        .data
    )
    budgets = {
        b["category_id"]: float(b["amount"])
        for b in db.table("budgets").select("category_id, amount").execute().data
    }

    start, end = _month_range(month)
    rows = (
        db.table("transactions")
        .select("category_id, amount")
        .eq("type", "expense")
        .gte("date", start)
        .lt("date", end)
        .execute()
        .data
    )
    spent: dict[str, float] = {}
    for r in rows:
        spent[r["category_id"]] = spent.get(r["category_id"], 0.0) + float(r["amount"])

    items = []
    for c in cats:
        amount = budgets.get(c["id"])
        s = spent.get(c["id"], 0.0)
        items.append({
            "category_id": c["id"],
            "category_name": c["name"],
            "category_icon": c["icon"],
            "category_color": c["color"],
            "budget_amount": amount,
            "spent": s,
            "remaining": round(amount - s, 2) if amount is not None else None,
            "pct": round(s / amount * 100, 1) if amount else None,
        })
    return items


def get_budget_status(category_id: str, month: str) -> dict | None:
    return next(
        (i for i in list_budget_status(month) if i["category_id"] == category_id), None
    )


def budget_summary(month: str) -> dict:
    """Aggregate for the dashboard card: only categories that have a budget."""
    budgeted = [i for i in list_budget_status(month) if i["budget_amount"] is not None]
    total_budget = sum(i["budget_amount"] for i in budgeted)
    total_spent = sum(i["spent"] for i in budgeted)
    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "pct": round(total_spent / total_budget * 100, 1) if total_budget else 0,
        "over": [i for i in budgeted if i["pct"] > 100],
    }


def upsert_budget(category_id: str, amount: float) -> dict:
    """Create or replace the budget for an expense category.

    Raises LookupError if the category doesn't exist, ValueError if it's
    an income category (business rule 1 of stage 5).
    """
    db = get_client()
    cat = db.table("categories").select("id, type").eq("id", category_id).execute().data
    if not cat:
        raise LookupError("Category not found")
    if cat[0]["type"] != "expense":
        raise ValueError("Only expense categories can have a budget")
    result = (
        db.table("budgets")
        .upsert({"category_id": category_id, "amount": amount}, on_conflict="category_id")
        .execute()
    )
    return result.data[0]


def delete_budget(category_id: str) -> None:
    db = get_client()
    db.table("budgets").delete().eq("category_id", category_id).execute()
