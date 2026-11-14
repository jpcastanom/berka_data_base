"""'Inicio' tab: dashboard with totals and distributions read from the model."""

from pathlib import Path

import ipywidgets as w

from berka_bank.db import Database, error_text
from berka_bank.ui.widgets import (
    MOVEMENT,
    actions,
    bars,
    button,
    callout,
    kpi,
    kpi_row,
    output,
    render,
    section,
)

HERO_SVG = (Path(__file__).parent / "hero.svg").read_text(encoding="utf-8")
HERO = (
    '<div class="bk-hero"><div><h1>Banco Berka:<br>clientes, cuentas<br>y operaciones</h1>'
    "<p>Consulta, registra y audita la información del banco sobre MySQL.</p>"
    '<div class="bk-hero-tags"><span>Función</span><span>Procedimiento</span><span>Vista</span><span>2 triggers</span></div>'
    f"</div><div>{HERO_SVG}</div></div>"
)

SQL_TOTALS = """
    SELECT (SELECT COUNT(*) FROM Cliente)         AS clientes,
           (SELECT COUNT(*) FROM Cuenta)          AS cuentas,
           (SELECT COUNT(*) FROM Transacciones)   AS transacciones,
           (SELECT COUNT(*) FROM Prestamos)       AS prestamos,
           (SELECT COUNT(*) FROM Tarjeta)         AS tarjetas
"""
SQL_MOVEMENTS = (
    "SELECT Tipo_Movimiento AS tipo, COUNT(*) AS n FROM Transacciones GROUP BY Tipo_Movimiento ORDER BY n DESC"
)
SQL_LOANS = """
    SELECT e.Codigo_Estado AS codigo, e.Descripcion_Estado AS descripcion, COUNT(p.Codigo_Prestamos) AS n
    FROM Estado_Prestamo e LEFT JOIN Prestamos p ON p.Codigo_Estado = e.Codigo_Estado
    GROUP BY e.Codigo_Estado, e.Descripcion_Estado ORDER BY e.Codigo_Estado
"""
MOVEMENT_TONE = {"PRIJEM": "ok", "VYDAJ": "danger", "VYBER": "gold"}
LOAN_TONE = {"A": "ok", "B": "danger", "C": "", "D": "gold"}

GUIDE = """
<ol class="bk-steps">
  <li><b>Clientes</b> y <b>Transacciones</b>: consultar, insertar, actualizar y borrar registros.</li>
  <li><b>Extracto</b>: ejecuta el procedimiento <code>sp_extracto_cuenta</code>.</li>
  <li><b>Saldo</b>: ejecuta la función <code>fn_saldo_cuenta</code>.</li>
  <li><b>Vista</b>: consulta la vista <code>vw_resumen_cuenta</code>: una fila por cuenta.</li>
  <li><b>Auditoría</b>: registros del trigger <code>trg_cliente_after_update</code>.</li>
</ol>
"""


def build(db: Database):
    refresh, out = button("Actualizar resumen", "refresh", "info"), output()

    def load(_=None):
        try:
            t = db.query(SQL_TOTALS).iloc[0]
            movements = db.query(SQL_MOVEMENTS)
            loans = db.query(SQL_LOANS)
        except Exception as e:
            return render(out, callout(error_text(e), "error"))

        tiles = kpi_row(
            kpi("Clientes", f"{int(t.clientes):,}"),
            kpi("Cuentas", f"{int(t.cuentas):,}", tone="teal"),
            kpi("Transacciones", f"{int(t.transacciones):,}", tone="strong"),
            kpi("Préstamos", f"{int(t.prestamos):,}", tone="gold"),
            kpi("Tarjetas", f"{int(t.tarjetas):,}", tone="ok"),
        )
        mov_bars = bars(
            [(MOVEMENT.get(r.tipo, r.tipo), int(r.n), MOVEMENT_TONE.get(r.tipo, "")) for r in movements.itertuples()]
        )
        loan_bars = bars(
            [(f"{r.codigo} · {r.descripcion}", int(r.n), LOAN_TONE.get(r.codigo, "")) for r in loans.itertuples()]
        )
        two = (
            '<div class="bk-two">'
            f'<div class="bk-card"><h4 class="bk-h4" style="margin-bottom:14px">Movimientos por tipo</h4>{mov_bars}</div>'
            f'<div class="bk-card"><h4 class="bk-h4" style="margin-bottom:14px">Estado de los préstamos</h4>{loan_bars}</div>'
            "</div>"
        )
        render(out, tiles, two)

    refresh.on_click(load)
    load()
    panel = section(
        "Resumen del banco",
        "Vista general de los datos migrados al modelo físico <code>banco_berka</code>.",
        out,
        actions(refresh),
        w.HTML(GUIDE),
        badge="Dashboard",
    )
    return w.VBox([w.HTML(HERO), panel])  # the hero sits on the page, not inside a card
