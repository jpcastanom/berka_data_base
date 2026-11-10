"""Project settings, read from config/config.toml (falls back to config.example.toml)."""

import getpass
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    user: str
    password: str
    staging_db: str
    model_db: str
    berka_sql: Path
    reload_staging: bool
    rebuild_model: bool
    ui_port: int
    open_browser: bool


def config_path() -> Path:
    """BERKA_CONFIG env var > config/config.toml > config/config.example.toml."""
    if env := os.environ.get("BERKA_CONFIG"):
        return Path(env)
    local = CONFIG_DIR / "config.toml"
    return local if local.exists() else CONFIG_DIR / "config.example.toml"


def resolve_password(configured: str) -> str:
    """Config value > MYSQL_PASSWORD env var > interactive prompt."""
    if configured:
        return configured
    if env := os.environ.get("MYSQL_PASSWORD"):
        return env
    # Terminal or Jupyter notebook: ask once. (The Voilà kernel always gets it through MYSQL_PASSWORD.)
    if (sys.stdin and sys.stdin.isatty()) or "ipykernel" in sys.modules:
        return getpass.getpass("Contraseña de MySQL: ")
    raise RuntimeError("No MySQL password: set it in config/config.toml or in the MYSQL_PASSWORD environment variable.")


def load_settings(path: Path | None = None) -> Settings:
    path = path or config_path()
    with open(path, "rb") as f:
        cfg = tomllib.load(f)

    mysql, dbs = cfg.get("mysql", {}), cfg.get("databases", {})
    data, pipe, ui = cfg.get("data", {}), cfg.get("pipeline", {}), cfg.get("ui", {})

    berka_sql = Path(data.get("berka_sql", "data/berka.sql.gz"))
    if not berka_sql.is_absolute():
        berka_sql = PROJECT_ROOT / berka_sql

    return Settings(
        host=mysql.get("host", "localhost"),
        port=int(mysql.get("port", 3306)),
        user=mysql.get("user", "root"),
        password=resolve_password(mysql.get("password", "")),
        staging_db=dbs.get("staging", "berka"),
        model_db=dbs.get("model", "banco_berka"),
        berka_sql=berka_sql,
        reload_staging=bool(pipe.get("reload_staging", False)),
        rebuild_model=bool(pipe.get("rebuild_model", False)),
        ui_port=int(ui.get("port", 8866)),
        open_browser=bool(ui.get("open_browser", True)),
    )
