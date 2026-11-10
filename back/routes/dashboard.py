# ==================================================
# ROUTER DEL DASHBOARD
# ==================================================
# Expone un único endpoint que entrega TODOS los indicadores
# del panel en una sola llamada. Así el frontend hace 1 request
# y no 10.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from back import crud, models, schemas
from database.database import get_db
from database.security import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Devuelve el resumen completo del panel para la organización
    (tenant) del usuario autenticado.

    La autenticación se resuelve con get_current_user (valida el
    JWT) y el tenant_id se toma del usuario para que NUNCA se
    filtren datos de otra empresa.
    """
    return crud.get_dashboard_summary(db=db, tenant_id=current_user.tenant_id)
