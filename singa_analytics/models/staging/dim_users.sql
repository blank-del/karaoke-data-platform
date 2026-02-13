select
    CAST(user_id as INTEGER) as user_id,
    country,
    signup_source,
    CAST(join_date as DATE) as join_date
from cdc_product_db_public_users