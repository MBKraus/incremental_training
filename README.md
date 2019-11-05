# Keeping your ML model in shape with Kafka, Airflow and MLFlow
## *How to incrementally update your ML model in an automated way as new training data becomes available*

Fitting and serving your machine learning (ML) model is one thing, but what about keeping it in shape over time?

Let's say we got a ML model that has been put in production and is actively serving predictions. Simultaneously, we got new training data that becomes available in a streaming way while users use the model. Incrementally updating the model with new data can improve the model, whilst it also might reduce model drift. However, it often comes with additional overhead. Luckily, there are tools that allow you to automate many parts of this process. 

This repository takes on the topic of incrementally updating a ML model as new data becomes available. It mainly leans on three nifty tools, being Kafka, Airflow, and MLFlow. 
