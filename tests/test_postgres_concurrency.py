import os
import threading
from decimal import Decimal

import pytest

DATABASE_URL = os.getenv("DATABASE_URL", "")

pytestmark = pytest.mark.postgres

if not DATABASE_URL.startswith("postgresql"):
    pytest.skip(
        "Testes de concorrência reservados para PostgreSQL real: defina DATABASE_URL.",
        allow_module_level=True,
    )

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.security_entities import Company
from app.models.inventory_entities import StockItem
from app.models.reservation_entities import StockReservation, StockReservationLine
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository


def _factory():
    engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return engine, Session


def _setup_item(Session, quantity=1, reserved=0):
    db = Session()
    company = Company(name="Empresa Concorrencia")
    db.add(company)
    db.flush()
    item = StockItem(
        company_id=company.id,
        material_code="PG-CONC",
        variant="PADRAO",
        kind="UNIDADE",
        quantity=quantity,
        reserved_quantity=reserved,
        status="DISPONIVEL" if quantity else "CONSUMIDO",
    )
    db.add(item)
    db.commit()
    ids = company.id, item.id
    db.close()
    return ids


def _run_two_workers(fn):
    barrier = threading.Barrier(2)
    results = []
    lock = threading.Lock()

    def worker(label):
        try:
            barrier.wait(timeout=10)
            value = fn(label)
            with lock:
                results.append(("OK", value))
        except Exception as exc:
            with lock:
                results.append((type(exc).__name__, None))

    threads = [threading.Thread(target=worker, args=(f"CONC-{i}",)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    assert all(not thread.is_alive() for thread in threads)
    return results


def test_postgres_concurrent_reservations_do_not_oversubscribe():
    engine, Session = _factory()
    try:
        company_id, item_id = _setup_item(Session)

        def reserve(label):
            db = Session()
            try:
                reservation = InventoryTransactionRepository(db).reserve_atomically(
                    company_id=company_id,
                    allocations=[(item_id, Decimal("1"))],
                    reference=label,
                )
                db.commit()
                return reservation.id
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        results = _run_two_workers(reserve)
        assert sum(status == "OK" for status, _ in results) == 1

        check = Session()
        item = check.get(StockItem, item_id)
        assert Decimal(str(item.reserved_quantity)) == Decimal("1")
        check.close()
    finally:
        engine.dispose()


def _create_reservation(Session, company_id, item_id):
    db = Session()
    reservation = InventoryTransactionRepository(db).reserve_atomically(
        company_id=company_id,
        allocations=[(item_id, Decimal("1"))],
        reference="BASE-RESERVA",
    )
    db.commit()
    rid = reservation.id
    db.close()
    return rid


def test_postgres_concurrent_consumption_is_single_shot():
    engine, Session = _factory()
    try:
        company_id, item_id = _setup_item(Session)
        reservation_id = _create_reservation(Session, company_id, item_id)

        def consume(label):
            db = Session()
            try:
                reservation = InventoryTransactionRepository(db).consume_reservation_atomically(
                    company_id=company_id,
                    reservation_id=reservation_id,
                    reference=label,
                )
                db.commit()
                return reservation.id
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        results = _run_two_workers(consume)
        assert sum(status == "OK" for status, _ in results) == 1

        check = Session()
        item = check.get(StockItem, item_id)
        reservation = check.get(StockReservation, reservation_id)
        assert Decimal(str(item.quantity)) == Decimal("0")
        assert Decimal(str(item.reserved_quantity)) == Decimal("0")
        assert reservation.status == "CONSUMIDA"
        check.close()
    finally:
        engine.dispose()


def test_postgres_reservation_and_consumption_do_not_create_negative_balances():
    engine, Session = _factory()
    try:
        company_id, item_id = _setup_item(Session)
        reservation_id = _create_reservation(Session, company_id, item_id)

        def action(label):
            db = Session()
            try:
                if label.endswith("0"):
                    value = InventoryTransactionRepository(db).consume_reservation_atomically(
                        company_id, reservation_id, label
                    )
                else:
                    value = InventoryTransactionRepository(db).reserve_atomically(
                        company_id, [(item_id, Decimal("1"))], label
                    )
                db.commit()
                return value.id
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        results = _run_two_workers(action)
        check = Session()
        item = check.get(StockItem, item_id)
        assert Decimal(str(item.quantity)) >= 0
        assert Decimal(str(item.reserved_quantity)) >= 0
        assert Decimal(str(item.reserved_quantity)) <= Decimal(str(item.quantity))
        check.close()
    finally:
        engine.dispose()


def test_postgres_cross_company_reservation_cannot_touch_foreign_item():
    engine, Session = _factory()
    try:
        db = Session()
        company_a = Company(name="Empresa A")
        company_b = Company(name="Empresa B")
        db.add_all([company_a, company_b])
        db.flush()
        item = StockItem(
            company_id=company_b.id,
            material_code="PG-TENANT",
            variant="PADRAO",
            kind="UNIDADE",
            quantity=1,
            reserved_quantity=0,
            status="DISPONIVEL",
        )
        db.add(item)
        db.commit()
        a_id, item_id = company_a.id, item.id
        db.close()

        db = Session()
        with pytest.raises(Exception):
            InventoryTransactionRepository(db).reserve_atomically(
                company_id=a_id,
                allocations=[(item_id, Decimal("1"))],
                reference="CROSS-TENANT",
            )
        db.rollback()
        check = db.execute(select(StockItem).where(StockItem.id == item_id)).scalar_one()
        assert Decimal(str(check.reserved_quantity)) == Decimal("0")
        db.close()
    finally:
        engine.dispose()
