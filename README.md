# Singa Home Assignment

## Folder
1.  `airflow`: Contains the DAGs in python are for ingesting data, loading the data into duckdb, and for running the dbt models.
2.  `pipeline.py`: Python script that generates mock data, loads it into an in-memory database (DuckDB), and calculates metrics.
3.  `singa_analytics/models/marts/cost_per_user.sql`: The raw SQL queries used for cost per user.
4.  `singa_analytics/models/marts/new_paying.sql`: The raw SQL queries used for cost new paying customers.
5.  `dummy_s3`: Acts as storage for hosting the CSV files.
6.  `singa_analytics`: Contains folders for dbt.

## How to Run the Pipeline
This pipeline uses Python and DuckDB (an SQL OLAP database).

1.  **Install Docker:**

2.  **Run with Docker:**
    ```bash
    docker build -t duckdb-pipeline .
    docker run --rm duckdb-pipeline
    ```
1.  **Output:**
    *   The pipeline will generate CSV files (mock data).
    *   It will populate the Duckdb