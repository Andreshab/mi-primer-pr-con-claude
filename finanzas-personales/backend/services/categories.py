from database import get_client
from models.category import CategoryCreate, CategoryUpdate


def list_categories(type_filter: str | None = None) -> list[dict]:
    db = get_client()
    q = db.table("categories").select("*").order("name")
    if type_filter:
        q = q.eq("type", type_filter)
    return q.execute().data


def get_category(category_id: str) -> dict | None:
    db = get_client()
    result = db.table("categories").select("*").eq("id", category_id).execute()
    return result.data[0] if result.data else None


def create_category(payload: CategoryCreate) -> dict:
    db = get_client()
    result = db.table("categories").insert(payload.model_dump()).execute()
    return result.data[0]


def update_category(category_id: str, payload: CategoryUpdate) -> dict | None:
    db = get_client()
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return get_category(category_id)
    result = db.table("categories").update(data).eq("id", category_id).execute()
    return result.data[0] if result.data else None


def delete_category(category_id: str) -> bool:
    db = get_client()
    # Block deletion if category has transactions
    used = db.table("transactions").select("id").eq("category_id", category_id).limit(1).execute()
    if used.data:
        return False
    db.table("categories").delete().eq("id", category_id).execute()
    return True


def get_or_create_category(name: str, type_: str) -> str:
    """Used during CSV import: returns existing category id or creates a new one."""
    db = get_client()
    result = db.table("categories").select("id").eq("name", name).eq("type", type_).execute()
    if result.data:
        return result.data[0]["id"]
    new = db.table("categories").insert({"name": name, "type": type_}).execute()
    return new.data[0]["id"]
