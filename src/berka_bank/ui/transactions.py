"""'Transacciones' tab: query, insert (balance computed by the trigger), update and delete."""

from datetime import date

import ipywidgets as w
import pandas as pd

from berka_bank.db import Database, error_text
from berka_bank.ui.widgets import (
    Catalogs,
    actions,
    button,
    field,
    grid,
    message,
    output,
    row,
    section,
    tabs,
    to_none,
)

BADGE = {"badge": "Tabla Transacciones", "badge_tone": "teal"}


def transaction_form(cat: Catalogs) -> dict:
    """Reusable form (insert / update). Keys are the column names."""
    return {
        "Fecha_Realizada": field(w.DatePicker, "Fecha", value=date.today()),
        "Tipo_Movimiento": field(w.Dropdown, "Tipo de movimiento", options=cat.movement_type),
        "Operacion_Efectuada": field(w.Dropdown, "Operación", options=cat.operation, index=0),
        "Caracterizacion_Operacion": field(
            w.Dropdown, "Caracterización (k_symbol)", options=cat.characterization, index=0
        ),
        "Monto_Involucrado": field(w.BoundedFloatText, "Monto (Kč)", value=1000, min=-1e9, max=1e9),
        "Banco": field(w.Dropdown, "Banco contraparte", options=cat.bank, index=0),
        "Cuenta_Contraparte": field(w.IntText, "Cuenta contraparte (0 = ninguna)", value=0),
    }


def form_values(form: dict) -> dict:
    v = {k: x.value for k, x in form.items()}
    v["Cuenta_Contraparte"] = to_none(v["Cuenta_Contraparte"])
    return v


def query_tab(db: Database, cat: Catalogs):
    q_account = field(w.IntText, "Cuenta (0 = todas)", value=576)
    q_type = field(w.Dropdown, "Tipo de movimiento", options=[("(todos)", None)] + cat.movement_type, index=0)
    q_from = field(w.DatePicker, "Desde (opcional)")
    q_to = field(w.DatePicker, "Hasta (opcional)")
    q_lim = field(w.BoundedIntText, "Máximo de filas", value=25, min=1, max=10000)
    btn, out = button("Consultar", "search", "info"), output()

    def run(_=None):
        filters, params = [], {"lim": q_lim.value}
        if to_none(q_account.value):
            filters.append("Identificador_Cuenta = :c")
            params["c"] = q_account.value
        if q_from.value:
            filters.append("Fecha_Realizada >= :desde")
            params["desde"] = q_from.value
        if q_to.value:
            filters.append("Fecha_Realizada <= :hasta")
            params["hasta"] = q_to.value
        if q_type.value:
            filters.append("Tipo_Movimiento = :tipo")
            params["tipo"] = q_type.value
        where = (" WHERE " + " AND ".join(filters)) if filters else ""
        try:
            df = db.query(
                "SELECT * FROM Transacciones"
                + where
                + " ORDER BY Fecha_Realizada DESC, Codigo_Transacciones DESC LIMIT :lim",
                params,
            )
            message(out, f"<b>{len(df)}</b> transacción(es), las más recientes primero.", "info", df)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Consultar transacciones",
        "Todos los filtros son opcionales.",
        grid(q_account, q_type, q_from, q_to, q_lim),
        actions(btn),
        out,
        **BADGE,
    )


def insert_tab(db: Database, cat: Catalogs):
    i_account = field(w.IntText, "Cuenta", value=576)
    form = transaction_form(cat)
    btn, out = button("Insertar transacción", "plus", "success"), output()

    def run(_=None):
        params = form_values(form) | {"c": i_account.value}
        try:
            new_id = db.execute(
                """
                INSERT INTO Transacciones (Identificador_Cuenta, Fecha_Realizada, Tipo_Movimiento, Operacion_Efectuada,
                                           Caracterizacion_Operacion, Monto_Involucrado, Banco, Cuenta_Contraparte)
                VALUES (:c, :Fecha_Realizada, :Tipo_Movimiento, :Operacion_Efectuada,
                        :Caracterizacion_Operacion, :Monto_Involucrado, :Banco, :Cuenta_Contraparte)""",
                params,
            ).lastrowid
            df = db.query("SELECT * FROM Transacciones WHERE Codigo_Transacciones = :id", {"id": new_id})
            message(
                out,
                f"Transacción <b>{new_id}</b> registrada. Saldo resultante calculado por el trigger: "
                f"<b>{df.Saldo_Resultante_Cuenta[0]:,.2f} Kč</b>",
                "ok",
                df,
            )
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Nueva transacción",
        "No se pide el saldo: lo calcula el trigger <code>trg_transacciones_before_insert</code>, "
        "que además rechaza montos ≤ 0 y fechas anteriores a la apertura de la cuenta.",
        grid(i_account, *form.values()),
        actions(btn),
        out,
        **BADGE,
    )


def update_tab(db: Database, cat: Catalogs):
    u_id = field(w.IntText, "Código transacción", value=0)
    load_btn = button("Cargar", "download", "info")
    form = transaction_form(cat)
    u_balance = field(w.FloatText, "Saldo resultante (Kč)", value=0)
    save_btn, out = button("Guardar cambios", "save", "warning"), output()
    state = {"id": None}

    def enable(on):
        for x in [*form.values(), u_balance, save_btn]:
            x.disabled = not on

    enable(False)

    def load(_=None):
        df = db.query("SELECT * FROM Transacciones WHERE Codigo_Transacciones = :id", {"id": u_id.value})
        if df.empty:
            state["id"] = None
            enable(False)
            return message(out, f"No existe la transacción {u_id.value}.", "error")
        r = df.iloc[0]
        state["id"] = int(r.Codigo_Transacciones)
        for k, x in form.items():
            value = r[k]
            if pd.isna(value):
                if k != "Cuenta_Contraparte":
                    x.index = 0  # "(ninguna)" / "(ninguno)"
                    continue
                value = 0
            elif k == "Monto_Involucrado":
                value = float(value)
            elif k == "Cuenta_Contraparte":
                value = int(value)
            x.value = value
        u_balance.value = float(r.Saldo_Resultante_Cuenta)
        enable(True)
        message(out, f"Transacción <b>{state['id']}</b> (cuenta {int(r.Identificador_Cuenta)}) cargada.", "info")

    def save(_=None):
        if state["id"] is None:
            return message(out, "Primero cargue una transacción.", "error")
        params = form_values(form) | {"saldo": u_balance.value, "id": state["id"]}
        try:
            db.execute(
                """
                UPDATE Transacciones
                SET Fecha_Realizada = :Fecha_Realizada, Tipo_Movimiento = :Tipo_Movimiento,
                    Operacion_Efectuada = :Operacion_Efectuada, Caracterizacion_Operacion = :Caracterizacion_Operacion,
                    Monto_Involucrado = :Monto_Involucrado, Saldo_Resultante_Cuenta = :saldo,
                    Banco = :Banco, Cuenta_Contraparte = :Cuenta_Contraparte
                WHERE Codigo_Transacciones = :id""",
                params,
            )
            df = db.query("SELECT * FROM Transacciones WHERE Codigo_Transacciones = :id", {"id": state["id"]})
            message(out, "Transacción actualizada.", "ok", df)
        except Exception as e:
            message(out, error_text(e), "error")

    load_btn.on_click(load)
    save_btn.on_click(save)
    return section(
        "Modificar transacción",
        "Corrige datos de un movimiento. El saldo se edita manualmente "
        "(el trigger solo actúa al insertar). La restricción <code>CHECK</code> impide montos negativos.",
        row(u_id, load_btn),
        grid(*form.values(), u_balance),
        actions(save_btn),
        out,
        **BADGE,
    )


def delete_tab(db: Database):
    d_id = field(w.IntText, "Código transacción", value=0)
    confirm = w.Checkbox(description="Confirmo que deseo borrar esta transacción", indent=False)
    btn, out = button("Borrar transacción", "trash", "danger"), output()

    def run(_=None):
        if not confirm.value:
            return message(out, "Marque la casilla de confirmación.", "error")
        try:
            n = db.execute("DELETE FROM Transacciones WHERE Codigo_Transacciones = :id", {"id": d_id.value}).rowcount
            message(
                out,
                f"Transacción <b>{d_id.value}</b> eliminada." if n else f"No existe la transacción {d_id.value}.",
                "ok" if n else "error",
            )
        except Exception as e:
            message(out, error_text(e), "error")
        confirm.value = False

    btn.on_click(run)
    return section(
        "Eliminar transacción", "Esta acción no se puede deshacer.", grid(d_id), confirm, actions(btn), out, **BADGE
    )


def build(db: Database, cat: Catalogs):
    return tabs(
        [
            ("Consultar", query_tab(db, cat)),
            ("Insertar", insert_tab(db, cat)),
            ("Actualizar", update_tab(db, cat)),
            ("Borrar", delete_tab(db)),
        ],
        sub=True,
    )
