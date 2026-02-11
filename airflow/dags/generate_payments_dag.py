from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import uuid
import random
from pathlib import Path
import logging 
logger = logging.getLogger(__name__)
default_args = {
    'owner': 'data_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def generate_payments():
    """Generate fake payment data"""
    curr_date = datetime.now().strftime('%Y-%m-%d')
    
    payments_data = []
    payment_amounts = [0, 4.99, 9.99]  # Corresponding to free, basic, premium plans
    # Generate payments for 100 users with 50% conversion rate
    for user_id in range(100):
        if random.random() > 0.5:  # 50% conversion rate
            payments_data.append({
                'payment_id': str(uuid.uuid4()),
                'user_id': user_id,
                'amount': random.choice(payment_amounts),
                'currency': 'USD',
                'payment_date': curr_date,
                'method': 'Credit Card'
            })
    
    df_payments = pd.DataFrame(payments_data)
    year = curr_date.split('-')[0]
    month = curr_date.split('-')[1]
    day = curr_date.split('-')[2]

    output_dir = Path(f'/opt/airflow/dummy_s3/payments/{year}/{month}/{day}')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'source_payments.csv'
    df_payments.to_csv(output_path, index=False)
    
    logger.info(f"Generated {output_path} with {len(payments_data)} payments")
    return payments_data

with DAG(
    'generate_payments',
    default_args=default_args,
    schedule="15 0 * * *",
    catchup=False,
    doc_md=__doc__,
) as dag:

    generate_payments_task = PythonOperator(
        task_id='generate_payments',
        python_callable=generate_payments,
        doc="Generate fake payment data"
    )
