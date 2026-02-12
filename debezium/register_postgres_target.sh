#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" localhost:8083/connectors/jdbc-connector)
if [ "$RESPONSE" -eq 200 ]; then    
    echo "Connector already exists. Skipping creation."
else
    echo "Creating connector..."
    curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{"name": "jdbc-connector","config": {"connector.class": "io.debezium.connector.jdbc.JdbcSinkConnector","tasks.max": "1","connection.url":"jdbc:postgresql://warehouse-db:5432/warehouse_db","connection.username": "admin","connection.password": "admin","topics": "cdc_product_db.public.users,cdc_product_db.public.songs,cdc_product_db.public.subscriptions","insert.mode": "upsert","delete.enabled": "true","primary.key.mode": "record_key","schema.evolution": "basic", "use.time.zone": "UTC"}}'
fi