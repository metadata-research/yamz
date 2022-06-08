import click
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from app.term.models import Term, Tag

app = create_app()
app.app_context().push()


db = SQLAlchemy(app)

# regular expression for finding tags
import re

ref_regex = re.compile("#\{\s*(([gstkm])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")


def list_tagged_terms():
    # find all the terms that have to old style tags
    yamz_tagged_terms = Term.query.filter(Term.definition.contains("#{"), Term.status=="published")

    # print the definitions of the terms with the old style tags
    for term in yamz_tagged_terms:
        print(term.term_string)
        print(term.definition)
    print(yamz_tagged_terms.count())


# add the commands to the cli
@click.group()
def tag():
    pass


# register each command to respond to python tag.py command
@click.command()
def listtaggedterms():
    list_tagged_terms()


tag.add_command(listtaggedterms)


if __name__ == "__main__":
    tag()
