
import airflow
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from src.models.initial_model_functions import load_preprocess, fit_model

PATH_STREAM_SAMPLE = "/data/stream_sample.p"
PATH_TEST_SET = "/data/test_set.p"
INITIAL_MODEL_PATH = "/models/current_model/initial_model.H5"

BATCH_SIZE = 128
NUM_CLASSES = 10
EPOCHS = 4

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),      # this in combination with catchup=False ensures the DAG being triggered from the current date onwards along the set interval
    'provide_context': True,                            # this is set to True as we want to pass variables on from one task to another
}

dag = DAG(
    dag_id='initial_model_DAG',
    default_args=args,
    schedule_interval= '@once',             # set interval
	catchup=False,                          # indicate whether or not Airflow should do any runs for intervals between the start_date and the current date that haven't been run thus far
)


task1 = PythonOperator(
    task_id='load_preprocess',
    python_callable=load_preprocess,        # function to be executed
    op_kwargs={'path_stream_sample': PATH_STREAM_SAMPLE,        # input arguments
			   'path_test_set': PATH_TEST_SET},
    dag=dag,
)

task2 = PythonOperator(
    task_id='fit_model',
    python_callable=fit_model,
    op_kwargs={'batch_size': BATCH_SIZE,
               'epochs': EPOCHS,
			   'num_classes': NUM_CLASSES,
               'initial_model_path': INITIAL_MODEL_PATH},
    dag=dag,
)

task1 >> task2                  # set task priority
