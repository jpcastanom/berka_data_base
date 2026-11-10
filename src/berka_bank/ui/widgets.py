"""Reusable building blocks: form fields, cards, tables, KPIs, bars and dropdown catalogs."""

import datetime as dt
import numbers
from dataclasses import dataclass
from decimal import Decimal
from html import escape
from typing import ClassVar

import ipywidgets as w
import pandas as pd
from IPython.display import HTML, clear_output, display

from berka_bank.db import Database

FREQUENCY = {
    "POPLATEK MESICNE": "Mensual",
    "POPLATEK TYDNE": "Semanal",
    "POPLATEK PO OBRATU": "Por transacción",
}
MOVEMENT = {"PRIJEM": "Ingresos", "VYDAJ": "Egresos", "VYBER": "Retiros en efectivo"}
COUNT_PREFIXES = ("Num", "Cantidad", "Total", "Filas", "Habitantes")


# ---------------------------------------------------------------- form fields
def field(cls, label, **kw):
    """Input widget whose label is rendered above it by `grid` / `labeled`."""
    widget = cls(description="", layout=w.Layout(width="100%"), **kw)
    widget.add_class("bk-input")
    widget._bk_label = label
    return widget


def labeled(widget):
    label = getattr(widget, "_bk_label", None)
    if label is None:
        return widget
    box = w.VBox([w.HTML(f'<label class="bk-label">{escape(label)}</label>'), widget], layout=w.Layout(width="100%"))
    box.add_class("bk-field")
    return box


def grid(*widgets, cols=2):
    box = w.GridBox(
        [labeled(x) for x in widgets],
        layout=w.Layout(grid_template_columns=f"repeat({cols}, minmax(0, 1fr))", width="100%"),
    )
    box.add_class("bk-grid")
    return box


def row(*widgets):
    """Fields and buttons on one line (buttons aligned with the input boxes)."""
    box = w.HBox([labeled(x) for x in widgets])
    box.add_class("bk-row")
    return box


def button(description, icon, style):
    return w.Button(description=description, icon=icon, button_style=style)


def actions(*buttons):
    box = w.HBox(list(buttons))
    box.add_class("bk-actions")
    return box


def output():
    out = w.Output()
    out.add_class("bk-out")
    return out


def to_none(value):
    """Turn 0 / '' into None for filters and optional fields."""
    return None if value in (0, "", None) else value


# ----------------------------------------------------------------------- html
def callout(body, kind="ok"):
    icon = {"ok": "✓", "error": "✕", "info": "i"}[kind]
    body = escape(body) if kind == "error" else body  # database errors are plain text
    return f'<div class="bk-callout bk-{kind}"><span class="bk-callout-icon">{icon}</span><div>{body}</div></div>'


def _is_null(v):
    try:
        return v is None or bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def _cell(v, col):
    """(html, is_numeric) for one table cell."""
    if _is_null(v):
        return '<span class="bk-null">—</span>', False
    if isinstance(v, bool):
        return ("Sí" if v else "No"), False
    if isinstance(v, (dt.datetime, pd.Timestamp)):
        return v.strftime("%Y-%m-%d %H:%M:%S" if (v.hour or v.minute or v.second) else "%Y-%m-%d"), False
    if isinstance(v, dt.date):
        return v.isoformat(), False
    if isinstance(v, float) and v.is_integer():  # int column that pandas turned into float because of NULLs
        return (f"{int(v):,}" if col.startswith(COUNT_PREFIXES) else str(int(v))), True
    if isinstance(v, (Decimal, float)):
        return f"{float(v):,.2f}", True
    if isinstance(v, numbers.Integral):
        return (f"{int(v):,}" if col.startswith(COUNT_PREFIXES) else str(int(v))), True
    return escape(str(v)), False


def table(df, max_rows=500):
    if df is None or df.empty:
        return '<div class="bk-empty">Sin resultados</div>'
    shown = df.head(max_rows)
    cols = [str(c) for c in shown.columns]
    rows = [[_cell(v, c) for v, c in zip(rec, cols)] for rec in shown.itertuples(index=False, name=None)]
    # a column is numeric (right-aligned) when its first non-null value is
    numeric = [next((cells[i][1] for cells in rows if "bk-null" not in cells[i][0]), False) for i in range(len(cols))]
    head = "".join(
        f"<th{' class=bk-num' if n else ''}>{escape(c.replace('_', ' '))}</th>" for c, n in zip(cols, numeric)
    )
    body = "".join(
        "<tr>"
        + "".join(f"<td{' class=bk-num' if n else ''}>{html}</td>" for (html, _), n in zip(cells, numeric))
        + "</tr>"
        for cells in rows
    )
    note = ""
    if len(df) > max_rows:
        note = f'<div class="bk-table-note">Se muestran las primeras {max_rows:,} de {len(df):,} filas.</div>'
    return (
        f'<div class="bk-table-wrap"><table class="bk-table"><thead><tr>{head}</tr></thead>'
        f"<tbody>{body}</tbody></table>{note}</div>"
    )


def kpi(label, value, sub="", tone=""):
    sub_html = f'<div class="bk-kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="bk-kpi bk-{tone}"><div class="bk-kpi-label">{label}</div>'
        f'<div class="bk-kpi-value">{value}</div>{sub_html}</div>'
    )


def kpi_row(*tiles):
    return f'<div class="bk-kpis">{"".join(tiles)}</div>'


def bars(items):
    """items: (label, value, tone). Horizontal bars with share of the total."""
    total = sum(v for _, v, _ in items) or 1
    peak = max((v for _, v, _ in items), default=0) or 1
    rows = []
    for label, value, tone in items:
        rows.append(
            f'<div><div class="bk-bar-top"><b>{escape(label)}</b><span>{value:,} · {value / total:.1%}</span></div>'
            f'<div class="bk-bar-track"><div class="bk-bar-fill bk-{tone}" style="width:{value / peak * 100:.1f}%"></div></div></div>'
        )
    return f'<div class="bk-bars">{"".join(rows)}</div>'


def money(value):
    return f"{float(value):,.2f} Kč"


def money_html(value, sign=""):
    """Amount for KPI tiles: the currency is a smaller suffix so it never wraps."""
    return f'{sign}{float(value):,.2f}<span class="bk-unit">Kč</span>'


def render(out, *html):
    """Replace the content of an Output widget with HTML blocks."""
    with out:
        clear_output()
        for block in html:
            display(HTML(block))


def message(out, body, kind="ok", df=None):
    render(out, callout(body, kind), *([table(df)] if df is not None else []))


# --------------------------------------------------------------------- layout
def section(title, help_text, *children, badge=None, badge_tone=""):
    badge_html = f'<span class="bk-badge bk-{badge_tone}">{badge}</span>' if badge else ""
    help_html = f'<p class="bk-card-help">{help_text}</p>' if help_text else ""
    head = w.HTML(
        f'<div class="bk-card-head"><div><h3 class="bk-card-title">{title}</h3>{help_html}</div>{badge_html}</div>'
    )
    card = w.VBox([head, *children], layout=w.Layout(width="100%"))
    card.add_class("bk-card")
    return card


def tabs(pairs, sub=False):
    tab = w.Tab(children=[content for _, content in pairs])
    for i, (title, _) in enumerate(pairs):
        tab.set_title(i, title)
    tab.add_class("bk-subtabs" if sub else "bk-tabs")
    return tab


# ------------------------------------------------------------------- catalogs
@dataclass(frozen=True)
class Catalogs:
    """Options for the dropdowns. Districts and k_symbols are read from the database."""

    district: list
    characterization: list
    gender: ClassVar[list] = [("Masculino (M)", "M"), ("Femenino (F)", "F")]
    movement_type: ClassVar[list] = [
        ("PRIJEM - ingreso", "PRIJEM"),
        ("VYDAJ - egreso", "VYDAJ"),
        ("VYBER - retiro en efectivo", "VYBER"),
    ]
    operation: ClassVar[list] = [
        ("(ninguna)", None),
        ("VKLAD - depósito en efectivo", "VKLAD"),
        ("VYBER - retiro en efectivo", "VYBER"),
        ("VYBER KARTOU - retiro con tarjeta", "VYBER KARTOU"),
        ("PREVOD Z UCTU - cobro desde otro banco", "PREVOD Z UCTU"),
        ("PREVOD NA UCET - transferencia a otro banco", "PREVOD NA UCET"),
    ]
    bank: ClassVar[list] = [("(ninguno)", None)] + [
        (b, b) for b in ("AB", "CD", "EF", "GH", "IJ", "KL", "MN", "OP", "QR", "ST", "UV", "WX", "YZ")
    ]

    @classmethod
    def load(cls, db: Database) -> "Catalogs":
        districts = db.query("SELECT ID_Distrito, Nombre_Distrito FROM Distrito ORDER BY Nombre_Distrito")
        symbols = db.query(
            """SELECT DISTINCT Caracterizacion_Operacion AS v FROM Transacciones
               WHERE Caracterizacion_Operacion IS NOT NULL ORDER BY 1"""
        )["v"]
        return cls(
            district=[(f"{r.Nombre_Distrito} ({r.ID_Distrito})", int(r.ID_Distrito)) for r in districts.itertuples()],
            characterization=[("(ninguna)", None)] + [(v, v) for v in symbols],
        )
