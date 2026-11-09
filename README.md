# DataOps: cálculo del salario total de empleados

Proyecto final del curso DataOps de DMC Institute (2026).

Pipeline de Azure Data Factory que une la tabla `rrhh.empleado` de PostgreSQL con el archivo mensual de comisiones `ComisionEmpleados_V1_<AAAAMM>.csv`, calcula el salario total de cada empleado y guarda el resultado en formato Parquet en un Data Lake. El código se versiona en Azure Repos y se despliega con Azure Pipelines a los entornos de prueba (QAS) y producción (PRD).

```
salario_total = mnt_salario + comision_aplicada
comision_aplicada = min(comision, mnt_tope_comision)   si el empleado tiene tope
                  = comision                            si no tiene tope
                  = 0                                   si no figura en el CSV
```

## Arquitectura

```
PostgreSQL rrhh.empleado ──Copy──► raw/empleados/empleado.parquet ──┐
                                                                    ├─► Data Flow ─► curated/salario_total/periodo=<AAAAMM>/
CSV de comisiones ─────────────────► raw/comisiones/*.csv ──────────┘

Key Vault: credenciales de PostgreSQL, leídas por Data Factory con identidad administrada
Azure Repos (adf/) ─► Azure Pipelines: CI ─► CD QAS ─► aprobación ─► CD PRD
```

El pipeline `pl_salario_total` tiene dos actividades. La primera copia la tabla de empleados al Data Lake, porque los Data Flows de ADF no leen directamente de un PostgreSQL externo. La segunda ejecuta el Data Flow `df_salario_total`, que hace un left join por `empleado_id`, aplica las reglas de comisión y escribe el Parquet. Recibe dos parámetros: `periodo` (por defecto `202610`) y `aplicar_tope` (`si` o `no`).

## Contenido del repositorio

| Ruta | Contenido |
|---|---|
| `adf/` | Recursos de Data Factory en JSON: linked services, datasets, data flow y pipeline. Data Factory DEV escribe aquí al estar conectado a Git |
| `pipelines/` | Definición del CI/CD (`azure-pipelines.yml`) y plantilla de despliegue por entorno (`templates/deploy-adf.yml`) |
| `build/` | `package.json` con `@microsoft/azure-data-factory-utilities`, que valida ADF y exporta las plantillas ARM |
| `scripts/` | `provisionar_azure.sh` crea la infraestructura de un entorno; `ejecutar_pipeline_adf.sh` lanza el pipeline y espera su resultado |
| `tests/` | Pruebas estáticas del código ADF, pruebas de calidad de la salida y resultado esperado del periodo 202610 |
| `data/sample/` | CSV de comisiones del periodo 202610 |
| `docs/` | Enunciado, [informe final](docs/Informe_Final_DataOps_Frank_Vargas.docx) y evidencias del desarrollo ([índice](docs/evidencias/README.md)) |
| `BITACORA.md` | Registro de cada etapa del proyecto, con problemas encontrados y soluciones |

## Recursos por entorno

Región `eastus`, con la convención de nombres del curso.

| Recurso | DEV | QAS | PRD |
|---|---|---|---|
| Grupo de recursos | `az-fv-dev-de-rg-dataops` | `az-fv-qas-de-rg-dataops` | `az-fv-prd-de-rg-dataops` |
| Data Factory | `az-fv-dev-de-dfc-etl` | `az-fv-qas-de-dfc-etl` | `az-fv-prd-de-dfc-etl` |
| Data Lake (ADLS Gen2) | `azfvdevdedlslake` | `azfvqasdedlslake` | `azfvprddedlslake` |
| Key Vault | `az-fv-dev-de-kvt-etl` | `az-fv-qas-de-kvt-etl` | `az-fv-prd-de-kvt-etl` |

Cada Data Lake tiene un contenedor `raw` (entradas) y otro `curated` (salida). Solo el Data Factory de DEV está conectado a Git; QAS y PRD reciben los cambios únicamente por CI/CD.

## Despliegue

Requisitos: suscripción de Azure con rol Owner, Azure CLI, Git y una organización de Azure DevOps conectada al mismo directorio de Microsoft Entra que la suscripción. En Windows, los scripts se ejecutan con Git Bash.

1. Iniciar sesión en Azure:
   ```bash
   az login --tenant <TENANT_ID> --use-device-code
   az account set --subscription "<SUSCRIPCION>"
   ```
2. Crear la infraestructura de cada entorno. La contraseña de PostgreSQL se pasa por variable de entorno y solo queda guardada en Key Vault:
   ```bash
   PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh dev
   PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh qas
   PG_PASSWORD='<contraseña>' ./scripts/provisionar_azure.sh prd
   ```
   El script crea el grupo de recursos, el Data Lake con sus contenedores y el CSV en `raw/comisiones/`, el Key Vault con los secretos `pg-host`, `pg-port`, `pg-db`, `pg-user` y `pg-password`, y el Data Factory con identidad administrada y permisos sobre el Key Vault y el Data Lake.
3. Conectar Data Factory DEV a Git: en ADF Studio, *Manage → Git configuration*, con Azure DevOps Git, repositorio `dataops-dmc`, rama de colaboración `main` y carpeta raíz `/adf`.
4. Crear en Azure DevOps la service connection `CONEXION_AZURE` (Azure Resource Manager con workload identity federation) y los environments `ADF-QAS` y `ADF-PRD`, este último con aprobación obligatoria.
5. Registrar `pipelines/azure-pipelines.yml` como pipeline. Desde entonces, cada cambio en `main` que toque `adf/`, `pipelines/`, `tests/`, `build/` o `scripts/` lo ejecuta automáticamente.

Para probar el pipeline en DEV sin pasar por CI/CD, en ADF Studio se usa *Depurar → Usar el entorno de ejecución de la actividad*, que mantiene el clúster encendido solo durante la ejecución.

## CI/CD

| Etapa | Pasos |
|---|---|
| CI | Pruebas estáticas con pytest, validación de los recursos de ADF y exportación de las plantillas ARM como artefacto |
| CD QAS | Script previo (detiene triggers), despliegue ARM con los parámetros de QAS, script posterior (limpieza), ejecución de `pl_salario_total` y pruebas de calidad sobre el Parquet generado |
| CD PRD | Espera la aprobación del environment `ADF-PRD` y repite la secuencia en producción |

Las plantillas ARM se generan en el CI con la herramienta oficial de Microsoft; no se usa el botón *Publicar* de ADF. Por entorno solo cambian tres parámetros: `factoryName`, la URL del Data Lake y la URL del Key Vault.

## Pruebas

- `tests/test_adf_estatico.py` (22 pruebas, se ejecutan en el CI): estructura de los JSON, referencias entre recursos, credenciales solo desde Key Vault, Data Lake con identidad administrada y reglas de negocio del data flow.
- `tests/validar_salida.py` (11 pruebas, se ejecutan en QAS y PRD después de cada despliegue): compara el Parquet de salida con `tests/esperado_salario_total_202610.csv`, que se calculó por separado a partir de la base y del CSV. Revisa esquema, conteo, duplicados, nulos, valores por empleado, comisión cero, respeto del tope, fórmula y suma total.

Ejecución local de las pruebas de calidad:
```bash
az storage blob download-batch --account-name azfvdevdedlslake --auth-mode key \
  --source curated --pattern "salario_total/periodo=202610/*.parquet" --destination salida
pip install pandas pyarrow
python tests/validar_salida.py salida tests/esperado_salario_total_202610.csv
```

Resultado del periodo 202610: 48 empleados, 15 sin comisión, 13 con tope aplicado y una suma de `salario_total` de 352,183.40.

## Seguridad

- El repositorio no contiene credenciales. La contraseña de PostgreSQL vive en Key Vault y el archivo original con la conexión está excluido por `.gitignore`.
- Data Factory accede a Key Vault y al Data Lake con su identidad administrada (RBAC), sin claves.
- La service connection usa workload identity federation, sin secretos que rotar, y tiene rol Contributor solo sobre los grupos de recursos de QAS y PRD.
- El servidor PostgreSQL del curso no admite SSL, por lo que la conexión no va cifrada. Es una limitación de la fuente, no del pipeline.

## Costos y limpieza

Una ejecución completa del CI/CD cuesta alrededor de 0.45 USD, casi todo por el clúster del Data Flow en QAS y PRD. Para eliminar todos los recursos al terminar:
```bash
for e in dev qas prd; do az group delete -n az-fv-$e-de-rg-dataops --yes --no-wait; done
```

## Autor

Frank Vargas Chavez
