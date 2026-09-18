from sqlalchemy.orm import Session
from app.models.entities import Quote, QuoteItem, QuoteRuleSnapshot, QuotePriceSnapshot, QuotePricingSnapshot

class QuoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, quote: Quote) -> Quote:
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        return quote

    def get(self, quote_id: int, company_id: int | None = None) -> Quote | None:
        query = self.db.query(Quote).filter(Quote.id == quote_id)
        if company_id is not None:
            query = query.filter(Quote.company_id == company_id)
        return query.first()

    def add_calculated_items(self, quote: Quote, calculated) -> None:
        for item in calculated.parts:
            quote.items.append(QuoteItem(
                material_code=item["material_code"],
                cut_type=item["cut_type"],
                length_mm=item["length_mm"],
                quantity=item["quantity"],
                unit_price=0,
                total_price=0,
            ))
        for snap in calculated.rule_snapshots:
            quote.snapshots.append(QuoteRuleSnapshot(
                rule_code=snap["rule_code"],
                expression_snapshot=snap["expression_snapshot"],
                value_snapshot=snap["value_snapshot"],
            ))


    def add_price_snapshots(self, quote: Quote, snapshots: list[dict]) -> None:
        for s in snapshots:
            quote_price = QuotePriceSnapshot(
                material_code=s["material_code"],
                variant=s["variant"],
                unit=s["unit"],
                unit_price=s["unit_price"],
                supplier=s.get("supplier"),
            )
            quote.price_snapshots.append(quote_price)

    def add_pricing_snapshot(self, quote: Quote, result: dict) -> None:
        quote.pricing_snapshots.append(QuotePricingSnapshot(
            quote_id=quote.id,
            method=result["method"],
            material_cost=result["material_cost"],
            labor_total=result["labor_total"],
            indirect_variable=result["indirect_variable"],
            indirect_fixed=result["indirect_fixed"],
            freight=result["freight"],
            tax_percent=result["tax_percent"],
            tax_amount=result["tax_amount"],
            target_margin_percent=result["target_margin_percent"],
            target_markup_percent=result["target_markup_percent"],
            base_cost=result["base_cost"],
            sale_price=result["sale_price"],
            profit=result["profit"],
            effective_margin_percent=result["effective_margin_percent"],
            effective_markup_percent=result["effective_markup_percent"],
        ))
