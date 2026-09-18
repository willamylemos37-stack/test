from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "migrations"

def test_migrations_are_ordered_and_have_unique_checksums():
    files = sorted(MIGRATIONS.glob("*.sql"))
    assert [p.name[:4] for p in files] == [f"{i:04d}" for i in range(1, 20)]
    hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
    assert len(hashes) == len(set(hashes))
    assert all(p.read_text(encoding="utf-8").strip() for p in files)

def test_model_001_seed_never_registers_mp352():
    text = (MIGRATIONS / "0003_seed_model_001.sql").read_text(encoding="utf-8")
    assert "('MP-352'" not in text
    assert "AND material_code='MP-352'" in text
    assert "MOD-001" in text


def test_migration_runner_accepts_sqlalchemy_psycopg_url():
    text = (ROOT / "scripts" / "migrate.py").read_text(encoding="utf-8")
    assert 'postgresql+psycopg://' in text
    assert 'psycopg_url' in text


def test_migration_runner_has_new_database_legacy_skip_guard():
    text = (ROOT / "scripts" / "migrate.py").read_text(encoding="utf8")
    assert "0002_upgrade_legacy_v4_6_to_v5_15.sql" in text
    assert "is_new_schema_without_legacy_columns" in text
    assert "information_schema.columns" in text


def test_mp309_rules_migration_contains_two_and_four_leaf_rules():
    from pathlib import Path
    text = Path('database/migrations/0018_mp309_rules_2_4_leaves.sql').read_text(encoding='utf-8')
    assert "L105_2" in text
    assert "(L - 105) / 2" in text
    assert "L178_4" in text
    assert "(L - 178) / 4" in text
