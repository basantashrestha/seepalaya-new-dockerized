## Overview
Backend system for Seepalaya, which is implemented with Django and Django Rest Framework. The API endpoints are documented
with Swagger which can be accessed at `/api/schema`. We have used hacksoft’s django style guide which serves our purpose of reducing code coupling, enhancing maintainability & providing a way to reason about the code in a simple manner. The full style guide can be read [here](https://github.com/HackSoftware/Django-Styleguide). It covers almost all the things that need to be kept in mind while dealing with this codebase.

## Technology Used
    - Django, Django Rest Framework
    - Celery
    - RabbitMQ
    - PostgreSQL
    - Elasticsearch

**Note:** This docs focuses on the core code part of the project and setting it up for development on a local machine.For the containerized version and the setting up process in the server or through docker, please consult the readme file [here](https://git2023.olenepal.org/olenepal/seepalaya-new-dockerized.git)

## Prerequisites
At the time of initial setup and development, the project was tested and worked on with the following specified versions.
- Python 3.11.4
- Postgres 15.5
- RabbitMQ 3.13.2
- ElasticSearch 7.12.1

## Directory Structure
```

```

## Setup
1. Clone the github repo.
    ```
    git clone https://git2023.olenepal.org/olenepal/seepalaya-new-backend.git
    ```
2. Switch to the development branch `dev`.
    ```sh
    git checkout dev
    ```
3. Navigate to the working directory.
    ```sh
    cd seepalaya-new-backend
    ```
4.  Create a new virtual environment and activate it.
    ```sh
    python -m venv env
    ```
    ```sh
    env/scripts/activate
    ```
5. Install the required dependencies from the requiremnts_dev.txt file.
    ```sh
    pip install -r src/requirements/requirements_dev.txt
    ```
6. Create a new directory logs in the src directory.
7. On one terminal run the django server.
    ```sh
    python manage.py runserver
    ```
    On another terminal navigate to src and run the celery worker.
    ```sh
    celery -A config worker --loglevel=info -P eventlet
    ```
    Make sure the postgres database is running at port 5432 and the databases `courses` and `celery_tasks` had been created.
8. The server should now be running and accessible at [localhost:8000](localhost:8000). Navigate to [localhost:8000/api/schema](localhost:8000/api/schema) to explore the existing API endpoints.


## Start Guide

Start working on the project without affecting the main branches.
As of now, only the dev branch is used. Any new feature should be developed on a new branch and then merged with the dev branch afterwards.

### To create a new branch

```sh
git checkout -b your-branch-name
```

### To push the branch to remote git server

```sh
git push -u origin your-branch-name
```

### To merge to the dev branch

**1. First checkout to dev branch**

```sh
git checkout dev
```

**2. Merge changes from your branch**

```sh
git merge your-branch-name
```

**3. Push changes**

```sh
git push
```

**4. Checkout back to your branch**

```sh
git checkout your-branch-name
```


### running celery worker

Windows - `celery -A config worker --loglevel=info -P eventlet`

Linux - `celery -A config worker -l info`
