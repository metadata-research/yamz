import os
import pandas
from app import db
from app.term.models import Term, TermSet
from app.user.models import User
from app.term.helpers import get_ark_id
from flask import current_app

"""a dictionary of sources to be used in the term set"""
SOURCES = {
    "Helio Ontology": "Helio Ontology",
    "Heliophysics Event Knowledge Base": "HEK",
    "NASA CCMC, SWEET, SPASE": "NASA CCMC, SWEET, SPASE",
    "NASA Heliophysics Vocabulary": "NASA Heliophysics Vocabulary",
    "Space Weather Glossary": "NOAA SWPC SpWx Glossary",
    "Space Weather Glossary": "SET SpWx Glossary",
    "ESA Space Weather Glossary": "ESA SpWx Glossary",
    "Unified Astronomy Thesaurus": "UAT",
    "AGU Index Terms": "AGU Index Terms",
}

"""lines to use for formatting"""
pound_line = "#" * 80
dash_line = "-" * 80


"""get a list of json files in the uploads/helio directory
"""
cwd = os.getcwd()  # current working directory
uploads_dir = os.path.join(cwd, "uploads", "helio")  # uploads/helio
json_files = [f for f in os.listdir(uploads_dir) if f.endswith(".json")]


def print_file_list() -> None:
    """print a numbered list of json files in the uploads/helio directory
    """
    count = 0
    for filename in json_files:
        count += 1
        print("[{count}] {filename}".format(count=count, filename=filename))


def get_file_info(file_no) -> pandas.DataFrame:
    """load json file by index in 'json_files'
    and return pandas content info
    Args:
        file_no (string): the file number to load passed as an argument to the cli
        python helio.py info 10
    """
    file = json_files[int(file_no) - 1]
    filepath = os.path.join(uploads_dir, file)
    dataframe_from_json = pandas.read_json(filepath)
    return dataframe_from_json


def show_file_info(file_no) -> pandas.DataFrame:
    """Print the contents of a json file by index in 'json_files'
    """
    dataframe_from_json = get_file_info(file_no)
    print(dataframe_from_json)


def load_terms_from_json(file_no) -> list:
    """Extract the terms and definitions from a json file by index in 'json_files'
    as well as the source and division. In this case only the first since it is the same for every entry
    Print to the console and return the list of terms and definitions
    Args:
        file_no (string): the file number to load passed as an argument to the cli
        python helio.py info 10

    Returns:
        list: Three lists of terms, sources, and divisions. Usually only one source
        but multiple divisions
    """
    json_dataframe = get_file_info(file_no)
    term_list = json_dataframe["Terms"]
    source = SOURCES[json_dataframe["Source Name"][0]]
    divisions = json_dataframe["Division"][0]

    print(pound_line)
    print("source:", source)
    print("divisions:", divisions)
    print(pound_line)
    for term in term_list:
        print("term:", term["Term"], "\n")
        print("definition:", term["Definition"])
        print(dash_line)
    return term_list, source, divisions


def create_term_set(set_name, set_description, owner_email) -> TermSet:
    """a component function to create a termset in the database to organize importso

    Args:
        set_name (string): the name that will appear in the term set list
        set_description (string): Arbitrary description of the term set
        source (string): the vocabulary source as in the sources array
        owner_email (string): the email of the owner to be used as the contributor.
            must exist in the db already
    """
    user = User.query.filter_by(email=owner_email).first(
    )  # take the first if multiple accounts match

    new_set = TermSet(
        user_id=user.id,
        source="upload",
        name=set_name,
        description=set_description,
    )
    new_set.save()
    return new_set


def insert_terms() -> None:
    """insert terms from a json file into the database"""
    term_list = load_terms_from_json()
    for term in term_list:
        insert_term(term["Term"], term["Definition"])


def insert_term(term, definition, user_email='jakkbl@gmail.com') -> None:
    """insert a single term into the database

    Args:
        term (string): the term to be inserted
        definition (string): the definition of the term
        user_email (string): the email of the owner to be used as the contributor.
    """
    user = User.query.filter_by(email=user_email).first()

    term_string = term
    definition = definition
    ark_id = get_ark_id()
    shoulder = current_app.config["SHOULDER"]
    naan = current_app.config["NAAN"]
    ark = shoulder + str(ark_id)
    owner_id = user.id

    new_term = Term(
        ark_id=ark_id,
        shoulder=shoulder,
        naan=naan,
        owner_id=owner_id,
        term_string=term_string,
        definition=definition,
        # examples=examples,
        concept_id=ark,
    )
    new_term.save()
