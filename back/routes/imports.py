from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from back import models
from back.schemas.finance_import import FinanceImportRequest
from back.services.finance_import import import_finance_rows
from database.database import get_db
from database.security import get_current_user


router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/finance")
def import_finance(
    payload: FinanceImportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return import_finance_rows(db, current_user.tenant_id, payload)
