# VidMe - Movie Rental API
This is the back end for a movie rental service. This is a project in my ongoing journey to get better with python web development. The goal is to use docker, flask, a SQL database, and maybe even add redis to create a movie rental business.


## Getting set up
### Build and run the app
In order to get set up, please run ```docker-compose up --build```
** you will only need to run --build the first time building the image, or any time a new package is added in requirements.txt **

### Set up the database
[Open a 2nd terminal]
Using the CLI run ```docker-compose exec web vidme db reset --with-testdb```

### Access the API

* Using Linux, Docker for Windows or Docker for Mac?

    Send requests to http://localhost:8000

* Using Docker Toolbox?

    Edit `config/settings.py` and switch `SERVER_NAME` from `localhost:8000` to `192.168.99.100:8000`
    Send requests to http://192.168.99.100:8000

## CLI
A custom CLI was built to make running common commands easier such as tests, flake8, and resetting/seeding the database. While the container is running, open a 2nd terminal and run ```docker-compose exec web vidme``` to see a list of commands.