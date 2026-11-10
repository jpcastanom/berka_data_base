"""MySQL connection helpers (SQLAlchemy engines + execute/query shortcuts)."""

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from berka_bank.config import Settings


class Database:
    """Holds one engine for the server (no database selected) and one for the model DB."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.server = self._engine(None)
        self._model: Engine | None = None

    def _engine(self, database: str | None) -> Engine:
        s = self.settings
        url = URL.create(
            "mysql+pymysql",
            username=s.user,
            password=s.password,
            host=s.host,
            port=s.port,
            database=database,
            query={"charset": "utf8mb4"},
        )
        return create_engine(url, pool_pre_ping=True)

    @property
    def model(self) -> Engine:
        """Engine bound to the model database (created lazily, after the DB exists)."""
        if self._model is None:
            self._model = self._engine(self.settings.model_db)
        return self._model

    def execute(self, sql: str, params: dict | None = None, engine: Engine | None = None):
        """Run one statement inside a transaction (commit on success, rollback on error)."""
        with (engine or self.model).begin() as con:
            return con.execute(text(sql), params or {})

    def query(self, sql: str, params: dict | None = None, engine: Engine | None = None) -> pd.DataFrame:
        """Return the result of a SELECT as a DataFrame."""
        with (engine or self.model).connect() as con:
            return pd.read_sql(text(sql), con, params=params or {})

    def raw_connection(self, database: str | None = None) -> pymysql.Connection:
        """Plain PyMySQL connection, for big scripts and multi-result procedures."""
        s = self.settings
        return pymysql.connect(
            host=s.host, port=s.port, user=s.user, password=s.password, database=database, charset="utf8mb4"
        )

    def version(self) -> str:
        with self.server.connect() as con:
            return con.execute(text("SELECT VERSION()")).scalar()


ERROR_HINTS = {
    1451: "No se puede borrar: otros registros dependen de este (llave foránea).",
    1452: "El valor de la llave foránea no existe (p. ej. la cuenta o el distrito).",
    3819: "Se viola una restricción CHECK del modelo.",
    1048: "Falta un campo obligatorio.",
}


def error_text(e: Exception) -> str:
    """Readable (Spanish, shown in the UI) message from a MySQL exception."""
    orig = getattr(e, "orig", e)
    args = getattr(orig, "args", ())
    if len(args) >= 2:
        code, message = args[0], args[1]
        hint = ERROR_HINTS.get(code, "")
        return f"Error {code}: {message}" + (f" — {hint}" if hint else "")
    return str(orig)
