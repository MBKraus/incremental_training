
import airflow

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from src.data.data_functions import get_data_from_kafka, load_data
from src.models.update_functions import load_current_model, update_model, data_to_archive
from src.preprocessing.preprocessing_functions import preprocessing

CLIENT = 'kafka:9092'
TOPIC = 'TopicA'

PATH_NEW_DATA = '/data/to_use_for_model_update/'
PATH_USED_DATA = '/data/used_for_model_update/'
PATH_TEST_SET = '/data/test_set.p'

PATH_INITIAL_MODEL = '/models/initial_model'
PATH_CURRENT_MODEL = '/models/current_model/'

PATH_MODEL_ARCHIVE = '/models/archive/'

BATCH_SIZE = 128
NUM_CLASSES = 10
EPOCHS = 4


args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),       # this in combination with catchup=False ensures the DAG being triggered from the current date onwards along the set interval
    'provide_context': True,                            # this is set to True as we want to pass variables on from one task to another
}

dag = DAG(
    dag_id='update_DAG',
    default_args=args,
	schedule_interval='@daily',        # set interval
	catchup=False,                    # indicate whether or not Airflow should do any runs for intervals between the start_date and the current date that haven't been run thus far
)


task1 = PythonOperator(
    task_id='get_data_from_kafka',
    python_callable=get_data_from_kafka,            # function called to get data from the Kafka topic and store it
    op_kwargs={'path_new_data': PATH_NEW_DATA,
               'client': CLIENT,
               'topic': TOPIC},
    dag=dag,
)

task2 = PythonOperator(
    task_id='load_data',
    python_callable=load_data,                      # function called to load data for further processing
    op_kwargs={'path_new_data': PATH_NEW_DATA,
               'path_test_set': PATH_TEST_SET},
    dag=dag,
)

task3 = PythonOperator(
    task_id='preprocessing',                # function called to preprocess data
    python_callable=preprocessing,
    op_kwargs={},
    dag=dag,
)

task4 = PythonOperator(
    task_id='update_model',
    python_callable=update_model,                       # function called to update model
    op_kwargs = {'num_classes': NUM_CLASSES,
                 'epochs': EPOCHS,
                 'batch_size': BATCH_SIZE,
                 'path_current_model': PATH_CURRENT_MODEL,
                 'path_model_archive': PATH_MODEL_ARCHIVE,
                 },
    dag=dag,
)

task5 = PythonOperator(
    task_id='data_to_archive',
    python_callable=data_to_archive,             # function called to archive data used for updating the model
    op_kwargs = {'path_new_data': PATH_NEW_DATA,
                 'path_used_data': PATH_USED_DATA,
                 },
    dag=dag,
)

task1 >> task2 >> task3 >> task4 >> task5       # set task priority
