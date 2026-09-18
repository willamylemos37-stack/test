from decimal import Decimal
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.inventory_entities import StockItem, StockMovement
from app.models.reservation_entities import StockReservation
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.services.transactional_flow import TransactionFlowError

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    S = sessionmaker(bind=engine, future=True)
    db = S()
    yield db
    db.close()

def seed(db, qty="5", company=1):
    item = StockItem(
        company_id=company, material_code="MP-X", variant="BARRA_3000",
        kind="BARRA", length_mm=3000, quantity=Decimal(qty),
        reserved_quantity=Decimal("0"), status="DISPONIVEL"
    )
    db.add(item); db.commit(); db.refresh(item)
    return item.id

def test_reserve_and_consume(session):
    item_id = seed(session)
    repo = InventoryTransactionRepository(session)
    r = repo.reserve_atomically(1, [(item_id, Decimal("2"))], "ORC-1")
    session.expire_all()
    item = session.get(StockItem, item_id)
    assert Decimal(str(item.reserved_quantity)) == Decimal("2")
    assert Decimal(str(item.quantity)) == Decimal("5")
    repo.consume_reservation_atomically(1, r.id, "OP-1")
    session.expire_all()
    item = session.get(StockItem, item_id)
    assert Decimal(str(item.quantity)) == Decimal("3")
    assert Decimal(str(item.reserved_quantity)) == Decimal("0")

def test_shortage_rolls_back(session):
    item_id = seed(session, "1")
    with pytest.raises(TransactionFlowError):
        InventoryTransactionRepository(session).reserve_atomically(
            1, [(item_id, Decimal("2"))], "ORC-X"
        )
    assert session.scalar(select(StockReservation).where(StockReservation.reference=="ORC-X")) is None
    item = session.get(StockItem, item_id)
    assert Decimal(str(item.reserved_quantity)) == Decimal("0")

def test_multi_item_shortage_rolls_back_everything(session):
    a, b = seed(session, "2"), seed(session, "1")
    with pytest.raises(TransactionFlowError):
        InventoryTransactionRepository(session).reserve_atomically(
            1, [(a, Decimal("2")), (b, Decimal("2"))], "ORC-MULTI"
        )
    assert session.scalar(select(StockReservation).where(StockReservation.reference=="ORC-MULTI")) is None
    assert Decimal(str(session.get(StockItem,a).reserved_quantity)) == 0
    assert Decimal(str(session.get(StockItem,b).reserved_quantity)) == 0

def test_wrong_company_cannot_reserve(session):
    item_id = seed(session, "5", company=7)
    with pytest.raises(TransactionFlowError):
        InventoryTransactionRepository(session).reserve_atomically(
            1, [(item_id, Decimal("1"))], "ORC-SEC"
        )

def test_consumption_rollback_on_inconsistent_second_line(session):
    a, b = seed(session, "5"), seed(session, "5")
    repo = InventoryTransactionRepository(session)
    r = repo.reserve_atomically(1, [(a, Decimal("2"))], "ORC-A")
    # Artificial inconsistency to prove all-or-nothing consumption.
    session.execute(
        StockItem.__table__.update().where(StockItem.id==b).values(quantity=0)
    )
    session.commit()
    # Add a second line manually to the reservation; it will fail and rollback.
    from app.models.reservation_entities import StockReservationLine
    session.add(StockReservationLine(reservation_id=r.id,item_id=b,quantity=Decimal("1")))
    session.commit()
    with pytest.raises(TransactionFlowError):
        repo.consume_reservation_atomically(1, r.id, "OP-FAIL")
    session.expire_all()
    assert session.get(StockItem,a).quantity == Decimal("5")
    assert session.get(StockItem,a).reserved_quantity == Decimal("2")
    assert session.get(StockReservation,r.id).status == "ATIVA"
