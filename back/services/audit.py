from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from back.models.audit_log import AuditLog


_SENSITIVE_FIELDS = {
    "password",
    "hashed_password",
    "token",
    "token_hash",
    "recovery_code",
    "code_hash",
}


def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {
            key: _json_safe(item)
            for key, item in value.items()
            if key.lower() not in _SENSITIVE_FIELDS
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    raise TypeError(f"Unsupported audit value: {type(value).__name__}")


def snapshot_fields(instance, fields):
    return {
        field: _json_safe(getattr(instance, field))
        for field in fields
    }


def record_audit_event(
    db: Session,
    tenant_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None,
    before_data: dict | None = None,
    after_data: dict | None = None,
    actor_user_id: int | None = None,
) -> AuditLog:
    event = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id or db.info.get("audit_actor_id"),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_data=_json_safe(before_data),
        after_data=_json_safe(after_data),
    )
    db.add(event)
    return event
