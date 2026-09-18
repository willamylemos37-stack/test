from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class StockItem(Base):
    __tablename__ = "estoque_itens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    material_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(40), nullable=False, default="PADRAO")
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # BARRA, RETALHO, UNIDADE
    length_mm: Mapped[int|None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(14,3), nullable=False, default=1)
    reserved_quantity: Mapped[float] = mapped_column(Numeric(14,3), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DISPONIVEL")
    source_item_id: Mapped[int|None] = mapped_column(ForeignKey("estoque_itens.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_estoque_item_qty_nonnegative"),
        CheckConstraint("reserved_quantity >= 0 AND reserved_quantity <= quantity", name="ck_estoque_reserved_qty_valid"),
        CheckConstraint("length_mm IS NULL OR length_mm > 0", name="ck_estoque_item_length_positive"),
    )

class StockMovement(Base):
    __tablename__ = "estoque_movimentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("estoque_itens.id", ondelete="RESTRICT"), nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(14,3), nullable=False)
    reference: Mapped[str|None] = mapped_column(String(120), nullable=True)
    note: Mapped[str|None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
