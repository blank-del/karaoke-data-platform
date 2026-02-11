from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import random
import logging
from pathlib import Path
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def generate_marketing():
    """Generate fake marketing spend data"""
    
    marketing_data = []
    curr_date = datetime.now().strftime('%Y-%m-%d')
    
    # Generate marketing data
    for channel in ['Google', 'Facebook']:
        marketing_data.append({
            'date': curr_date,
            'channel': channel,
            'campaign': f'{channel}_Campaign',
            'spend': random.randint(50, 200),
            'clicks': random.randint(100, 500),
            'impressions': random.randint(1000, 5000)
        })
    
    df_marketing = pd.DataFrame(marketing_data)
    # using current date to create subdirectories for year/month/day under dummy_s3/marketing
    # current date is treated as the date at which the data is generated and not when the script was run
    year = curr_date.split('-')[0]
    month = curr_date.split('-')[1]
    day = curr_date.split('-')[2]

    output_dir = Path(f'/opt/airflow/dummy_s3/marketing/{year}/{month}/{day}')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'source_marketing.csv'
    df_marketing.to_csv(output_path, index=False)
    
    logger.info(f"Generated {output_path} with {len(marketing_data)} marketing records")
    return marketing_data

with DAG(
    'generate_marketing',
    default_args=default_args,
    schedule="15 0 * * *",
    catchup=False,
    doc_md=__doc__,
) as dag:

    generate_marketing_task = PythonOperator(
        task_id='generate_marketing',
        python_callable=generate_marketing,
        doc="Generate fake marketing spend data"
    )
