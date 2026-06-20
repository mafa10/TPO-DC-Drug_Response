{{ config(
    materialized='external',
    location='mart_ML_drugresponse.parquet'
) }}

WITH silver_data AS (
    SELECT * FROM {{ ref('stg_drugresponse') }}
),

baselines AS (
    SELECT * FROM {{ ref('int_cancer_baselines') }}
),

features AS (
    SELECT
        curve_id,
        drug_id,
        cell_line_id,

        ln_ic50,
        auc_value,

        min_concentration,
        max_concentration,
        rmse_score,
        z_score,

        cancer_type,
        biological_pathway,

        -- Amplitud de dosis
        (max_concentration - min_concentration) AS dose_amplitude

    FROM silver_data

    WHERE biological_pathway != 'unknown'
)

SELECT 
    f.*,
    b.baseline_ic50
FROM features f
LEFT JOIN baselines b ON f.cancer_type = b.cancer_type