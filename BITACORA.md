# Bitácora del proyecto

Registro de las etapas del proyecto, en orden cronológico (08/11/2026). Para cada etapa se indica qué se hizo, por qué, los problemas encontrados y cómo se resolvieron. Los números de evidencia corresponden a [docs/evidencias](docs/evidencias/README.md).

## 1. Análisis y preparación

**1. Revisión del enunciado y de los datos.** El objetivo es unir la tabla PostgreSQL `rrhh.empleado` con el CSV de comisiones por `empleado_id`, calcular `salario_total` y guardar un Parquet en el Data Lake, con despliegue automatizado de desarrollo a producción. El enunciado tiene inconsistencias menores: el nombre del CSV cambia entre versiones (`_202510`, `_202608`) y el archivo entregado es `ComisionEmpleados_V1_202610.csv`, por lo que el periodo se trató como parámetro. El CSV usa `;` como separador, está en UTF-8, tiene 34 filas y el nombre del empleado lleva una coma interna ("Juan, Pérez"). El archivo de conexión a la base trae la contraseña en texto plano, así que se decidió no versionarlo y guardar la contraseña en Key Vault.

**2. Suscripción de Azure.** La cuenta estaba creada pero sin suscripción, lo que impide crear recursos (evidencia 01). Se creó una suscripción de pago por uso, `FRANK PRIV - DEP OPS`, con rol Owner (evidencia 02). Costo estimado del proyecto: unos 2 USD, porque solo el clúster del Data Flow cobra de forma relevante y solo mientras está encendido.

**3. Azure CLI e inicio de sesión.** `winget` no estaba disponible en el equipo, por lo que Azure CLI se instaló con el MSI oficial. El primer `az login` falló porque el directorio exige autenticación multifactor, y luego Microsoft bloqueó temporalmente el envío de códigos por correo por exceso de intentos. Se resolvió con el inicio de sesión por código de dispositivo:
```
az login --tenant 0e2a992a-2881-4290-a6f1-c34c509bd83f --use-device-code
```

**4. Proveedores de recursos.** Se registraron `Microsoft.DataFactory`, `Microsoft.Storage` y `Microsoft.KeyVault` en la suscripción, requisito previo para crear esos servicios. No tiene costo.

**5. Decisiones de arquitectura.**

| Decisión | Elección | Motivo |
|---|---|---|
| Herramienta de datos | Azure Data Factory | Es la que pide el enunciado y genera plantillas ARM, que se exigen versionar |
| Repositorio y CI/CD | Azure Repos + Azure Pipelines | Repositorio, pipelines, environments y aprobaciones en una sola plataforma |
| Entornos | DEV, QAS y PRD | El enunciado pide desarrollo, prueba y producción |
| Región | `eastus` | La misma del material del curso |
| Nombres | `az-fv-<entorno>-de-<tipo>-<nombre>` | Convención del curso, con las iniciales FV |

**6. Presupuesto.** Se creó el presupuesto mensual `presupuesto-dataops` de 5 USD, con avisos por correo al 50 % y al 100 % del gasto real y al 100 % del gasto pronosticado. Sirve para detectar a tiempo un recurso olvidado encendido.

## 2. Infraestructura

**7. Script de aprovisionamiento.** [scripts/provisionar_azure.sh](scripts/provisionar_azure.sh) crea un entorno completo con un solo comando y permite reproducir exactamente lo mismo en QAS y PRD:

- grupo de recursos con etiquetas `proyecto` y `entorno`;
- Data Lake ADLS Gen2 con TLS 1.2, sin acceso público y con los contenedores `raw` y `curated`; sube el CSV a `raw/comisiones/`;
- Key Vault con autorización RBAC y los secretos `pg-host`, `pg-port`, `pg-db`, `pg-user` y `pg-password`;
- Data Factory con identidad administrada, que recibe los roles *Key Vault Secrets User* sobre el Key Vault y *Storage Blob Data Contributor* sobre el Data Lake.

La contraseña no está en el script: se pasa con la variable de entorno `PG_PASSWORD`.

**8. Entorno DEV.** Se verificó que los nombres del Data Lake y del Key Vault estuvieran libres (son únicos en todo Azure) y se ejecutó el script. Comprobaciones: los tres recursos creados, los cinco secretos presentes, el CSV en `raw/comisiones/` (917 bytes) y los cuatro roles asignados.

## 3. Azure DevOps y repositorio

**9. Organización y proyecto.** Se creó la organización `frankvargaschavez201` con el proyecto privado `dataops-dmc` (evidencias 03 a 12). Hubo cuatro problemas, todos por el directorio de Microsoft Entra:

| Problema | Causa | Solución |
|---|---|---|
| El formulario no encontraba ninguna suscripción (06) | La cuenta de Gmail abre por defecto el directorio "Microsoft account", que no tiene suscripciones | *Switch directory* → Directorio predeterminado |
| La suscripción aparecía, pero "You need to be an owner or contributor" (07) | Retraso de Azure DevOps con una suscripción recién creada; Azure CLI confirmó el rol Owner | Reintentar unos minutos después |
| La organización quedó en "Microsoft account" y la API rechazaba la sesión de Azure | Directorio distinto al de la suscripción | *Organization settings → Microsoft Entra → Connect directory* (13, 14) |
| Tras conectar, Azure DevOps cerraba la sesión al entrar | El perfil seguía en "Microsoft account" | Elegir Directorio predeterminado en `aex.dev.azure.com/me` (15, 16) |

Con el mismo directorio, la API de Azure DevOps acepta la sesión de Azure CLI y la service connection se puede crear sin credenciales manuales (evidencia 17).

**10. Repositorio Git.** Se inicializó el repositorio con la rama `main` y la estructura `adf/`, `pipelines/`, `scripts/`, `tests/`, `data/sample/` y `docs/`. El `.gitignore` excluye el material del curso, los archivos originales del enunciado (incluido el zip con la conexión), los `.zip`, `.sql` y `.env`. Antes del primer commit se buscó la contraseña en todos los archivos a subir y no apareció en ninguno. Desde entonces, cada cambio entró a `main` por pull request (seis en total).

**11. Conexión de Data Factory DEV con Git.** Se configuró la integración de `az-fv-dev-de-dfc-etl` con Azure DevOps Git: repositorio `dataops-dmc`, rama de colaboración `main` y carpeta raíz `/adf`. Lo que se construye en ADF queda versionado como JSON. QAS y PRD no se conectan a Git: reciben los cambios solo por CI/CD.

## 4. Pipeline de Data Factory

**12. Perfil de los datos.** Se consultó `rrhh.empleado` con un cliente `psql` temporal en Docker y el usuario de solo lectura del curso.

- 48 empleados, IDs del 1 al 50 (no existen el 4 ni el 49), sin salarios nulos.
- `mnt_salario` y `mnt_tope_comision` son `numeric(10,2)`; 18 empleados tienen tope (300 a 580) y 30 no.
- 15 empleados no figuran en el CSV: 6, 7, 8, 38 a 48 y 50.
- El CSV trae una comisión para el ID 4, que no existe en la tabla.
- El servidor no tiene SSL activo (`SHOW ssl = off`).

**13. Reglas de negocio.**

- Left join desde empleados: se incluyen todos, con comisión 0 si no figuran en el CSV. La comisión del ID 4 se descarta.
- Tope: `comision_aplicada = min(comision, mnt_tope_comision)` cuando el empleado tiene tope.
- El tope se controla con el parámetro `aplicar_tope` (`si`/`no`), porque reduce las comisiones de 13 empleados de unos 10,000 a menos de 600.
- `salario_total = mnt_salario + comision_aplicada`.

**14. Desarrollo del pipeline.** Los recursos de ADF se escribieron como JSON en una rama de feature y entraron a `main` con el PR #1 (evidencias 19 a 21):

| Tipo | Nombre | Función |
|---|---|---|
| Linked service | `ls_kv_etl` | Key Vault del entorno |
| Linked service | `ls_adls_lake` | Data Lake, con identidad administrada |
| Linked service | `ls_pgsql_empleado` | PostgreSQL; la contraseña se lee de Key Vault |
| Dataset | `ds_pg_empleado` | Tabla `rrhh.empleado` |
| Dataset | `ds_adls_empleado_parquet` | `raw/empleados/empleado.parquet` |
| Dataset | `ds_adls_comision_csv` | CSV del periodo en `raw/comisiones/` |
| Dataset | `ds_adls_salario_parquet` | `curated/salario_total/periodo=<AAAAMM>/` |
| Data flow | `df_salario_total` | Join, reglas de comisión y salida Parquet |
| Pipeline | `pl_salario_total` | Copy y luego Data Flow, con los parámetros `periodo` y `aplicar_tope` |

Se usan dos actividades porque el Data Flow no lee directamente de un PostgreSQL externo. La salida tiene 14 columnas: datos del empleado, salario, comisión original, tope, indicadores `tiene_comision` y `tope_aplicado`, comisión aplicada, `salario_total`, periodo y fecha de proceso.

En paralelo se calculó el resultado esperado con Python, directamente desde la base y el CSV: [tests/esperado_salario_total_202610.csv](tests/esperado_salario_total_202610.csv), con 48 filas y una suma de 352,183.40.

**15. Validación en ADF Studio.** Sin costo (evidencias 22 a 34):

- ADF Studio cargó desde Git el pipeline, los cuatro datasets y el data flow (26).
- *Validar todo* terminó sin errores (27).
- La prueba de conexión fue correcta en los tres linked services: Data Lake y Key Vault con identidad administrada, y PostgreSQL con la contraseña de Key Vault (30 a 32).

**16. Primera ejecución de prueba.** Se ejecutó con *Depurar → Usar el entorno de ejecución de la actividad*, que enciende el clúster solo durante la ejecución. Se descartó la sesión de depuración del data flow, que lo mantiene encendido una hora (evidencias 35 a 37). La copia funcionó, pero el Data Flow falló con `DF-FN-0030 - least should have all inputs of type DecimalType`.

- Causa: la copia escribe los montos como `decimal(38,18)`, como se comprobó leyendo el Parquet con pyarrow, mientras que el data flow los declaraba como `decimal(10,2)`. `least()` exige tipos idénticos.
- Solución (PR #2): declarar el origen como `decimal(38,18)`, convertir salario, tope y comisión a `decimal(10,2)` antes de compararlos y reemplazar `least()` por `iif()`.

**17. Segunda ejecución de prueba.** Correcta: copia en 17 s y Data Flow en 3 min 41 s (evidencia 38). Sobre el Parquet de salida se ejecutó [tests/validar_salida.py](tests/validar_salida.py), y las 11 pruebas pasaron (evidencia 39). Resultado: 48 filas, 15 empleados sin comisión, 13 con tope aplicado y una suma de 352,183.40, idéntica al cálculo independiente.

## 5. CI/CD

**18. Agente de Azure Pipelines.** El formulario para solicitar el paralelismo gratuito fue retirado (evidencia 40). Ahora Microsoft lo otorga al vincular la organización a una suscripción. La API confirmó un trabajo paralelo hospedado con 1,800 minutos mensuales.

**19. Entornos QAS y PRD.** Se crearon con el mismo script de aprovisionamiento. Se verificaron en ambos el CSV, los cinco secretos y los cuatro roles. Los Data Factory quedan vacíos hasta el primer despliegue.

**20. Diseño del CI/CD.** Las plantillas ARM se generan con `@microsoft/azure-data-factory-utilities` ([build/package.json](build/package.json)) en lugar del botón *Publicar*, que es la publicación automatizada que recomienda Microsoft. Antes de subirlo se probó localmente en Docker: la validación terminó sin errores y la exportación generó la plantilla y su archivo de parámetros.

- [pipelines/azure-pipelines.yml](pipelines/azure-pipelines.yml), etapa CI: pytest con [tests/test_adf_estatico.py](tests/test_adf_estatico.py) (22 pruebas, publicadas en la pestaña Tests), validación de ADF y exportación del artefacto `ArmTemplate`.
- [pipelines/templates/deploy-adf.yml](pipelines/templates/deploy-adf.yml), etapas CD_QAS y CD_PRD (solo desde `main`): script previo, despliegue ARM con los parámetros del entorno, script posterior, ejecución de `pl_salario_total` con [scripts/ejecutar_pipeline_adf.sh](scripts/ejecutar_pipeline_adf.sh), descarga del Parquet y pruebas de calidad.
- Los environments `ADF-QAS` y `ADF-PRD` se crearon por API. `ADF-PRD` tiene un check de aprobación con plazo de 72 horas.

**21. Service connection.** Se creó `CONEXION_AZURE`: Azure Resource Manager con registro de aplicación automático y workload identity federation, sin contraseñas ni secretos que rotar (evidencias 41 a 43). El formulario proponía por defecto un grupo de recursos interno de Azure DevOps, que habría impedido desplegar en QAS y PRD; se eligió "All resource groups". Como eso le daba el rol Contributor sobre toda la suscripción, se aplicó mínimo privilegio: Contributor solo sobre los grupos de QAS y PRD, y se quitó el rol a nivel de suscripción.

**22. Ejecución #1 del CI/CD.** Tras el PR #3 se registró el pipeline `dataops-adf-cicd` y se autorizó su uso de los environments. El CI y el despliegue ARM en QAS fueron correctos, pero el script posterior falló con `Cannot index into a null array`.

- Causa: con `-deleteDeployment`, el script de Microsoft busca el despliegue cuyo nombre empieza con `ArmTemplateForFactory`, y el despliegue se llamaba `adf-<número>`.
- Solución (PR #4): `deploymentName: ArmTemplateForFactory-$(Build.BuildId)`.

**23. Ejecución #2 del CI/CD.** Se disparó automáticamente con el merge del PR #4. El despliegue, el script posterior y la ejecución real de `pl_salario_total` en QAS fueron correctos, con un Data Flow de 3 min 29 s (evidencias 44 y 45). Falló la descarga del Parquet: `destination must be an existing directory`.

- Causa: `az storage blob download-batch` exige que la carpeta destino exista.
- Solución (PR #5): crearla con `mkdir -p` antes de la descarga.

**24. Revisión previa a la ejecución #3.** Para no seguir corrigiendo por prueba y error, se verificaron los pasos pendientes uno por uno:

| Verificación | Método | Resultado |
|---|---|---|
| Descarga y pruebas de calidad | Mismos comandos del YAML, en una carpeta nueva, sobre el Parquet real de QAS, con las mismas versiones de pandas y pyarrow que instala el agente | 11/11 |
| Parámetros por entorno | Lectura de los linked services desplegados en QAS | Apuntan al Data Lake y al Key Vault de QAS |
| Requisitos de PRD | CSV, secretos, roles de Data Factory y de la service connection | Iguales a QAS |
| Environment `ADF-PRD` | API de permisos y checks | Pipeline autorizado y aprobación configurada |
| YAML corregido | API de vista previa de Azure Pipelines | Se expande sin errores |

**25. Ejecución #3 del CI/CD.** Correcta de principio a fin, disparada por el merge del PR #5, con una duración total de 15 min 32 s (evidencias 46 a 49).

| Etapa | Resultado | Duración | Detalle |
|---|---|---|---|
| CI | Correcto | 30 s | 22/22 pruebas, validación sin errores, artefacto ARM |
| CD QAS | Correcto | 6 min 04 s | Copia 21 s, Data Flow 3 min 35 s, pruebas de calidad 11/11 |
| Aprobación ADF-PRD | Aprobada | 1 min 31 s | Aprobador: Frank Vargas Chavez |
| CD PRD | Correcto | 7 min 08 s | Copia 19 s, Data Flow 4 min 33 s, pruebas de calidad 11/11 |

QAS y PRD produjeron el mismo resultado que DEV: 48 filas, 13 topes aplicados y una suma de 352,183.40.

## 6. Registro de pruebas

| # | Prueba | Entorno | Resultado | Corrección |
|---|---|---|---|---|
| 1 | Validación de ADF y conexión de los tres linked services | DEV | Correcto | — |
| 2 | Primera ejecución de `pl_salario_total` | DEV | Falló: tipos decimales en el data flow | PR #2 |
| 3 | Segunda ejecución y 11 pruebas de calidad | DEV | Correcto, 11/11 | — |
| 4 | Ejecución #1 del CI/CD | CI y QAS | CI correcto; falló el script posterior | PR #4 |
| 5 | Ejecución #2 del CI/CD | CI y QAS | Pipeline correcto en QAS; falló la descarga | PR #5 |
| 6 | Revisión de pasos pendientes y requisitos de PRD | QAS y PRD | Correcto | — |
| 7 | Ejecución #3 del CI/CD con aprobación | CI, QAS y PRD | Correcto: 22/22 en CI y 11/11 en cada entorno | — |

Costo acumulado del proyecto: alrededor de 1.50 USD, casi todo por las ejecuciones del Data Flow.

## Pendientes

- Al cerrar la evaluación, eliminar los tres grupos de recursos (comando en el [README](README.md)).
