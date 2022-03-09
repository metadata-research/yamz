import click
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from app.admin.data_io import *
from app.admin.user import *
from app.admin.term import *

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


@click.command()
def taggcw():
    tagGCW()


@click.command()
def printinner():
    printInner()


@click.command()
def splitterms():
    splitTerms()


@click.command()
def tagotherterms():
    tagOtherTerms()


@click.command()
def removetagterms():
    removeTagTerms_strings()


cli.add_command(addall)
# first do:
# flask db init
# flask db migrate -m "initial migration"

cli.add_command(addusers)  # 1
cli.add_command(setsuperuser)  # 2
cli.add_command(addterms)  # 3
cli.add_command(transfertags)  # 4


cli.add_command(printinner)  # test the split terms function for GCW terms
cli.add_command(splitterms)  # 5 actually split the terms

cli.add_command(tagotherterms)

# not used in initial migration
cli.add_command(transfertracking)
cli.add_command(transfervotes)
cli.add_command(removetagterms)

if __name__ == "__main__":
    cli()
