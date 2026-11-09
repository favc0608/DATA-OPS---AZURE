# Bitácora – Proyecto Final DataOps (DMC)

Registro paso a paso de lo que se va haciendo y por qué.

---

## 08/11/2026

### 1. Lectura del contexto
- **Qué:** leí CLAUDE.md, HALLAZGOS.md, proyectofinal.md, el CSV de comisiones y el zip EmpleadoSql.
- **Por qué:** entender el proyecto antes de tocar nada.
- **Resultado:**
  - Objetivo: unir la tabla PostgreSQL `rrhh.empleado` con el CSV por `empleado_id`, calcular `salario_total = mnt_salario + comision` y guardar un Parquet en el Data Lake, con CI/CD DEV → TEST → PRD.
  - CSV: separador `;`, 34 filas, faltan los IDs 6, 7 y 8.
  - La contraseña de la base de datos está en texto plano en el zip; no debe subirse al repositorio.

### 2. Verificación del plugin de Azure
- **Qué:** probé el plugin de Azure de Claude Code.
- **Resultado:** estaba instalado, pero no veía ninguna suscripción.

### 3. Suscripción de Azure
- **Problema:** la cuenta estaba creada, pero sin suscripción. El portal decía "¿No tiene ninguna suscripción?".
- **Solución:** creaste manualmente la suscripción de pago por uso **FRANK PRIV - DEP OPS**, con rol Propietario.
- **Costo estimado:** unos 2 USD si el Data Flow corre 30 minutos o menos (8 vCores × 0.273 USD/h). Solo cobra el clúster del Data Flow cuando está encendido; diseñar en el editor es gratis.

### 4. Instalación de Azure CLI
- **Qué:** Azure CLI (`az`) es la herramienta de línea de comandos para manejar Azure desde la terminal. El plugin la necesita para usar tu sesión.
- **Problema:** `winget` no existe en tu Windows.
- **Solución:** la instalaste con el MSI oficial de Microsoft desde PowerShell.

### 5. Inicio de sesión con verificación en dos pasos (MFA)
- **Problema 1:** `az login` falló porque tu directorio exige verificación en dos pasos.
- **Problema 2:** Microsoft bloqueó temporalmente el envío de códigos por correo, por demasiados intentos.
- **Solución:** inicio de sesión con código de dispositivo:
  `az login --tenant 0e2a992a-2881-4290-a6f1-c34c509bd83f --use-device-code`
  Ingresaste el código en https://login.microsoft.com/device.
- **Resultado:** sesión iniciada; la suscripción aparece como predeterminada y activa.

### 6. Registro de proveedores de recursos
- **Qué:** Azure exige "activar" cada tipo de servicio en la suscripción antes de crearlo. Se activaron:
  - `Microsoft.DataFactory` (Data Factory)
  - `Microsoft.Storage` (Data Lake / Blob Storage)
  - `Microsoft.KeyVault` (bóveda de secretos)
- **Costo:** gratis.
- **Resultado:** los tres quedaron registrados.

### 7. Actualización de HALLAZGOS.md
- Secciones 8 y 9 actualizadas con la suscripción y el avance.

### 8. Decisiones de arquitectura
- **Ruta:** Azure Data Factory (la que pide el enunciado y la que usa la clase 03).
- **Repositorio y CI/CD:** Azure DevOps (Azure Repos + Azure Pipelines), todo en una sola plataforma.
- **Iniciales:** `fv`. **Región:** `eastus` (la del curso).
- **Entornos:** `dev`, `qas` (prueba) y `prd`.
- **Nombres** (convención del curso):
  | Recurso | DEV |
  |---|---|
  | Grupo de recursos | `az-fv-dev-de-rg-dataops` |
  | Data Factory | `az-fv-dev-de-dfc-etl` |
  | Data Lake (ADLS Gen2) | `azfvdevdedlslake` |
  | Key Vault | `az-fv-dev-de-kvt-etl` |

### 9. Alerta de presupuesto
- **Qué:** presupuesto `presupuesto-dataops` de **5 USD al mes** sobre la suscripción.
- **Avisos por correo:** al 50 % y al 100 % del gasto real, y si el pronóstico indica que se superará el 100 %.
- **Por qué:** enterarse a tiempo si algo queda encendido (por ejemplo, el clúster del Data Flow).

### 10. Script de aprovisionamiento
- **Qué:** [scripts/provisionar_azure.sh](scripts/provisionar_azure.sh), que crea un entorno completo con un solo comando:
  `PG_PASSWORD='...' ./scripts/provisionar_azure.sh dev|qas|prd`
- **Qué crea:**
  - Grupo de recursos con etiquetas `proyecto` y `entorno`.
  - Data Lake ADLS Gen2 (espacio de nombres jerárquico, TLS 1.2, sin acceso público) con contenedores `raw` (entrada) y `curated` (salida Parquet). Sube el CSV a `raw/comisiones/`.
  - Key Vault con permisos RBAC y los secretos `pg-host`, `pg-port`, `pg-db`, `pg-user` y `pg-password`.
  - Data Factory con identidad administrada, que recibe los roles *Key Vault Secrets User* sobre el Key Vault y *Storage Blob Data Contributor* sobre el Data Lake.
- **Por qué un script:** reproducir exactamente lo mismo en QAS y PRD, y dejarlo como evidencia de infraestructura como código.
- **Seguridad:** la contraseña no está en el script; se pasa por la variable de entorno `PG_PASSWORD`.

### 11. Creación del entorno DEV
- **Qué:** se ejecutó el script para `dev`. Antes se comprobó que los nombres del Data Lake y del Key Vault estaban libres en Azure (son únicos a nivel mundial).
- **Verificación:**
  - Recursos creados: `azfvdevdedlslake`, `az-fv-dev-de-kvt-etl`, `az-fv-dev-de-dfc-etl`.
  - Secretos en el Key Vault: los 5 esperados.
  - CSV en `raw/comisiones/ComisionEmpleados_V1_202610.csv` (917 bytes).
  - Roles: Data Factory puede leer secretos y escribir en el Data Lake; tu usuario también.
- **Costo:** prácticamente 0 USD (Data Factory vacío no cobra; Data Lake y Key Vault, centavos).

### 12. Organización de Azure DevOps
- **Qué:** registro en https://dev.azure.com (se llega desde el portal buscando "Organizaciones de Azure DevOps"). Se descartó "Managed DevOps Pools", que cobra por hora.
- **Plan:** organización `fvargas-dmc`, proyecto privado `dataops-dmc` con Git, y solicitud del agente gratuito de pipelines.
- **Directorio:** Azure DevOps proponía por defecto "Microsoft account" (porque la cuenta es de Gmail); se cambió a **Directorio predeterminado** (el mismo de la suscripción). Así Azure DevOps y Azure comparten directorio y la conexión de servicio hacia la suscripción se crea casi automáticamente.
- **Problema 1:** el formulario "Almost done" no encontraba ninguna suscripción. **Causa:** había vuelto al directorio "Microsoft account". **Solución:** "Switch directory" → Directorio predeterminado.
- **Problema 2:** ya aparece la suscripción, pero Azure DevOps dice "You need to be an owner or contributor". Se comprobó con Azure CLI que el usuario **sí tiene rol Owner** sobre la suscripción, así que es un retraso o caché de Azure DevOps con suscripciones recién creadas. **Solución propuesta:** cerrar sesión, reintentar en incógnito o esperar 30–60 min.
- **Resultado:** organización `frankvargaschavez201` creada (https://dev.azure.com/frankvargaschavez201), con la suscripción vinculada para facturación. La pantalla final mostraba "Microsoft account": hay que confirmar en *Organization settings → Microsoft Entra* que esté conectada a Directorio predeterminado.
- **Proyecto:** `dataops-dmc`, privado, con Git (https://dev.azure.com/frankvargaschavez201/dataops-dmc).
- **Problema 3:** la API de Azure DevOps rechaza la sesión de Azure CLI y redirige a un inicio de sesión de cuenta personal (`switch_hint=P`). **Causa:** la organización quedó en "Microsoft account" y no en Directorio predeterminado. **Solución:** *Organization settings → Microsoft Entra → Connect directory* → Directorio predeterminado. Es seguro porque la organización solo tiene un usuario.
- **Resultado:** "Connect success!": la organización `frankvargaschavez201` quedó conectada a Directorio predeterminado (tenant `0e2a992a-…`). Hubo que cerrar sesión en Azure DevOps.
- **Incidente:** al probar el acceso, Claude ejecutó `az account clear`, que cerró la sesión de Azure CLI. No afectó los recursos; se volvió a iniciar sesión con código de dispositivo.
- **Problema 4:** después de conectar el directorio, Azure DevOps sacaba al usuario apenas iniciaba sesión, incluso en incógnito. **Causa:** el perfil seguía en "Microsoft account" y la organización ya estaba en Directorio predeterminado. **Solución:** en https://aex.dev.azure.com/me cambiar el selector a Directorio predeterminado y entrar al proyecto desde esa lista.
- **Resultado final:** acceso correcto a https://dev.azure.com/frankvargaschavez201/dataops-dmc.
- **Verificación desde la terminal:** con la sesión de Azure CLI renovada, la API de Azure DevOps responde HTTP 200, lista el proyecto `dataops-dmc` (privado) y su repositorio Git `dataops-dmc`, que todavía está vacío. Esto confirma que Azure y Azure DevOps comparten directorio.
- **Evidencias:** capturas 03 a 17.

### 13. Carpeta de evidencias
- **Qué:** las capturas se guardan en [docs/evidencias/](docs/evidencias/) con número y nombre descriptivo, y se listan en su [README](docs/evidencias/README.md) con fecha, descripción y paso de la bitácora.
- **Por qué:** el informe y las evidencias valen 6 de 20 puntos; así quedan ordenadas para armar el informe final.

### 14. Repositorio Git y primer push a Azure Repos
- **Qué:** se inicializó Git en la carpeta del proyecto (rama `main`) y se subió a https://dev.azure.com/frankvargaschavez201/dataops-dmc/_git/dataops-dmc.
- **Estructura:** `adf/` (recursos de Data Factory), `pipelines/` (YAML de CI/CD), `scripts/`, `tests/`, `data/sample/` (CSV de ejemplo), `docs/evidencias/`, más `README.md`, `BITACORA.md` y `HALLAZGOS.md`.
- **Seguridad:**
  - `.gitignore` excluye `CLASE/`, `PROYECTO/` (zip con la contraseña, PDF y CSV original), `*.zip`, `*.sql`, `.env` y salidas locales.
  - Antes del commit se buscó la contraseña de la base en todos los archivos a subir: no aparece en ninguno.
  - El push se autenticó con un token temporal de la sesión de Azure CLI (`http.extraHeader`), sin guardar credenciales en el equipo ni en el repositorio.
- **README:** describe el proyecto, la arquitectura, los recursos por entorno, la estructura y los pasos de despliegue (entregable del enunciado).
- **Commit:** `e5893ff Estructura inicial del repositorio DataOps` (29 archivos).
- **Evidencia:** captura 18 (Repos → Files con la estructura y el README).

### 15. Conexión de Data Factory DEV a Azure Repos
- **Qué:** se configuró la integración Git de `az-fv-dev-de-dfc-etl` con la API de Azure (`configureFactoryRepo`):
  | Parámetro | Valor |
  |---|---|
  | Tipo | Azure DevOps Git |
  | Organización / proyecto / repositorio | `frankvargaschavez201` / `dataops-dmc` / `dataops-dmc` |
  | Rama de colaboración | `main` |
  | Carpeta raíz | `/adf` |
  | Publicación | habilitada (al publicar, ADF genera las plantillas ARM en la rama `adf_publish`) |
- **Por qué:** todo lo que se construya en ADF Studio (linked services, datasets, data flows, pipelines) se guarda como JSON en `adf/` y queda versionado. Solo DEV se conecta a Git; QAS y PRD reciben los cambios por CI/CD.
- **Verificación:** la consulta al recurso devuelve la configuración Git esperada.
- **Costo:** 0 USD.

### 16. Perfil de los datos de PostgreSQL
- **Qué:** consulta de solo lectura a `rrhh.empleado` con un cliente `psql` temporal en Docker (`postgres:16-alpine`), sin guardar la contraseña.
- **Resultado:**
  - 48 empleados, IDs del 1 al 50 (no existen el 4 ni el 49). Ningún salario nulo.
  - Tipos: `empleado_id integer`, `mnt_salario numeric(10,2)` y `mnt_tope_comision numeric(10,2)`.
  - `mnt_tope_comision`: 18 empleados con tope (300 a 580) y 30 sin tope (nulo).
  - El servidor **no tiene SSL** (`SHOW ssl = off`), por lo que la conexión de ADF va con `sslMode = 0` (sin cifrar). Es una limitación del servidor del curso; se documenta como observación de seguridad.
- **Cruce con el CSV:**
  - 15 empleados sin comisión en el CSV: 6, 7, 8, 38–48 y 50.
  - El CSV trae comisión para el ID 4, que no existe en la tabla: se descarta (left join desde empleados).
  - Las comisiones del CSV (8,250–12,750) superan con creces los topes (300–580).

### 17. Reglas de negocio decididas
- **Empleados sin comisión:** se incluyen con comisión 0 (left join).
- **Tope de comisión:** se aplica `comision_aplicada = min(comision, mnt_tope_comision)` cuando el tope no es nulo; si es nulo, no hay tope.
- **Parámetro `aplicar_tope`** (`si`/`no`, por defecto `si`): permite ejecutar sin tope, porque con tope los 13 empleados afectados bajan de ~10,000 a ~300 de comisión.
- **Fórmula:** `salario_total = mnt_salario + comision_aplicada`.

### 18. Pipeline de Data Factory (código en `adf/`)
- **Qué:** se escribieron los recursos de ADF como JSON en la rama `feature/pipeline-salario-total`:
  | Tipo | Nombre | Función |
  |---|---|---|
  | Linked service | `ls_kv_etl` | Key Vault del entorno |
  | Linked service | `ls_adls_lake` | Data Lake, con identidad administrada |
  | Linked service | `ls_pgsql_empleado` | PostgreSQL (conector PostgreSqlV2), contraseña desde Key Vault |
  | Dataset | `ds_pg_empleado` | Tabla `rrhh.empleado` |
  | Dataset | `ds_adls_empleado_parquet` | `raw/empleados/empleado.parquet` |
  | Dataset | `ds_adls_comision_csv` | `raw/comisiones/<archivo>` (`;`, UTF-8, con encabezado) |
  | Dataset | `ds_adls_salario_parquet` | `curated/salario_total/periodo=<AAAAMM>/` |
  | Data flow | `df_salario_total` | Renombra columnas del CSV → left join → comisión y tope → `salario_total` → Parquet |
  | Pipeline | `pl_salario_total` | Copy (PostgreSQL → raw) y luego Data Flow; parámetros `periodo` y `aplicar_tope` |
- **Por qué dos etapas:** el Data Flow de ADF no lee directamente de un PostgreSQL externo; por eso primero se copia la tabla al Data Lake (Copy activity, centavos) y el Data Flow une dos archivos del lago.
- **Columnas de salida:** `empleado_id`, `nom_empleado`, `ape_empleado`, `cod_cargo`, `cod_departamento`, `mnt_salario`, `tiene_comision`, `comision_original`, `mnt_tope_comision`, `tope_aplicado`, `comision_aplicada`, `salario_total`, `periodo`, `fecha_proceso`.
- **Verificación:** los 9 archivos JSON son válidos.
- **Resultado esperado:** [tests/esperado_salario_total_202610.csv](tests/esperado_salario_total_202610.csv), calculado con Python directamente desde la base y el CSV: 48 filas, 15 sin comisión, 13 con tope aplicado, suma de `salario_total` = **352,183.40**. Servirá para comparar con la salida del pipeline.

---

## Pendiente
- [ ] Reiniciar VS Code para que el plugin de Azure encuentre `az`.
- [x] Decidir: ruta ADF o Python, y repositorio en GitHub o Azure Repos → ADF + Azure DevOps.
- [x] Decidir si se aplica el tope de comisión → sí, con parámetro `aplicar_tope`; empleados sin comisión → 0.
- [x] Crear la organización de Azure DevOps → `frankvargaschavez201`, proyecto `dataops-dmc`, conectada a Directorio predeterminado.
- [ ] Pedir el agente gratuito de pipelines (https://aka.ms/azpipelines-parallelism-request).
- [x] Crear una alerta de presupuesto → 5 USD/mes.
- [x] Crear el entorno DEV.
- [ ] Crear los entornos QAS y PRD.
- [x] Inicializar el repositorio Git y subirlo a Azure Repos.
- [x] Conectar ADF DEV a Azure Repos (rama `main`, carpeta `/adf`).
- [x] Escribir el pipeline de ADF (Copy + Data Flow) en `adf/`.
- [ ] Revisar y completar el pull request hacia `main`.
- [ ] Validar y ejecutar el pipeline en ADF Studio (debug) y comparar con el resultado esperado.
- [ ] Confirmar la fecha de entrega con el docente.
