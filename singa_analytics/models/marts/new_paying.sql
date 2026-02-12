{{ config(materialized='table') }}
WITH first_payments AS (
    SELECT 
        user_id, 
        MIN(payment_date) as first_payment_date
    FROM fact_payments
    GROUP BY user_id
)
SELECT 
    EXTRACT (MONTH FROM fp.first_payment_date) as month,
    u.country,
    u.signup_source as channel,
    COUNT(DISTINCT fp.user_id) as new_paying_users
FROM first_payments fp
JOIN dim_users u ON fp.user_id = u.user_id
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3