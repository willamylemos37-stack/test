from pydantic import BaseModel, Field

class QuoteInput(BaseModel):
    model_code: str = "MOD-001"
    unit: str = "mm"
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int = Field(gt=0)

class QuoteResponse(BaseModel):
    id: int
    code: str
    company_id: int | None = None
    model_code: str
    width_mm: int
    height_mm: int
    quantity: int
    status: str


from decimal import Decimal

class ProductionOrderInput(BaseModel):
    quote_id: int | None = Field(default=None, gt=0)
    reference: str | None = None
    model_code: str | None = None
    unit: str | None = None
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, gt=0)

class ProductionOrderResponse(BaseModel):
    id: int
    company_id: int
    quote_id: int | None
    reservation_id: int | None
    reference: str
    status: str
    model_code: str

class PriceInput(BaseModel):
    material_code: str
    description: str
    variant: str = "PADRAO"
    unit: str
    price: Decimal = Field(ge=0)
    supplier: str | None = None

class PriceResponse(BaseModel):
    id: int
    material_code: str
    description: str
    variant: str
    unit: str
    price: Decimal
    supplier: str | None = None

class CostInput(BaseModel):
    model_code: str = "MOD-001"
    unit: str = "mm"
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int = Field(gt=0)


class PriceFormationInput(BaseModel):
    model_code: str = "MOD-001"
    unit: str = "mm"
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int = Field(gt=0)
    labor_per_unit: Decimal = Field(default=Decimal("0"), ge=0)
    indirect_percent: Decimal = Field(default=Decimal("0"), ge=0)
    indirect_fixed: Decimal = Field(default=Decimal("0"), ge=0)
    freight: Decimal = Field(default=Decimal("0"), ge=0)
    tax_percent: Decimal = Field(default=Decimal("0"), ge=0)
    margin_percent: Decimal | None = Field(default=None, ge=0)
    markup_percent: Decimal | None = Field(default=None, ge=0)
    allow_provisional: bool = False

class GlassPieceInput(BaseModel):
    width_mm: int = Field(gt=0)
    height_mm: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)

class GlassSheetInput(BaseModel):
    width_mm: int = Field(gt=0)
    height_mm: int = Field(gt=0)
    kerf_mm: int = Field(default=3, ge=0)

class GlassOptimizationInput(BaseModel):
    pieces: list[GlassPieceInput]
    sheets: list[GlassSheetInput]
    price_by_size: dict[str, Decimal] | None = None

class FullQuoteInput(BaseModel):
    model_code: str = "MOD-001"
    unit: str = "mm"
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int = Field(default=1, gt=0)
    labor_per_unit: Decimal = Field(default=Decimal("0"), ge=0)
    indirect_percent: Decimal = Field(default=Decimal("0"), ge=0)
    indirect_fixed: Decimal = Field(default=Decimal("0"), ge=0)
    freight: Decimal = Field(default=Decimal("0"), ge=0)
    tax_percent: Decimal = Field(default=Decimal("0"), ge=0)
    margin_percent: Decimal | None = Field(default=None, ge=0)
    markup_percent: Decimal | None = Field(default=None, ge=0)
    glass_sheet_width_mm: int = Field(default=0, ge=0)
    glass_sheet_height_mm: int = Field(default=0, ge=0)
    glass_sheet_kerf_mm: int = Field(default=3, ge=0)
    glass_sheet_price: Decimal | None = Field(default=None, ge=0)
    allow_provisional: bool = False


class LoginInput(BaseModel):
    company_id: int
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

