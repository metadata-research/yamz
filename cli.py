import click
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from app.admin.data_io import *
from app.admin.user import *
from app.admin.term import *

app = create_app()
app.app_context().push()

#db = SQLAlchemy(app)


@click.group()
def cli():
    pass


@click.command()
@click.argument("email")
def setsuperuser(email):
    set_superuser(email)


@click.command()
def exportterms():
    export_terms()


@click.command()
def refreshterms():
    refresh_terms()


@click.command()
def importlcsh():
    import_lcsh()


cli.add_command(setsuperuser)
cli.add_command(exportterms)
cli.add_command(refreshterms)
cli.add_command(importlcsh)

if __name__ == "__main__":
    cli()
