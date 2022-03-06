import re
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
                print(term.term_string + ":")
                # print(tag)
                if excerpt != "":
                    print(excerpt)
                    print("------------------------")
                start = end
        start = 0


g_regex = re.compile("#\{\s*(([g])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")
ixuniq = "xq"
ixqlen = len(ixuniq)
tagstart = "#{g: "  # note: final space is important
