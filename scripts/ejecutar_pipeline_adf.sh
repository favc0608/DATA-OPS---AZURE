#!/usr/bin/env bash
# Ejecuta el pipeline pl_salario_total en un Data Factory y espera a que termine.
# Termina con código 0 si la ejecución es "Succeeded" y 1 en cualquier otro caso.
#
# Uso:
#   ./scripts/ejecutar_pipeline_adf.sh <grupo_recursos> <data_factory> [periodo] [aplicar_tope]
# Ejemplo:
#   ./scripts/ejecutar_pipeline_adf.sh az-fv-qas-de-rg-dataops az-fv-qas-de-dfc-etl 202610 si
set -euo pipefail
export MSYS_NO_PATHCONV=1

RG="${1:?Falta el grupo de recursos}"
ADF="${2:?Falta el nombre del Data Factory}"
PERIODO="${3:-202610}"
TOPE="${4:-si}"
API="api-version=2018-06-01"

SUB=$(az account show --query id -o tsv)
BASE="https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.DataFactory/factories/$ADF"

RUN=$(az rest --method post --url "$BASE/pipelines/pl_salario_total/createRun?$API" \
  --body "{\"periodo\":\"$PERIODO\",\"aplicar_tope\":\"$TOPE\"}" --query runId -o tsv)
echo "Ejecución iniciada en $ADF: runId=$RUN (periodo=$PERIODO, aplicar_tope=$TOPE)"

for _ in $(seq 1 60); do
  ESTADO=$(az rest --method get --url "$BASE/pipelineruns/$RUN?$API" --query status -o tsv)
  echo "$(date +%H:%M:%S) estado: $ESTADO"
  case "$ESTADO" in
    Succeeded)
      az rest --method post --url "$BASE/pipelineruns/$RUN/queryActivityruns?$API" \
        --body "{\"lastUpdatedAfter\":\"2020-01-01T00:00:00Z\",\"lastUpdatedBefore\":\"2100-01-01T00:00:00Z\"}" \
        --query "value[].{actividad:activityName, estado:status, duracion_ms:durationInMs}" -o table
      exit 0 ;;
    Failed|Cancelled)
      az rest --method get --url "$BASE/pipelineruns/$RUN?$API" --query message -o tsv
      exit 1 ;;
  esac
  sleep 20
done
echo "Tiempo de espera agotado (20 min)"
exit 1
