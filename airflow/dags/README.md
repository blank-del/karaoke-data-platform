# Airflow DAGs

This directory contains the Airflow DAG definitions used to drive the data pipeline for the Singa assignment project. Each DAG is responsible for either generating synthetic source data, loading it into the warehouse, or running dbt transformations.

## DAGs Overview

- **`generate_marketing_dag.py`** – creates fake marketing spend records daily and writes CSVs to `dummy_s3/marketing` partitioned by year/month/day (this format allows easier data pruning and partitioning).
- **`generate_payments_dag.py`** – produces synthetic payment data for users and stores CSVs in `dummy_s3/payments` with the same date partitioning scheme.
- **`load_marketing_to_warehouse_dag.py`** – reads the generated marketing CSV files and appends them into the `fact_marketing` table in Postgres, creating the table if it does not exist.
- **`load_payments_to_warehouse_dag.py`** – similar to the marketing loader, this DAG ingests payment CSVs into the `fact_payments` table.
- **`run_dbt_models_dag.py`** – executes dbt commands (`dbt run` followed by `dbt test`) against the `singa_analytics` project to transform raw data into models after ingestion.

## Architectural Notes

### Decoupling Ingestion and Load

To improve modularity and resilience, data generation (ingestion) and data loading are separated into distinct DAGs. This decoupling allows:

1. **Independent scheduling** – generators run at their own cadence, while loaders can backfill or reprocess without regenerating data.
2. **Simpler troubleshooting** – issues in ingestion do not immediately impact warehouse loading, and vice versa.
3. **Scalability** – the pipeline can easily add new generators or loaders without monolithic workflow changes.

### Parametrization and Idempotency

The scripts used by the load DAGs are parameterized by execution date (`context['ds']`), which ensures they target the correct file partitions and can be rerun for a specific date if necessary. They also perform upsert-style behavior by checking if data already exists for the execution date before copying new rows. This avoids duplication and makes the jobs idempotent which means that re‑running a load DAG will not insert the same records twice.

### Upsert Logic

The loaders query the warehouse tables for existing rows with the current date and skip insertion if data is present. This mechanism guarantees that accidental re-executions or backfills do not create duplicate records.