from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from models.transaction import TransactionCreate, TransactionUpdate
from services import transactions as svc

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/")
def list_transactions(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    category_id: str | None = None,
    type: str | None = Query(None, pattern="^(income|expense)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    return svc.list_transactions(
        month=month,
        category_id=category_id,
        type_filter=type,
        page=page,
        limit=limit,
    )


@router.post("/", status_code=201)
def create_transaction(payload: TransactionCreate):
    return svc.create_transaction(payload)


@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, payload: TransactionUpdate):
    result = svc.update_transaction(transaction_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str):
    svc.delete_transaction(transaction_id)


@router.post("/import", status_code=201)
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
    content = await file.read()
    result = svc.import_csv(content)
    return result
