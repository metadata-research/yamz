import re
from flask import render_template
from app.term.models import Relationship, Term, Tag
from app import db


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


###############################add other tag start here
g_regex = re.compile("#\{\s*(([g])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")
ixuniq = "xq"
ixqlen = len(ixuniq)
tagstart = "#{g: "  # final space is important


def printInner():
    terms = findGCW()
    start = 0
    end = 0
    for term in terms:
        definition = term.definition
        term_g = g_regex.findall(term.definition)
        for tag in term_g:
            tag = tagstart + tag[2] + tag[3] + "}"
            if not tag == "#{g: xqGCW | h1619}":
                end = definition.find(tag) + len(tag)
                excerpt = definition[start:end]
                excerpt = excerpt.replace("\n", "")
                excerpt = excerpt.replace("\n\n", "")
                # excerpt = excerpt[: excerpt.find(tag) - 1]
                print(term.term_string + " parent id " + str(term.id) + ":")
                print(tag)
                if excerpt != "":
                    print(excerpt)
                    print("------------------------")
                start = end
        start = 0


def splitTerms():
    terms = findGCW()
    start = 0
    end = 0
    for term in terms:
        definition = term.definition
        term_g = g_regex.findall(term.definition)
        for tag in term_g:
            tag = tagstart + tag[2] + tag[3] + "}"
            if not tag == "#{g: xqGCW | h1619}":
                end = definition.find(tag) + len(tag)
                excerpt = definition[start:end]
                excerpt = excerpt.replace("\n", "")
                excerpt = excerpt.replace("\n\n", "")
                print(term.term_string + "parent id " + str(term.id) + ":")
                print(excerpt)
                print("------------------------")
                start = end
                last_ark_id = db.session.query(db.func.max(Term.ark_id)).scalar()
                ark_id = int(last_ark_id + 1)
                shoulder = "h"
                naan = "99152"
                concept_id = shoulder + str(ark_id)
                child_term = Term(
                    term_string=term.term_string,
                    definition=excerpt,
                    ark_id=ark_id,
                    shoulder=shoulder,
                    naan=naan,
                    owner_id=1129,
                    concept_id=concept_id,
                )
                child_term.save()
                print(child_term.term_string + " added")
                db.session.refresh(child_term)
                gcwTag = Tag.query.filter_by(value="GCW").first()
                child_term.tags.append(gcwTag)
                print("Added GCW tag")
            term.add_child_relationship(child_term, "extractedFrom")
            db.session.commit()
        start = 0


def removeTagTerms():
    terms = Term.query.filter(Term.term_string.startswith("#{g: xq"))
    for term in terms:
        db.session.delete(term)
        db.session.commit()
        print(term.term_string)
