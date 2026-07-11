from database import get_client
from models.settings import SettingsUpdate, Settings


def get_settings() -> Settings:
    db = get_client()
    rows = db.table("settings").select("key, value").execute().data
    data = {r["key"]: r["value"] for r in rows}
    return Settings(
        currency=data.get("currency", "MXN"),
        currency_symbol=data.get("currency_symbol", "$"),
        currency_locale=data.get("currency_locale", "es-MX"),
    )


def update_settings(payload: SettingsUpdate) -> Settings:
    db = get_client()
    updates = payload.model_dump(exclude_none=True)
    for key, value in updates.items():
        db.table("settings").upsert({"key": key, "value": value}, on_conflict="key").execute()
    return get_settings()
