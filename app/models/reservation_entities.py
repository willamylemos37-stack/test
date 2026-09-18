from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class StockReservation(Base):
    __tablename__="estoque_reservas"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    company_id:Mapped[int]=mapped_column(ForeignKey("empresas.id",ondelete="CASCADE"),nullable=False,index=True)
    reference:Mapped[str]=mapped_column(String(120),nullable=False)
    status:Mapped[str]=mapped_column(String(20),nullable=False,default="ATIVA")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)

class StockReservationLine(Base):
    __tablename__="estoque_reserva_itens"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    reservation_id:Mapped[int]=mapped_column(ForeignKey("estoque_reservas.id",ondelete="CASCADE"),nullable=False,index=True)
    item_id:Mapped[int]=mapped_column(ForeignKey("estoque_itens.id",ondelete="RESTRICT"),nullable=False,index=True)
    quantity:Mapped[float]=mapped_column(Numeric(14,3),nullable=False)
    __table_args__=(UniqueConstraint("reservation_id","item_id",name="uq_reserva_item"),)
