"""Integration tests against a real MySQL 8 (the logic lives in SQL, so a mock proves nothing).

Connection: BERKA_TEST_HOST/PORT/USER/PASSWORD (default localhost:3306, root, "test").
A scratch database `banco_berka_test` is created and dropped; the real model is never touched.
Tests are skipped when MySQL is not reachable.
"""

import os
from pathlib import Path

import pytest

from berka_bank import routines, schema
from berka_bank.config import Settings
from berka_bank.db import Database

TEST_DB = "banco_berka_test"


@pytest.fixture(scope="session")
def db():
    settings = Settings(
        host=os.environ.get("BERKA_TEST_HOST", "127.0.0.1"),
        port=int(os.environ.get("BERKA_TEST_PORT", "3306")),
        user=os.environ.get("BERKA_TEST_USER", "root"),
        password=os.environ.get("BERKA_TEST_PASSWORD", "test"),
        staging_db="berka_test_unused",
        model_db=TEST_DB,
        berka_sql=Path("unused"),
        reload_staging=False,
        rebuild_model=False,
        ui_port=0,
        open_browser=False,
    )
    database = Database(settings)
    try:
        database.version()
    except Exception as e:
        pytest.skip(f"MySQL not reachable: {e}")
    schema.create(database)
    routines.create_all(database)
    yield database
    database.execute(f"DROP DATABASE IF EXISTS {TEST_DB}", engine=database.server)


FIXTURE = """
INSERT INTO Distrito VALUES
 (1, 'Praha',  'Prague',        1, 1.0, 1000, 10, 50, 1000),
 (2, 'Brno',   'south Moravia', 1, 2.0, 2000, 20, 60, 2000);
INSERT INTO Estado_Prestamo VALUES ('A','Finalizado sin problemas'),('B','Finalizado, préstamo no pagado'),
 ('C','Vigente sin problemas'),('D','Vigente, cliente en deuda');
INSERT INTO Cliente (Identificador_Cliente, Fecha_Nacimiento, Genero, ID_Distrito) VALUES
 (1, '1970-01-01', 'M', 1),   -- owner of account 1
 (2, '1980-02-02', 'F', 2),   -- owner of account 2
 (3, '1990-03-03', 'F', 1),   -- disponent of account 1
 (4, '1960-04-04', 'M', 1),   -- owner of account 3
 (5, '1950-05-05', 'F', 2);   -- disponent of account 1 (second one)
INSERT INTO Cuenta VALUES
 (1, '1995-01-01', 'POPLATEK MESICNE', 1),
 (2, '1996-06-01', 'POPLATEK TYDNE',   2),
 (3, '1997-01-01', 'POPLATEK PO OBRATU', 1),
 (4, '1997-02-01', 'POPLATEK MESICNE', 2);   -- account with no disposition at all
INSERT INTO Disposicion VALUES
 (1, 'OWNER',     1, 1), (2, 'DISPONENT', 3, 1), (3, 'DISPONENT', 5, 1),
 (4, 'OWNER',     2, 2),
 (5, 'OWNER',     4, 3);
INSERT INTO Tarjeta VALUES (1, 'gold', '1996-01-01', 1), (2, 'junior', '1996-01-01', 2);  -- disp 2 = a disponent's card
INSERT INTO Prestamos VALUES (1, 1, '1995-06-01', 50000, 12, 4000, 'C'), (2, 2, '1996-07-01', 80000, 24, 3500, 'B');
INSERT INTO Transacciones (Identificador_Cuenta, Fecha_Realizada, Tipo_Movimiento, Monto_Involucrado, Saldo_Resultante_Cuenta) VALUES
 (1, '1995-02-01', 'PRIJEM', 1000, 1000),
 (1, '1995-03-01', 'VYDAJ',   300,  700),
 (2, '1996-07-01', 'PRIJEM', 500,  500);
"""


@pytest.fixture
def loaded(db):
    """Small known dataset, reloaded for every test so tests cannot affect each other."""
    tables = [
        "Transacciones",
        "Tarjeta",
        "Prestamos",
        "Disposicion",
        "Cuenta",
        "Cliente",
        "Estado_Prestamo",
        "Distrito",
    ]
    with db.model.begin() as con:
        con.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0")
        for t in tables:
            con.exec_driver_sql(f"DELETE FROM {t}")
        con.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1")
    raw = db.raw_connection(TEST_DB)
    try:
        cur = raw.cursor()
        for statement in (s.strip() for s in FIXTURE.split(";") if s.strip()):
            cur.execute(statement)
        raw.commit()
    finally:
        raw.close()
    return db
