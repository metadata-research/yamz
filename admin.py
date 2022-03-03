import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update

from app import create_app
from app.term.models import Term
from app.user.models import User

from app.admin.data_io import *


app = create_app()
app.app_context().push()

db = SQLAlchemy(app)

create_app()


@click.group()
def cli():
    pass


@click.command()
def initdb():
    db.create_all()
    click.echo("Initialized the database")


@click.command()
def dropdb():
    click.echo("Dropped the database")


@click.command()
def transfer():
    click.echo("Transfer votes")


@click.command()
def addusers():
    add_users()


@click.command()
def addterms():
    add_terms()


@click.command()
def addall():
    add_users()
    add_terms()


cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(transfer)
cli.add_command(addusers)
cli.add_command(addterms)
cli.add_command(addall)

if __name__ == "__main__":
    cli()
