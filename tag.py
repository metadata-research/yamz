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

# find all the term definitions that contain the old style tags
def get_tagged_terms():
    return Term.query.filter(Term.definition.contains("#{"), Term.status=="published")

def get_terms_with_links():
    return Term.query.filter(Term.definition.contains("#{t"), Term.status=="published")

# list all the term definitions that contain the old style tags
def list_tagged_terms():    
    tagged_terms = get_tagged_terms()

    # print the definitions of the terms with the old style tags
    for term in tagged_terms:
        print(term.term_string)
        print(term.definition)
    print("total found: {}".format(tagged_terms.count()))


def list_terms_with_links():    
    linked_terms = get_terms_with_links()

    for term in linked_terms:
        print(term.term_string)
        print(term.definition)
    print("total found: {}".format(linked_terms.count()))




# add the commands to the cli
@click.group()
def tag():
    pass


# register each command to respond to python tag.py command
@click.command()
def listtaggedterms():
    list_tagged_terms()

@click.command()
def listlinkedterms():
    list_terms_with_links()


tag.add_command(listtaggedterms)
tag.add_command(listlinkedterms)

if __name__ == "__main__":
    tag()
