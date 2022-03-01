from app import app
import click

from app.user.models import User
from app.term.models import Term

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update


db = SQLAlchemy(app)


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
def zeroorcids():
    users = User.query.filter(User.orcid == "nil").all()

    stmt = update(users).where(users.orcid == "nil").values(orcid="")
    db.session.execute(stmt)


cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(transfer)
cli.add_command(zeroorcids)

if __name__ == "__main__":
    cli()
