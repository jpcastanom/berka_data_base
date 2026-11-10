"""Step 3: migrate staging data into the model and validate it against the data dictionary."""

import time

import pandas as pd
from sqlalchemy import text

from berka_bank.db import Database


def migration_statements(staging: str) -> list[tuple[str, str]]:
    """(target table, INSERT ... SELECT) pairs, in foreign-key order."""
    return [
        (
            "Distrito",
            f"""
        INSERT INTO Distrito (ID_Distrito, Nombre_Distrito, Region_que_pertenece, Cantidad_Municipios,
                              Tasa_Desempleo, Salario_Promedio, Cantidad_Emprendedores,
                              Grado_Urbanizacion, Numero_Habitantes)
        SELECT A1, A2, A3, A5 + A6 + A7 + A8, A13, A11, A14, A10, A4
        FROM {staging}.district""",
        ),
        (
            "Cliente",
            f"""
        INSERT INTO Cliente (Identificador_Cliente, Fecha_Nacimiento, Genero, ID_Distrito)
        SELECT client_id,
               CAST(CONCAT('19', LPAD(birth_number - IF(MOD(birth_number DIV 100, 100) > 50, 5000, 0), 6, '0')) AS DATE),
               IF(MOD(birth_number DIV 100, 100) > 50, 'F', 'M'),
               district_id
        FROM {staging}.client""",
        ),
        (
            "Cuenta",
            f"""
        INSERT INTO Cuenta (Identificador_Cuenta, Fecha_Apertura, Frecuencia_Emision_Estado_Cuenta, ID_Distrito)
        SELECT account_id, `date`, frequency, district_id
        FROM {staging}.account""",
        ),
        (
            "Disposicion",
            f"""
        INSERT INTO Disposicion (Codigo_Disposicion, Tipo_Disposicion, Identificador_Cliente, Identificador_Cuenta)
        SELECT disp_id, `type`, client_id, account_id
        FROM {staging}.disp""",
        ),
        (
            "Tarjeta",
            f"""
        INSERT INTO Tarjeta (Identificador_Tarjeta, Tipo_Tarjeta, Fecha_Emitida, Codigo_Disposicion)
        SELECT card_id, `type`, issued, disp_id
        FROM {staging}.card""",
        ),
        (
            "Estado_Prestamo",
            """
        INSERT INTO Estado_Prestamo (Codigo_Estado, Descripcion_Estado) VALUES
            ('A', 'Finalizado sin problemas'),
            ('B', 'Finalizado, préstamo no pagado'),
            ('C', 'Vigente sin problemas'),
            ('D', 'Vigente, cliente en deuda')""",
        ),
        (
            "Prestamos",
            f"""
        INSERT INTO Prestamos (Codigo_Prestamos, Identificador_Cuenta, Fecha_Concedido, Monto_Otorgado,
                               Duracion_Prestamo, Valor_Cuota_Periodica, Codigo_Estado)
        SELECT loan_id, account_id, `date`, amount, duration, payments, status
        FROM {staging}.loan""",
        ),
        (
            "Ordenes_de_pago",
            f"""
        INSERT INTO Ordenes_de_pago (Codigo_Orden_Pago, Identificador_Cuenta, Importe_Enviado,
                                     Tipo_O_Finalidad_Pago, Cuenta_Destino, Banco)
        SELECT order_id, account_id, amount, NULLIF(TRIM(k_symbol), ''), account_to, bank_to
        FROM {staging}.`order`""",
        ),
        (
            "Transacciones",
            f"""
        INSERT INTO Transacciones (Codigo_Transacciones, Identificador_Cuenta, Fecha_Realizada, Tipo_Movimiento,
                                   Operacion_Efectuada, Caracterizacion_Operacion, Monto_Involucrado,
                                   Saldo_Resultante_Cuenta, Banco, Cuenta_Contraparte)
        SELECT trans_id, account_id, `date`, `type`,
               NULLIF(TRIM(operation), ''), NULLIF(TRIM(k_symbol), ''), amount,
               balance, NULLIF(TRIM(bank), ''), `account`
        FROM {staging}.trans""",
        ),
    ]


# (check, SQL, value reported by the data dictionary)
VALIDATIONS = [
    ("Distritos", "SELECT COUNT(*) FROM Distrito", 77),
    ("Clientes", "SELECT COUNT(*) FROM Cliente", 5_369),
    ("Clientes hombres (M)", "SELECT COUNT(*) FROM Cliente WHERE Genero = 'M'", 2_724),
    ("Clientes mujeres (F)", "SELECT COUNT(*) FROM Cliente WHERE Genero = 'F'", 2_645),
    ("Cuentas", "SELECT COUNT(*) FROM Cuenta", 4_500),
    ("Disposiciones OWNER", "SELECT COUNT(*) FROM Disposicion WHERE Tipo_Disposicion = 'OWNER'", 4_500),
    ("Disposiciones DISPONENT", "SELECT COUNT(*) FROM Disposicion WHERE Tipo_Disposicion = 'DISPONENT'", 869),
    ("Tarjetas", "SELECT COUNT(*) FROM Tarjeta", 892),
    ("Préstamos", "SELECT COUNT(*) FROM Prestamos", 682),
    ("Órdenes de pago", "SELECT COUNT(*) FROM Ordenes_de_pago", 6_471),
    ("Transacciones", "SELECT COUNT(*) FROM Transacciones", 1_056_320),
    ("Transacciones sin operación", "SELECT COUNT(*) FROM Transacciones WHERE Operacion_Efectuada IS NULL", 183_114),
    (
        "Transacciones con k_symbol",
        "SELECT COUNT(*) FROM Transacciones WHERE Caracterizacion_Operacion IS NOT NULL",
        521_006,
    ),
]


def migrate(db: Database) -> None:
    for table, sql in migration_statements(db.settings.staging_db):
        start = time.time()
        rows = db.execute(sql).rowcount
        print(f"  {table:<16} {rows:>10,} rows  ({time.time() - start:.1f} s)")


def validate(db: Database) -> pd.DataFrame:
    """Compare model row counts with the counts in the data dictionary."""
    with db.model.connect() as con:
        result = pd.DataFrame(
            [(name, con.execute(text(sql)).scalar(), expected) for name, sql, expected in VALIDATIONS],
            columns=["Validación", "En la BD", "Diccionario"],
        )
    result["OK"] = result["En la BD"] == result["Diccionario"]
    return result
