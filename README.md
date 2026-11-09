# DataOps – Cálculo de salario total de empleados

Proyecto final del curso **DataOps** de DMC Institute.

Pipeline de **Azure Data Factory** que une la tabla PostgreSQL `dmc.rrhh.empleado` con el archivo de comisiones `ComisionEmpleados_V1_<AAAAMM>.csv`, calcula:

```
salario_total = mnt_salario + comision
```

y guarda el resultado en formato **Parquet** en un Data Lake (ADLS Gen2). El flujo se versiona en **Azure Repos** y se despliega con **Azure Pipelines** a los entornos DEV → QAS → PRD.

## Arquitectura

```
PostgreSQL (rrhh.empleado) ──┐
                             ├─► ADF Data Flow: join por empleado_id ─► Parquet en ADLS (curated/)
CSV en ADLS (raw/comisiones) ┘        └─ salario_total = mnt_salario + comision

Secretos de conexión ─► Azure Key Vault ─► Linked Service de ADF (identidad administrada)
Código ADF ─► Azure Repos (main) ─► Publicar ─► plantillas ARM ─► Azure Pipelines ─► QAS / PRD
```

## Recursos por entorno

Región `eastus`. Convención del curso: `az-<iniciales>-<entorno>-de-<tipo>-<nombre>`.

| Recurso | DEV | QAS | PRD |
|---|---|---|---|
| Grupo de recursos | `az-fv-dev-de-rg-dataops` | `az-fv-qas-de-rg-dataops` | `az-fv-prd-de-rg-dataops` |
| Data Factory | `az-fv-dev-de-dfc-etl` | `az-fv-qas-de-dfc-etl` | `az-fv-prd-de-dfc-etl` |
| Data Lake (ADLS Gen2) | `azfvdevdedlslake` | `azfvqasdedlslake` | `azfvprddedlslake` |
| Key Vault | `az-fv-dev-de-kvt-etl` | `az-fv-qas-de-kvt-etl` | `az-fv-prd-de-kvt-etl` |

Contenedores del Data Lake: `raw` (entrada: CSV de comisiones) y `curated` (salida: Parquet).

## Estructura del repositorio

| Carpeta / archivo | Contenido |
|---|---|
| `adf/` | Recursos de Data Factory (pipelines, data flows, datasets, linked services). Lo escribe ADF al estar conectado a Git |
| `pipelines/` | Definición YAML del CI/CD en Azure Pipelines |
| `scripts/` | `provisionar_azure.sh` crea la infraestructura de un entorno; `ejecutar_pipeline_adf.sh` ejecuta el pipeline y espera el resultado |
| `build/` | `package.json` con la herramienta de Microsoft que valida ADF y exporta las plantillas ARM |
| `tests/` | Pruebas estáticas del código ADF (pytest), pruebas de calidad de la salida y resultado esperado |
| `data/sample/` | CSV de comisiones de ejemplo (periodo 202610) |
| `docs/evidencias/` | Capturas de pantalla para el informe ([índice](docs/evidencias/README.md)) |
| `BITACORA.md` | Registro paso a paso del proyecto |
| `HALLAZGOS.md` | Análisis inicial: rúbrica, datos, decisiones |

## Despliegue

### Requisitos
- Suscripción de Azure con rol Owner.
- [Azure CLI](https://aka.ms/installazurecliwindowsx64) y Git. En Windows, ejecutar los scripts con Git Bash.
- Organización y proyecto en Azure DevOps conectados al mismo directorio (Microsoft Entra) que la suscripción.

### 1. Iniciar sesión en Azure
```bash
az login --tenant <TENANT_ID> --use-device-code
az account set --subscription "<SUSCRIPCION>"
```

### 2. Crear la infraestructura de cada entorno
La contraseña de PostgreSQL se pasa por variable de entorno y queda guardada solo en Key Vault:
```bash
PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh dev
PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh qas
PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh prd
```
El script crea el grupo de recursos, el Data Lake con sus contenedores (y sube el CSV a `raw/comisiones/`), el Key Vault con los secretos `pg-host`, `pg-port`, `pg-db`, `pg-user` y `pg-password`, y el Data Factory con identidad administrada y permisos sobre el Key Vault y el Data Lake.

### 3. Conectar Data Factory DEV a Git
En ADF Studio (DEV): *Manage → Git configuration* → Azure DevOps Git, repositorio `dataops-dmc`, rama de colaboración `main`, carpeta raíz `/adf`. También se puede hacer desde la terminal con la API `configureFactoryRepo` (ver [BITACORA.md](BITACORA.md), paso 15). Solo DEV se conecta a Git; QAS y PRD se actualizan por CI/CD.

### 4. Probar el pipeline en DEV
En ADF Studio: `pl_salario_total` → **Depurar** → *Usar el entorno de ejecución de la actividad* (el clúster solo vive durante la ejecución). Luego, para validar la salida:
```bash
az storage blob download-batch --account-name azfvdevdedlslake --auth-mode key \
  --source curated --pattern "salario_total/periodo=202610/*.parquet" --destination salida
pip install pandas pyarrow
python tests/validar_salida.py salida tests/esperado_salario_total_202610.csv
```

### 5. CI/CD con Azure Pipelines
Definición: [pipelines/azure-pipelines.yml](pipelines/azure-pipelines.yml) + [pipelines/templates/deploy-adf.yml](pipelines/templates/deploy-adf.yml). Se dispara con cada cambio en `main` (carpetas `adf/`, `pipelines/`, `tests/`, `build/`, `scripts/`).

| Etapa | Qué hace |
|---|---|
| **CI** | Pruebas estáticas del código ADF con pytest (`tests/test_adf_estatico.py`), validación con `@microsoft/azure-data-factory-utilities` y exportación de las plantillas ARM como artefacto |
| **CD_QAS** | Pre-despliegue (detiene triggers) → plantilla ARM con los parámetros de QAS → post-despliegue → ejecuta `pl_salario_total` → descarga el Parquet → `tests/validar_salida.py` |
| **CD_PRD** | Espera la **aprobación** del environment `ADF-PRD` y repite el despliegue y las pruebas en PRD |

Parámetros que cambian por entorno (el resto viene del ARM exportado):
`factoryName`, `ls_adls_lake_properties_typeProperties_url`, `ls_kv_etl_properties_typeProperties_baseUrl`.

No se usa el botón **Publicar** de ADF: las plantillas ARM se generan en el CI (publicación automatizada recomendada por Microsoft).

Requisitos en el proyecto de Azure DevOps:
- Service connection **`CONEXION_AZURE`** (Azure Resource Manager, workload identity federation) sobre la suscripción.
- Environments **`ADF-QAS`** y **`ADF-PRD`** (este con aprobación obligatoria).

### 6. Limpieza
Para no generar costos al terminar:
```bash
for e in dev qas prd; do az group delete -n az-fv-$e-de-rg-dataops --yes --no-wait; done
```

## Seguridad
- No hay credenciales en el repositorio. Los secretos viven en **Azure Key Vault**, y en Azure DevOps en **Variable Groups** marcados como secretos.
- Data Factory accede a Key Vault y al Data Lake con su **identidad administrada** (RBAC), sin claves.
- `.gitignore` excluye los archivos originales del curso, los `.zip` y `.sql` (contienen la conexión) y cualquier `.env`.

## Autor
Frank Vargas Chavez – DMC Institute, curso DataOps (2026).
