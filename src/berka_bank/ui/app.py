"""Assemble the full interface. Runs inside a Jupyter kernel (Voilà, JupyterLab or VS Code)."""

import ipywidgets as w
from IPython.display import display

from berka_bank.config import load_settings
from berka_bank.db import Database
from berka_bank.ui import clients, routines, transactions
from berka_bank.ui.widgets import Catalogs, tabs


def build(db: Database) -> w.Widget:
    cat = Catalogs.load(db)
    s = db.settings
    app = tabs(
        [
            ("Clientes", clients.build(db, cat)),
            ("Transacciones", transactions.build(db, cat)),
            ("Extracto (procedimiento)", routines.statement_panel(db)),
            ("Saldo (función)", routines.balance_panel(db)),
            ("Auditoría (trigger)", routines.audit_panel(db)),
        ]
    )
    return w.VBox(
        [
            w.HTML(
                '<h2 style="margin:0">Banco Berka — Gestión de clientes y operaciones</h2>'
                f"<small>Base de datos: <code>{s.model_db}</code> en {s.host}:{s.port}</small>"
            ),
            app,
        ]
    )


def show(db: Database | None = None) -> None:
    """Display the interface in the current notebook/Voilà page."""
    display(build(db or Database(load_settings())))
