from flask import render_template
from app.term.models import Relationship, Term, Tag


def findGCW():
    # first get all terms with the tag #{g: xqGCW | h1619}
    terms = Term.query.filter(Term.definition.contains("#{g: xqGCW | h1619}"))
    return terms


def tagGCW():
    # first get all terms with the tag #{g: xqGCW | h1619}
    terms = findGCW()
    gcwTag = Tag.query.filter_by(value="GCW").first()

    for term in terms:
        term.tags.append(gcwTag)
        term.save()

    print(terms.count())
