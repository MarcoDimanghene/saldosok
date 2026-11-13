from sqlalchemy.orm import Session, selectinload

from back.models import AuditLog


def get_audit_logs(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(AuditLog)
        .options(selectinload(AuditLog.actor))
        .filter(AuditLog.tenant_id == tenant_id)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
