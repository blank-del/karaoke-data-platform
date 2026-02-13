select
    CAST(song_id as INTEGER) as song_id,
    song_name as name,
    CAST(song_duration as INTEGER) as duration,
    country
from cdc_product_db_public_songs