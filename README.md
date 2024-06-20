# seepalaya-new-dockerized
This project takes new seepalaya app ( backend frontend etc ) and dockerize. 

Django backend talks to postgres.
Backend talks to broker rabbitmq broker if it has to run some task by queueing them. 
Celery which is exact copy of backend runs tasks in queue sortof as background. 
Searching and indexing is done through elastic search. 


