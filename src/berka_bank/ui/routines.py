"""Tabs for the stored procedure, the function and the audit trigger."""

from datetime import date

import ipywidgets as w
from IPython.display import HTML, display

from berka_bank.db import Database, error_text
from berka_bank.routines import account_statement
from berka_bank.ui.widgets import button, field, message, section


def statement_panel(db: Database):
    account = field(w.IntText, "Cuenta", value=576)
    start = field(w.DatePicker, "Desde", value=date(1997, 1, 1))
    end = field(w.DatePicker, "Hasta", value=date(1997, 12, 31))
    btn, out = button("Generar extracto", "file-text", "primary"), w.Output()

    def run(_=None):
        try:
            summary, detail = account_statement(db, account.value, start.value, end.value)
            message(out, "Resumen del periodo:", "info", summary)
            with out:
                display(HTML(f"<b>Detalle ({len(detail)} movimientos):</b>"))
                display(detail)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Extracto bancario",
        "Llama a <code>CALL sp_extracto_cuenta(cuenta, desde, hasta)</code>.",
        account,
        start,
        end,
        btn,
        out,
    )


def balance_panel(db: Database):
    account = field(w.IntText, "Cuenta", value=576)
    at = field(w.DatePicker, "A la fecha (vacío = actual)")
    btn, out = button("Consultar saldo", "money", "primary"), w.Output()

    def run(_=None):
        try:
            value = db.execute("SELECT fn_saldo_cuenta(:c, :f)", {"c": account.value, "f": at.value}).scalar()
            when = at.value.isoformat() if at.value else "hoy (último movimiento)"
            message(out, f"Saldo de la cuenta <b>{account.value}</b> a {when}: <b>{value:,.2f} Kč</b>")
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Saldo de una cuenta", "Llama a <code>SELECT fn_saldo_cuenta(cuenta, fecha)</code>.", account, at, btn, out
    )


def audit_panel(db: Database):
    btn, out = button("Refrescar", "refresh", "info"), w.Output()

    def run(_=None):
        try:
            df = db.query("SELECT * FROM Auditoria_Cliente ORDER BY Id_Auditoria DESC LIMIT 100")
            message(out, f"{len(df)} registro(s) de auditoría (más recientes primero).", "info", df)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section("Auditoría de clientes", "Registros que inserta <code>trg_cliente_after_update</code>.", btn, out)
