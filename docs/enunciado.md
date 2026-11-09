Evaluación trabajo práctico - 60% (21/07/2026 - 08/08/2026)
Especificaciones proyecto DataOps con Azure DevOps y Azure Data Factory

Cliente:
“Buscamos implementar un flujo automatizado que calcule las comisiones totales de los empleados combinando datos de una base PostgresSQL y un archivo CSV. Además, queremos garantizar que este pipeline sea desplegado automáticamente en un entorno de producción mediante prácticas de CI/CD, asegurando confiabilidad y eficiencia en cada despliegue.

1      Requerimientos específicos:
Pipeline de Azure Data Factory:
Extraiga datos de la tabla dmc.rrhh.empleado.
Procese el archivo CSV “ComisionEmpleados_V1_202608.csv” desde Azure Blob Storage.
Realice un Join basado en empleado_id para calcular el salario total:
salario_total = salario + comisión.
Genere una tabla consolidada en un archivo Parquet en el Data Lake.
CI/CD con Azure DevOps:
Configure un repositorio para versionar los pipelines y plantillas ARM.
Cree pipelines de CI para validar y realizar despliegue automatizado de los cambios en el repositorio.
Configure pipelines de CD para desplegar el flujo en entornos de desarrollo a producción automatizadas.
2         Implementación de DataOps con Azure DevOps y Azure Data Factory
2.1       Objetivo General
Desarrollar un flujo automatizado para el cálculo de comisiones de empleados, integrando datos de una base SQL y un archivo CSV en Azure Data Factory. El flujo debe implementarse y desplegarse de forma confiable en un entorno de producción mediante prácticas de CI/CD en Azure DevOps.

2.2       Objetivos Específicos
1.      Crear un pipeline en Azure Data Factory (o Python) que:

Extraiga datos de la tabla dmc.rrhh.empleado en PostgresSQL Database.
Procese el archivo CSV ComisionEmpleados_V1_202608.csv desde Azure Blob Storage.
Realice un Join entre ambas fuentes basado en empleado_id.
Genere como salida:
Un archivo Parquet almacenado en un Data Lake.
2.      Implementar prácticas de CI/CD utilizando Azure DevOps:

Versionar los pipelines y plantillas ARM en un repositorio Git.
Crear un pipeline de CI para validar y probar el flujo de datos.
Configurar un pipeline de CD para desplegar el flujo en los entornos de desarrollo, prueba y producción.
2.3       Descripción del Trabajo
2.3.1         Requerimientos
1.      Pipeline en Azure Data Factory (o Python)

Configurar las conexiones a la base de datos SQL y al Blob Storage.
Diseñar un flujo que procese el CSV, realice un Join con la tabla SQL y genere las salidas esperadas.
2.      Repositorio Git en Azure DevOps / Github

Subir el código del pipeline y las plantillas ARM para su versionamiento.
3.      Pipelines de CI/CD en Azure DevOps / Jenkins

Pipeline de CI/CD:
Despliegue automatizado en los entornos mencionados con aprobaciones automatizadas.
4.      Evidencias de Pruebas

Capturas de pantalla y logs que demuestren el correcto funcionamiento del flujo y las pruebas.
2.4       Entregables
·         Evidencias del despliegue y configuración de:

o   Pipeline de Azure Data Factory (o Python)

§  Flujo implementado y funcionando.

Captura de pantalla del pipeline ejecutándose con éxito.
o   Repositorio Git

Repositorio con el código de los pipelines y plantillas ARM.
Archivo README.md explicando el contenido del repositorio y los pasos para desplegar.
o   Pipelines de CI/CD

Capturas o registros mostrando los pipelines funcionando correctamente en los entornos correspondientes.
·         Informe Final

Breve resumen del proyecto.
Registro de pruebas realizadas y sus resultados.
2.5       Matriz de Evaluación (20 puntos)
 

Criterio

Descripción

Puntos

Pipeline en Data Factory  / Script Python

Extrae, transforma, y genera las salidas esperadas en Parquet / excel.

6

Repositorio Git

Uso adecuado de Git.

4

Pipelines de CI/CD

Configuración funcional con pruebas y despliegue en los entornos.

4

Informe Final y Evidencias

Informe completo y evidencias claras del funcionamiento.

6

3         Plazo de Entrega
Fecha límite: 01 de Noviembre 2026.
Subir los entregables al aula virtual DMC.
