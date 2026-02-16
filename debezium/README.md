# Debezium Connectors

This directory contains helper scripts and documentation for setting up Apache Debezium connectors used in the data pipeline project. Debezium is used to capture change data from a PostgreSQL source database and stream it into Kafka, then sink it into another PostgreSQL database acting as a data warehouse.

## Contents

- `register_postgres_source.sh` – A bash script that checks for and registers a Debezium PostgreSQL source connector (`users_song-connector`) with the Kafka Connect REST API, this connector monitors the `application_db` database and captures changes on the `users`, `songs`, and `subscriptions` tables using WAL (Write Ahead Logs).

- `register_postgres_target.sh` – A bash script that checks for and registers a Debezium JDBC sink connector (`jdbc-connector`). It reads from Kafka topics created by the source connector (each table has its own kafka topic) and writes/upserts records into the `warehouse_db` PostgreSQL database.

## Customization

- Modify the `table.include.list` or `topics` fields in the scripts to adjust which tables/topics are tracked, by default the table names in the warehouse are done using prefix name followed by topic name but this behavior can be changed by `collection.name.format` field in JDBC connector.

## Notes

- The source connector uses logical decoding via a replication slot and filtered publication to capture only the specified tables.
- The sink connector is configured in `upsert` mode with primary key support, enabling idempotent writes to the warehouse.