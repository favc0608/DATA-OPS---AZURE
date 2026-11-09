"""Pruebas estáticas del código de Azure Data Factory (se ejecutan en el CI, sin costo).

Revisan los JSON de adf/ sin conectarse a Azure: estructura, referencias entre
recursos, seguridad de credenciales y reglas de negocio del data flow. También
verifican que el resultado esperado sea coherente con las reglas.
"""
import csv
import json
from decimal import Decimal
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
ADF = RAIZ / "adf"
ESPERADO = RAIZ / "tests" / "esperado_salario_total_202610.csv"
CARPETAS = {"linkedService": "LinkedServiceReference", "dataset": "DatasetReference",
            "dataflow": "DataFlowReference", "pipeline": "PipelineReference"}


def cargar(carpeta, nombre):
    return json.loads((ADF / carpeta / f"{nombre}.json").read_text(encoding="utf-8"))


def todos():
    return {(p.parent.name, p.stem): json.loads(p.read_text(encoding="utf-8"))
            for p in ADF.glob("*/*.json")}


def referencias(nodo):
    if isinstance(nodo, dict):
        if "referenceName" in nodo and "type" in nodo:
            yield nodo["type"], nodo["referenceName"]
        for v in nodo.values():
            yield from referencias(v)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from referencias(v)


def script_df():
    return "\n".join(cargar("dataflow", "df_salario_total")["properties"]["typeProperties"]["scriptLines"])


# --- Estructura -----------------------------------------------------------

def test_existen_los_recursos_esperados():
    esperados = {("pipeline", "pl_salario_total"), ("dataflow", "df_salario_total"),
                 ("dataset", "ds_pg_empleado"), ("dataset", "ds_adls_empleado_parquet"),
                 ("dataset", "ds_adls_comision_csv"), ("dataset", "ds_adls_salario_parquet"),
                 ("linkedService", "ls_pgsql_empleado"), ("linkedService", "ls_adls_lake"),
                 ("linkedService", "ls_kv_etl")}
    assert esperados <= set(todos())


@pytest.mark.parametrize("clave", sorted(todos()), ids=lambda c: f"{c[0]}/{c[1]}")
def test_nombre_coincide_con_archivo(clave):
    assert todos()[clave]["name"] == clave[1]


def test_referencias_existen():
    recursos = todos()
    nombres = {(CARPETAS[c], n) for c, n in recursos if c in CARPETAS}
    rotas = [(c, n, r) for (c, n), j in recursos.items() for r in referencias(j)
             if r[0] in CARPETAS.values() and r not in nombres]
    assert not rotas, f"Referencias a recursos inexistentes: {rotas}"


# --- Seguridad ------------------------------------------------------------

def test_password_postgres_viene_de_key_vault():
    pwd = cargar("linkedService", "ls_pgsql_empleado")["properties"]["typeProperties"]["password"]
    assert pwd["type"] == "AzureKeyVaultSecret"
    assert pwd["store"]["referenceName"] == "ls_kv_etl"
    assert pwd["secretName"] == "pg-password"


def test_sin_claves_ni_cadenas_de_conexion_en_texto_plano():
    for (carpeta, nombre), j in todos().items():
        tp = j["properties"].get("typeProperties", {})
        for campo in ("accountKey", "connectionString", "sasUri", "servicePrincipalKey"):
            valor = tp.get(campo)
            assert valor is None or (isinstance(valor, dict) and valor.get("type") == "AzureKeyVaultSecret"), \
                f"{carpeta}/{nombre}: {campo} en texto plano"
        if "password" in tp:
            assert isinstance(tp["password"], dict) and tp["password"].get("type") == "AzureKeyVaultSecret"


def test_data_lake_usa_identidad_administrada():
    tp = cargar("linkedService", "ls_adls_lake")["properties"]["typeProperties"]
    assert set(tp) == {"url"}, "Solo URL: la autenticación es con la identidad administrada de ADF"


# --- Reglas de negocio ----------------------------------------------------

def test_join_es_left_por_empleado_id():
    s = script_df()
    assert "join(empleado_id == comision_empleado_id" in s
    assert "joinType:'left'" in s


def test_empleados_sin_comision_tienen_cero():
    assert "iif(isNull(comision), 0, comision)" in script_df()


def test_tope_de_comision_parametrizado():
    s = script_df()
    assert "$aplicar_tope == 'si'" in s
    assert "comision_original > tope_comision, tope_comision, comision_original" in s


def test_formula_salario_total():
    assert "salario_total = toDecimal(salario_base +" in script_df()


def test_salida_parquet_en_curated_por_periodo():
    tp = cargar("dataset", "ds_adls_salario_parquet")["properties"]["typeProperties"]
    assert cargar("dataset", "ds_adls_salario_parquet")["properties"]["type"] == "Parquet"
    assert tp["location"]["fileSystem"] == "curated"
    assert "periodo=" in tp["location"]["folderPath"]["value"]


def test_csv_separador_y_codificacion():
    tp = cargar("dataset", "ds_adls_comision_csv")["properties"]["typeProperties"]
    assert tp["columnDelimiter"] == ";"
    assert tp["encodingName"] == "UTF-8"
    assert tp["firstRowAsHeader"] is True


def test_pipeline_copy_luego_dataflow_con_parametros():
    p = cargar("pipeline", "pl_salario_total")["properties"]
    acts = {a["name"]: a for a in p["activities"]}
    assert acts["cp_pg_empleado_a_raw"]["type"] == "Copy"
    df = acts["df_calcular_salario_total"]
    assert df["type"] == "ExecuteDataFlow"
    assert df["dependsOn"][0]["activity"] == "cp_pg_empleado_a_raw"
    assert p["parameters"]["periodo"]["defaultValue"] == "202610"
    assert p["parameters"]["aplicar_tope"]["defaultValue"] == "si"


# --- Coherencia del resultado esperado --------------------------------------

def test_resultado_esperado_cumple_reglas():
    filas = list(csv.DictReader(ESPERADO.open(encoding="utf-8")))
    assert len(filas) == 48
    for f in filas:
        sal, com, apl, tot = (Decimal(f[c]) for c in ("mnt_salario", "comision_original", "comision_aplicada", "salario_total"))
        assert tot == sal + apl
        if f["mnt_tope_comision"]:
            assert apl == min(com, Decimal(f["mnt_tope_comision"]))
        else:
            assert apl == com
        if f["tiene_comision"] == "false":
            assert com == 0
