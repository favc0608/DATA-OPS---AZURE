"""Pruebas de calidad sobre la salida Parquet del pipeline pl_salario_total.

Compara los archivos Parquet de curated/salario_total/periodo=<AAAAMM>/
(descargados a una carpeta local) contra el resultado esperado calculado
desde la base y el CSV (tests/esperado_salario_total_<AAAAMM>.csv).

Uso:
    python tests/validar_salida.py <carpeta_parquet> [tests/esperado_salario_total_202610.csv]

Devuelve código 0 si todas las pruebas pasan y 1 si alguna falla.
"""
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd

COLUMNAS = [
    "empleado_id", "nom_empleado", "ape_empleado", "cod_cargo", "cod_departamento",
    "mnt_salario", "tiene_comision", "comision_original", "mnt_tope_comision",
    "tope_aplicado", "comision_aplicada", "salario_total", "periodo", "fecha_proceso",
]


def dec(v):
    return None if pd.isna(v) or v == "" else Decimal(str(v)).quantize(Decimal("0.01"))


def main(carpeta: str, esperado_csv: str) -> int:
    archivos = sorted(Path(carpeta).rglob("*.parquet"))
    if not archivos:
        print(f"FALLA: no hay archivos .parquet en {carpeta}")
        return 1
    real = pd.concat([pd.read_parquet(a) for a in archivos], ignore_index=True)
    esp = pd.read_csv(esperado_csv, dtype=str, keep_default_na=False)

    pruebas = []

    def prueba(nombre, ok, detalle=""):
        pruebas.append(ok)
        print(f"{'OK   ' if ok else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not ok else ""))

    faltan = [c for c in COLUMNAS if c not in real.columns]
    prueba("Esquema: están las 14 columnas esperadas", not faltan, f"faltan {faltan}")
    prueba(f"Conteo de filas = {len(esp)}", len(real) == len(esp), f"real {len(real)}")
    prueba("empleado_id sin duplicados", real["empleado_id"].is_unique)
    prueba("salario_total sin nulos", real["salario_total"].notna().all())
    prueba("salario_total > 0", (real["salario_total"].map(dec) > 0).all())
    prueba("Todos los empleados de la base están en la salida",
           set(real["empleado_id"].astype(int)) == set(esp["empleado_id"].astype(int)))

    real_idx = real.set_index(real["empleado_id"].astype(int))
    errores = []
    for _, e in esp.iterrows():
        r = real_idx.loc[int(e["empleado_id"])]
        for col in ["mnt_salario", "comision_original", "mnt_tope_comision", "comision_aplicada", "salario_total"]:
            if dec(r[col]) != dec(e[col]):
                errores.append(f"id {e['empleado_id']} {col}: real {r[col]} esperado {e[col]}")
        for col in ["tiene_comision", "tope_aplicado"]:
            if str(bool(r[col])).lower() != e[col]:
                errores.append(f"id {e['empleado_id']} {col}: real {r[col]} esperado {e[col]}")
    prueba("Valores por empleado iguales al esperado", not errores, "; ".join(errores[:5]))

    sin_com = sorted(real.loc[~real["tiene_comision"].astype(bool), "empleado_id"].astype(int))
    prueba("Empleados sin comisión tienen comision_aplicada = 0",
           all(dec(v) == 0 for v in real.loc[~real["tiene_comision"].astype(bool), "comision_aplicada"]),
           f"ids {sin_com}")
    prueba("comision_aplicada <= mnt_tope_comision cuando hay tope",
           all(dec(a) <= dec(t) for a, t in zip(real["comision_aplicada"], real["mnt_tope_comision"]) if dec(t) is not None))
    prueba("salario_total = mnt_salario + comision_aplicada",
           all(dec(s) == dec(m) + dec(c) for s, m, c in zip(real["salario_total"], real["mnt_salario"], real["comision_aplicada"])))

    suma_real = sum(dec(v) for v in real["salario_total"])
    suma_esp = sum(dec(v) for v in esp["salario_total"])
    prueba(f"Suma de salario_total = {suma_esp}", suma_real == suma_esp, f"real {suma_real}")

    print(f"\nResumen: {sum(pruebas)}/{len(pruebas)} pruebas OK | filas {len(real)} | "
          f"sin comisión {len(sin_com)} | tope aplicado {int(real['tope_aplicado'].astype(bool).sum())} | "
          f"suma salario_total {suma_real}")
    return 0 if all(pruebas) else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "tests/esperado_salario_total_202610.csv"))
