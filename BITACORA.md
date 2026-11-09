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
- **Git:** commit `229c9fa` en la rama `feature/pipeline-salario-total` y **pull request #1** hacia `main` (https://dev.azure.com/frankvargaschavez201/dataops-dmc/_git/dataops-dmc/pullrequest/1). Antes del commit se verificó que la contraseña no aparezca en el diff.
- **Merge:** PR #1 aprobado y completado (merge sin fast-forward, commit `1f25d85`); la rama feature se borró. Evidencias 19–22.

### 19. Pruebas en ADF Studio (sin costo)
- **Carga desde Git:** ADF Studio, en la rama `main`, muestra el pipeline, los 4 datasets y el data flow escritos como JSON (evidencia 27).
- **Validar todo:** "Se validó su fábrica. No se ha encontrado ningún error" (evidencia 28).
- **Prueba de conexión de los servicios vinculados:**
  | Servicio vinculado | Autenticación | Resultado |
  |---|---|---|
  | `ls_adls_lake` | Identidad administrada de ADF | ✅ Conexión correcta |
  | `ls_kv_etl` | Identidad administrada de ADF | ✅ Conexión correcta |
  | `ls_pgsql_empleado` | Usuario + contraseña leída de Key Vault | ✅ Conexión correcta |
- **Conclusión:** los permisos RBAC del script de aprovisionamiento funcionan, y ADF llega al PostgreSQL del curso desde Azure. Evidencias 29–33.

### 20. Primera ejecución de prueba (debug): falla del Data Flow
- **Cómo se ejecutó:** Depurar → "Usar el entorno de ejecución de la actividad". Así el clúster se enciende solo durante la ejecución; se descartó la "sesión de depuración del flujo de datos", que deja un clúster 1 hora encendido (evidencias 36–38).
- **Resultado:**
  - ✅ La copia `cp_pg_empleado_a_raw` funcionó: `raw/empleados/empleado.parquet` con 48 filas.
  - ❌ El Data Flow falló con `DF-FN-0030 - least should have all inputs of type DecimalType(...)`. Los demás errores (`DF-EXPR-010 Column 'tope_aplicado' ... unavailable`) eran consecuencia del primero.
- **Causa:** la copia escribe los montos de PostgreSQL como `decimal(38,18)` (se comprobó leyendo el Parquet con `pyarrow`), pero el Data Flow los declaraba como `decimal(10,2)` y la comisión del CSV se convertía con otro tipo. La función `least()` exige tipos decimales idénticos.
- **Corrección** (rama `fix/df-tipos-decimales`):
  - El origen `srcEmpleado` declara `mnt_salario` y `mnt_tope_comision` como `decimal(38,18)`, como vienen en el archivo.
  - En `calcComision` se convierten explícitamente a `decimal(10,2)`: `salario_base`, `tope_comision` y `comision_original`.
  - `least()` se reemplazó por `iif(comision_original > tope_comision, tope_comision, comision_original)`, con los dos lados del mismo tipo.
- **Costo de la ejecución fallida:** unos 0.10–0.20 USD (el clúster arrancó y falló al analizar el flujo).
- **Lección:** revisar el esquema real de los archivos intermedios antes de declarar tipos en el Data Flow.
- **Git:** PR #2 completado (merge `c620c5f`).

### 21. Segunda ejecución de prueba: éxito y pruebas de calidad
- **Ejecución:** run `e92bdfaa-3a82-4a3d-873d-1a646af046cf`, con el runtime de actividad.
  | Actividad | Estado | Duración |
  |---|---|---|
  | `cp_pg_empleado_a_raw` (Copy) | ✅ Correcto | 17 s |
  | `df_calcular_salario_total` (Data Flow) | ✅ Correcto | 3 min 41 s |
- **Salida:** `curated/salario_total/periodo=202610/part-00000-…snappy.parquet` (un solo archivo).
- **Pruebas de calidad** (`tests/validar_salida.py`, ejecutado en Docker con pandas y pyarrow, comparando con `tests/esperado_salario_total_202610.csv`): **11/11 OK**.
  | Prueba | Resultado |
  |---|---|
  | Esquema con las 14 columnas | ✅ |
  | 48 filas | ✅ |
  | `empleado_id` sin duplicados | ✅ |
  | `salario_total` sin nulos y > 0 | ✅ |
  | Todos los empleados de la base presentes | ✅ |
  | Valores por empleado iguales al esperado | ✅ |
  | 15 empleados sin comisión con comisión 0 | ✅ |
  | `comision_aplicada` ≤ tope (13 empleados topados) | ✅ |
  | `salario_total = mnt_salario + comision_aplicada` | ✅ |
  | Suma de `salario_total` = 352,183.40 | ✅ |
- **Costo de la ejecución:** ~0.15–0.25 USD.
- **Evidencias:** 39 (captura de la ejecución exitosa) y 40 (resultado de las pruebas).

### 22. Agente gratuito de Azure Pipelines
- **Qué:** el formulario https://aka.ms/azpipelines-parallelism-request fue retirado. Microsoft ahora otorga el paralelismo gratuito automáticamente al vincular la organización a una suscripción para facturación (evidencia 41).
- **Verificación por API** (`distributedtask/resourceusage`): la organización tiene **1 trabajo paralelo hospedado por Microsoft** con **1,800 minutos al mes** para proyectos privados.
- **Conclusión:** no hace falta un agente propio; los pipelines de CI/CD pueden correr ya.

### 23. Entornos QAS y PRD
- **Qué:** se ejecutó `scripts/provisionar_azure.sh qas` y `... prd`.
- **Recursos:** `az-fv-qas-de-rg-dataops` y `az-fv-prd-de-rg-dataops`, cada uno con Data Lake (`azfvqasdedlslake` / `azfvprddedlslake`) con el CSV en `raw/comisiones/`, Key Vault con los 5 secretos y Data Factory vacío con identidad administrada y sus roles.
- **Verificación:** 5 secretos, CSV presente y los mismos 4 roles que en DEV, en ambos entornos.
- **Por qué vacíos:** QAS y PRD no se conectan a Git; su contenido llega solo por el CD.

### 24. Diseño y prueba local del CI/CD
- **Herramienta:** `@microsoft/azure-data-factory-utilities` (definida en [build/package.json](build/package.json)), que valida los recursos de ADF y exporta las plantillas ARM sin pulsar "Publicar" (publicación automatizada recomendada por Microsoft).
- **Prueba local** en Docker (`node:20-slim`): "Validation finished. No errors found" y exportación correcta. Parámetros ARM generados: `factoryName`, URL del Data Lake, URL del Key Vault, y servidor, base y usuario de PostgreSQL. En QAS y PRD solo cambian los tres primeros.
- **Pipeline YAML** ([pipelines/azure-pipelines.yml](pipelines/azure-pipelines.yml) y [pipelines/templates/deploy-adf.yml](pipelines/templates/deploy-adf.yml)):
  - **CI:** pytest con [tests/test_adf_estatico.py](tests/test_adf_estatico.py) (resultados publicados en la pestaña Tests), validación de ADF y exportación del artefacto `ArmTemplate`.
  - **CD_QAS / CD_PRD** (solo desde `main`): pre-despliegue, despliegue ARM con parámetros del entorno, post-despliegue, ejecución real de `pl_salario_total` con [scripts/ejecutar_pipeline_adf.sh](scripts/ejecutar_pipeline_adf.sh), descarga del Parquet y `tests/validar_salida.py`.
- **Pruebas estáticas:** 22 pruebas (estructura y nombres, referencias entre recursos, contraseña desde Key Vault, sin claves en texto plano, Data Lake con identidad administrada, left join, comisión 0, tope parametrizado, fórmula, salida Parquet por periodo, CSV `;` UTF-8, orden Copy → Data Flow, coherencia del resultado esperado). Localmente: **22 passed**.
- **Environments en Azure DevOps** (creados por API): `ADF-QAS` y `ADF-PRD`. `ADF-PRD` tiene un **check de aprobación** (aprobador: Frank Vargas Chavez, plazo 72 h) con la instrucción de revisar QAS antes de aprobar.
- **Costo por ejecución completa del CI/CD:** ~0.50 USD (una ejecución del Data Flow en QAS y otra en PRD). El CI no tiene costo de Azure.
- **Git:** commit `852fae4` en `feature/cicd-azure-pipelines` y **PR #3** hacia `main`. La sesión de Claude se cortó durante el push; al retomarla se verificó que el commit, el push y el PR se habían completado.

### 25. Service connection `CONEXION_AZURE`
- **Qué:** conexión de Azure Pipelines hacia la suscripción, creada en *Project settings → Service connections*: Azure Resource Manager, *App registration (automatic)*, credencial **workload identity federation** (OpenID Connect, sin contraseñas ni secretos que rotar), acceso para todos los pipelines.
- **Problema:** el formulario proponía por defecto el grupo `VisualStudioOnline-C5CE…` (interno de Azure DevOps, creado al vincular la facturación); con él la conexión no podría desplegar en QAS ni en PRD. **Solución:** se eligió "All resource groups".
- **Mínimo privilegio:** "All resource groups" le daba *Contributor* sobre toda la suscripción (incluido DEV). Con Azure CLI se le asignó *Contributor* solo sobre `az-fv-qas-de-rg-dataops` y `az-fv-prd-de-rg-dataops` y se eliminó el rol a nivel de suscripción. Resultado verificado: únicamente esos dos roles.
- **Evidencias:** 42–44.

### 26. Primera ejecución del CI/CD (run #1, `20261109.1`): falla en post-despliegue
- **Registro:** PR #3 completado (merge `6f866da`); pipeline `dataops-adf-cicd` creado por API desde `pipelines/azure-pipelines.yml`; se autorizó su uso de los environments `ADF-QAS` y `ADF-PRD`.
- **Resultado:**
  - ✅ **CI:** pytest (22 pruebas), validación de ADF, exportación ARM y artefacto.
  - ✅ CD_QAS: pre-despliegue y **despliegue de la plantilla ARM en `az-fv-qas-de-dfc-etl`**.
  - ❌ CD_QAS: post-despliegue → `Cannot index into a null array` (línea 718 de `PrePostDeploymentScript.ps1`). CD_PRD se omitió.
- **Causa:** con `-deleteDeployment $true`, el script de Microsoft busca el despliegue ARM cuyo nombre empiece con `ArmTemplate_master` o `ArmTemplateForFactory` para borrarlo del historial; el despliegue se había llamado `adf-<BuildNumber>`, así que no encontró ninguno.
- **Corrección** (rama `fix/nombre-deployment-arm`): `deploymentName: ArmTemplateForFactory-$(Build.BuildId)`.
- **Costo:** 0 USD (no llegó a ejecutarse el Data Flow).

### 27. Segunda ejecución del CI/CD (run #2, `20261109.2`): pipeline OK en QAS, falla en la descarga
- **Disparo:** automático (`individualCI`) al completar el PR #4 en `main`.
- **Resultado:**
  - ✅ CI.
  - ✅ CD_QAS: pre-despliegue, despliegue ARM (`ArmTemplateForFactory-2`) y **post-despliegue** (la corrección funcionó).
  - ✅ CD_QAS: **ejecución real de `pl_salario_total` en `az-fv-qas-de-dfc-etl`** (run `01f48129-…`): `cp_pg_empleado_a_raw` Succeeded (17 s) y `df_calcular_salario_total` Succeeded (3 min 29 s). La autenticación fue con la identidad federada de la service connection.
  - ❌ Descarga del Parquet: `ERROR: incorrect usage: destination must be an existing directory`. Las pruebas de calidad y PRD no se ejecutaron.
- **Causa:** `az storage blob download-batch` exige que la carpeta destino exista; en la prueba local se había creado antes, en el pipeline no.
- **Corrección** (rama `fix/carpeta-descarga-salida`): `mkdir -p $(Agent.TempDirectory)/salida` antes de la descarga.
- **Costo:** ~0.20 USD (una ejecución del Data Flow en QAS).
- **Evidencias:** 45–46.

---

## Pendiente
- [ ] Reiniciar VS Code para que el plugin de Azure encuentre `az`.
- [x] Decidir: ruta ADF o Python, y repositorio en GitHub o Azure Repos → ADF + Azure DevOps.
- [x] Decidir si se aplica el tope de comisión → sí, con parámetro `aplicar_tope`; empleados sin comisión → 0.
- [x] Crear la organización de Azure DevOps → `frankvargaschavez201`, proyecto `dataops-dmc`, conectada a Directorio predeterminado.
- [x] Agente gratuito de pipelines → otorgado automáticamente (1 trabajo paralelo, 1,800 min/mes).
- [x] Crear una alerta de presupuesto → 5 USD/mes.
- [x] Crear el entorno DEV.
- [x] Crear los entornos QAS y PRD.
- [x] Inicializar el repositorio Git y subirlo a Azure Repos.
- [x] Conectar ADF DEV a Azure Repos (rama `main`, carpeta `/adf`).
- [x] Escribir el pipeline de ADF (Copy + Data Flow) en `adf/`.
- [x] Revisar y completar el pull request hacia `main` (PR #1).
- [x] Validar y ejecutar el pipeline en ADF Studio (debug) y comparar con el resultado esperado → 11/11 pruebas OK.
- [x] Guardar la captura 39 (ejecución exitosa).
- [x] Escribir el pipeline de CI/CD (YAML), pruebas estáticas y environments con aprobación.
- [x] Crear la service connection `CONEXION_AZURE` (limitada a los grupos de QAS y PRD).
- [ ] Completar el PR #3 y registrar el pipeline en Azure Pipelines.
- [ ] Ejecutar el CI/CD completo (CI → QAS → aprobación → PRD) y capturar evidencias.
- [ ] Confirmar la fecha de entrega con el docente.
