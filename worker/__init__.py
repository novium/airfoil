from celery import Celery

celery = Celery(__name__, broker='amqp://guest:guest@broker:5672',backend='rpc://')