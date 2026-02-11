#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" localhost:8083/connectors/users_song-connector)
if [ "$RESPONSE" -eq 200 ]; then    
    echo "Connector already exists. Skipping creation."
else
    echo "Creating connector..."
    curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{"name": "users_song-connector","config": {"connector.class": "io.debezium.connector.postgresql.PostgresConnector","tasks.max": "1","database.hostname": "application-db","database.port": "5432","database.user": "admin","database.password": "admin","database.dbname": "application_db","topic.prefix": "cdc_product_db","slot.name": "cdc_product_slot","publication.autocreate.mode": "filtered","table.include.list": "public.users,public.songs,public.subscriptions","schema.history.internal.kafka.bootstrap.servers": "kafka:9092","schema.history.internal.kafka.topic": "schema-changes.product_db"}}'
fi