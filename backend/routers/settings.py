from fastapi import APIRouter
from models.settings import SettingsUpdate
from services import settings as svc

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/")
def get_settings():
    return svc.get_settings()


@router.put("/")
def update_settings(payload: SettingsUpdate):
    return svc.update_settings(payload)
