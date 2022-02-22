from flask import render_template
from app.term import term_blueprint as term
from app.term.models import Term
from app.term.format import *

# these filters are to duplicate the functionality of seaice.pretty but might be replaced with a markdown editor
@term.app_template_filter("convert_line_breaks")
def convert_line_breaks(string):
    string = string.replace("\n", "\n<br>")
    return string


# this is taken largely as is from seaice.pretty since we're going to use a comoponent instead
@term.app_template_filter("format_tags")
def format_tags(string):
    def references_to_html(match):
        """Input a regular expression match and return the reference as Text.

        A reference has the form #{ reftype: humstring [ | IDstring ] }
        - reftype is one of
            t (term), g (tag), s (section), m (mtype), k (link)
            #t (term), g (tag), e (element), v (value), m (mtype), k (link)
        - humstring is the human-readable equivalent of IDstring
        - IDstring is a machine-readable string, either a concept_id or,
            in the case of "k" link, a URL.
        - Note that the reference should have been normalized before being
            stored in the database. (xxx check if that's true for API uploading)

        :param match: Regular expression match.
        :type match: re.MatchObject
        """
        (rp) = match.groups()  # rp = ref parts, the part between #{ and }
        # we want subexpressions 1, 2, and 4
        reference_type, display_string, id_string = rp[1], rp[2], rp[4]
        if not reference_type:
            reference_type = "t"
        if not display_string and not id_string:  # when empty
            return ""

        if reference_type == "g":
            # yyy in theory don't need to check before removing uniquerifier string
            #     as all normalized tag ids will start with it
            if display_string.startswith(ixuniq):  # stored index "uniquerifier" string
                display_string = display_string[
                    ixqlen:
                ]  # but remove "uniquerifier" on display
            return "#" + display_string

        if reference_type == "k":  # an external link (URL)
            if display_string and not id_string:  # assume the caller
                id_string = display_string  # mixed up the order
            if not display_string:  # if no humanstring
                display_string = id_string  # use link text instead
            if not id_string.startswith("https:"):
                id_string = "https://" + id_string
            return "%s (%s)" % (display_string, id_string)

        if display_string.startswith("---"):  # EndRefs
            if display_string.startswith("---e"):
                return "\nElements: "
            if display_string.startswith("---v"):
                return "\nValues: "
            if display_string.startswith("---t"):
                return "\n "

        return display_string

    # (g, t, k, m) = rp[1:5]
    string = ref_regex.sub(lambda match: references_to_html(match), string)
    string = string.replace("##", "#")  # escape mechanism
    string = string.replace("&&", "&")
    return string


@term.route("/<concept_id>")  # change concelpt id to ark
def display_term(concept_id):
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    return render_template("term/display_term.jinja", selected_term=selected_term)
