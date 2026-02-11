from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from pathlib import Path
import duckdb
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def load_payments_to_duckdb():
    """Scan generated payment CSVs and append new rows into DuckDB fact table.

    Expects payment CSVs under `/opt/airflow/dummy_s3/payments/YYYY/MM/DD/source_payments.csv`.
    Writes into `/opt/airflow/singa_analytics/analytics.duckdb` table `fact_payments`.
    """
    base_payments = Path('/opt/airflow/dummy_s3/payments')

    db_dir = Path('/opt/airflow/singa_analytics')
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / 'analytics.duckdb'

    try:
        conn = duckdb.connect(database=str(db_path))
        logger.info('Connected to DuckDB at %s', db_path)

        # Ensure fact table exists
        conn.sql('''
            CREATE TABLE IF NOT EXISTS fact_payments (
                payment_id INTEGER,
                user_id INTEGER,
                amount DOUBLE,
                currency VARCHAR,
                payment_date DATE,
                method VARCHAR
            );
        ''')

        csv_files = list(base_payments.rglob('source_payments.csv'))
        if not csv_files:
            logger.info('No payment CSV files found under %s', base_payments)
            return

        logger.info('Found %d payment CSV files to process', len(csv_files))

        for f in csv_files:
            file_path = str(f)
            logger.info('Processing payments file %s', file_path)
            try:
                insert_sql = f"""
                    INSERT INTO fact_payments
                    SELECT
                        CAST(payment_id AS INTEGER) AS payment_id,
                        CAST(user_id AS INTEGER) AS user_id,
                        CAST(amount AS DOUBLE) AS amount,
                        currency,
                        CAST(payment_date AS DATE) AS payment_date,
                        method
                    FROM read_csv_auto('{file_path}') AS t
                    WHERE t.payment_id NOT IN (SELECT payment_id FROM fact_payments);
                """
                conn.sql(insert_sql)
                total = conn.execute('SELECT COUNT(*) FROM fact_payments').fetchone()[0]
                logger.info('After processing %s total rows in fact_payments: %d', file_path, total)
            except Exception:
                logger.exception('Failed to process %s', file_path)

        conn.close()
    except Exception:
        logger.exception('Failed to connect to DuckDB at %s', db_path)
        raise


with DAG(
    'load_payments_to_warehouse',
    default_args=default_args,
    schedule='@once',
    catchup=False,
    doc_md=__doc__,
) as dag:

    load_payments_task = PythonOperator(
        task_id='load_payments_to_duckdb',
        python_callable=load_payments_to_duckdb,
        doc='Load generated payment CSVs into DuckDB',
        dag=dag,
    )
