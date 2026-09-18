from app.db import Base, engine, SessionLocal
from app.models.security_entities import Company, User
from app.models.audit_entities import AuditEvent
from app.services.audit import record_audit


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_record_audit_persists_event():
    db=SessionLocal()
    try:
        c=Company(name="Audit Test"); db.add(c); db.commit(); db.refresh(c)
        e=record_audit(db, action="TESTE", company_id=c.id, details={"ok": True})
        got=db.get(AuditEvent,e.id)
        assert got.company_id==c.id and got.action=="TESTE" and got.details=={"ok": True}
    finally: db.close()
