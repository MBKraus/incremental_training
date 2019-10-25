import keras
from keras.datasets import mnist
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import pickle
import logging
import os


def load_preprocess(**kwargs):

	# load and preprocess MNIST data for initial model fit

	img_rows, img_cols = 28, 28

	# split data between train and test sets
	(x_train, y_train), (x_test, y_test) = mnist.load_data()

	# convert images into the right shape
	# source: https://keras.io/examples/mnist_cnn/

	if K.image_data_format() == 'channels_first':
		x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
		x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
		input_shape = (1, img_rows, img_cols)
	else:
		x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
		x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
		input_shape = (img_rows, img_cols, 1)

	x_train = x_train.astype('float32')
	x_test = x_test.astype('float32')

	# normalize data

	x_train /= 255
	x_test /= 255

	# Set train samples apart that will serve as streaming data later on

	x_stream = x_train[:20000]
	y_stream = y_train[:20000]

	x_train = x_train[20000:]
	y_train = y_train[20000:]

	stream_sample = [x_stream, y_stream]

	pickle.dump(stream_sample, open(os.getcwd() + kwargs['path_stream_sample'], "wb"))

	# Store test set

	test_set = [x_test, y_test]

	pickle.dump(test_set, open(os.getcwd() + kwargs['path_test_set'], "wb"))

	return x_train, y_train, x_test, y_test, input_shape

def construct_model(num_classes, input_shape):

	# construct model framework
	# source: https://keras.io/examples/mnist_cnn/

	model = Sequential()
	model.add(Conv2D(32, kernel_size=(3, 3),
					 activation='relu',
					 input_shape=input_shape))
	model.add(Conv2D(64, (3, 3), activation='relu'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(0.25))
	model.add(Flatten())
	model.add(Dense(128, activation='relu'))
	model.add(Dropout(0.5))
	model.add(Dense(num_classes, activation='softmax'))

	model.compile(loss=keras.losses.categorical_crossentropy,
				  optimizer=keras.optimizers.Adadelta(),
				  metrics=['accuracy'])
	return model

def fit_model(**kwargs):

	# fit model along preprocessed data and constructed model framework

	ti = kwargs['ti']
	loaded = ti.xcom_pull(task_ids='load_preprocess')

	logging.info('variables successfully fetched from previous task')

	x_train = loaded[0]
	y_train = loaded[1]
	x_test = loaded[2]
	y_test = loaded[3]

	input_shape = loaded[4]

	num_classes = kwargs['num_classes']

	# convert class vectors to binary class matrices

	y_train = keras.utils.to_categorical(y_train, num_classes)
	y_test = keras.utils.to_categorical(y_test, num_classes)

	# construct & fit

	model = construct_model(num_classes, input_shape)
	model.fit(x_train, y_train,
	          batch_size=kwargs['batch_size'],
	          epochs=kwargs['epochs'],
	          verbose=1,
	          validation_data=(x_test, y_test))

	# evaluate

	score = model.evaluate(x_test, y_test, verbose=0)

	logging.info('Test - loss:', score[0])
	logging.info('Test - accuracy:', score[1])

	model.save(os.getcwd() + kwargs['initial_model_path'])

