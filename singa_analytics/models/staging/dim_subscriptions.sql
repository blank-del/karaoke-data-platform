select
    CAST(subscription_id as INTEGER) as subscription_id,
    subscription_type as type,
    CAST(subscription_price as FLOAT) as price
from cdc_product_db_public_subscriptions