from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    currency: str | None = None
    currency_symbol: str | None = None
    currency_locale: str | None = None


class Settings(BaseModel):
    currency: str
    currency_symbol: str
    currency_locale: str
