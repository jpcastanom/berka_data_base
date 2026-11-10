"""Assemble the full interface. Runs inside a Jupyter kernel (Voilà, JupyterLab or VS Code)."""

import ipywidgets as w
from IPython.display import display

from berka_bank.config import load_settings
from berka_bank.db import Database
from berka_bank.ui import clients, home, routines, transactions
from berka_bank.ui.theme import theme
from berka_bank.ui.widgets import Catalogs, tabs

LOGO = (
    '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.7" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/>'
    '<path d="M3 20h18"/></svg>'
)


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
            ("Auditoría", routines.audit_panel(db)),
        ]
    )
    root = w.VBox([theme(), header(db), app, w.HTML(FOOTER)])
    root.add_class("bk-root")
    return root


def show(db: Database | None = None) -> None:
    """Display the interface in the current notebook/Voilà page."""
    display(build(db or Database(load_settings())))
