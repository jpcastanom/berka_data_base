"""Step 2: physical model (database banco_berka) with the corrections of the second delivery.

Tables are created in dependency order: first the ones without foreign keys
(Distrito, Estado_Prestamo), then the ones that reference them.
"""

from sqlalchemy import text

from berka_bank.db import Database

MODEL_TABLES = [
    "Distrito",
    "Cliente",
    "Cuenta",
    "Disposicion",
    "Tarjeta",
    "Transacciones",
    "Estado_Prestamo",
    "Prestamos",
    "Ordenes_de_pago",
    "Auditoria_Cliente",
]

DDL_TEMPLATE = """
DROP DATABASE IF EXISTS {model_db};
CREATE DATABASE {model_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE {model_db};

-- 2.1 Distrito
CREATE TABLE Distrito (
    ID_Distrito             INT           NOT NULL,
    Nombre_Distrito         VARCHAR(80)   NOT NULL,
    Region_que_pertenece    VARCHAR(30)   NOT NULL,
    Cantidad_Municipios     INT           NOT NULL,
    Tasa_Desempleo          DECIMAL(5,2)  NOT NULL,
    Salario_Promedio        DECIMAL(10,2) NOT NULL,
    Cantidad_Emprendedores  INT           NOT NULL,
    Grado_Urbanizacion      DECIMAL(5,2)  NOT NULL,
    Numero_Habitantes       INT           NOT NULL,
    CONSTRAINT pk_distrito PRIMARY KEY (ID_Distrito),
    CONSTRAINT uq_distrito_nombre UNIQUE (Nombre_Distrito),
    CONSTRAINT ck_distrito_municipios CHECK (Cantidad_Municipios >= 1),
    CONSTRAINT ck_distrito_desempleo  CHECK (Tasa_Desempleo BETWEEN 0 AND 100),
    CONSTRAINT ck_distrito_urbaniz    CHECK (Grado_Urbanizacion BETWEEN 0 AND 100),
    CONSTRAINT ck_distrito_habitantes CHECK (Numero_Habitantes > 0)
);

-- 2.2 Cliente
CREATE TABLE Cliente (
    Identificador_Cliente  INT      NOT NULL AUTO_INCREMENT,
    Fecha_Nacimiento       DATE     NOT NULL,
    Genero                 CHAR(1)  NOT NULL,
    ID_Distrito            INT      NOT NULL,
    CONSTRAINT pk_cliente PRIMARY KEY (Identificador_Cliente),
    CONSTRAINT fk_cliente_distrito FOREIGN KEY (ID_Distrito) REFERENCES Distrito (ID_Distrito),
    CONSTRAINT ck_cliente_genero CHECK (Genero IN ('M', 'F')),
    CONSTRAINT ck_cliente_fecha  CHECK (Fecha_Nacimiento >= '1900-01-01')
);

-- 2.3 Cuenta (ya no tiene Codigo_Prestamos: la relación se guarda en Prestamos)
CREATE TABLE Cuenta (
    Identificador_Cuenta              INT          NOT NULL AUTO_INCREMENT,
    Fecha_Apertura                    DATE         NOT NULL,
    Frecuencia_Emision_Estado_Cuenta  VARCHAR(30)  NOT NULL,
    ID_Distrito                       INT          NOT NULL,
    CONSTRAINT pk_cuenta PRIMARY KEY (Identificador_Cuenta),
    CONSTRAINT fk_cuenta_distrito FOREIGN KEY (ID_Distrito) REFERENCES Distrito (ID_Distrito),
    CONSTRAINT ck_cuenta_frecuencia CHECK (Frecuencia_Emision_Estado_Cuenta IN
        ('POPLATEK MESICNE', 'POPLATEK TYDNE', 'POPLATEK PO OBRATU'))
);

-- 2.4 Disposicion
CREATE TABLE Disposicion (
    Codigo_Disposicion     INT          NOT NULL AUTO_INCREMENT,
    Tipo_Disposicion       VARCHAR(45)  NOT NULL,
    Identificador_Cliente  INT          NOT NULL,
    Identificador_Cuenta   INT          NOT NULL,
    CONSTRAINT pk_disposicion PRIMARY KEY (Codigo_Disposicion),
    CONSTRAINT fk_disp_cliente FOREIGN KEY (Identificador_Cliente) REFERENCES Cliente (Identificador_Cliente),
    CONSTRAINT fk_disp_cuenta  FOREIGN KEY (Identificador_Cuenta)  REFERENCES Cuenta (Identificador_Cuenta),
    CONSTRAINT ck_disp_tipo CHECK (Tipo_Disposicion IN ('OWNER', 'DISPONENT'))
);

-- 2.5 Tarjeta
CREATE TABLE Tarjeta (
    Identificador_Tarjeta  INT          NOT NULL AUTO_INCREMENT,
    Tipo_Tarjeta           VARCHAR(45)  NOT NULL,
    Fecha_Emitida          DATE         NOT NULL,
    Codigo_Disposicion     INT          NOT NULL,
    CONSTRAINT pk_tarjeta PRIMARY KEY (Identificador_Tarjeta),
    CONSTRAINT uq_tarjeta_disposicion UNIQUE (Codigo_Disposicion),
    CONSTRAINT fk_tarjeta_disp FOREIGN KEY (Codigo_Disposicion) REFERENCES Disposicion (Codigo_Disposicion),
    CONSTRAINT ck_tarjeta_tipo CHECK (Tipo_Tarjeta IN ('classic', 'junior', 'gold'))
);

-- 2.6 Transacciones (+ Caracterizacion_Operacion, antes k_symbol)
CREATE TABLE Transacciones (
    Codigo_Transacciones       INT            NOT NULL AUTO_INCREMENT,
    Identificador_Cuenta       INT            NOT NULL,
    Fecha_Realizada            DATE           NOT NULL,
    Tipo_Movimiento            VARCHAR(45)    NOT NULL,
    Operacion_Efectuada        VARCHAR(30)    NULL,
    Caracterizacion_Operacion  VARCHAR(30)    NULL,
    Monto_Involucrado          DECIMAL(12,2)  NOT NULL,
    Saldo_Resultante_Cuenta    DECIMAL(12,2)  NOT NULL,
    Banco                      CHAR(2)        NULL,
    Cuenta_Contraparte         BIGINT         NULL,
    CONSTRAINT pk_transacciones PRIMARY KEY (Codigo_Transacciones),
    CONSTRAINT fk_trans_cuenta FOREIGN KEY (Identificador_Cuenta) REFERENCES Cuenta (Identificador_Cuenta),
    CONSTRAINT ck_trans_tipo  CHECK (Tipo_Movimiento IN ('PRIJEM', 'VYDAJ', 'VYBER')),
    CONSTRAINT ck_trans_monto CHECK (Monto_Involucrado >= 0),
    INDEX idx_trans_cuenta_fecha (Identificador_Cuenta, Fecha_Realizada, Codigo_Transacciones)
);

-- 2.7 Estado_Prestamo (código como letra, igual que en los datos)
CREATE TABLE Estado_Prestamo (
    Codigo_Estado       CHAR(1)      NOT NULL,
    Descripcion_Estado  VARCHAR(60)  NOT NULL,
    CONSTRAINT pk_estado_prestamo PRIMARY KEY (Codigo_Estado)
);

-- 2.8 Prestamos (FK a Cuenta, única: una cuenta tiene 0 o 1 préstamo)
CREATE TABLE Prestamos (
    Codigo_Prestamos       INT            NOT NULL AUTO_INCREMENT,
    Identificador_Cuenta   INT            NOT NULL,
    Fecha_Concedido        DATE           NOT NULL,
    Monto_Otorgado         DECIMAL(12,2)  NOT NULL,
    Duracion_Prestamo      INT            NOT NULL,
    Valor_Cuota_Periodica  DECIMAL(10,2)  NOT NULL,
    Codigo_Estado          CHAR(1)        NOT NULL,
    CONSTRAINT pk_prestamos PRIMARY KEY (Codigo_Prestamos),
    CONSTRAINT uq_prestamos_cuenta UNIQUE (Identificador_Cuenta),
    CONSTRAINT fk_prestamo_cuenta FOREIGN KEY (Identificador_Cuenta) REFERENCES Cuenta (Identificador_Cuenta),
    CONSTRAINT fk_prestamo_estado FOREIGN KEY (Codigo_Estado) REFERENCES Estado_Prestamo (Codigo_Estado),
    CONSTRAINT ck_prestamo_duracion CHECK (Duracion_Prestamo IN (12, 24, 36, 48, 60)),
    CONSTRAINT ck_prestamo_monto    CHECK (Monto_Otorgado > 0 AND Valor_Cuota_Periodica > 0)
);

-- 2.9 Ordenes_de_pago
CREATE TABLE Ordenes_de_pago (
    Codigo_Orden_Pago      INT            NOT NULL AUTO_INCREMENT,
    Identificador_Cuenta   INT            NOT NULL,
    Importe_Enviado        DECIMAL(10,2)  NOT NULL,
    Tipo_O_Finalidad_Pago  VARCHAR(30)    NULL,
    Cuenta_Destino         BIGINT         NOT NULL,
    Banco                  CHAR(2)        NOT NULL,
    CONSTRAINT pk_ordenes_pago PRIMARY KEY (Codigo_Orden_Pago),
    CONSTRAINT fk_orden_cuenta FOREIGN KEY (Identificador_Cuenta) REFERENCES Cuenta (Identificador_Cuenta),
    CONSTRAINT ck_orden_importe CHECK (Importe_Enviado > 0)
);

-- Tabla de auditoría (la llena el trigger trg_cliente_after_update)
CREATE TABLE Auditoria_Cliente (
    Id_Auditoria             INT          NOT NULL AUTO_INCREMENT,
    Identificador_Cliente    INT          NOT NULL,
    Fecha_Nacimiento_Antes   DATE         NULL,
    Fecha_Nacimiento_Despues DATE         NULL,
    Genero_Antes             CHAR(1)      NULL,
    Genero_Despues           CHAR(1)      NULL,
    Distrito_Antes           INT          NULL,
    Distrito_Despues         INT          NULL,
    Usuario                  VARCHAR(100) NOT NULL,
    Fecha_Cambio             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_auditoria_cliente PRIMARY KEY (Id_Auditoria)
);
"""


def ddl(model_db: str) -> list[str]:
    """DDL split into statements (none of them contains an inner ';')."""
    script = DDL_TEMPLATE.replace("{model_db}", model_db)
    return [s.strip() for s in script.split(";") if s.strip()]


def is_built(db: Database) -> bool:
    """True if every model table exists and the model already holds data."""
    try:
        existing = set(
            db.query(
                "SELECT TABLE_NAME AS t FROM information_schema.TABLES WHERE TABLE_SCHEMA = :s",
                {"s": db.settings.model_db},
                engine=db.server,
            )["t"]
        )
        if not set(MODEL_TABLES) <= existing:
            return False
        return db.query("SELECT COUNT(*) AS n FROM Distrito")["n"][0] > 0
    except Exception:
        return False


def create(db: Database) -> None:
    """DROP and CREATE the model database (destructive)."""
    with db.server.begin() as con:
        for statement in ddl(db.settings.model_db):
            con.execute(text(statement))
