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
ixuniq = "xq"
ixqlen = len(ixuniq)
tagstart = "#{"  # final space is important


# find all the term definitions that contain the old style tags
def get_tagged_terms():
    return Term.query.filter(Term.definition.contains("#{"), Term.status == "published")


def list_tags_in_definition():
    # get all terms with the tag #{t
    linked_terms = get_tagged_terms()
    start, end = 0, 0
    # iterate through all the defintions with each loop extracting the tags
    for term in linked_terms:
        definition = term.definition

        # find all the tags in the definition
        term_tags = ref_regex.findall(definition)

        # print the term and the tags
        print("term string: " + term.term_string)

        # list all the tags in the definition
        for tag in term_tags:

            # isolate the id of the term that is a tag
            term_id = tag[3][3:]

            # isolate the tag value
            tag_string = tag[2]

            # build the tag string to replace (the old style tag)
            tag_to_replace = tagstart + tag[0] + " " + tag[2] + tag[3] + "}"

            # build the replacement URL
            replacement_url = '['+ tag_string + ']' + '(https://n2t.net/99152/' + term_id + ')'

            if tag_to_replace.startswith("#{t: "):

                #print("replace " + tag_to_replace + " with " + replacement_url)
                definition = definition.replace(tag_to_replace, replacement_url)
                term.definition = definition
                print(term.definition)
                

        print()

    print("total found: {}".format(linked_terms.count()))


# add the commands to the cli
@click.group()
def tag():
    pass


# register each command to respond to python tag.py command
@click.command()
def listtags():
    list_tags_in_definition()


tag.add_command(listtags)

if __name__ == "__main__":
    tag()
