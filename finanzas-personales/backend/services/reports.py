from database import get_client


def monthly_summary(month: str) -> dict:
    """month: YYYY-MM. Returns total income, expense, balance."""
    db = get_client()
    year, m = month.split("-")
    start = f"{month}-01"
    next_m = int(m) % 12 + 1
    next_y = int(year) + (1 if int(m) == 12 else 0)
    end = f"{next_y}-{next_m:02d}-01"

    rows = (
        db.table("transactions")
        .select("type, amount")
        .gte("date", start)
        .lt("date", end)
        .execute()
        .data
    )

    income = sum(float(r["amount"]) for r in rows if r["type"] == "income")
    expense = sum(float(r["amount"]) for r in rows if r["type"] == "expense")
    return {
        "month": month,
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "transaction_count": len(rows),
    }


def by_category(month: str | None = None, type_filter: str | None = None) -> list[dict]:
    """Expenses (or incomes) grouped by category for a given month."""
    db = get_client()
    q = (
        db.table("transactions")
        .select("amount, type, categories(id, name, icon, color)")
    )

    if month:
        year, m = month.split("-")
        start = f"{month}-01"
        next_m = int(m) % 12 + 1
        next_y = int(year) + (1 if int(m) == 12 else 0)
        end = f"{next_y}-{next_m:02d}-01"
        q = q.gte("date", start).lt("date", end)

    if type_filter:
        q = q.eq("type", type_filter)

    rows = q.execute().data

    # Group by category in Python (Supabase REST doesn't support GROUP BY)
    totals: dict[str, dict] = {}
    for r in rows:
        cat = r["categories"]
        cat_id = cat["id"]
        if cat_id not in totals:
            totals[cat_id] = {
                "category_id": cat_id,
                "category_name": cat["name"],
                "category_icon": cat["icon"],
                "category_color": cat["color"],
                "total": 0.0,
                "count": 0,
            }
        totals[cat_id]["total"] += float(r["amount"])
        totals[cat_id]["count"] += 1

    result = sorted(totals.values(), key=lambda x: x["total"], reverse=True)

    # Add percentage
    grand_total = sum(x["total"] for x in result)
    for item in result:
        item["pct"] = round(item["total"] / grand_total * 100, 1) if grand_total else 0

    return result


def monthly_trend(months: int = 6) -> list[dict]:
    """Returns income/expense totals for the last N months."""
    from datetime import date, timedelta
    import calendar

    db = get_client()
    today = date.today()
    result = []

    for i in range(months - 1, -1, -1):
        # Go back i months from current
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        label = f"{year}-{month:02d}"
        start = f"{label}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_dt = date(year, month, last_day) + timedelta(days=1)
        end = end_dt.isoformat()

        rows = (
            db.table("transactions")
            .select("type, amount")
            .gte("date", start)
            .lt("date", end)
            .execute()
            .data
        )

        income = sum(float(r["amount"]) for r in rows if r["type"] == "income")
        expense = sum(float(r["amount"]) for r in rows if r["type"] == "expense")
        result.append({
            "month": label,
            "income": income,
            "expense": expense,
            "balance": income - expense,
        })

    return result


def goals_progress() -> list[dict]:
    db = get_client()
    return (
        db.table("savings_goals_with_progress")
        .select("*")
        .eq("status", "active")
        .order("deadline")
        .execute()
        .data
    )
