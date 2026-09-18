import os
os.environ["APP_SECRET_KEY"]="test-secret-etapa-47"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.security_entities import Company, User
from app.models.inventory_entities import StockItem
from app.models.production_entities import ProductionOrder
from app.models.audit_entities import AuditEvent
from app.security import hash_password

A=992; B=993

def setup_module():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    for cid,email in [(A,"a@empresa.local"),(B,"b@empresa.local")]:
        if not db.query(Company).filter_by(id=cid).first():
            db.add(Company(id=cid,name=f"Empresa {cid}",active=True)); db.flush()
            db.add(User(company_id=cid,email=email,password_hash=hash_password("senha-12345"),role="ADMIN"))
    db.commit(); db.close()

def token(company,email):
    c=TestClient(app); r=c.post('/auth/login',json={'company_id':company,'email':email,'password':'senha-12345'}); assert r.status_code==200; return r.json()['access_token']

def test_quote_isolation_and_production_creation():
    c=TestClient(app); ta=token(A,'a@empresa.local'); tb=token(B,'b@empresa.local')
    ra=c.post('/orcamentos',headers={'Authorization':'Bearer '+ta},json={'model_code':'MOD-001','unit':'mm','width':1003,'height':1000,'quantity':1}); assert ra.status_code==200
    qid=ra.json()['id']
    rb=c.get(f'/orcamentos/{qid}',headers={'Authorization':'Bearer '+tb}); assert rb.status_code==404
    rp=c.post('/producao',headers={'Authorization':'Bearer '+tb},json={'quote_id':qid}); assert rp.status_code==404
    rp=c.post('/producao',headers={'Authorization':'Bearer '+ta},json={'quote_id':qid}); assert rp.status_code==200
    assert rp.json()['company_id']==A and rp.json()['quote_id']==qid

def test_stock_and_production_cross_company_are_inaccessible():
    db=SessionLocal()
    item=StockItem(company_id=A,material_code='MP-X',variant='PADRAO',kind='UNIDADE',quantity=1,reserved_quantity=0,status='DISPONIVEL')
    db.add(item); db.commit(); db.refresh(item)
    order=ProductionOrder(company_id=A,reference='OP-A',status='ABERTA',model_code='MOD-001',input_snapshot='{}',technical_snapshot='{}')
    db.add(order); db.commit(); db.refresh(order)
    item_id, order_id = item.id, order.id
    db.close()
    c=TestClient(app); tb=token(B,'b@empresa.local')
    r=c.post(f'/producao/{order_id}/reservar',headers={'Authorization':'Bearer '+tb},json={'allocations':[{'item_id':item_id,'quantity':1}]})
    assert r.status_code==404

def test_persisted_quote_to_production_to_consumption_flow():
    db=SessionLocal()
    item=StockItem(company_id=A,material_code='MP-FLOW',variant='PADRAO',kind='UNIDADE',quantity=2,reserved_quantity=0,status='DISPONIVEL')
    db.add(item); db.commit(); db.refresh(item)
    item_id=item.id
    db.close()

    c=TestClient(app); ta=token(A,'a@empresa.local'); tb=token(B,'b@empresa.local')
    rq=c.post('/orcamentos',headers={'Authorization':'Bearer '+ta},json={'model_code':'MOD-001','unit':'mm','width':1003,'height':1000,'quantity':1})
    assert rq.status_code==200
    qid=rq.json()['id']

    ro=c.post('/producao',headers={'Authorization':'Bearer '+ta},json={'quote_id':qid})
    assert ro.status_code==200
    oid=ro.json()['id']

    db=SessionLocal(); order=db.query(ProductionOrder).filter_by(id=oid).first()
    import json
    snap=json.loads(order.technical_snapshot)
    assert snap['quote_id']==qid and snap['parts'] and snap['rule_snapshots']
    db.close()

    assert c.get(f'/producao/{oid}',headers={'Authorization':'Bearer '+ta}).status_code==200
    assert c.get(f'/producao/{oid}',headers={'Authorization':'Bearer '+tb}).status_code==404

    rr=c.post(f'/producao/{oid}/reservar',headers={'Authorization':'Bearer '+ta},json={
        'allocations':[{'item_id':item_id,'quantity':1}], 'reference':f'RESERVA-OP-{oid}'})
    assert rr.status_code==200
    assert rr.json()['reservation_status']=='ATIVA'

    ri=c.post(f'/producao/{oid}/iniciar',headers={'Authorization':'Bearer '+ta})
    assert ri.status_code==200 and ri.json()['production_status']=='EM_PRODUCAO'

    rc=c.post(f'/producao/{oid}/concluir',headers={'Authorization':'Bearer '+ta})
    assert rc.status_code==200
    assert rc.json()['production_status']=='CONCLUIDA'
    assert rc.json()['reservation_status']=='CONSUMIDA'

    db=SessionLocal(); item=db.query(StockItem).filter_by(id=item_id).first(); order=db.query(ProductionOrder).filter_by(id=oid).first()
    assert item.quantity == 1 and item.reserved_quantity == 0
    assert order.status == 'CONCLUIDA'
    events = db.query(AuditEvent).filter(AuditEvent.company_id == A, AuditEvent.resource_id == str(oid)).all()
    actions = {e.action for e in events}
    assert {'OP_CRIADA', 'OP_RESERVADA', 'OP_INICIADA', 'OP_CONCLUIDA'} <= actions
    db.close()


def test_reservation_endpoint_is_all_or_nothing():
    db=SessionLocal()
    item1=StockItem(company_id=A,material_code='MP-ATOMIC-1',variant='PADRAO',kind='UNIDADE',quantity=1,reserved_quantity=0,status='DISPONIVEL')
    item2=StockItem(company_id=A,material_code='MP-ATOMIC-2',variant='PADRAO',kind='UNIDADE',quantity=1,reserved_quantity=0,status='DISPONIVEL')
    order=ProductionOrder(company_id=A,reference='OP-ATOMIC',status='ABERTA',model_code='MOD-001',input_snapshot='{}',technical_snapshot='{}')
    db.add_all([item1,item2,order]); db.commit(); db.refresh(item1); db.refresh(item2); db.refresh(order)
    ids=item1.id,item2.id,order.id
    db.close()
    c=TestClient(app); ta=token(A,'a@empresa.local')
    r=c.post(f'/producao/{ids[2]}/reservar',headers={'Authorization':'Bearer '+ta},json={
        'allocations':[{'item_id':ids[0],'quantity':1},{'item_id':ids[1],'quantity':2}]})
    assert r.status_code==409
    db=SessionLocal(); a=db.query(StockItem).filter_by(id=ids[0]).first(); b=db.query(StockItem).filter_by(id=ids[1]).first(); o=db.query(ProductionOrder).filter_by(id=ids[2]).first()
    assert a.reserved_quantity == 0 and b.reserved_quantity == 0 and o.reservation_id is None
    db.close()
