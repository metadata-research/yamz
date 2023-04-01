import os
import pandas
from app import db
from app.term.models import Term, TermSet
from app.user.models import User
from app.term.helpers import get_ark_id
from flask import current_app

"""a dictionary of sources to be used in the term set.
The key is the source name as it appears in the json file
"""
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


def print_termset_list():
    """print a list of term sets in the database by name and id"""
    termsets = TermSet.query.order_by(TermSet.name)
    for termset in termsets:
        print("[{id}] {termset}".format(id=termset.id, termset=termset.name))


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
    return file, dataframe_from_json


def show_file_info(file_no) -> pandas.DataFrame:
    """Print the contents of a json file by index in 'json_files'

    Args: file_no (string): the file number to load passed as an argument to the cli
    """
    dataframe_from_json = get_file_info(file_no)
    print(dataframe_from_json)


def load_terms_from_json(file_no) -> list:
    """Extract the terms and definitions from a json file by index in 'json_files'
    as well as the source and division. In this case only the first since it is the same for every entry
    Print to the console and return the list of terms and definitions
    Args:
        file_no (string): the file number to load passed as an argument to the cli

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


def create_term_set(name, source, owner_email) -> TermSet:
    """a component function to create a termset in the database to organize imports

    Args:
        set_name (string): the name that will appear in the term set list
        set_description (string): Arbitrary description of the term set
        source (string): the vocabulary source as in the sources array
        owner_email (string): the email of the owner to be used as the contributor.
            must exist in the db already
    """

    set_name = name
    set_source = source
    user = User.query.filter_by(email=owner_email).first(
    )  # take the first if multiple accounts match
    set_user_id = user.id
    """ ark_id = get_ark_id()
    Right now the ark_id is a placeholder if we decide to assign
    arks to sets. Right now get_ark_id based on the last index of the terms table
    so we would need to implement a global way to generate ark_ids to use it here.
    """

    new_set = TermSet(
        name=set_name,
        source=set_source,
        user_id=set_user_id,
        # description=set_description,
    )
    new_set.save()
    print("created term set: " + new_set.name)
    print("id:", new_set.id)
    print("user:", user)
    return new_set


def delete_term_set(termset_id) -> None:
    """delete a termset from the database
    Args:
        termset_id (string): the id of the termset to be deleted
    """
    termset = TermSet.query.get(termset_id)
    print("deleting term set:", termset.name)
    termset.delete()


def insert_terms(termset, data_frame) -> None:
    """insert terms from a json file into the database"""
    term_list = data_frame["Terms"]
    for term in term_list:
        try:
            new_term = insert_term(
                term["Term"], term["Definition"], termset.user_id)
        except Exception as e:
            print(e)
            print("failed to insert term:", term["Term"])
            print("skipping")
        else:
            print("inserted term:", term["Term"])
            termset.terms.append(new_term)


def insert_term(term, definition, user_id) -> Term:
    """insert a single term into the database

    Args:
        term (string): the term to be inserted
        definition (string): the definition of the term
        user_id (string): the id of the user to be used as the contributor
    """

    term_string = term
    term_definition = definition
    ark_id = get_ark_id()
    shoulder = current_app.config["SHOULDER"]
    naan = current_app.config["NAAN"]
    ark = shoulder + str(ark_id)
    owner_id = user_id

    new_term = Term(
        ark_id=ark_id,
        shoulder=shoulder,
        naan=naan,
        owner_id=owner_id,
        term_string=term_string,
        definition=term_definition,
        concept_id=ark,
        # examples=examples,
    )
    new_term.save()
    return new_term

# this is a rough draft of the import function


def import_terms() -> None:
    """import terms from a json file into the database"""
    print("Type the number of the file to import and press enter.")
    print_file_list()
    file_no = int(input("file number: "))
    file, dataframe_from_json = get_file_info(file_no)
    print("File to import:", file)
    proceed = input("Proceed? (y/n): ")
    if not proceed == "y":
        print("exiting")
        exit()
    else:
        print("importing terms...")
        set_name = SOURCES[dataframe_from_json["Source Name"][0]]
        set_source = file
        term_set = create_term_set(
            set_name, set_source, "yamz.development@gmail.com")
        insert_terms(term_set, dataframe_from_json)
        print("import complete")
