# TPO Grupo 4 — Análisis de Respuesta Farmacológica (GDSC2)

Pipeline de datos completo sobre el dataset `drug_response`: ingesta, transformación ELT con **dbt**, métricas de calidad de datos y entrenamiento de modelo de machine learning predictivo.

## Arquitectura del pipeline (Medallion)

```text
Datasets/ (CSV)
     │
     ▼
ingesta.py      ← Script de Python: Ingesta del CSV crudo a DuckDB (RAW / Bronze)
     │
     ▼
dbt run (STG)   ← Capa Silver (models/staging/): Limpieza, normalización y tests lógicos
     │
     ├──► dbt run (MART_BI) ← Capa Gold (models/mart/): Modelo analítico y estrella para BI
     ├──► dbt run (MART_ML) ← Capa Gold (models/mart/): Ingeniería de features para ML
     └──► dbt run (MART_DQ) ← Capa Gold (models/mart/): Auditoría y métricas de Data Quality
             │
             ▼
machine_learning.py ← Pipeline Sklearn: Consume el Parquet de ML y entrena predicciones
```

## Estructura del repositorio

```text
TPO-DC-Drug_Response/
├── Datasets/                          ← CSV original (no incluido en el repo)
├── models/                            ← Modelos de transformación ELT en dbt
│   ├── bronze/                        ← Declaración de las fuentes de datos (RAW)
│   ├── staging/                       ← Limpieza, estandarización de strings y casteos
│   └── mart/                          ← Modelos Gold finales (BI, ML, Quality)
├── eda/                               ← EDA del dataset
    └── EDA_datosCrudos_GDSC2.ipynb/   ← EDA de datos crudos del dataset
├── tests/                             ← Validaciones personalizadas de dbt (ej. assert de rangos)
├── ingesta.py                         ← Script inicial (CSV → Base DuckDB)
├── machine_learning.py                ← Entrenamiento del modelo ML usando Scikit-Learn
├── qualityDoc.md                      ← Documentación detallada de Calidad de Datos
├── dbt_project.yml                    ← Configuración central del proyecto dbt
├── profiles.yml                       ← Perfil de conexión a base de datos DuckDB
├── requirements.txt                   
└── .gitignore
```

## Requisitos previos

- Python 3.10 o superior
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone [https://github.com/mafa10/TPO-DC-Drug_Response.git](https://github.com/mafa10/TPO-DC-Drug_Response.git)
cd TPO-DC-Drug_Response

# 2. Crear y activar entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Instalar dependencias (Pandas, DuckDB, dbt-duckdb, Scikit-Learn)
pip install -r requirements.txt
```

## Datasets

El archivo CSV base **no está incluido en el repositorio** por restricciones de tamaño y buenas prácticas. Descargalo y colocalo en la carpeta `Datasets/` en la raíz del proyecto.

| Archivo esperado | Descripción |
|---|---|
| `drug_response.csv` | Dataset de la respuesta farmacológica (genómica) en líneas celulares con variables experimentales (AUC, concentración, etc). |

> Fuente: Base de datos *Genomics of Drug Sensitivity in Cancer (GDSC2)*.

## Cómo correr el proyecto

Los procesos deben ejecutarse **en orden**. Cada etapa nutre la base de datos DuckDB para que el siguiente componente funcione correctamente.

### Paso 1 — Ingesta (Capa Bronze / RAW)

```bash
python ingesta.py
```

Lee el CSV crudo desde la carpeta `Datasets/`, inicializa la base de datos local `DuckDB` y crea la capa Bronze sin modificar la inmutabilidad de los datos originales.

### Paso 2 — ELT (Capa Silver STG y Gold MART)

Toda la transformación, limpieza (tratamiento de nulos, inconsistencias) y creación de reglas de negocio se hace mediante `dbt`. Asegurate de configurar tu entorno apuntando a `profiles.yml` de ser necesario.

```bash
# Instalar paquetes o dependencias de dbt (si corresponde)
dbt deps

# Ejecutar todos los modelos de transformación
dbt run

# Ejecutar las pruebas lógicas y de calidad de datos
dbt test
```

*Esto generará los modelos finales y los persistirá dinámicamente como archivos `.parquet`.*

### Paso 3 — Pipeline de Machine Learning

```bash
python machine_learning.py
```

Este script lee automáticamente el Mart optimizado (`mart_ML_drugresponse.parquet`), separa conjuntos de Train y Test, y aplica el entrenamiento predictivo sobre el target.

## Tablas Analíticas Generadas (Data Marts)

Al finalizar el flujo de `dbt`, se generan tres salidas físicas (formato Parquet) altamente optimizadas:

| Archivo Generado | Propósito |
|---|---|
| `mart_BI_drugresponse.parquet` | Tablas desnormalizadas / estrella listas para consumir desde el **Tablero de Comando** (Power BI/Looker). |
| `mart_ML_drugresponse.parquet` | Dataset transformado con escalado numérico y *one-hot encoding* para algoritmos supervisados. |
| `mart_data_quality_drugresponse.parquet`| Tracking automático de filas con errores lógicos (valores negativos, áreas erróneas). |

## Modelo de Machine Learning

**Problema:** Regresión supervisada para predecir la efectividad relativa del fármaco sobre el tejido.

**Features utilizadas:** `drug_id`, `cell_line_name`, `min_concentration`, `max_concentration`, `dose_amplitude`, estatus público del experimento, entre otros.

**Modelos entrenados:**

| Modelo | Descripción / Uso |
|---|---|
| **Random Forest Regressor** | Implementado con `scikit-learn` por su robustez ante relaciones no lineales en curvas dosis-respuesta (AUC / IC50). |

> *Nota: Las métricas finales del entrenamiento, las pruebas y los valores de evaluación (como R² y RMSE) se imprimen por consola al finalizar la ejecución del paso 3.*

## Dependencias

| Librería | Propósito principal |
|---|---|
| `pandas` | Manipulación de estructuras e interacciones en memoria |
| `duckdb` | Motor de base de datos OLAP embebida para almacenamiento |
| `dbt-core` | Orquestador de transformaciones SQL ELT |
| `dbt-duckdb` | Adaptador del motor a dbt |
| `scikit-learn` | Pipeline de modelado de Machine Learning |
