import click

from sqlalchemy_utils import database_exists, create_database

from vidme.app import create_app
from vidme.extensions import db
from vidme.blueprints.user.models import User

# create an app context for the database connection
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
                help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()
    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)

    return None


@click.command()
def seed():
    """
    Seed the database with an initial user. The username, email and password
    are taken from the app config.

    :return: User instance
    """

    params = {
        'role': 'admin',
        'email': app.config['SEED_ADMIN_EMAIL'],
        'username': app.config['SEED_ADMIN_USERNAME'],
        'password': app.config['SEED_ADMIN_PASSWORD']
    }

    return User(**params).save()


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
                help='Create a test db too?')
@click.pass_context
def reset(ctx, with_testdb):
    """
    Init and seed the database automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed)
    
    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset)