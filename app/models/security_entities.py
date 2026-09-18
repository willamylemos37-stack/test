from datetime import datetime,UTC
from sqlalchemy import Boolean,DateTime,ForeignKey,Integer,String,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.db import Base
class Company(Base):
    __tablename__="empresas"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(160),nullable=False)
    active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)
class User(Base):
    __tablename__="usuarios"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    company_id:Mapped[int]=mapped_column(ForeignKey("empresas.id",ondelete="CASCADE"),nullable=False,index=True)
    email:Mapped[str]=mapped_column(String(255),nullable=False)
    password_hash:Mapped[str]=mapped_column(String(512),nullable=False)
    role:Mapped[str]=mapped_column(String(40),nullable=False,default="VENDEDOR")
    active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),nullable=False)
    __table_args__=(UniqueConstraint("company_id","email",name="uq_usuario_empresa_email"),)
