from app.services.production_workflow import approve_and_prepare, start_production, finish_production
from app.models.production_entities import ProductionOrder  # noqa: F401
from app.models.reservation_entities import StockReservation, StockReservationLine  # noqa: F401
from app.models.inventory_entities import StockItem, StockMovement  # noqa: F401
from app.models.security_entities import Company, User  # noqa: F401
from app.models.audit_entities import AuditEvent  # noqa: F401
from app.security import verify_password, create_token, SecurityError, TOKEN_TTL_SECONDS
from app.api_security import current_actor
from app.security_context import ActorContext, assert_company
import os
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from app.runtime_config import is_production, validate_runtime_config
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import AUTO_CREATE_SCHEMA, Base, engine, get_db, ensure_dev_schema
from app.models.entities import Quote, QuotePricingSnapshot
from app.repositories.quote_repository import QuoteRepository
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.services.transactional_flow import TransactionFlowError
from app.schemas import (
    CostInput, FullQuoteInput, GlassOptimizationInput, PriceFormationInput,
    PriceInput, PriceResponse, QuoteInput, QuoteResponse, LoginInput, TokenResponse,
    ProductionOrderInput, ProductionOrderResponse,
)
from app.services.calculator import calculate_model
from app.services.costing import calculate_cost, calculate_full_cost
from app.services.cutting import optimize_profile
from app.services.glass_cutting import GlassPiece, GlassSheet, choose_by_cost, optimize_glass
from app.services.price_formation import form_price
from app.services.pricing import get_current_prices, set_price
from app.services.validation import normalize_dimensions, validate_kerf, validate_margin_or_markup
from app.services.audit import record_audit
from app.services.product_catalog import supported_product_families, public_catalog, public_catalog

VERSION = "5.51.0"
_LOGIN_ATTEMPTS = {}
_LOGIN_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_WINDOW_SECONDS", "60"))
_LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_RATE_MAX_ATTEMPTS", "10"))

logger = logging.getLogger("esquadrias.api")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        supplied_request_id = (request.headers.get("X-Request-ID") or "").strip()
        request_id = supplied_request_id if supplied_request_id and len(supplied_request_id) <= 64 and all(c.isalnum() or c in "-_" for c in supplied_request_id) else uuid4().hex
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled API error request_id=%s path=%s", request_id, request.url.path)
            raise
        response.headers["X-Request-ID"] = request_id
        response.headers.setdefault("Access-Control-Expose-Headers", "X-Request-ID")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store" if request.method != "GET" else response.headers.get("Cache-Control", "no-store")
        if is_production():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        elapsed = (time.perf_counter() - started) * 1000
        logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.2f", request_id, request.method, request.url.path, response.status_code, elapsed)
        return response



validate_runtime_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if AUTO_CREATE_SCHEMA:
        Base.metadata.create_all(bind=engine)
    yield


allowed_origins = [
    x.strip()
    for x in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500"
    ).split(",")
    if x.strip()
]

app = FastAPI(
    title="Esquadrias API", version=VERSION, lifespan=lifespan,
    docs_url=None if is_production() else "/docs",
    redoc_url=None if is_production() else "/redoc",
    openapi_url=None if is_production() else "/openapi.json",
)
@app.get("/catalogo/tipos-produto")
def list_product_types():
    return [{"code": item.code, "name": item.name, "description": item.description, "status": item.status} for item in supported_product_families()]


@app.get("/catalogo/publico")
def public_product_catalog():
    """Catálogo seguro para futura vitrine pública; sem preços ou regras internas."""
    return list(public_catalog())


app.add_middleware(SecurityHeadersMiddleware)
if AUTO_CREATE_SCHEMA:
    Base.metadata.create_all(bind=engine)
    ensure_dev_schema()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def dimensions_or_400(data) -> tuple[int, int]:
    try:
        return normalize_dimensions(data.model_code, data.unit, data.width, data.height)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def calculate_or_400(width_mm: int, height_mm: int, quantity: int, model_code: str = "MOD-001"):
    try:
        return calculate_model(model_code, width_mm, height_mm, quantity)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def validate_kerf_or_400(kerf_mm: int) -> None:
    try:
        validate_kerf(kerf_mm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def validate_pricing_input_or_400(data: PriceFormationInput | FullQuoteInput) -> None:
    try:
        validate_margin_or_markup(data.margin_percent, data.markup_percent)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



@app.post("/auth/login", response_model=TokenResponse)
def auth_login(data: LoginInput, db: Session = Depends(get_db), request: Request = None):
    # Limite simples por IP/processo; em produção, o proxy/WAF deve aplicar o limite global.
    now = time.time()
    ip = request.client.host if request and request.client else "unknown"
    key = f"{ip}:{data.email.strip().lower()}"
    attempts = [t for t in _LOGIN_ATTEMPTS.get(key, []) if now - t < _LOGIN_WINDOW_SECONDS]
    if len(attempts) >= _LOGIN_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Muitas tentativas de login. Tente novamente mais tarde.")
    attempts.append(now); _LOGIN_ATTEMPTS[key] = attempts
    user = db.query(User).filter(
        User.company_id == data.company_id,
        User.email == data.email.strip().lower(),
    ).first()
    if not user or not user.active or not verify_password(data.password, user.password_hash):
        try:
            record_audit(db, action="LOGIN_FALHA", company_id=data.company_id,
                         ip_address=ip, details={"email": data.email.strip().lower()})
        except Exception:
            logger.exception("Audit failure on login failure")
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    company = db.query(Company).filter(Company.id == user.company_id, Company.active == True).first()
    if not company:
        raise HTTPException(status_code=403, detail="Empresa inativa.")
    try:
        token = create_token(str(user.id), str(user.company_id), user.role)
    except SecurityError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    try:
        record_audit(db, action="LOGIN_SUCESSO", company_id=user.company_id, user_id=user.id,
                     ip_address=ip, details={"role": user.role})
    except Exception:
        logger.exception("Audit failure on successful login")
    return TokenResponse(access_token=token, expires_in=TOKEN_TTL_SECONDS)

@app.get("/auth/me")
def auth_me(actor: ActorContext = Depends(current_actor)):
    return {"user_id": actor.user_id, "company_id": actor.company_id, "email": actor.email}

@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ready", "version": VERSION}
    except Exception:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="Banco de dados indisponível.")


@app.post("/calcular")
def calcular(data: QuoteInput):
    width_mm, height_mm = dimensions_or_400(data)
    return calculate_or_400(width_mm, height_mm, data.quantity, data.model_code).__dict__


@app.post("/orcamentos", response_model=QuoteResponse)
def criar_orcamento(data: QuoteInput, db: Session = Depends(get_db), actor: ActorContext = Depends(current_actor)):
    width_mm, height_mm = dimensions_or_400(data)
    calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    code = "ORC-" + uuid4().hex[:10].upper()
    quote = Quote(
        code=code,
        model_code=calculated.model_code,
        width_mm=width_mm,
        height_mm=height_mm,
        quantity=data.quantity,
        status="RASCUNHO",
        company_id=actor.company_id,
    )
    repo = QuoteRepository(db)
    repo.add_calculated_items(quote, calculated)
    return repo.create(quote)


@app.get("/orcamentos/{quote_id}", response_model=QuoteResponse)
def consultar_orcamento(quote_id: int, db: Session = Depends(get_db), actor: ActorContext = Depends(current_actor)):
    quote = QuoteRepository(db).get(quote_id, actor.company_id)
    if not quote:
        raise HTTPException(404, "Orçamento não encontrado.")
    if hasattr(quote, "company_id"):
        assert_company(actor, quote.company_id)
    return quote


@app.post("/precos", response_model=PriceResponse)
def cadastrar_preco(data: PriceInput, db: Session = Depends(get_db), actor: ActorContext = Depends(current_actor)):
    return set_price(
        db, data.material_code, data.description, data.unit,
        data.price, data.supplier, data.variant, actor.company_id
    )


@app.get("/precos/{material_code}")
def consultar_preco(material_code: str, db: Session = Depends(get_db), variant: str = "PADRAO", actor: ActorContext = Depends(current_actor)):
    prices = get_current_prices(db, [material_code], variant, actor.company_id)
    if material_code not in prices:
        raise HTTPException(404, "Preço não cadastrado.")
    return {"material_code": material_code, "price": prices[material_code]}


@app.post("/custo")
def calcular_custo(data: CostInput, db: Session = Depends(get_db)):
    width_mm, height_mm = dimensions_or_400(data)
    calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    return calculate_cost(db, calculated)


@app.post("/corte")
def calcular_corte(data: CostInput, db: Session = Depends(get_db), kerf_mm: int = 3):
    width_mm, height_mm = dimensions_or_400(data)
    validate_kerf_or_400(kerf_mm)
    calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    out = []
    for code in sorted({p["material_code"] for p in calculated.parts}):
        pieces = []
        for part in calculated.parts:
            if part["material_code"] == code:
                pieces.extend([part["length_mm"]] * part["quantity"])
        p3 = get_current_prices(db, [code], "BARRA_3000").get(code)
        p6 = get_current_prices(db, [code], "BARRA_6000").get(code)
        result = optimize_profile(pieces, p3, p6, kerf_mm)
        out.append({
            "material_code": code,
            "bar_length_mm": result["bar_length_mm"],
            "bar_count": result["bar_count"],
            "kerf_mm": result["kerf_mm"],
            "total_scrap_mm": sum(bar.scrap_mm for bar in result["bars"]),
            "cost": result["cost"],
            "alternative_3000_bars": result["alternative_3000_bars"],
            "alternative_6000_bars": result["alternative_6000_bars"],
            "alternative_3000_cost": result["alternative_3000_cost"],
            "alternative_6000_cost": result["alternative_6000_cost"],
        })
    return {"model_code": data.model_code, "items": out}


@app.post("/custo-completo")
def calcular_custo_completo(data: CostInput, db: Session = Depends(get_db), kerf_mm: int = 3):
    width_mm, height_mm = dimensions_or_400(data)
    validate_kerf_or_400(kerf_mm)
    calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    return calculate_full_cost(db, calculated, kerf_mm)


@app.post("/formar-preco")
def formar_preco(data: PriceFormationInput, db: Session = Depends(get_db), kerf_mm: int = 3):
    width_mm, height_mm = dimensions_or_400(data)
    validate_pricing_input_or_400(data)
    validate_kerf_or_400(kerf_mm)
    calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    cost = calculate_full_cost(db, calculated, kerf_mm)

    if cost["status"] == "PRECO_INCOMPLETO" and not data.allow_provisional:
        raise HTTPException(409, {
            "message": "Custo incompleto: cadastre os preços faltantes antes de formar o preço final.",
            "missing_prices": cost["missing_prices"],
            "status": cost["status"],
        })

    result = form_price(
        material_cost=cost["total_cost"],
        labor_total=data.labor_per_unit * data.quantity,
        indirect_percent=data.indirect_percent,
        indirect_fixed=data.indirect_fixed,
        freight=data.freight,
        tax_percent=data.tax_percent,
        margin_percent=data.margin_percent,
        markup_percent=data.markup_percent,
    )
    result["cost_status"] = cost["status"]
    result["missing_prices"] = cost["missing_prices"]
    result["provisional"] = cost["status"] == "PRECO_INCOMPLETO"
    return result


@app.post("/orcamentos/{quote_id}/formar-preco")
def formar_preco_orcamento(
    quote_id: int,
    data: PriceFormationInput,
    db: Session = Depends(get_db),
    kerf_mm: int = 3,
    actor: ActorContext = Depends(current_actor),
):
    quote = QuoteRepository(db).get(quote_id, actor.company_id)
    if not quote:
        raise HTTPException(404, "Orçamento não encontrado.")
    if hasattr(quote, "company_id") and quote.company_id is not None:
        assert_company(actor, quote.company_id)
    if data.model_code != quote.model_code:
        raise HTTPException(400, "Modelo informado não corresponde ao orçamento.")
    validate_pricing_input_or_400(data)
    validate_kerf_or_400(kerf_mm)

    calculated = calculate_or_400(quote.width_mm, quote.height_mm, quote.quantity)
    cost = calculate_full_cost(db, calculated, kerf_mm)
    if cost["status"] == "PRECO_INCOMPLETO" and not data.allow_provisional:
        raise HTTPException(409, {
            "message": "Custo incompleto: o preço não foi gravado como definitivo.",
            "missing_prices": cost["missing_prices"],
            "status": cost["status"],
        })

    result = form_price(
        material_cost=cost["total_cost"],
        labor_total=data.labor_per_unit * quote.quantity,
        indirect_percent=data.indirect_percent,
        indirect_fixed=data.indirect_fixed,
        freight=data.freight,
        tax_percent=data.tax_percent,
        margin_percent=data.margin_percent,
        markup_percent=data.markup_percent,
    )
    quote.total_cost = result["base_cost"]
    quote.sale_price = result["sale_price"]
    repo = QuoteRepository(db)
    repo.add_price_snapshots(quote, cost.get("price_snapshots", []))
    repo.add_pricing_snapshot(quote, result)
    db.commit()
    db.refresh(quote)

    result.update({
        "quote_id": quote.id,
        "quote_code": quote.code,
        "cost_status": cost["status"],
        "missing_prices": cost["missing_prices"],
        "provisional": cost["status"] == "PRECO_INCOMPLETO",
    })
    return result


@app.get("/orcamentos/{quote_id}/formacao-preco")
def consultar_formacao_preco(quote_id: int, db: Session = Depends(get_db)):
    quote = QuoteRepository(db).get(quote_id)
    if not quote:
        raise HTTPException(404, "Orçamento não encontrado.")
    rows = db.query(QuotePricingSnapshot).filter(
        QuotePricingSnapshot.quote_id == quote_id
    ).order_by(QuotePricingSnapshot.id.desc()).all()
    return {
        "quote_id": quote.id,
        "quote_code": quote.code,
        "total_cost": quote.total_cost,
        "sale_price": quote.sale_price,
        "snapshots": [{
            "id": row.id,
            "method": row.method,
            "base_cost": row.base_cost,
            "sale_price": row.sale_price,
            "profit": row.profit,
            "effective_margin_percent": row.effective_margin_percent,
            "effective_markup_percent": row.effective_markup_percent,
            "tax_percent": row.tax_percent,
            "target_margin_percent": row.target_margin_percent,
            "target_markup_percent": row.target_markup_percent,
        } for row in rows],
    }


@app.post("/otimizar-vidro")
def otimizar_vidro(data: GlassOptimizationInput):
    pieces = [GlassPiece(p.width_mm, p.height_mm, p.quantity) for p in data.pieces]
    sheets = [GlassSheet(s.width_mm, s.height_mm, s.kerf_mm) for s in data.sheets]
    results = optimize_glass(pieces, sheets)
    price_map = None
    chosen = None
    if data.price_by_size:
        price_map = {}
        for key, value in data.price_by_size.items():
            try:
                w, h = [int(x) for x in key.lower().replace("x", " ").split()]
                price_map[(w, h)] = float(value)
            except Exception as exc:
                raise HTTPException(400, f"Formato de preço inválido: {key}. Use LxH.") from exc
        chosen = choose_by_cost(results, price_map)
    return {
        "alternatives": results,
        "selected_by_cost": chosen,
        "selection_reason": "MENOR_CUSTO" if chosen else "SEM_PRECO_DE_CHAPA",
    }


@app.post("/orcamento-completo")
def orcamento_completo(
    data: FullQuoteInput,
    db: Session = Depends(get_db),
    kerf_mm: int = 3,
):
    width_mm, height_mm = dimensions_or_400(data)
    validate_pricing_input_or_400(data)
    validate_kerf_or_400(kerf_mm)
    technical = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
    cost = calculate_full_cost(db, technical, kerf_mm)

    pricing = form_price(
        material_cost=cost["total_cost"],
        labor_total=data.labor_per_unit * data.quantity,
        indirect_percent=data.indirect_percent,
        indirect_fixed=data.indirect_fixed,
        freight=data.freight,
        tax_percent=data.tax_percent,
        margin_percent=data.margin_percent,
        markup_percent=data.markup_percent,
    )
    pricing.update({
        "cost_status": cost["status"],
        "missing_prices": cost["missing_prices"],
        "provisional": cost["status"] == "PRECO_INCOMPLETO",
    })

    glass_result = None
    if data.glass_sheet_width_mm and data.glass_sheet_height_mm:
        pieces = [
            GlassPiece(int(pane["width_mm"]), int(pane["height_mm"]), int(pane.get("quantity", 1)))
            for pane in technical.glass
        ]
        if pieces:
            sheet = GlassSheet(
                data.glass_sheet_width_mm,
                data.glass_sheet_height_mm,
                data.glass_sheet_kerf_mm,
            )
            alternatives = optimize_glass(pieces, [sheet])
            glass_result = alternatives[0]
            glass_result["sheet_total_cost"] = (
                round(glass_result["sheet_count"] * float(data.glass_sheet_price), 2)
                if data.glass_sheet_price is not None else None
            )

    return {
        "model_code": data.model_code,
        "input": {
            "unit": data.unit,
            "width": data.width,
            "height": data.height,
            "quantity": data.quantity,
            "width_mm": width_mm,
            "height_mm": height_mm,
        },
        "technical": technical,
        "cost": cost,
        "pricing": pricing,
        "glass_sheets": glass_result,
        "status": "PROVISORIO" if pricing["provisional"] else "PRONTO_PARA_ORCAMENTO",
    }



@app.post("/producao", response_model=ProductionOrderResponse)
def criar_producao(data: ProductionOrderInput, db: Session = Depends(get_db), actor: ActorContext = Depends(current_actor)):
    """Cria uma OP persistida pertencente à empresa autenticada.

    Quando baseada em orçamento, o orçamento precisa pertencer à mesma empresa.
    """
    quote = None
    if data.quote_id is not None:
        quote = QuoteRepository(db).get(data.quote_id, actor.company_id)
        if quote is None:
            raise HTTPException(404, "Orçamento não encontrado.")
        model_code = quote.model_code
        input_snapshot = {
            "model_code": quote.model_code, "unit": "mm",
            "width": quote.width_mm, "height": quote.height_mm, "quantity": quote.quantity,
        }
        technical_snapshot = {
            "source": "orcamento",
            "quote_id": quote.id,
            "quote_code": quote.code,
            "parts": [
                {
                    "material_code": item.material_code,
                    "cut_type": item.cut_type,
                    "length_mm": item.length_mm,
                    "quantity": item.quantity,
                }
                for item in quote.items
            ],
            "rule_snapshots": [
                {
                    "rule_code": snap.rule_code,
                    "expression_snapshot": snap.expression_snapshot,
                    "value_snapshot": snap.value_snapshot,
                }
                for snap in quote.snapshots
            ],
        }
        reference = data.reference or quote.code
    else:
        if not all(v is not None for v in (data.model_code, data.unit, data.width, data.height, data.quantity)):
            raise HTTPException(400, "Informe quote_id ou os dados completos da OP.")
        try:
            width_mm, height_mm = normalize_dimensions(data.model_code, data.unit, data.width, data.height)
            calculated = calculate_or_400(width_mm, height_mm, data.quantity, data.model_code)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        model_code = data.model_code
        input_snapshot = {
            "model_code": data.model_code, "unit": data.unit,
            "width": data.width, "height": data.height, "quantity": data.quantity,
            "width_mm": width_mm, "height_mm": height_mm,
        }
        technical_snapshot = {"parts": calculated.parts, "rule_snapshots": calculated.rule_snapshots}
        reference = data.reference or "OP-" + uuid4().hex[:10].upper()

    import json
    order = ProductionOrder(
        company_id=actor.company_id, quote_id=quote.id if quote else None,
        reference=reference, status="ABERTA", model_code=model_code,
        input_snapshot=json.dumps(input_snapshot, ensure_ascii=False),
        technical_snapshot=json.dumps(technical_snapshot, ensure_ascii=False),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    try:
        record_audit(db, action="OP_CRIADA", company_id=actor.company_id, user_id=actor.user_id,
                     resource_type="ProductionOrder", resource_id=order.id,
                     details={"reference": order.reference, "quote_id": order.quote_id})
    except Exception:
        logger.exception("Audit failure on production creation")
    return order


@app.get("/producao/{production_id}", response_model=ProductionOrderResponse)
def consultar_producao(
    production_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(current_actor),
):
    """Consulta uma OP somente dentro da empresa autenticada."""
    order = db.execute(
        select(ProductionOrder).where(
            ProductionOrder.id == production_id,
            ProductionOrder.company_id == actor.company_id,
        )
    ).scalar_one_or_none()
    if order is None:
        raise HTTPException(404, "Ordem não encontrada.")
    return order


@app.post("/producao/{production_id}/reservar")
def reservar_producao(production_id: int, payload: dict,
                      db: Session = Depends(get_db),
                      actor: ActorContext = Depends(current_actor)):
    """Cria e vincula uma reserva explícita à OP dentro da mesma transação."""
    allocations_raw = payload.get("allocations") or []
    reference = str(payload.get("reference") or f"OP-{production_id}")
    allocations=[]
    try:
        for x in allocations_raw:
            allocations.append((int(x["item_id"]), x["quantity"]))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(400, "allocations inválidas.")
    if not allocations:
        raise HTTPException(400, "Informe pelo menos uma alocação.")
    try:
        db.rollback()  # current_actor may have opened a read transaction
        with db.begin():
            order=db.execute(select(ProductionOrder).where(
                ProductionOrder.id==production_id,
                ProductionOrder.company_id==actor.company_id
            ).with_for_update()).scalar_one_or_none()
            if order is None: raise HTTPException(404, "Ordem não encontrada.")
            if order.status != "ABERTA": raise HTTPException(409, "Somente OP ABERTA pode receber reserva.")
            if order.reservation_id is not None: raise HTTPException(409, "OP já possui reserva vinculada.")
            reservation=InventoryTransactionRepository(db).reserve_atomically(
                actor.company_id, allocations, reference
            )
            order.reservation_id=reservation.id
            db.flush()
        try:
            record_audit(db, action="OP_RESERVADA", company_id=actor.company_id, user_id=actor.user_id,
                         resource_type="ProductionOrder", resource_id=order.id,
                         details={"reservation_id": reservation.id})
        except Exception:
            logger.exception("Audit failure on production reservation")
        return {"production_id": order.id, "reservation_id": reservation.id,
                "production_status": order.status, "reservation_status": reservation.status}
    except HTTPException:
        raise
    except TransactionFlowError as exc:
        raise HTTPException(409, str(exc))

@app.post("/producao/{production_id}/iniciar")
def iniciar_producao_persistida(production_id: int,
                                db: Session = Depends(get_db),
                                actor: ActorContext = Depends(current_actor)):
    try:
        db.rollback()  # current_actor may have opened a read transaction
        with db.begin():
            order=db.execute(select(ProductionOrder).where(
                ProductionOrder.id==production_id,
                ProductionOrder.company_id==actor.company_id
            ).with_for_update()).scalar_one_or_none()
            if order is None: raise HTTPException(404, "Ordem não encontrada.")
            if order.status != "ABERTA": raise HTTPException(409, "Transição inválida para produção.")
            if order.reservation_id is None: raise HTTPException(409, "OP sem reserva.")
            reservation=db.execute(select(StockReservation).where(
                StockReservation.id==order.reservation_id,
                StockReservation.company_id==actor.company_id
            ).with_for_update()).scalar_one_or_none()
            if reservation is None: raise HTTPException(409, "Reserva não encontrada.")
            if reservation.status != "ATIVA": raise HTTPException(409, "Reserva não está ATIVA.")
            order.status="EM_PRODUCAO"
            db.flush()
        try:
            record_audit(db, action="OP_INICIADA", company_id=actor.company_id, user_id=actor.user_id,
                         resource_type="ProductionOrder", resource_id=order.id,
                         details={"reservation_id": reservation.id})
        except Exception:
            logger.exception("Audit failure on production start")
        return {"production_id": order.id, "production_status": order.status,
                "reservation_id": reservation.id, "reservation_status": reservation.status}
    except HTTPException:
        raise

@app.post("/producao/{production_id}/concluir")
def concluir_producao_persistida(production_id: int,
                                 db: Session = Depends(get_db),
                                 actor: ActorContext = Depends(current_actor)):
    try:
        db.rollback()  # current_actor may have opened a read transaction
        with db.begin():
            order=db.execute(select(ProductionOrder).where(
                ProductionOrder.id==production_id,
                ProductionOrder.company_id==actor.company_id
            ).with_for_update()).scalar_one_or_none()
            if order is None: raise HTTPException(404, "Ordem não encontrada.")
            if order.status != "EM_PRODUCAO": raise HTTPException(409, "OP precisa estar EM_PRODUCAO.")
            if order.reservation_id is None: raise HTTPException(409, "OP sem reserva.")
            reservation=InventoryTransactionRepository(db).consume_reservation_atomically(
                actor.company_id, order.reservation_id, f"CONCLUSAO-OP-{order.id}"
            )
            order.status="CONCLUIDA"
            db.flush()
        try:
            record_audit(db, action="OP_CONCLUIDA", company_id=actor.company_id, user_id=actor.user_id,
                         resource_type="ProductionOrder", resource_id=order.id,
                         details={"reservation_id": reservation.id})
        except Exception:
            logger.exception("Audit failure on production completion")
        return {"production_id": order.id, "production_status": order.status,
                "reservation_id": reservation.id, "reservation_status": reservation.status}
    except HTTPException:
        raise
    except TransactionFlowError as exc:
        raise HTTPException(409, str(exc))

@app.post("/workflow/aprovar")
def workflow_aprovar(payload: dict):
    return approve_and_prepare(payload.get("quote_status",""), payload.get("reservation_status"))

@app.post("/workflow/iniciar-producao")
def workflow_iniciar(payload: dict):
    return start_production(payload.get("production_status",""), payload.get("reservation_status",""))

@app.post("/workflow/concluir-producao")
def workflow_concluir(payload: dict):
    return finish_production(payload.get("production_status",""), payload.get("reservation_status",""))
