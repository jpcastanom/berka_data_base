"""Step 4: stored function, procedure, view and triggers.

They are created from Python, so no DELIMITER is needed. Triggers are created
AFTER the migration; otherwise they would fire for every historical transaction.
"""

import pandas as pd

from berka_bank.db import Database

# Balance of an account at a date (NULL date = current balance, no movements = 0).
FN_ACCOUNT_BALANCE = """
CREATE FUNCTION fn_saldo_cuenta(p_cuenta INT, p_fecha DATE)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_saldo DECIMAL(12,2);

    SET v_saldo = (
        SELECT Saldo_Resultante_Cuenta
        FROM Transacciones
        WHERE Identificador_Cuenta = p_cuenta
          AND (p_fecha IS NULL OR Fecha_Realizada <= p_fecha)
        ORDER BY Fecha_Realizada DESC, Codigo_Transacciones DESC
        LIMIT 1
    );

    RETURN IFNULL(v_saldo, 0);
END
"""

# Bank statement of an account between two dates: summary result set + detail result set.
SP_ACCOUNT_STATEMENT = """
CREATE PROCEDURE sp_extracto_cuenta(IN p_cuenta INT, IN p_desde DATE, IN p_hasta DATE)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Cuenta WHERE Identificador_Cuenta = p_cuenta) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cuenta indicada no existe';
    END IF;

    IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rango de fechas inválido (desde debe ser <= hasta)';
    END IF;

    -- 1) Resumen del periodo
    SELECT c.Identificador_Cuenta,
           d.Nombre_Distrito                                         AS Sucursal,
           c.Frecuencia_Emision_Estado_Cuenta                        AS Frecuencia,
           p_desde                                                   AS Desde,
           p_hasta                                                   AS Hasta,
           fn_saldo_cuenta(p_cuenta, DATE_SUB(p_desde, INTERVAL 1 DAY)) AS Saldo_Inicial,
           COALESCE(SUM(CASE WHEN t.Tipo_Movimiento = 'PRIJEM'  THEN t.Monto_Involucrado END), 0) AS Total_Ingresos,
           COALESCE(SUM(CASE WHEN t.Tipo_Movimiento <> 'PRIJEM' THEN t.Monto_Involucrado END), 0) AS Total_Egresos,
           COUNT(t.Codigo_Transacciones)                             AS Num_Movimientos,
           fn_saldo_cuenta(p_cuenta, p_hasta)                        AS Saldo_Final
    FROM Cuenta c
    JOIN Distrito d ON d.ID_Distrito = c.ID_Distrito
    LEFT JOIN Transacciones t
           ON t.Identificador_Cuenta = c.Identificador_Cuenta
          AND t.Fecha_Realizada BETWEEN p_desde AND p_hasta
    WHERE c.Identificador_Cuenta = p_cuenta
    GROUP BY c.Identificador_Cuenta, d.Nombre_Distrito, c.Frecuencia_Emision_Estado_Cuenta;

    -- 2) Detalle de movimientos
    SELECT Codigo_Transacciones, Fecha_Realizada, Tipo_Movimiento, Operacion_Efectuada,
           Caracterizacion_Operacion, Monto_Involucrado, Saldo_Resultante_Cuenta,
           Banco, Cuenta_Contraparte
    FROM Transacciones
    WHERE Identificador_Cuenta = p_cuenta
      AND Fecha_Realizada BETWEEN p_desde AND p_hasta
    ORDER BY Fecha_Realizada, Codigo_Transacciones;
END
"""

# Validates amount and date, defaults the date and computes the resulting balance.
TRG_TRANSACTIONS_BEFORE_INSERT = """
CREATE TRIGGER trg_transacciones_before_insert
BEFORE INSERT ON Transacciones
FOR EACH ROW
BEGIN
    DECLARE v_apertura DATE;

    IF NEW.Monto_Involucrado IS NULL OR NEW.Monto_Involucrado <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El monto de la transacción debe ser mayor que 0';
    END IF;

    IF NEW.Fecha_Realizada IS NULL THEN
        SET NEW.Fecha_Realizada = CURDATE();
    END IF;

    SELECT Fecha_Apertura INTO v_apertura
    FROM Cuenta WHERE Identificador_Cuenta = NEW.Identificador_Cuenta;

    IF v_apertura IS NOT NULL AND NEW.Fecha_Realizada < v_apertura THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha es anterior a la apertura de la cuenta';
    END IF;

    IF NEW.Saldo_Resultante_Cuenta IS NULL THEN
        SET NEW.Saldo_Resultante_Cuenta =
            fn_saldo_cuenta(NEW.Identificador_Cuenta, NEW.Fecha_Realizada)
            + IF(NEW.Tipo_Movimiento = 'PRIJEM', NEW.Monto_Involucrado, -NEW.Monto_Involucrado);
    END IF;
END
"""

# Audits every real change of a client into Auditoria_Cliente.
TRG_CLIENT_AFTER_UPDATE = """
CREATE TRIGGER trg_cliente_after_update
AFTER UPDATE ON Cliente
FOR EACH ROW
BEGIN
    IF NOT (OLD.Fecha_Nacimiento <=> NEW.Fecha_Nacimiento)
       OR NOT (OLD.Genero <=> NEW.Genero)
       OR NOT (OLD.ID_Distrito <=> NEW.ID_Distrito) THEN
        INSERT INTO Auditoria_Cliente (Identificador_Cliente,
                                       Fecha_Nacimiento_Antes, Fecha_Nacimiento_Despues,
                                       Genero_Antes, Genero_Despues,
                                       Distrito_Antes, Distrito_Despues,
                                       Usuario)
        VALUES (NEW.Identificador_Cliente,
                OLD.Fecha_Nacimiento, NEW.Fecha_Nacimiento,
                OLD.Genero, NEW.Genero,
                OLD.ID_Distrito, NEW.ID_Distrito,
                CURRENT_USER());
    END IF;
END
"""

# One row per account (inner joins: owner and district always exist). Card and loan are
# optional, and each is unique per disposition / account, so rows never multiply.
VW_ACCOUNT_OVERVIEW = """
CREATE VIEW vw_resumen_cuenta AS
SELECT c.Identificador_Cuenta,
       c.Fecha_Apertura,
       c.Frecuencia_Emision_Estado_Cuenta                  AS Frecuencia,
       d.Nombre_Distrito                                   AS Sucursal,
       d.Region_que_pertenece                              AS Region,
       cl.Identificador_Cliente                            AS Id_Titular,
       cl.Fecha_Nacimiento                                 AS Nacimiento_Titular,
       cl.Genero                                           AS Genero_Titular,
       (SELECT COUNT(*) FROM Disposicion x
         WHERE x.Identificador_Cuenta = c.Identificador_Cuenta
           AND x.Tipo_Disposicion = 'DISPONENT')           AS Num_Autorizados,
       t.Tipo_Tarjeta                                      AS Tarjeta_Titular,
       p.Codigo_Prestamos,
       p.Monto_Otorgado                                    AS Monto_Prestamo,
       p.Codigo_Estado                                     AS Estado_Prestamo,
       e.Descripcion_Estado                                AS Descripcion_Estado_Prestamo,
       fn_saldo_cuenta(c.Identificador_Cuenta, NULL)       AS Saldo_Actual
FROM Cuenta c
JOIN Distrito d       ON d.ID_Distrito = c.ID_Distrito
JOIN Disposicion o    ON o.Identificador_Cuenta = c.Identificador_Cuenta AND o.Tipo_Disposicion = 'OWNER'
JOIN Cliente cl       ON cl.Identificador_Cliente = o.Identificador_Cliente
LEFT JOIN Tarjeta t   ON t.Codigo_Disposicion = o.Codigo_Disposicion
LEFT JOIN Prestamos p ON p.Identificador_Cuenta = c.Identificador_Cuenta
LEFT JOIN Estado_Prestamo e ON e.Codigo_Estado = p.Codigo_Estado
"""

# The view calls fn_saldo_cuenta, so the function goes first.
ROUTINES = [
    ("FUNCTION", "fn_saldo_cuenta", FN_ACCOUNT_BALANCE),
    ("PROCEDURE", "sp_extracto_cuenta", SP_ACCOUNT_STATEMENT),
    ("VIEW", "vw_resumen_cuenta", VW_ACCOUNT_OVERVIEW),
    ("TRIGGER", "trg_transacciones_before_insert", TRG_TRANSACTIONS_BEFORE_INSERT),
    ("TRIGGER", "trg_cliente_after_update", TRG_CLIENT_AFTER_UPDATE),
]

NO_LOAN = "-"  # filter value for "accounts without a loan"


def create_all(db: Database) -> None:
    """Drop and recreate every routine (idempotent, cheap)."""
    for kind, name, body in ROUTINES:
        db.execute(f"DROP {kind} IF EXISTS {name}")
        db.execute(body)
        print(f"  {kind.lower():<9} {name}")


def account_statement(db: Database, account: int, start, end) -> tuple[pd.DataFrame, pd.DataFrame]:
    """CALL sp_extracto_cuenta and return (summary, detail). Uses callproc + nextset for the 2 result sets."""
    raw = db.model.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_extracto_cuenta", (account, start, end))
        summary = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        cur.nextset()
        detail = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        cur.close()
        return summary, detail
    finally:
        raw.close()


def account_overview(db: Database, account: int | None = None, region: str | None = None, loan: str | None = None):
    """Rows of vw_resumen_cuenta. `loan`: a status letter (A-D), NO_LOAN for accounts without one, None for all."""
    where, params = [], {}
    if account:
        where.append("Identificador_Cuenta = :account")
        params["account"] = account
    if region:
        where.append("Region = :region")
        params["region"] = region
    if loan == NO_LOAN:
        where.append("Codigo_Prestamos IS NULL")
    elif loan:
        where.append("Estado_Prestamo = :loan")
        params["loan"] = loan
    clause = f"WHERE {' AND '.join(where)}" if where else ""
    return db.query(f"SELECT * FROM vw_resumen_cuenta {clause} ORDER BY Identificador_Cuenta", params)
