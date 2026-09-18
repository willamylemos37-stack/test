from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Model(Base):
    __tablename__ = "modelos"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    leaves: Mapped[int] = mapped_column(Integer)
    product_type: Mapped[str] = mapped_column(String(30), default="ESQUADRIA", index=True)
    status: Mapped[str] = mapped_column(String(30), default="ATIVO")

class TechnicalRule(Base):
    __tablename__ = "regras_tecnicas"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    expression: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

class ModelComponent(Base):
    __tablename__ = "modelo_componentes"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("modelos.id"))
    material_code: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer)
    cut_rule: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[Model] = relationship()

class Quote(Base):
    __tablename__ = "orcamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    model_code: Mapped[str] = mapped_column(String(30))
    width_mm: Mapped[int] = mapped_column(Integer)
    height_mm: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="RASCUNHO")
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    items: Mapped[list["QuoteItem"]] = relationship(cascade="all, delete-orphan")
    snapshots: Mapped[list["QuoteRuleSnapshot"]] = relationship(cascade="all, delete-orphan")
    price_snapshots: Mapped[list["QuotePriceSnapshot"]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    pricing_snapshots: Mapped[list["QuotePricingSnapshot"]] = relationship(back_populates="quote", cascade="all, delete-orphan")

class QuoteItem(Base):
    __tablename__ = "orcamento_itens"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("orcamentos.id"))
    material_code: Mapped[str] = mapped_column(String(50))
    cut_type: Mapped[str] = mapped_column(String(30))
    length_mm: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0)
    total_price: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)

class QuoteRuleSnapshot(Base):
    __tablename__ = "orcamento_regras_snapshot"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("orcamentos.id"))
    rule_code: Mapped[str] = mapped_column(String(50))
    expression_snapshot: Mapped[str] = mapped_column(String(255))
    value_snapshot: Mapped[str] = mapped_column(String(255))

class ScrapStock(Base):
    __tablename__ = "estoque_retals"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    material_code: Mapped[str] = mapped_column(String(50), index=True)
    length_mm: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="DISPONIVEL")
    source_quote_code: Mapped[str | None] = mapped_column(String(40), nullable=True)


class PriceCatalog(Base):
    __tablename__ = "catalogo_precos"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    material_code: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(160))
    variant: Mapped[str] = mapped_column(String(40), default="PADRAO")
    unit: Mapped[str] = mapped_column(String(20))
    price: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0)
    supplier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    active: Mapped[str] = mapped_column(String(20), default="ATIVO")

class PriceHistory(Base):
    __tablename__ = "historico_precos"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    material_code: Mapped[str] = mapped_column(String(50), index=True)
    variant: Mapped[str] = mapped_column(String(40), default="PADRAO")
    price: Mapped[Decimal] = mapped_column(Numeric(14,4))
    unit: Mapped[str] = mapped_column(String(20))
    supplier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    source: Mapped[str] = mapped_column(String(120), default="CADASTRO")


class QuotePriceSnapshot(Base):
    __tablename__ = "orcamento_precos_snapshot"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("orcamentos.id"))
    material_code: Mapped[str] = mapped_column(String(50))
    variant: Mapped[str] = mapped_column(String(40))
    unit: Mapped[str] = mapped_column(String(20))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,4), default=0)
    supplier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quote: Mapped["Quote"] = relationship(back_populates="price_snapshots")

class QuotePricingSnapshot(Base):
    __tablename__ = "orcamento_formacao_preco_snapshot"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("orcamentos.id"))
    method: Mapped[str] = mapped_column(String(20))
    material_cost: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    labor_total: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    indirect_variable: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    indirect_fixed: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    freight: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    tax_percent: Mapped[Decimal] = mapped_column(Numeric(8,4), default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    target_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(8,4), nullable=True)
    target_markup_percent: Mapped[Decimal | None] = mapped_column(Numeric(8,4), nullable=True)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    profit: Mapped[Decimal] = mapped_column(Numeric(14,2), default=0)
    effective_margin_percent: Mapped[Decimal] = mapped_column(Numeric(8,4), default=0)
    effective_markup_percent: Mapped[Decimal] = mapped_column(Numeric(8,4), default=0)
    quote: Mapped["Quote"] = relationship(back_populates="pricing_snapshots")

