"""'Clientes' tab: query, insert, update (fires the audit trigger) and delete on Cliente."""

from datetime import date

import ipywidgets as w

from berka_bank.db import Database, error_text
from berka_bank.ui.widgets import Catalogs, button, field, message, section, tabs, to_none

SQL_CLIENT_DETAIL = """
    SELECT c.Identificador_Cliente, c.Fecha_Nacimiento, c.Genero, c.ID_Distrito, d.Nombre_Distrito,
           (SELECT COUNT(*) FROM Disposicion x WHERE x.Identificador_Cliente = c.Identificador_Cliente) AS Num_Cuentas
    FROM Cliente c JOIN Distrito d ON d.ID_Distrito = c.ID_Distrito
"""


def query_tab(db: Database, cat: Catalogs):
    q_id = field(w.IntText, "ID cliente (0 = todos)", value=0)
    q_dist = field(w.Dropdown, "Distrito", options=[("(todos)", None)] + cat.district, value=None)
    q_gen = field(w.Dropdown, "Género", options=[("(todos)", None)] + cat.gender, value=None)
    q_lim = field(w.BoundedIntText, "Máximo de filas", value=25, min=1, max=10000)
    btn, out = button("Consultar", "search", "info"), w.Output()

    def run(_=None):
        filters, params = [], {"lim": q_lim.value}
        if to_none(q_id.value):
            filters.append("c.Identificador_Cliente = :id")
            params["id"] = q_id.value
        if q_dist.value is not None:
            filters.append("c.ID_Distrito = :dist")
            params["dist"] = q_dist.value
        if q_gen.value is not None:
            filters.append("c.Genero = :gen")
            params["gen"] = q_gen.value
        where = (" WHERE " + " AND ".join(filters)) if filters else ""
        try:
            df = db.query(SQL_CLIENT_DETAIL + where + " ORDER BY c.Identificador_Cliente LIMIT :lim", params)
            message(out, f"{len(df)} cliente(s) encontrados.", "info", df)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section("Consultar clientes", "Filtros opcionales.", q_id, q_dist, q_gen, q_lim, btn, out)


def insert_tab(db: Database, cat: Catalogs):
    i_date = field(w.DatePicker, "Fecha de nacimiento", value=date(1980, 1, 1))
    i_gen = field(w.Dropdown, "Género", options=cat.gender)
    i_dist = field(w.Dropdown, "Distrito", options=cat.district)
    btn, out = button("Insertar cliente", "plus", "success"), w.Output()

    def run(_=None):
        if i_date.value is None:
            return message(out, "Seleccione la fecha de nacimiento.", "error")
        try:
            new_id = db.execute(
                "INSERT INTO Cliente (Fecha_Nacimiento, Genero, ID_Distrito) VALUES (:f, :g, :d)",
                {"f": i_date.value, "g": i_gen.value, "d": i_dist.value},
            ).lastrowid
            df = db.query(SQL_CLIENT_DETAIL + " WHERE c.Identificador_Cliente = :id", {"id": new_id})
            message(out, f"Cliente insertado con ID <b>{new_id}</b>.", "ok", df)
        except Exception as e:
            message(out, error_text(e), "error")

    btn.on_click(run)
    return section(
        "Nuevo cliente", "El ID lo asigna la base de datos (AUTO_INCREMENT).", i_date, i_gen, i_dist, btn, out
    )


def update_tab(db: Database, cat: Catalogs):
    u_id = field(w.IntText, "ID cliente", value=1)
    load_btn = button("Cargar", "download", "info")
    u_date = field(w.DatePicker, "Fecha de nacimiento", disabled=True)
    u_gen = field(w.Dropdown, "Género", options=cat.gender, disabled=True)
    u_dist = field(w.Dropdown, "Distrito", options=cat.district, disabled=True)
    save_btn, out = button("Guardar cambios", "save", "warning"), w.Output()
    save_btn.disabled = True
    state = {"id": None}
    editable = (u_date, u_gen, u_dist, save_btn)

    def load(_=None):
        df = db.query("SELECT * FROM Cliente WHERE Identificador_Cliente = :id", {"id": u_id.value})
        if df.empty:
            state["id"] = None
            for x in editable:
                x.disabled = True
            return message(out, f"No existe el cliente {u_id.value}.", "error")
        row = df.iloc[0]
        state["id"] = int(row.Identificador_Cliente)
        u_date.value, u_gen.value, u_dist.value = row.Fecha_Nacimiento, row.Genero, int(row.ID_Distrito)
        for x in editable:
            x.disabled = False
        message(out, f'Cliente {state["id"]} cargado. Modifique los campos y pulse "Guardar cambios".', "info")

    def save(_=None):
        if state["id"] is None:
            return message(out, "Primero cargue un cliente.", "error")
        try:
            n = db.execute(
                """UPDATE Cliente SET Fecha_Nacimiento = :f, Genero = :g, ID_Distrito = :d
                              WHERE Identificador_Cliente = :id""",
                {"f": u_date.value, "g": u_gen.value, "d": u_dist.value, "id": state["id"]},
            ).rowcount
            audit = db.query(
                """SELECT * FROM Auditoria_Cliente WHERE Identificador_Cliente = :id
                                ORDER BY Id_Auditoria DESC LIMIT 5""",
                {"id": state["id"]},
            )
            body = (
                "Cliente actualizado. Últimos registros de auditoría (trigger):"
                if n
                else "No hubo cambios que guardar."
            )
            message(out, body, "ok" if n else "info", audit)
        except Exception as e:
            message(out, error_text(e), "error")

    load_btn.on_click(load)
    save_btn.on_click(save)
    return section(
        "Modificar cliente",
        "Cada cambio queda registrado por el trigger de auditoría.",
        w.HBox([u_id, load_btn]),
        u_date,
        u_gen,
        u_dist,
        save_btn,
        out,
    )


def delete_tab(db: Database):
    d_id = field(w.IntText, "ID cliente", value=0)
    confirm = w.Checkbox(description="Confirmo que deseo borrar este cliente", indent=False)
    btn, out = button("Borrar cliente", "trash", "danger"), w.Output()

    def run(_=None):
        if not confirm.value:
            return message(out, "Marque la casilla de confirmación.", "error")
        try:
            n = db.execute("DELETE FROM Cliente WHERE Identificador_Cliente = :id", {"id": d_id.value}).rowcount
            message(
                out,
                f"Cliente {d_id.value} eliminado." if n else f"No existe el cliente {d_id.value}.",
                "ok" if n else "error",
            )
        except Exception as e:
            message(out, error_text(e), "error")
        confirm.value = False

    btn.on_click(run)
    return section(
        "Eliminar cliente",
        "Un cliente con cuentas (disposiciones) no se puede borrar: lo impide la llave foránea.",
        d_id,
        confirm,
        btn,
        out,
    )


def build(db: Database, cat: Catalogs):
    return tabs(
        [
            ("Consultar", query_tab(db, cat)),
            ("Insertar", insert_tab(db, cat)),
            ("Actualizar", update_tab(db, cat)),
            ("Borrar", delete_tab(db)),
        ]
    )
