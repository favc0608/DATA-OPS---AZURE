# Evidencias – Proyecto Final DataOps

Capturas para el informe final, en orden cronológico. Cada una enlaza con su paso en [BITACORA.md](../../BITACORA.md).

| # | Archivo | Fecha | Qué muestra | Paso de la bitácora |
|---|---|---|---|---|
| 01 | [01_portal_cuenta_sin_suscripcion.png](01_portal_cuenta_sin_suscripcion.png) | 08/11/2026 | Portal de Azure con la cuenta creada pero sin suscripción | 3. Suscripción de Azure |
| 02 | [02_suscripcion_payg_activa.png](02_suscripcion_payg_activa.png) | 08/11/2026 | Suscripción de pago por uso "FRANK PRIV - DEP OPS" activa, rol Propietario | 3. Suscripción de Azure |
| 03 | [03_busqueda_organizaciones_devops.png](03_busqueda_organizaciones_devops.png) | 08/11/2026 | Búsqueda de "Organizaciones de Azure DevOps" en el portal | 12. Organización de Azure DevOps |
| 04 | [04_registro_azure_devops.png](04_registro_azure_devops.png) | 08/11/2026 | Registro inicial en Azure DevOps | 12. Organización de Azure DevOps |
| 05 | [05_azure_devops_directorio.png](05_azure_devops_directorio.png) | 08/11/2026 | Perfil de Azure DevOps en "Directorio predeterminado", antes de crear la organización | 12. Organización de Azure DevOps |
| 06 | [06_azure_devops_crear_organizacion.png](06_azure_devops_crear_organizacion.png) | 08/11/2026 | Formulario de creación de la organización: no encuentra la suscripción para facturación | 12. Organización de Azure DevOps |
| 07 | [07_azure_devops_error_rol_suscripcion.png](07_azure_devops_error_rol_suscripcion.png) | 08/11/2026 | La suscripción ya aparece, pero Azure DevOps dice que falta rol Owner/Contributor | 12. Organización de Azure DevOps |
| 08 | [08_azure_devops_organizacion_creada.png](08_azure_devops_organizacion_creada.png) | 08/11/2026 | Organización creada; redirigiendo a Azure DevOps | 12. Organización de Azure DevOps |
| 09 | [09_azure_devops_crear_proyecto.png](09_azure_devops_crear_proyecto.png) | 08/11/2026 | Organización `frankvargaschavez201` lista para crear el primer proyecto | 12. Organización de Azure DevOps |
| 10 | [10_azure_devops_proyecto_creado.png](10_azure_devops_proyecto_creado.png) | 08/11/2026 | Proyecto privado `dataops-dmc` creado | 12. Organización de Azure DevOps |
| 11 | [11_azure_devops_project_settings.png](11_azure_devops_project_settings.png) | 08/11/2026 | Configuración del proyecto: proceso Basic, administrador Frank Vargas Chavez | 12. Organización de Azure DevOps |
| 12 | [12_azure_devops_organizacion_proyectos.png](12_azure_devops_organizacion_proyectos.png) | 08/11/2026 | Vista de la organización `frankvargaschavez201` con el proyecto `dataops-dmc` | 12. Organización de Azure DevOps |
| 13 | [13_azure_devops_conectar_entra.png](13_azure_devops_conectar_entra.png) | 08/11/2026 | Conexión de la organización a Microsoft Entra "Directorio predeterminado" (tenant de la suscripción) | 12. Organización de Azure DevOps |
| 14 | [14_azure_devops_entra_conectado.png](14_azure_devops_entra_conectado.png) | 08/11/2026 | "Connect success!": organización conectada a Directorio predeterminado | 12. Organización de Azure DevOps |
| 15 | [15_azure_devops_perfil_microsoft_account.png](15_azure_devops_perfil_microsoft_account.png) | 08/11/2026 | Perfil en "Microsoft account": la organización ya no aparece porque se movió a Directorio predeterminado | 12. Organización de Azure DevOps |
| 16 | [16_azure_devops_org_en_directorio_predeterminado.png](16_azure_devops_org_en_directorio_predeterminado.png) | 08/11/2026 | Con Directorio predeterminado seleccionado aparece la organización (Owner) y el proyecto `dataops-dmc` | 12. Organización de Azure DevOps |
| 17 | [17_azure_devops_proyecto_acceso_ok.png](17_azure_devops_proyecto_acceso_ok.png) | 08/11/2026 | Acceso correcto al proyecto `dataops-dmc` tras conectar el directorio | 12. Organización de Azure DevOps |
| 18 | [18_azure_repos_primer_commit.png](18_azure_repos_primer_commit.png) | 08/11/2026 | Azure Repos → Files: estructura del repositorio, commit `e5893ff` y README | 14. Repositorio Git y primer push |
| 19 | [19_azure_repos_rama_feature_actualizada.png](19_azure_repos_rama_feature_actualizada.png) | 08/11/2026 | Aviso de Azure Repos: rama `feature/pipeline-salario-total` actualizada | 18. Pipeline de Data Factory |
| 20 | [20_pull_request_1_activo.png](20_pull_request_1_activo.png) | 08/11/2026 | Pull request #1 activo, sin conflictos, con descripción del cambio | 18. Pipeline de Data Factory |
| 21 | [21_pull_request_1_completar_merge.png](21_pull_request_1_completar_merge.png) | 08/11/2026 | Completar PR #1: merge sin fast-forward y borrado de la rama feature | 18. Pipeline de Data Factory |
| 22 | [22_pull_request_1_completado.png](22_pull_request_1_completado.png) | 08/11/2026 | PR #1 completado y aprobado: merge `1f25d85` a `main` | 18. Pipeline de Data Factory |
| 23 | [23_portal_buscar_data_factory.png](23_portal_buscar_data_factory.png) | 08/11/2026 | Búsqueda de "Factorías de datos (V2)" en el portal | 19. Pruebas en ADF Studio |
| 24 | [24_adf_dev_informacion_general.png](24_adf_dev_informacion_general.png) | 08/11/2026 | Data Factory `az-fv-dev-de-dfc-etl` en el portal: estado Succeeded, East US, grupo `az-fv-dev-de-rg-dataops` | 19. Pruebas en ADF Studio |
| 25 | [25_adf_studio_cargando.png](25_adf_studio_cargando.png) | 08/11/2026 | ADF Studio cargando | 19. Pruebas en ADF Studio |
| 26 | [26_adf_studio_inicio.png](26_adf_studio_inicio.png) | 08/11/2026 | Página de inicio de ADF Studio para `az-fv-dev-de-dfc-etl` | 19. Pruebas en ADF Studio |
| 27 | [27_adf_author_recursos_desde_git.png](27_adf_author_recursos_desde_git.png) | 08/11/2026 | Author: ADF cargó desde Git el pipeline, los 4 datasets y el data flow | 19. Pruebas en ADF Studio |
| 28 | [28_adf_validar_todo_sin_errores.png](28_adf_validar_todo_sin_errores.png) | 08/11/2026 | "Validar todo": se validó la fábrica, sin errores | 19. Pruebas en ADF Studio |
| 29 | [29_adf_servicios_vinculados_rama_main.png](29_adf_servicios_vinculados_rama_main.png) | 08/11/2026 | Manage → Servicios vinculados (rama main): ADLS, Key Vault y PostgreSQL | 19. Pruebas en ADF Studio |
| 30 | [30_adf_servicios_vinculados_validacion.png](30_adf_servicios_vinculados_validacion.png) | 08/11/2026 | Servicios vinculados junto al resultado de validación sin errores | 19. Pruebas en ADF Studio |
| 31 | [31_adf_test_conexion_adls.png](31_adf_test_conexion_adls.png) | 08/11/2026 | `ls_adls_lake`: identidad administrada, prueba de conexión correcta | 19. Pruebas en ADF Studio |
| 32 | [32_adf_test_conexion_keyvault.png](32_adf_test_conexion_keyvault.png) | 08/11/2026 | `ls_kv_etl`: identidad administrada, prueba de conexión correcta | 19. Pruebas en ADF Studio |
| 33 | [33_adf_test_conexion_postgresql.png](33_adf_test_conexion_postgresql.png) | 08/11/2026 | `ls_pgsql_empleado`: contraseña desde Key Vault, prueba de conexión correcta | 19. Pruebas en ADF Studio |
| 34 | [34_adf_data_flow_df_salario_total.png](34_adf_data_flow_df_salario_total.png) | 08/11/2026 | Diagrama del data flow `df_salario_total` (2 orígenes, join, cálculos, sink) y sus parámetros | 19. Pruebas en ADF Studio |
| 35 | [35_adf_pipeline_pl_salario_total.png](35_adf_pipeline_pl_salario_total.png) | 08/11/2026 | Pipeline `pl_salario_total`: Copy → Data Flow, con parámetros `periodo` y `aplicar_tope` | 19. Pruebas en ADF Studio |
| 36 | [36_adf_dialogo_depuracion_flujo.png](36_adf_dialogo_depuracion_flujo.png) | 08/11/2026 | Diálogo para activar la sesión de depuración del data flow (1 hora); se canceló para usar el runtime de actividad | 20. Ejecución de prueba |
| 37 | [37_adf_depurar_runtime_actividad.png](37_adf_depurar_runtime_actividad.png) | 08/11/2026 | Menú Depurar: opción "Usar el entorno de ejecución de la actividad" (clúster solo durante la ejecución) | 20. Ejecución de prueba |
| 38 | [38_adf_debug_en_curso.png](38_adf_debug_en_curso.png) | 08/11/2026 | Ejecución de depuración en curso (run `387325b4-…`), copia en cola | 20. Ejecución de prueba |
| 39 | [39_adf_debug_exitoso.png](39_adf_debug_exitoso.png) | 08/11/2026 | Segunda ejecución (run `e92bdfaa-…`): copia Correcto (17 s) y Data Flow Correcto (3 min 41 s) | 21. Ejecución exitosa |
| 40 | [40_resultado_pruebas_calidad_202610.txt](40_resultado_pruebas_calidad_202610.txt) | 08/11/2026 | Resultado de `tests/validar_salida.py` sobre el Parquet de salida: 11/11 pruebas OK | 21. Ejecución exitosa |
| 41 | [41_formulario_paralelismo_retirado.png](41_formulario_paralelismo_retirado.png) | 08/11/2026 | El formulario de paralelismo gratuito fue retirado: se otorga automáticamente al vincular la facturación | 22. Agente de Azure Pipelines |
| 42 | [42_service_connection_formulario.png](42_service_connection_formulario.png) | 08/11/2026 | Formulario de la service connection `CONEXION_AZURE` (ARM, workload identity federation, suscripción) | 25. Service connection |
| 43 | [43_service_connection_todos_los_grupos.png](43_service_connection_todos_los_grupos.png) | 08/11/2026 | `CONEXION_AZURE` con alcance "All resource groups" y acceso para todos los pipelines | 25. Service connection |
| 44 | [44_service_connection_creada.png](44_service_connection_creada.png) | 08/11/2026 | `CONEXION_AZURE` creada: Azure Resource Manager con workload identity federation (OpenID Connect) | 25. Service connection |
| 45 | [45_cicd_run2_desplegando_arm_qas.png](45_cicd_run2_desplegando_arm_qas.png) | 08/11/2026 | Run #20261109.2: despliegue de la plantilla ARM en `az-fv-qas-de-dfc-etl` (deployment `ArmTemplateForFactory-2`, validación correcta) | 27. CI/CD run #2 |
| 46 | [46_cicd_run2_ejecutando_pipeline_qas.png](46_cicd_run2_ejecutando_pipeline_qas.png) | 08/11/2026 | Run #20261109.2: pre/post-despliegue OK; ejecución de `pl_salario_total` en QAS iniciada (login con workload identity federation) | 27. CI/CD run #2 |
| 47 | [47_cicd_run3_qas_ok_esperando_aprobacion.png](47_cicd_run3_qas_ok_esperando_aprobacion.png) | 08/11/2026 | Run #20261109.3: CI y CD_QAS correctos; CD_PRD esperando aprobación | 29. CI/CD run #3 |
| 48 | [48_cicd_run3_aprobacion_prd.png](48_cicd_run3_aprobacion_prd.png) | 08/11/2026 | Panel de aprobación manual del environment ADF-PRD (plazo 2 días) | 29. CI/CD run #3 |
