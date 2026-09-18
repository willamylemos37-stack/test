from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def run_script(name, *args, env=None):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / name), *args], cwd=ROOT, capture_output=True, text=True, env=env)

def test_backup_requires_postgres_url():
    r = run_script("backup_postgres.py", "x.dump", env={"PATH": "/usr/bin"})
    assert r.returncode == 2
    assert "DATABASE_URL" in r.stderr

def test_restore_requires_explicit_confirmation(tmp_path):
    dump = tmp_path / "x.dump"; dump.write_bytes(b"x")
    env = {"DATABASE_URL": "postgresql://x", "PATH": "/usr/bin"}
    r = run_script("restore_postgres.py", str(dump), env=env)
    assert r.returncode == 2
    assert "RESTORE_CONFIRM" in r.stderr

def test_restore_requires_existing_file():
    env = {"DATABASE_URL": "postgresql://x", "RESTORE_CONFIRM": "YES", "PATH": "/usr/bin"}
    r = run_script("restore_postgres.py", "/does/not/exist.dump", env=env)
    assert r.returncode == 2

def test_operational_doc_exists():
    assert (ROOT / "docs" / "ETAPA_53_OPERACAO_BACKUP_ERROS.md").is_file()
