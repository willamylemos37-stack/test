from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "migrations"


def test_canonical_postgres_migrations_are_complete():
    names = [p.name for p in sorted(MIGRATIONS.glob("*.sql"))]
    assert names == [
        "0001_baseline_v5_15.sql",
        "0002_upgrade_legacy_v4_6_to_v5_15.sql",
        "0003_seed_model_001.sql",
        "0004_inventory.sql",
        "0005_reservations.sql",
        "0006_production_orders.sql",
        "0007_workflow_indexes.sql",
        "0008_transactional_workflow.sql",
        "0009_reserved_quantity.sql",
        "0010_tenant_prices.sql",
        "0011_production_reservation.sql",
        "0012_quote_company.sql",
        "0013_audit_events.sql",
            "0014_product_type.sql",
            "0015_glass_rule_model_001.sql",
            "0016_model_001_technical_rules.sql",
            "0017_glass_rule_model_001_direct.sql",
            "0018_mp309_rules_2_4_leaves.sql",
            "0019_model_002_4_leaves.sql",
    ]


def test_postgres_runner_points_to_canonical_migrations():
    text = (ROOT / "scripts" / "migrate.py").read_text(encoding="utf-8")
    assert 'ROOT / "database" / "migrations"' in text
