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
def list():
    print_file_list()


@click.command()
@click.argument("file_no")
def info(file_no):
    show_file_info(file_no)


@click.command()
@click.argument("file_no")
def terms(file_no):
    load_terms_from_json(file_no)


cli.add_command(list)
cli.add_command(info)
cli.add_command(terms)

if __name__ == "__main__":
    cli()
