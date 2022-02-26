from flask import render_template, redirect, url_for, current_app, request
from flask_login import current_user, login_required
from app.term import term_blueprint as term
from app.term.models import *
from app.term.forms import *
from app.utilities import *


# these filters are to duplicate the functionality of seaice.pretty but might be replaced with a markdown editor
@term.app_template_filter("convert_line_breaks")
def convert_line_breaks(string):
    string = string.replace("\n", "\n<br>")
    return string


@term.app_template_filter("format_tags")
def format_tags(string):
    string = ref_regex.sub(lambda match: references_to_html(match), string)
    string = string.replace("##", "#")  # escape mechanism
    string = string.replace("&&", "&")
    return string


@term.app_template_filter("format_score")
def format_score(score):
    pass


@term.route("/<concept_id>")  # change concelpt id to ark
def display_term(concept_id):
    form = EmptyForm()
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    return render_template(
        "term/display_term.jinja", selected_term=selected_term, form=form
    )


@term.route("/alternates/<term_string>")  # change concelpt id to ark
def show_alternate_terms(term_string):
    form = EmptyForm()
    selected_terms = Term.query.filter_by(term_string=term_string)
    return render_template(
        "term/display_terms.jinja",
        selected_terms=selected_terms,
        form=form,
        alternatives_for_string=term_string,
    )


@term.route("/create", methods=["GET", "POST"])
@login_required
def create_term():
    form = CreateTermForm()
    if form.validate_on_submit():
        term_string = form.term_string.data
        definition = form.definition.data
        examples = form.examples.data
        new_term = Term(term_string, definition, examples)
        new_term.save()
        return redirect(url_for("term.display_term", concept_id=new_term.concept_id))
    return render_template("term/create_term.jinja", form=form)


@term.route("/list")
def list_terms():
    return redirect(url_for("term.list_alphabetical"))


@term.route("/list/alphabetical")
def list_alphabetical():
    sort_type = "alphabetical"
    sort_order = request.args.get("order", "ascending")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]

    if sort_order == "descending":
        term_list = Term.query.order_by(Term.term_string.desc()).paginate(
            page, per_page, False
        )
    else:
        term_list = Term.query.order_by(Term.term_string.asc()).paginate(
            page, per_page, False
        )

    pager = Pager(term_list, page, per_page, Term.query.count())

    return render_template(
        "term/list_terms.jinja",
        term_list=term_list.items,
        sort_type=sort_type,
        sort_order=sort_order,
        pager=pager,
    )


@term.route("track/<concept_id>", methods=["POST"])
@login_required
def track_term(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        tracked_term = Term.query.filter_by(concept_id=concept_id).first()
        tracked_term.track(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("untrack/<concept_id>", methods=["POST"])
@login_required
def untrack_term(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        term = Term.query.filter_by(concept_id=concept_id).first()
        term.untrack(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


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
        return tag_to_term_link(display_string, id_string)

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


def tag_to_term_link(display_string, concept_id):
    tag_term = Term.query.filter_by(concept_id=concept_id).first()
    if tag_term is None:
        term_link = display_string
        definition = ""
    else:
        definition = tag_term.definition
        term_link = '<a class="term-tag" container="body" data-bs-toggle="tooltip" data-bs-placement="top" title="{definition}" href="tag/{href}">{link_text}</a>'.format(
            href=display_string, link_text=display_string, definition=definition
        )  # or ../tag if tag is a separate module

    return term_link
