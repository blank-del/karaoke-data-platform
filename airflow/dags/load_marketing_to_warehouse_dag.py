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

def create_marketing_table():
    """Create fact_marketing table in Postgres if it doesn't exist."""
    pg_hook = PostgresHook(postgres_conn_id='my_local_pg')
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_marketing (
                date            DATE,
                channel         VARCHAR(100),
                campaign        VARCHAR(50),
                spend           NUMERIC(12, 2),
                clicks          INTEGER,
                impressions     INTEGER
            );
        """)
        conn.commit()
        logger.info('fact_marketing table created/verified successfully')

    except Exception as e:
        conn.rollback()
        logger.error('Failed to create fact_marketing table: %s', e)
        raise

    finally:
        cur.close()
        conn.close()

def load_marketing_to_postgres(**context):
    """Scan generated marketing CSVs and append new rows into Postgres table.

    Expects marketing CSVs under `/opt/airflow/dummy_s3/marketing/YYYY/MM/DD/source_marketing.csv`.
    Writes into Postgres table `fact_marketing`.
    """
    execution_date = context['ds'] 
    date_obj = datetime.strptime(execution_date, '%Y-%m-%d')

    year  = date_obj.strftime('%Y')                         # e.g. '2026'
    month = date_obj.strftime('%m')                         # e.g. '01'
    day   = date_obj.strftime('%d')                         # e.g. '15'

    base_marketing = Path('/opt/airflow/dummy_s3/marketing')

    db_conn_str = "postgresql://admin:admin@warehouse-db:5432/warehouse_db" 

    pg_hook = PostgresHook(postgres_conn_id='my_local_pg')
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    # check if data already exists
    cur.execute(
            "SELECT COUNT(*) FROM fact_marketing WHERE date = %s",
            (execution_date,)
    )
    count = cur.fetchone()[0]
    if count > 0:
        logger.info('Data for date %s already exists in fact_marketing, skipping load', execution_date)
        cur.close()
        conn.close()
        return

    csv_files = list(base_marketing.glob(f'{year}/{month}/{day}/*.csv'))
    if not csv_files:
        logger.info('No marketing CSV files found under %s', base_marketing)
        return

    logger.info('Found %d marketing CSV files to process', len(csv_files))
    for csv_file in csv_files:
        logger.info('Processing marketing CSV file: %s', csv_file)
        with open(csv_file, 'r') as f:
            cur.copy_expert(sql="""
                            COPY fact_marketing FROM STDIN WITH (FORMAT CSV, HEADER);
                            """,
                            file=f)
        conn.commit()
        cur.close()
        logger.info('Finished processing marketing CSV file: %s', csv_file)

with DAG(
    'load_marketing_to_warehouse',
    default_args=default_args,
    schedule="0 8 * * *",
    catchup=False,
    doc_md=__doc__,
) as dag:
    create_table_task = PythonOperator(
        task_id='create_marketing_table',
        python_callable=create_marketing_table,
        doc='Create fact_marketing table in Postgres if it does not exist',
        dag=dag,
    )

    load_marketing_task = PythonOperator(
        task_id='load_marketing_to_postgres',
        python_callable=load_marketing_to_postgres,
        doc='Load generated marketing CSVs into Postgres',
        dag=dag,
    )

    create_table_task >> load_marketing_task