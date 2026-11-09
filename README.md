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
| `scripts/` | Automatización: `provisionar_azure.sh` crea la infraestructura de un entorno |
| `tests/` | Pruebas de calidad de datos |
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

### 4. CI/CD
*En construcción.* Se documentará aquí el pipeline de Azure Pipelines (validación, generación de plantillas ARM y despliegue a QAS y PRD con aprobaciones).

## Seguridad
- No hay credenciales en el repositorio. Los secretos viven en **Azure Key Vault**, y en Azure DevOps en **Variable Groups** marcados como secretos.
- Data Factory accede a Key Vault y al Data Lake con su **identidad administrada** (RBAC), sin claves.
- `.gitignore` excluye los archivos originales del curso, los `.zip` y `.sql` (contienen la conexión) y cualquier `.env`.

## Autor
Frank Vargas Chavez – DMC Institute, curso DataOps (2026).
