# VidMe - Movie Rental API
This is the back end for a movie rental service. This is a project in my ongoing journey to get better with python web development. The goal is to use docker, flask, a SQL database, and maybe even add redis to create a movie rental business.

In order to get set up, please run:

## Build and run the app
docker-compose up --build

Then access the API:

* Using Linux, Docker for Windows or Docker for Mac?

    Send requests to http://localhost:8000

* Using Docker Toolbox?

    Edit `config/settings.py` and switch `SERVER_NAME` from `localhost:8000` to `192.168.99.100:8000`
    Send requests to http://192.168.99.100:8000 