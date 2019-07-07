# VidMe - Movie Rental API
As part of an ongoing journey to learn python web development the plan is to create a restful API for a movie rental business using flask, docker, stripe, and a postgres database. Currently, users can sign up, authenticate themselves, and access the billing API to do a number of things regarding subscribing to a plan, viewing billing info, and updating their billing information and plan. There's also a custom admin API to manage user accounts/subscriptions which will grow as more is added to the application. Future plans for this app are to maybe include redis and celery to allow for efficient emailing and of course adding the ability to rent/return movies.

If running locally make sure to check ```example.env``` to see what you need for the ```.env``` file and ```instance/settings.py.prod_example``` will show you values you would need for production for the ```instance/settings.py```


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
A custom CLI was built to make running common commands easier such as tests, flake8, and resetting/seeding the database. While the container is running, open a 2nd terminal(or run ```docker-compose up -d```) and run ```docker-compose exec web vidme``` to see a list of commands.

## Tests
If running tests make sure that you've already ran the ```docker-compose exec web vidme db reset --with-testdb``` command or there will be no test database. Once thats set up run ```docker-compose exec web vidme test```. Coverage is currently at 84%.