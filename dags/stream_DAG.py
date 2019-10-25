
import airflow

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from src.data.kafka_producer import generate_stream

PATH_STREAM_SAMPLE = "/data/stream_sample.p"

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),      # this in combination with catchup=False ensures the DAG being triggered from the current date onwards along the set interval
    'provide_context': True,                            # this is set to True as we want to pass variables on from one task to another
}

dag = DAG(
    dag_id='stream_DAG',
    default_args=args,
    schedule_interval= '@hourly',      # set interval
	catchup=False,                     # indicate whether or not Airflow should do any runs for intervals between the start_date and the current date that haven't been run thus far
)


task1 = PythonOperator(
    task_id='generate_stream',
    python_callable=generate_stream,        # function to be executed
    op_kwargs={'path_stream_sample': PATH_STREAM_SAMPLE},        # input arguments
    dag=dag,
)


