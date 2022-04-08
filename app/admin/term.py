import re, enum
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


ref_regex = re.compile("#\{\s*(([gstkm])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")

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
            new_tag = tag[2]
            new_tag = new_tag[2:]
            tag = tagstart + tag[2] + tag[3] + "}"
            if not tag == "#{g: xqGCW | h1619}":
                end = definition.find(tag) + len(tag)
                excerpt = definition[start:end]
                excerpt = excerpt.replace("\n", "")
                excerpt = excerpt.replace("\n\n", "")
                # excerpt = excerpt[: excerpt.find(tag) - 1]
                print(term.term_string + " parent id " + str(term.id) + ":")
                print(tag)
                print(new_tag)
                if excerpt != "":
                    print(excerpt)
                    print("------------------------")
                start = end
        start = 0


class status(enum.Enum):
    archived = (1, "archived")
    published = (2, "published")
    draft = (3, "draft")


def splitTerms():
    terms = findGCW()
    print("total gcw = " + str(terms.count()))
    start = 0
    end = 0
    for term in terms:
        term.status = "archived"
        definition = term.definition
        term_g = g_regex.findall(term.definition)
        for tag in term_g:
            new_tag = tag[2]
            new_tag = new_tag[2:]
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
                other_tag = Tag.query.filter_by(value=new_tag).first()
                child_term.tags.append(gcwTag)
                if other_tag:
                    child_term.tags.append(other_tag)
                print("Added GCW tag")
                print("Added" + tag)
            term.add_child_relationship(child_term, "extractedFrom")
            db.session.commit()
        start = 0


def removeTagTerms_strings():
    terms = Term.query.filter(Term.term_string.startswith("#{g: xq"))
    for term in terms:
        db.session.delete(term)
        db.session.commit()
        print(term.term_string)


def tagOtherTerms():
    terms = Term.query
    for term in terms:
        term_ref = g_regex.findall(term.definition)
        for tag in term_ref:
            new_tag = tag[2]
            new_tag = new_tag[2:]
            tag = tagstart + tag[2] + tag[3] + "}"
            if not tag == "#{g: xqGCW | h1619}":
                tag_row = Tag.query.filter_by(value=new_tag).first()
                # print("to be tagged with" + new_tag)
                if not tag_row is None:
                    if not term.status.value == status.archived.value:
                        if not Tag.query.filter_by(value=new_tag).first() in term.tags:
                            definition = term.definition.replace(tag, "")
                            term.tags.append(tag_row)
                            term.definition = definition
                            term.save()

                            print("added tag " + new_tag)
                            print(term.term_string)
                            print(definition)
                            print("_______________________________________________")
                        # term.tags.append(tag_row)
                        # term.save()
                        # else:
                        #    print("tag already exists")
                    # else:
                    #   print("archived term not added")
                    # term.tags.append(tag_row)
                    # term.save()
                    # print(definition)

def clean_tags():
    terms = Term.query
    for term in terms:
        term_ref = g_regex.findall(term.definition)
        for tag in term_ref:
            tag_ref = tagstart + tag[2] + tag[3] + "}"
            term_tag = tag[2].replace("xq", "")
            if not "ambiguous" in tag_ref:
                if term_tag in str(term.tags):
                    print("strip " + tag_ref)
                    term.definition = term.definition.replace(tag_ref, "")
                    print(term.definition)
                    db.session.add(term)
    db.session.commit()
                    
                
                    
                
    