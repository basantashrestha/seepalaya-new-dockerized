# seepalaya-new-dockerized
This project takes seepalaya backend, frontend etc and dockerize it. 
Celery, rabbitmq and elasticsearch also added. 

## Communications between components: 
- Django backend can talk to postgres.
- Backend talks to broker rabbitmq broker if it has to run some task by queueing them. 
- Celery which is exact copy of backend runs tasks in queue. For example when delay is added. 
- Searching and indexing is done through elasticsearch. 


