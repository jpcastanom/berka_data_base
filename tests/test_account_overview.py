"""vw_resumen_cuenta and account_overview(): content, joins, edge cases and filters."""

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from berka_bank import routines
from berka_bank.routines import NO_LOAN, account_overview


def row(df, account):
    return df[df.Identificador_Cuenta == account].iloc[0]


def test_columns_are_stable(loaded):
    assert list(account_overview(loaded).columns) == [
        "Identificador_Cuenta", "Fecha_Apertura", "Frecuencia", "Sucursal", "Region", "Id_Titular",
        "Nacimiento_Titular", "Genero_Titular", "Num_Autorizados", "Tarjeta_Titular", "Codigo_Prestamos",
        "Monto_Prestamo", "Estado_Prestamo", "Descripcion_Estado_Prestamo", "Saldo_Actual",
    ]  # fmt: skip


def test_one_row_per_account_with_owner(loaded):
    df = account_overview(loaded)
    # account 1 has 1 owner + 2 disponents + card + loan: still a single row; account 4 has no owner: no row
    assert sorted(df.Identificador_Cuenta) == [1, 2, 3]
    assert df.Identificador_Cuenta.is_unique


def test_owner_data_comes_from_owner_not_disponent(loaded):
    r = row(account_overview(loaded), 1)
    assert (r.Id_Titular, r.Genero_Titular, r.Nacimiento_Titular) == (1, "M", date(1970, 1, 1))


def test_district_and_frequency(loaded):
    r = row(account_overview(loaded), 2)
    assert (r.Sucursal, r.Region, r.Frecuencia) == ("Brno", "south Moravia", "POPLATEK TYDNE")
    assert row(account_overview(loaded), 1).Fecha_Apertura == date(1995, 1, 1)


def test_disponent_count(loaded):
    df = account_overview(loaded)
    assert [int(row(df, a).Num_Autorizados) for a in (1, 2, 3)] == [2, 0, 0]


def test_card_is_the_owners_not_a_disponents(loaded):
    df = account_overview(loaded)
    assert row(df, 1).Tarjeta_Titular == "gold"
    assert pd.isna(row(df, 2).Tarjeta_Titular)  # its only card belongs to a disponent of account 1
    assert pd.isna(row(df, 3).Tarjeta_Titular)


def test_loan_data_and_description_from_catalog(loaded):
    df = account_overview(loaded)
    r = row(df, 1)
    assert (r.Codigo_Prestamos, r.Monto_Prestamo, r.Estado_Prestamo) == (1, Decimal("50000.00"), "C")
    assert r.Descripcion_Estado_Prestamo == "Vigente sin problemas"
    r3 = row(df, 3)
    assert r3[["Codigo_Prestamos", "Monto_Prestamo", "Estado_Prestamo", "Descripcion_Estado_Prestamo"]].isna().all()


def test_balance_matches_function_and_is_zero_without_movements(loaded):
    df = account_overview(loaded)
    assert [row(df, a).Saldo_Actual for a in (1, 2, 3)] == [Decimal("700.00"), Decimal("500.00"), Decimal("0.00")]
    for a in (1, 2, 3):
        assert row(df, a).Saldo_Actual == loaded.execute("SELECT fn_saldo_cuenta(:a, NULL)", {"a": a}).scalar()


def test_balance_follows_new_transactions_through_the_trigger(loaded):
    loaded.execute(
        "INSERT INTO Transacciones (Identificador_Cuenta, Fecha_Realizada, Tipo_Movimiento, Monto_Involucrado)"
        " VALUES (3, '1997-05-01', 'PRIJEM', 250)"
    )
    assert row(account_overview(loaded), 3).Saldo_Actual == Decimal("250.00")


def test_view_follows_updates_to_the_underlying_tables(loaded):
    loaded.execute("UPDATE Cliente SET Genero = 'F' WHERE Identificador_Cliente = 1")
    loaded.execute("UPDATE Prestamos SET Codigo_Estado = 'D' WHERE Codigo_Prestamos = 1")
    r = row(account_overview(loaded), 1)
    assert r.Genero_Titular == "F"
    assert r.Descripcion_Estado_Prestamo == "Vigente, cliente en deuda"


def test_owner_added_later_makes_the_account_appear(loaded):
    loaded.execute("INSERT INTO Disposicion VALUES (6, 'OWNER', 5, 4)")
    assert 4 in set(account_overview(loaded).Identificador_Cuenta)


# ------------------------------------------------------------------- filters
def test_filter_by_account(loaded):
    assert list(account_overview(loaded, account=2).Identificador_Cuenta) == [2]
    assert account_overview(loaded, account=999).empty
    assert len(account_overview(loaded, account=0)) == 3  # 0 = no filter (the UI default)


def test_filter_by_region(loaded):
    assert list(account_overview(loaded, region="Prague").Identificador_Cuenta) == [1, 3]
    assert account_overview(loaded, region="nowhere").empty


@pytest.mark.parametrize(
    ("loan", "expected"),
    [("C", [1]), ("B", [2]), ("A", []), (NO_LOAN, [3]), (None, [1, 2, 3])],
)
def test_filter_by_loan(loaded, loan, expected):
    assert list(account_overview(loaded, loan=loan).Identificador_Cuenta) == expected


def test_filters_combine(loaded):
    assert list(account_overview(loaded, region="Prague", loan=NO_LOAN).Identificador_Cuenta) == [3]
    assert account_overview(loaded, account=1, region="south Moravia").empty


@pytest.mark.parametrize("payload", ["' OR '1'='1", "x'; DROP TABLE Cuenta; --", "%", "Prague' --"])
def test_filters_are_parameterized(loaded, payload):
    assert account_overview(loaded, region=payload).empty
    assert account_overview(loaded, loan=payload).empty
    assert loaded.query("SELECT COUNT(*) AS n FROM Cuenta")["n"][0] == 4  # nothing was dropped


# ------------------------------------------------------------- deployment
def test_create_all_is_idempotent_and_registers_the_view(loaded):
    routines.create_all(loaded)
    routines.create_all(loaded)
    assert ("VIEW", "vw_resumen_cuenta") in {(k, n) for k, n, _ in routines.ROUTINES}
    assert len(account_overview(loaded)) == 3


def test_view_is_a_real_view_in_the_catalog(loaded):
    n = loaded.query(
        "SELECT COUNT(*) AS n FROM information_schema.VIEWS WHERE TABLE_SCHEMA = DATABASE() "
        "AND TABLE_NAME = 'vw_resumen_cuenta'"
    )["n"][0]
    assert n == 1
