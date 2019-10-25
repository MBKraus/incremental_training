import keras
from keras.models import Sequential, load_model
import os
import time
import logging
import mlflow.keras


def load_current_model(model_path, file_m):

	model = load_model(os.getcwd()+model_path + str(file_m))
	model.compile(loss=keras.losses.categorical_crossentropy,
				  optimizer=keras.optimizers.Adadelta(),
				  metrics=['accuracy'])
	return model


def update_model(**kwargs):

	ti = kwargs['ti']
	loaded = ti.xcom_pull(task_ids='preprocessing')

	logging.info('variables successfully fetched from previous task')

	new_samples = loaded[0]
	test_set = loaded[1]

	# load new samples

	x_new = new_samples[0]
	y_new = new_samples[1]

	y_new = keras.utils.to_categorical(y_new, kwargs['num_classes'])

	# load test set

	x_test = test_set[0]
	y_test = test_set[1]

	y_test = keras.utils.to_categorical(y_test, kwargs['num_classes'])

	# get current_model

	for file_m in os.listdir(os.getcwd()+kwargs['path_current_model']):
		if 'H5' in file_m:

			mlflow.set_tracking_uri('http://mlflow:5000')

			with mlflow.start_run():

				model = load_current_model(kwargs['path_current_model'], file_m)

				# get score of current model

				current_score = model.evaluate(x_test, y_test, verbose=0)

				# update model with new data and evaluate score

				model.fit(x_new, y_new,
						  batch_size=kwargs['batch_size'],
						  epochs=kwargs['epochs'],
						  verbose=1,
						  validation_data=(x_test, y_test))

				updated_score = model.evaluate(x_test, y_test, verbose=0)

				# log results to MLFlow

				mlflow.log_metric('Epochs', kwargs['epochs'])
				mlflow.log_metric('Batch size', kwargs['batch_size'])

				mlflow.log_metric('test accuracy - current model', current_score[1])
				mlflow.log_metric('test accuracy - updated model', updated_score[1])

				mlflow.log_metric('loss - current model', current_score[0])
				mlflow.log_metric('loss - updated model', updated_score[0])

				mlflow.log_metric('Number of new samples used for training', x_new.shape[0])

				# if the updated model outperforms the current model -> move current version to archive and promote the updated model

				if updated_score[1] - current_score[1] > 0:

					logging.info('Updated model stored')
					mlflow.set_tag('status', 'the model from this run replaced the current version ')

					updated_model_name = 'model_' + str(time.strftime("%Y%m%d_%H%M"))

					model.save(os.getcwd()+kwargs['path_current_model'] + updated_model_name + '.H5')

					os.rename(os.getcwd()+kwargs['path_current_model']+file_m, os.getcwd()+kwargs['path_model_archive']+file_m)

				else:
					logging.info('Current model maintained')
					mlflow.set_tag('status', 'the model from this run did not replace the current version ')

		else:

			logging.info(file_m + ' is not a model')


def data_to_archive(**kwargs):

	# store data that was used for updating the model in archive along date + time tag

	for file_d in os.listdir(os.getcwd()+kwargs['path_new_data']):
		if 'new_samples.p' in file_d:

			os.rename(os.getcwd()+kwargs['path_new_data'] + file_d, os.getcwd()+kwargs['path_used_data'] + file_d)

			logging.info('data used for updating the model has been moved to archive')

		else:
			print('no data found')
