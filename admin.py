import click
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from app.admin.data_io import *
from app.admin.user import *

app = create_app()
app.app_context().push()

db = SQLAlchemy(app)


@click.group()
def cli():
    pass


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


@click.command()
def transfertracking():
    transfer_tracking()


@click.command()
def transfervotes():
    transfer_votes


@click.command()
def transfertags():
    transfer_tags()


@click.command()
@click.argument("email")
def setsuperuser(email):
    set_superuser(email)


cli.add_command(addusers)
cli.add_command(addterms)
cli.add_command(addall)
cli.add_command(transfertracking)
cli.add_command(transfervotes)
cli.add_command(transfertags)
cli.add_command(setsuperuser)

if __name__ == "__main__":
    cli()
