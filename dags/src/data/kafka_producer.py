from kafka  import KafkaProducer
import random
import pickle
import os
import logging
from time import sleep
from json import dumps


def encode_to_json(x_train, y_train):
	x = dumps(x_train.tolist())
	y = dumps(y_train.tolist())
	jsons_comb = [x, y]

	return jsons_comb

def generate_stream(**kwargs):

	producer = KafkaProducer(bootstrap_servers=['kafka:9092'],                              # set up Producer
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

	stream_sample = pickle.load(open(os.getcwd() + kwargs['path_stream_sample'], "rb"))       # load stream sample file

	rand = random.sample(range(0, 20000), 200)                                                # the stream sample consists of 20000 observations - and along this setup 200 samples are selected randomly

	x_new = stream_sample[0]
	y_new = stream_sample[1]

	logging.info('Partitions: ', producer.partitions_for('TopicA'))

	for i in rand:
		json_comb = encode_to_json(x_new[i], y_new[i])                                         # pick observation and encode to JSON
		producer.send('TopicA', value=json_comb)                                               # send encoded observation to Kafka topic
		logging.info("Sent number: {}".format(y_new[i]))
		sleep(1)

	producer.close()
