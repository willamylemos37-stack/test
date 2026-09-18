from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class ProductionOrder(Base):
    __tablename__="ordens_producao"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    company_id:Mapped[int]=mapped_column(ForeignKey("empresas.id",ondelete="CASCADE"),nullable=False,index=True)
    quote_id:Mapped[int|None]=mapped_column(ForeignKey("orcamentos.id",ondelete="SET NULL"),nullable=True,index=True)
    reservation_id:Mapped[int|None]=mapped_column(ForeignKey("estoque_reservas.id",ondelete="SET NULL"),nullable=True,index=True)
    reference:Mapped[str]=mapped_column(String(120),nullable=False)
    status:Mapped[str]=mapped_column(String(24),nullable=False,default="ABERTA")
    model_code:Mapped[str]=mapped_column(String(40),nullable=False)
    input_snapshot:Mapped[str]=mapped_column(Text,nullable=False)
    technical_snapshot:Mapped[str]=mapped_column(Text,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)
