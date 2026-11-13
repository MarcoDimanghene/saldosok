from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from back import models, schemas
from back.crud.audit import get_audit_logs
from database.database import get_db
from database.security import get_current_tenant_admin


router = APIRouter(prefix="/audit", tags=["Auditoría"])


@router.get("/", response_model=list[schemas.AuditLogResponse])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_tenant_admin),
):
    logs = get_audit_logs(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
    )
    return [
        {
            "id": entry.id,
            "actor_user_id": entry.actor_user_id,
            "actor_name": (
                entry.actor.nombre or entry.actor.username
                if entry.actor
                else "Usuario eliminado"
            ),
            "action": entry.action,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "before_data": entry.before_data,
            "after_data": entry.after_data,
            "created_at": entry.created_at,
        }
        for entry in logs
    ]
