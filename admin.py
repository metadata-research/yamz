<<<<<<< HEAD
from app import app
import click

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

from app.term.models import Term


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
def transfer_votes():
    click.echo("Transfer votes")


cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(transfer_votes)

if __name__ == "__main__":
    cli()
=======
>>>>>>> parent of c3bae07... add relationship and admin module
