"""Assemble the full interface. Runs inside a Jupyter kernel (Voilà, JupyterLab or VS Code)."""

from pathlib import Path

import ipywidgets as w
from IPython.display import display

from berka_bank.config import load_settings
from berka_bank.db import Database
from berka_bank.ui import clients, home, routines, transactions
from berka_bank.ui.theme import theme
from berka_bank.ui.widgets import Catalogs, tabs

LOGO = (Path(__file__).parent / "logo.svg").read_text(encoding="utf-8")


def header(db: Database) -> w.HTML:
    s = db.settings
    return w.HTML(
        '<div class="bk-header">'
        f'<div class="bk-brand"><div class="bk-logo">{LOGO}</div><div>'
        '<div class="bk-title">Banco Berka</div>'
        '<div class="bk-subtitle">Gestión de clientes y operaciones bancarias</div></div></div>'
        f'<div class="bk-conn"><span class="bk-dot"></span>Conectado<small>{s.model_db} · {s.host}:{s.port}</small></div>'
        "</div>"
    )


FOOTER = (
    '<div class="bk-footer">Bases de Datos · Tercera entrega · '
    "Juan Felipe Molano Vega y Juan Pablo Castaño Morales</div>"
)


def build(db: Database) -> w.Widget:
    cat = Catalogs.load(db)
    app = tabs(
        [
            ("Inicio", home.build(db)),
            ("Clientes", clients.build(db, cat)),
            ("Transacciones", transactions.build(db, cat)),
            ("Extracto", routines.statement_panel(db)),
            ("Saldo", routines.balance_panel(db)),
            ("Vista", routines.overview_panel(db)),
            ("Auditoría", routines.audit_panel(db)),
        ]
    )
    root = w.VBox([theme(), header(db), app, w.HTML(FOOTER)])
    root.add_class("bk-root")
    return root


def show(db: Database | None = None) -> None:
    """Display the interface in the current notebook/Voilà page."""
    display(build(db or Database(load_settings())))
