import click
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from app.admin.helio import *
from app.admin.user import *
from app.admin.term import *

app = create_app()
app.app_context().push()

db = SQLAlchemy(app)


@click.group()
def cli():
    pass


@click.command()
def create():
    import_terms()


@click.command()
def deleteset():
    delete_term_set()

@click.command()
def deleteterms():
    delete_terms_in_termset()

@click.command()
@click.argument("file_no")
def info(file_no):
    show_file_info(file_no)


@click.command()
def list():
    print_file_list()


@click.command()
def setlist():
    print_termset_list()


cli.add_command(create)
cli.add_command(deleteset)
cli.add_command(deleteterms)
cli.add_command(info)
cli.add_command(list)
cli.add_command(setlist)

if __name__ == "__main__":
    cli()
