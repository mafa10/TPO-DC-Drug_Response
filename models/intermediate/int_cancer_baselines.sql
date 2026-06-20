{{ config(materialized='view') }}

SELECT
    cancer_type,
    ROUND(AVG(ln_ic50), 4) AS baseline_ic50
FROM {{ ref('stg_drugresponse') }}
GROUP BY cancer_type