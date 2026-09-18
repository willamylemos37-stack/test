from __future__ import annotations

from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_entities import StockItem, StockMovement
from app.models.reservation_entities import StockReservation, StockReservationLine
from app.services.transactional_flow import TransactionFlowError


class InventoryTransactionRepository:
    """Operações atômicas de estoque.

    Em PostgreSQL, with_for_update() bloqueia as linhas até o commit/rollback.
    Em SQLite o recurso é ignorado pelo banco; por isso concorrência real deve
    ser validada em PostgreSQL antes de produção.
    """

    def __init__(self, db: Session):
        self.db = db

    def _transaction(self):
        # Se o chamador já abriu uma transação, usa SAVEPOINT; caso contrário,
        # cria a transação principal. Em ambos os casos, a operação é atômica
        # no seu próprio escopo.
        return self.db.begin_nested() if self.db.in_transaction() else self.db.begin()

    def reserve_atomically(
        self,
        company_id: int,
        allocations: list[tuple[int, Decimal]],
        reference: str,
    ) -> StockReservation:
        if not allocations:
            raise TransactionFlowError("Reserva sem itens.")

        # A operação usa transação própria ou SAVEPOINT quando o chamador já iniciou uma transação.
        with self._transaction():
            ids = [item_id for item_id, _ in allocations]
            if len(ids) != len(set(ids)):
                raise TransactionFlowError("Item repetido na reserva.")

            rows = self.db.scalars(
                select(StockItem)
                .where(
                    StockItem.id.in_(ids),
                    StockItem.company_id == company_id,
                    StockItem.status == "DISPONIVEL",
                )
                .with_for_update()
            ).all()

            items = {row.id: row for row in rows}
            if len(items) != len(ids):
                raise TransactionFlowError(
                    "Item de estoque indisponível ou pertencente a outra empresa."
                )

            # Revalidação acontece DENTRO da transação, depois do lock.
            normalized = []
            for item_id, raw_qty in allocations:
                qty = Decimal(str(raw_qty))
                if qty <= 0:
                    raise TransactionFlowError("Quantidade deve ser positiva.")
                item = items[item_id]
                available = Decimal(str(item.quantity)) - Decimal(str(item.reserved_quantity))
                if available < qty:
                    raise TransactionFlowError(
                        "Estoque insuficiente; nenhuma reserva foi efetivada."
                    )
                normalized.append((item, qty))

            reservation = StockReservation(
                company_id=company_id,
                reference=reference,
                status="ATIVA",
            )
            self.db.add(reservation)
            self.db.flush()

            for item, qty in normalized:
                item.reserved_quantity = Decimal(str(item.reserved_quantity)) + qty
                self.db.add(
                    StockReservationLine(
                        reservation_id=reservation.id,
                        item_id=item.id,
                        quantity=qty,
                    )
                )
                self.db.add(
                    StockMovement(
                        company_id=company_id,
                        item_id=item.id,
                        movement_type="RESERVA",
                        quantity=qty,
                        reference=reference,
                        note="Reserva atômica de estoque",
                    )
                )

            self.db.flush()
            self.db.refresh(reservation)
            return reservation

    def consume_reservation_atomically(
        self,
        company_id: int,
        reservation_id: int,
        reference: str,
    ) -> StockReservation:
        with self._transaction():
            reservation = self.db.execute(
                select(StockReservation)
                .where(
                    StockReservation.id == reservation_id,
                    StockReservation.company_id == company_id,
                )
                .with_for_update()
            ).scalar_one_or_none()

            if reservation is None:
                raise TransactionFlowError("Reserva não encontrada para a empresa.")
            if reservation.status != "ATIVA":
                raise TransactionFlowError("Somente reserva ATIVA pode ser consumida.")

            lines = self.db.scalars(
                select(StockReservationLine)
                .where(StockReservationLine.reservation_id == reservation_id)
                .with_for_update()
            ).all()

            if not lines:
                raise TransactionFlowError("Reserva sem linhas.")

            locked_items = {}
            for line in lines:
                item = self.db.execute(
                    select(StockItem)
                    .where(
                        StockItem.id == line.item_id,
                        StockItem.company_id == company_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()
                if item is None:
                    raise TransactionFlowError("Item de estoque não encontrado.")
                locked_items[item.id] = item

            # Revalidação integral antes de qualquer baixa.
            for line in lines:
                item = locked_items[line.item_id]
                qty = Decimal(str(line.quantity))
                if Decimal(str(item.reserved_quantity)) < qty:
                    raise TransactionFlowError(
                        "Saldo reservado inconsistente; consumo revertido."
                    )
                if Decimal(str(item.quantity)) < qty:
                    raise TransactionFlowError(
                        "Saldo físico insuficiente; consumo revertido."
                    )

            for line in lines:
                item = locked_items[line.item_id]
                qty = Decimal(str(line.quantity))
                item.quantity = Decimal(str(item.quantity)) - qty
                item.reserved_quantity = Decimal(str(item.reserved_quantity)) - qty
                if Decimal(str(item.quantity)) == 0:
                    item.status = "CONSUMIDO"

                self.db.add(
                    StockMovement(
                        company_id=company_id,
                        item_id=item.id,
                        movement_type="CONSUMO",
                        quantity=-qty,
                        reference=reference,
                        note="Consumo de reserva",
                    )
                )

            reservation.status = "CONSUMIDA"
            self.db.flush()
            self.db.refresh(reservation)
            return reservation
