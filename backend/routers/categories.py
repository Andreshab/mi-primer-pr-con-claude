from fastapi import APIRouter, HTTPException, Query
from models.category import CategoryCreate, CategoryUpdate, Category
from services import categories as svc

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[dict])
def list_categories(type: str | None = Query(None, pattern="^(income|expense)$")):
    return svc.list_categories(type_filter=type)


@router.post("/", response_model=dict, status_code=201)
def create_category(payload: CategoryCreate):
    return svc.create_category(payload)


@router.put("/{category_id}", response_model=dict)
def update_category(category_id: str, payload: CategoryUpdate):
    result = svc.update_category(category_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return result


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: str):
    ok = svc.delete_category(category_id)
    if not ok:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category with existing transactions. Reassign them first.",
        )
