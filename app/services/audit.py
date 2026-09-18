from sqlalchemy.orm import Session
from app.models.audit_entities import AuditEvent

def record_audit(db: Session, *, action: str, company_id: int | None = None,
                 user_id: int | None = None, resource_type: str | None = None,
                 resource_id: str | int | None = None, request_id: str | None = None,
                 ip_address: str | None = None, details: dict | None = None,
                 commit: bool = True) -> AuditEvent:
    event = AuditEvent(company_id=company_id, user_id=user_id, action=action,
                       resource_type=resource_type,
                       resource_id=str(resource_id) if resource_id is not None else None,
                       request_id=request_id, ip_address=ip_address, details=details)
    db.add(event)
    if commit:
        db.commit(); db.refresh(event)
    else:
        db.flush()
    return event
