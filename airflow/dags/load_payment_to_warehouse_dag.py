from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def create_payment_table():
    """Create fact_payment table in Postgres if it doesn't exist."""
    pg_hook = PostgresHook(postgres_conn_id='my_local_pg')
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_payments (
                payment_id      UUID,
                user_id         INTEGER,
                amount          NUMERIC(12, 2),
                currency        VARCHAR(20),
                payment_date    DATE,
                method          VARCHAR(20)
            );
        """)
        conn.commit()
        logger.info('fact_marketing table created/verified successfully')

    except Exception as e:
        conn.rollback()
        logger.error('Failed to create fact_payments table: %s', e)
        raise

    finally:
        cur.close()
        conn.close()


def load_payments_to_postgres(**context):
    """Scan generated payment CSVs and append new rows into Postgres table.

    Expects payment CSVs under `/opt/airflow/dummy_s3/payments/YYYY/MM/DD/source_payments.csv`.
    Writes into Postgres table `fact_payments`.
    """
    execution_date = context['ds'] 
    date_obj = datetime.strptime(execution_date, '%Y-%m-%d')

    year  = date_obj.strftime('%Y')                         # e.g. '2026'
    month = date_obj.strftime('%m')                         # e.g. '01'
    day   = date_obj.strftime('%d')

    base_payments = Path('/opt/airflow/dummy_s3/payments')

    db_conn_str = "postgresql://admin:admin@warehouse-db:5432/warehouse_db" 
    pg_hook = PostgresHook(postgres_conn_id='my_local_pg')
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    # check if data already exists
    cur.execute(
            "SELECT COUNT(*) FROM fact_payments WHERE payment_date = %s",
            (execution_date,)
    )
    count = cur.fetchone()[0]
    if count > 0:
        logger.info('Data for date %s already exists in fact_marketing, skipping load', execution_date)
        cur.close()
        conn.close()
        return

    csv_files = list(base_payments.rglob('source_payments.csv'))
    if not csv_files:
        logger.info('No payment CSV files found under %s', base_payments)
        return

    logger.info('Found %d payment CSV files to process', len(csv_files))
    for csv_file in csv_files:
        logger.info('Processing payments CSV file: %s', csv_file)
        with open(csv_file, 'r') as f:
            cur.copy_expert(sql="""
                            COPY fact_payments FROM STDIN WITH (FORMAT CSV, HEADER);
                            """,
                            file=f)
    conn.commit()
    conn.close()
    logger.info('Finished processing payments CSV file: %s', csv_file)
with DAG(
    'load_payments_to_warehouse',
    default_args=default_args,
    schedule="0 8 * * *",
    catchup=False,
    doc_md=__doc__,
) as dag:
    create_table_task = PythonOperator(
        task_id='create_payments_table',
        python_callable=create_payment_table,
        doc='Create fact_payments table in Postgres if it does not exist',
        dag=dag,
    )

    load_payments_task = PythonOperator(
        task_id='load_payments_to_postgres',
        python_callable=load_payments_to_postgres,
        doc='Load generated payment CSVs into DuckDB',
        dag=dag,
    )
