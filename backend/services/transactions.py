import csv
import io
from datetime import date
from database import get_client
from models.transaction import TransactionCreate, TransactionUpdate
from services.categories import get_or_create_category


def list_transactions(
    month: str | None = None,
    category_id: str | None = None,
    type_filter: str | None = None,
    page: int = 1,
    limit: int = 50,
) -> dict:
    db = get_client()
    q = db.table("transactions").select(
        "*, categories(name, icon, color, type)"
    ).order("date", desc=True)

    if month:
        # month format: YYYY-MM
        start = f"{month}-01"
        year, m = month.split("-")
        next_m = int(m) % 12 + 1
        next_y = int(year) + (1 if int(m) == 12 else 0)
        end = f"{next_y}-{next_m:02d}-01"
        q = q.gte("date", start).lt("date", end)

    if category_id:
        q = q.eq("category_id", category_id)
    if type_filter:
        q = q.eq("type", type_filter)

    offset = (page - 1) * limit
    q = q.range(offset, offset + limit - 1)

    result = q.execute()
    return {"data": result.data, "page": page, "limit": limit}


def get_transaction(transaction_id: str) -> dict | None:
    db = get_client()
    result = (
        db.table("transactions")
        .select("*, categories(name, icon, color, type)")
        .eq("id", transaction_id)
        .execute()
    )
    return result.data[0] if result.data else None


def create_transaction(payload: TransactionCreate) -> dict:
    db = get_client()
    data = payload.model_dump()
    data["category_id"] = str(data["category_id"])
    data["amount"] = float(data["amount"])
    data["date"] = data["date"].isoformat()
    data["source"] = "manual"
    result = db.table("transactions").insert(data).execute()
    return result.data[0]


def update_transaction(transaction_id: str, payload: TransactionUpdate) -> dict | None:
    db = get_client()
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "category_id" in data:
        data["category_id"] = str(data["category_id"])
    if "amount" in data:
        data["amount"] = float(data["amount"])
    if "date" in data:
        data["date"] = data["date"].isoformat()
    if not data:
        return get_transaction(transaction_id)
    result = db.table("transactions").update(data).eq("id", transaction_id).execute()
    return result.data[0] if result.data else None


def delete_transaction(transaction_id: str) -> bool:
    db = get_client()
    db.table("transactions").delete().eq("id", transaction_id).execute()
    return True


def import_csv(content: bytes) -> dict:
    """
    Expected CSV columns: date, amount, type, category, description
    date format: YYYY-MM-DD
    type: income | expense
    """
    text = content.decode("utf-8-sig")  # handles BOM from Excel exports
    reader = csv.DictReader(io.StringIO(text))

    inserted = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            category_id = get_or_create_category(
                row["category"].strip(), row["type"].strip()
            )
            db = get_client()
            db.table("transactions").insert({
                "amount": float(row["amount"]),
                "type": row["type"].strip(),
                "category_id": category_id,
                "description": row.get("description", "").strip() or None,
                "date": row["date"].strip(),
                "source": "import",
            }).execute()
            inserted += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e), "data": dict(row)})

    return {"inserted": inserted, "errors": errors}
