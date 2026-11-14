"""Tabs for the stored procedure, the function, the account view and the audit trigger."""

from datetime import date

import ipywidgets as w

from berka_bank.db import Database, error_text
from berka_bank.routines import NO_LOAN, account_overview, account_statement
from berka_bank.ui.widgets import (
    FREQUENCY,
    actions,
    button,
    callout,
    field,
    grid,
    kpi,
    kpi_row,
    message,
    money_html,
    output,
    render,
    section,
    table,
)


def statement_panel(db: Database):
    account = field(w.IntText, "Cuenta", value=576)
    start = field(w.DatePicker, "Desde", value=date(1997, 1, 1))
    end = field(w.DatePicker, "Hasta", value=date(1997, 12, 31))
    btn, out = button("Generar extracto", "file-text", "primary"), output()

    def run(_=None):
        try:
            summary, detail = account_statement(db, account.value, start.value, end.value)
            s = summary.iloc[0]
            info = (
                f"Cuenta <b>{int(s.Identificador_Cuenta)}</b> · Sucursal <b>{s.Sucursal}</b> · "
                f"Estado de cuenta {FREQUENCY.get(s.Frecuencia, s.Frecuencia).lower()} · "
                f"{s.Desde} → {s.Hasta}"
            )
            tiles = kpi_row(
                kpi("Saldo inicial", money_html(s.Saldo_Inicial)),
                kpi("Ingresos", money_html(s.Total_Ingresos, "+ "), tone="ok"),
                kpi("Egresos", money_html(s.Total_Egresos, "− "), tone="danger"),
                kpi("Movimientos", f"{int(s.Num_Movimientos):,}", tone="teal"),
                kpi("Saldo final", money_html(s.Saldo_Final), tone="strong"),
            )
            render(
                out,
                callout(info, "info"),
                tiles,
                f'<h4 class="bk-h4">Detalle de movimientos ({len(detail):,})</h4>',
                table(detail),
            )
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Extracto bancario",
        "Llama a <code>CALL sp_extracto_cuenta(cuenta, desde, hasta)</code>. Devuelve el resumen del periodo "
        "y el detalle de movimientos.",
        grid(account, start, end, cols=3),
        actions(btn),
        out,
        badge="Procedimiento",
        badge_tone="gold",
    )


def balance_panel(db: Database):
    account = field(w.IntText, "Cuenta", value=576)
    at = field(w.DatePicker, "A la fecha (vacío = actual)")
    btn, out = button("Consultar saldo", "money", "primary"), output()

    def run(_=None):
        try:
            value = db.execute("SELECT fn_saldo_cuenta(:c, :f)", {"c": account.value, "f": at.value}).scalar()
            when = at.value.isoformat() if at.value else "hoy (último movimiento)"
            render(
                out,
                kpi_row(
                    kpi(f"Saldo · cuenta {account.value}", money_html(value), f"A la fecha: {when}", tone="strong")
                ),
            )
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Saldo de una cuenta",
        "Llama a <code>SELECT fn_saldo_cuenta(cuenta, fecha)</code>. Si la cuenta no tiene movimientos, el saldo es 0.",
        grid(account, at),
        actions(btn),
        out,
        badge="Función",
        badge_tone="gold",
    )


def audit_panel(db: Database):
    btn, out = button("Refrescar", "refresh", "info"), output()

    def run(_=None):
        try:
            df = db.query("SELECT * FROM Auditoria_Cliente ORDER BY Id_Auditoria DESC LIMIT 100")
            message(out, f"<b>{len(df)}</b> registro(s) de auditoría, los más recientes primero.", "info", df)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Auditoría de clientes",
        "Registros que inserta <code>trg_cliente_after_update</code> cada vez que cambia un cliente: "
        "valores anteriores y nuevos, usuario y fecha.",
        actions(btn),
        out,
        badge="Trigger",
        badge_tone="gold",
    )


def overview_panel(db: Database):
    regions = db.query("SELECT DISTINCT Region_que_pertenece AS r FROM Distrito ORDER BY 1")["r"]
    account = field(w.IntText, "Cuenta (0 = todas)", value=0)
    region = field(w.Dropdown, "Región", options=[("(todas)", "")] + [(r, r) for r in regions], value="")
    states = db.query("SELECT Codigo_Estado AS c, Descripcion_Estado AS d FROM Estado_Prestamo ORDER BY 1")
    loan = field(
        w.Dropdown,
        "Préstamo",
        options=[("(todos)", ""), ("Sin préstamo", NO_LOAN)] + [(f"{r.c} · {r.d}", r.c) for r in states.itertuples()],
        value="",
    )
    btn, out = button("Consultar", "search", "primary"), output()

    def run(_=None):
        try:
            df = account_overview(db, account.value, region.value, loan.value)
            render(
                out,
                kpi_row(
                    kpi("Cuentas", f"{len(df):,}", tone="teal"),
                    kpi("Con préstamo", f"{int(df.Codigo_Prestamos.notna().sum()):,}", tone="gold"),
                    kpi("Saldo total", money_html(df.Saldo_Actual.sum()), tone="strong"),
                ),
                table(df),
            )
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Resumen de cuentas",
        "Consulta la vista <code>vw_resumen_cuenta</code>: una fila por cuenta con sucursal, titular, tarjeta, "
        "préstamo y saldo actual.",
        grid(account, region, loan, cols=3),
        actions(btn),
        out,
        badge="Vista",
        badge_tone="gold",
    )
