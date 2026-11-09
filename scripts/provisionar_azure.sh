#!/usr/bin/env bash
# Crea la infraestructura de un entorno: grupo de recursos, Data Lake (ADLS Gen2),
# Key Vault con los secretos de PostgreSQL y Data Factory con identidad administrada.
#
# Uso:
#   PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh dev|qas|prd
#
# Variables opcionales: INICIALES (fv), LOCATION (eastus), CSV (archivo a subir a raw/).
# La contraseña nunca se guarda en el repositorio: se pasa por variable de entorno.
set -euo pipefail
export MSYS_NO_PATHCONV=1   # evita que Git Bash convierta rutas /subscriptions/... en rutas de Windows

ENV="${1:?Uso: provisionar_azure.sh dev|qas|prd}"
case "$ENV" in dev|qas|prd) ;; *) echo "Entorno inválido: $ENV" >&2; exit 1 ;; esac
: "${PG_PASSWORD:?Falta la variable PG_PASSWORD}"

INI="${INICIALES:-fv}"
LOCATION="${LOCATION:-eastus}"
CSV="${CSV:-PROYECTO/ComisionEmpleados_V1_202610.csv}"

RG="az-$INI-$ENV-de-rg-dataops"
ADF="az-$INI-$ENV-de-dfc-etl"
SA="az${INI}${ENV}dedlslake"
KV="az-$INI-$ENV-de-kvt-etl"
TAGS=(proyecto=dataops-dmc "entorno=$ENV")

SUB=$(az account show --query id -o tsv)
ME=$(az ad signed-in-user show --query id -o tsv)

echo "== [$ENV] Grupo de recursos $RG"
az group create -n "$RG" -l "$LOCATION" --tags "${TAGS[@]}" -o none

echo "== [$ENV] Data Lake $SA (contenedores raw y curated)"
az storage account create -n "$SA" -g "$RG" -l "$LOCATION" \
  --sku Standard_LRS --kind StorageV2 --hns true \
  --min-tls-version TLS1_2 --allow-blob-public-access false \
  --tags "${TAGS[@]}" -o none
for c in raw curated; do
  az storage container-rm create --storage-account "$SA" -g "$RG" -n "$c" -o none
done
SA_ID=$(az storage account show -n "$SA" -g "$RG" --query id -o tsv)

if [[ -f "$CSV" ]]; then
  echo "== [$ENV] Subiendo $(basename "$CSV") a raw/comisiones/"
  az storage blob upload --account-name "$SA" --auth-mode key --overwrite \
    --container-name raw --name "comisiones/$(basename "$CSV")" --file "$CSV" -o none
fi

echo "== [$ENV] Key Vault $KV"
if ! az keyvault show -n "$KV" -o none 2>/dev/null; then
  az keyvault create -n "$KV" -g "$RG" -l "$LOCATION" \
    --enable-rbac-authorization true --retention-days 7 \
    --tags "${TAGS[@]}" -o none
fi
KV_ID=$(az keyvault show -n "$KV" --query id -o tsv)
az role assignment create --assignee-object-id "$ME" --assignee-principal-type User \
  --role "Key Vault Secrets Officer" --scope "$KV_ID" -o none

echo "== [$ENV] Guardando secretos de PostgreSQL (puede esperar a que se apliquen los permisos)"
set_secret() {
  for i in {1..12}; do
    az keyvault secret set --vault-name "$KV" -n "$1" --value "$2" -o none 2>/dev/null && return 0
    sleep 10
  done
  echo "No se pudo guardar el secreto $1" >&2; return 1
}
set_secret pg-host     "mgg.vps.webdock.cloud"
set_secret pg-port     "5432"
set_secret pg-db       "dmc"
set_secret pg-user     "usr_ro_dmc_rrhh_estudiantes"
set_secret pg-password "$PG_PASSWORD"

echo "== [$ENV] Data Factory $ADF (identidad administrada)"
ADF_PID=$(az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.DataFactory/factories/$ADF?api-version=2018-06-01" \
  --body "{\"location\":\"$LOCATION\",\"identity\":{\"type\":\"SystemAssigned\"},\"tags\":{\"proyecto\":\"dataops-dmc\",\"entorno\":\"$ENV\"}}" \
  --query identity.principalId -o tsv)

echo "== [$ENV] Permisos de Data Factory sobre Key Vault y Data Lake"
az role assignment create --assignee-object-id "$ADF_PID" --assignee-principal-type ServicePrincipal \
  --role "Key Vault Secrets User" --scope "$KV_ID" -o none
az role assignment create --assignee-object-id "$ADF_PID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$SA_ID" -o none
az role assignment create --assignee-object-id "$ME" --assignee-principal-type User \
  --role "Storage Blob Data Contributor" --scope "$SA_ID" -o none

echo "== [$ENV] Listo"
az resource list -g "$RG" --query "[].{recurso:name, tipo:type}" -o table
