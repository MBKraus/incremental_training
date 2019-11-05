# Keeping your ML model in shape with Kafka, Airflow and MLFlow
### How to incrementally update your ML model in an automated way as new training data becomes available

Fitting and serving your machine learning (ML) model is one thing, but what about keeping it in shape over time?

Let's say we got a ML model that has been put in production and is actively serving predictions. Simultaneously, we got new training data that becomes available in a streaming way while users use the model. Incrementally updating the model with new data can improve the model, whilst it also might reduce model drift. However, it often comes with additional overhead. Luckily, there are tools that allow you to automate many parts of this process. 

This repository takes on the topic of incrementally updating a ML model as new data becomes available. It mainly leans on three nifty tools, being Kafka, Airflow, and MLFlow. 

Where would these tools fit in when it comes to incorporating new data into your model by means of automated incremental updates of the model? Let's break it down along the previously mentioned hypothetical case where we have an ML model that is serving predictions:

* First, we would need to set up the environment and create an initial ML model
* Once that's done, we could simulate streaming data coming in as users use the ML model and publish this to a Kafka feed
* Then, we can periodically extract the data from this feed and use it to update the ML model, gauge its relative performance and put it up for use if it outperforms the current version of the model - all orchestrated with the help of Airflow
* We further log the results, model parameters, and sample characteristics of each update run with MLFlow

In order to set up this hypothetical case in a replicable (local) format, whilst mimicking the microservices architecture that is nowadays often employed within companies, everything has been set up along a set of Docker containers orchestrated by means of Docker Compose.
