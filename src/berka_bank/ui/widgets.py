"""Shared widget helpers and dropdown catalogs for the interface."""

from dataclasses import dataclass
from typing import ClassVar

import ipywidgets as w
from IPython.display import HTML, clear_output, display

from berka_bank.db import Database

STYLE = {"description_width": "170px"}
WIDTH = w.Layout(width="460px")


def field(cls, description, **kw):
    return cls(description=description, style=STYLE, layout=WIDTH, **kw)


def button(description, icon, style):
    return w.Button(description=description, icon=icon, button_style=style, layout=w.Layout(width="180px"))


def message(output, body, kind="ok", df=None):
    color = {"ok": "#2e7d32", "error": "#c62828", "info": "#1565c0"}[kind]
    with output:
        clear_output()
        display(HTML(f"<div style='margin:6px 0;padding:6px 10px;border-left:4px solid {color}'>{body}</div>"))
        if df is not None:
            display(df)


def section(title, help_text, *children):
    return w.VBox(
        [w.HTML(f'<h4 style="margin:4px 0">{title}</h4><small>{help_text}</small>'), *children],
        layout=w.Layout(padding="8px"),
    )


def tabs(pairs):
    tab = w.Tab(children=[content for _, content in pairs])
    for i, (title, _) in enumerate(pairs):
        tab.set_title(i, title)
    return tab


def to_none(value):
    """Turn 0 / '' into None for filters and optional fields."""
    return None if value in (0, "", None) else value


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
        symbols = db.query("""SELECT DISTINCT Caracterizacion_Operacion AS v FROM Transacciones
                              WHERE Caracterizacion_Operacion IS NOT NULL ORDER BY 1""")["v"]
        return cls(
            district=[(f"{r.Nombre_Distrito} ({r.ID_Distrito})", int(r.ID_Distrito)) for r in districts.itertuples()],
            characterization=[("(ninguna)", None)] + [(v, v) for v in symbols],
        )
