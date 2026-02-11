WITH new_users_by_channel AS (
    -- Count new paying users attributed to each channel
    SELECT 
        channel,
        sum(new_paying_users) as new_users
    FROM
        {{ ref("new_paying") }}
    GROUP BY 1
),
total_spend_by_channel AS (
    -- Sum spend
    SELECT 
        channel,
        SUM(spend) as total_spend
    FROM fact_marketing
    GROUP BY 1
)
SELECT 
    s.channel,
    s.total_spend,
    COALESCE(n.new_users, 0) as new_paying_users,
    ROUND(s.total_spend / NULLIF(n.new_users, 0), 2) as cost_per_new_user
FROM total_spend_by_channel s
LEFT JOIN new_users_by_channel n ON s.channel = n.channel
ORDER BY cost_per_new_user DESC