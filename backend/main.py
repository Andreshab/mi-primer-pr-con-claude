import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_client
from routers import budgets, categories, transactions, goals, reports, settings, pages

app = FastAPI(title="Finanzas Personales")

app.mount("/static", StaticFiles(directory="static"), name="static")

# JSON API
app.include_router(categories.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

# HTML pages + HTMX partials
app.include_router(pages.router)


@app.get("/health")
def health():
    db = get_client()
    result = db.table("settings").select("key, value").execute()
    return {
        "status": "ok",
        "commit": os.getenv("RENDER_GIT_COMMIT", "local"),
        "settings": result.data,
    }
