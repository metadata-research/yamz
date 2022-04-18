from app.term import term_blueprint as term
from app.term.forms import *
from app.term.models import *
from app.utilities import *
from flask import (
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import desc


@term.before_request
def before_request():
    g.search_form = SearchForm()


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


@term.app_template_filter("as_contributor_link")
def as_link(contributor):
    if contributor is None:
        return ""
    elif contributor.orcid and contributor.orcid != "nil":
        return '<a href="https://orcid.org/{}">{}</a>'.format(
            contributor.orcid, contributor.full_name
        )
    else:
        return '<a href="mailto:{}">{}</a>'.format(
            contributor.email, contributor.full_name
        )


@term.app_template_filter("format_date")
def format_date(date):
    return date.strftime("%Y.%m.%d")


@term.app_template_filter("format_score")
def format_score(score):
    pass


@term.route("ark:/99152/<concept_id>")
@term.route("/ark/<concept_id>")
def display_term(concept_id):
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    if selected_term is None:
        abort(404)
    form = EmptyForm()
    comment_form = CommentForm()
    comments = selected_term.comments.order_by(Comment.modified.desc())
    return render_template(
        "term/display_term.jinja",
        selected_term=selected_term,
        form=form,
        comments=comments,
        comment_form=comment_form,
    )


@term.route("/id/<term_id>")  # change concelpt id to ark
def display_term_by_id(term_id):
    form = EmptyForm()
    selected_term = Term.query.get_or_404(term_id)
    return redirect(url_for("term.display_term", concept_id=selected_term.concept_id))


@term.route("/alternates/<term_string>")  # change concelpt id to ark
def show_alternate_terms(term_string):
    form = EmptyForm()
    include = request.args.get("include", "published")
    if "published" in include:
        selected_terms = Term.query.filter_by(
            term_string=term_string, status="published"
        )
    else:
        selected_terms = Term.query.filter_by(term_string=term_string)
    # selected_terms = published_terms.union(all_terms)

    return render_template(
        "term/display_terms.jinja",
        selected_terms=selected_terms,
        form=form,
        alternatives_for_string=term_string,
        headline="Alternate Definitions " + "for " + term_string,
    )


@term.route("/contribute/create", methods=["GET", "POST"])
@login_required
def create_term():
    form = CreateTermForm()
    if form.validate_on_submit():
        if db.session.query(Term.ark_id).first() is None:
            last_ark_id = 0
        else:
            last_ark_id = db.session.query(db.func.max(Term.ark_id)).scalar()
        ark_id = int(last_ark_id) + 1
        shoulder = current_app.config["SHOULDER"]
        naan = current_app.config["NAAN"]
        term_string = form.term_string.data.strip()
        owner_id = current_user.id
        definition = form.definition.data
        examples = form.examples.data
        concept_id = shoulder + str(ark_id)

        new_term = Term(
            ark_id=ark_id,
            shoulder=shoulder,
            naan=naan,
            owner_id=owner_id,
            term_string=term_string,
            definition=definition,
            examples=examples,
            concept_id=concept_id,
        )
        new_term.save()
        return redirect(url_for("term.display_term", concept_id=new_term.concept_id))

    return render_template("term/create_term.jinja", form=form)


@term.route("/contribute/edit/<concept_id>", methods=["POST"])
@login_required
def edit_term(concept_id):
    form = EditTermForm()
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    if form.validate_on_submit():
        selected_term.term_string = form.term_string.data.strip()
        selected_term.definition = form.definition.data
        selected_term.examples = form.examples.data
        selected_term.update()
        # flash("Term updated.")
        return redirect(url_for("term.display_term", concept_id=concept_id))
    else:
        form.term_string.data = selected_term.term_string
        form.definition.data = selected_term.definition
        form.examples.data = selected_term.examples
        return render_template("term/edit_term.jinja", form=form)


@term.route("/contribute/delete/<concept_id>", methods=["POST"])
@login_required
def delete_term(concept_id):
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    if selected_term is None:
        abort(500)
    if selected_term.owner_id == current_user.id or current_user.is_administrator:
        selected_term.delete()
        flash("Term deleted.")
    else:
        flash("You are not authorized to delete this term.")
    return redirect(url_for("term.list_terms"))


# here we are using term id because the key is better as an integer and we don't have to look it up
# we should probably decide if we are going to use the concept id or the term id
# for now it has to be like this because of the seaice db schema
@term.route("comment/<term_id>", methods=["POST"])
@login_required
def add_comment(term_id):
    form = CommentForm()
    if form.validate_on_submit():
        owner_id = current_user.id
        term_id = term_id
        comment_string = form.comment_string.data

        new_comment = Comment(
            owner_id=owner_id, term_id=term_id, comment_string=comment_string
        )
        new_comment.save()

        return redirect(url_for("term.display_term_by_id", term_id=term_id))
    return redirect(url_for("term.display_term_by_id", term_id=term_id))


# TODO: filter by published status
@term.route("/search")
def search():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]
    sort_type = "search"
    search_terms = g.search_form.q.data
    search_terms = " & ".join(search_terms.split(" "))

    term_list = (
        Term.query.filter(Term.__ts_vector__.match(search_terms))
        # .filter(Term.status != status.deleted)
        .paginate(page, per_page, False)
    )

    # pager = Pager(term_list, page, per_page, len(term_list.items))
    next_url = (
        url_for("term.search", q=search_terms, page=term_list.next_num)
        if term_list.has_next
        else None
    )
    prev_url = (
        url_for("term.search", q=search_terms, page=term_list.prev_num)
        if term_list.has_prev
        else None
    )
    return render_template(
        "term/search_results.jinja",
        term_list=term_list.items,
        sort_type=sort_type,
        search_terms=search_terms,
        next_url=next_url,
        prev_url=prev_url,
    )


@term.route("/list")
def list_terms():
    return redirect(url_for("term.list_top_terms_alphabetical"))


@term.route("/list/alphabetical")
def list_alphabetical():
    sort_type = "alphabetical"
    sort_order = request.args.get("order", "ascending")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]

    if sort_order == "descending":
        term_list = (
            Term.query.filter_by(status="published")
            .order_by(Term.term_string.desc())
            .paginate(page, per_page, False)
        )
    else:
        term_list = (
            Term.query.filter_by(status="published")
            .order_by(Term.term_string.asc())
            .paginate(page, per_page, False)
        )

    pager = Pager(term_list, page, per_page, Term.query.count())

    return render_template(
        "term/list_terms.jinja",
        term_list=term_list.items,
        sort_type=sort_type,
        sort_order=sort_order,
        pager=pager,
    )


# @term.route("/list/alphabetical/<letter>")
@term.route("/list/alphabetical/top")
def list_top_terms_alphabetical():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]

    query_result = (
        db.session.query(Term.term_string, db.func.count(Term.term_string))
        .filter_by(status="published")
        .group_by(Term.term_string)
        .order_by(Term.term_string.asc())
    )

    pager = query_result.paginate(page, per_page, False)
    term_list = pager.items

    return render_template(
        "term/list_top_terms.jinja", term_list=term_list, pager=pager
    )


# @term.route("/list/alphabetical/<letter>")


@term.route("/list/tag/<int:tag_id>")
def list_terms_by_tag(tag_id):
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]
    tag = Tag.query.get_or_404(tag_id)
    pager = (
        Term.query.filter(Term.tags.any(id=tag_id))
        .order_by(Term.term_string)
        .paginate(page, per_page, False)
    )
    term_list = pager.items

    return render_template(
        "term/terms_by_tag.jinja",
        term_list=term_list,
        pager=pager,
        tag_id=tag_id,
        tag=tag.value,
    )


@term.route("/list/score")
def list_score():
    term_list = (
        db.session.query(Term)
        .filter(Term.term_vote != 0)
        .order_by(desc(Term.term_vote), Term.term_string)
        .limit(current_app.config["TERMS_PER_PAGE"])
    )
    return render_template(
        "term/highscore_terms.jinja", term_list=term_list, sort_type="high score"
    )


@term.route("/list/recent")
def list_recent():
    term_list = Term.query.order_by(Term.modified.desc()).limit(
        current_app.config["TERMS_PER_PAGE"]
    )
    return render_template(
        "term/highscore_terms.jinja", term_list=term_list, sort_type="recent"
    )


@term.route("/tag/create", methods=["GET", "POST"])
def create_tag():
    tag_form = TagForm()
    if tag_form.validate_on_submit():
        tag_category = tag_form.category.data
        tag_value = tag_form.value.data
        tag_description = tag_form.description.data

        tag = Tag.query.filter_by(name=tag_category, value=tag_value).first()
        if tag is None:
            new_tag = Tag(
                name=tag_category, value=tag_value, description=tag_description
            )
            new_tag.save()
            return redirect(url_for("term.list_tags"))
        else:
            flash("Tag already exists")
            return redirect(url_for("term.edit_tag, tag_id=tag.id"))

    else:
        return render_template("tag/create_tag.jinja", form=tag_form)


@term.route("tag/edit/<int:tag_id>", methods=["GET", "POST"])
@login_required
def edit_tag(tag_id):
    tag_form = TagForm()
    tag = Tag.query.get_or_404(tag_id)
    if tag_form.validate_on_submit():
        tag.category = tag_form.category.data
        tag.value = tag_form.value.data
        tag.description = tag_form.description.data
        tag.save()
        flash(
            'Tag updated.  <small>[<a href="'
            + url_for("term.list_tags")
            + '">Return to list]</a></small>'
        )
        return redirect(url_for("term.edit_tag", tag_id=tag_id))
    tag_form.category.data = tag.category
    tag_form.value.data = tag.value
    tag_form.description.data = tag.description
    return render_template("tag/edit_tag.jinja", form=tag_form)


@term.route("/tag/delete/<int:tag_id>", methods=["GET", "POST"])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.delete()
    return redirect(url_for("term.list_tags"))


@term.route("tag/list")
def list_tags():
    tags = Tag.query.order_by(Tag.value)
    return render_template("tag/list_tags.jinja", tags=tags)


@term.route("track/<concept_id>", methods=["POST"])
@login_required
def track_term(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        tracked_term = Term.query.filter_by(concept_id=concept_id).first()
        tracked_term.track(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))
    return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("untrack/<concept_id>", methods=["POST"])
@login_required
def untrack_term(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        tracked_term = Term.query.filter_by(concept_id=concept_id).first()
        tracked_term.untrack(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("/vote/up/<concept_id>", methods=["POST"])
@login_required
def vote_up(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        selected_term = Term.query.filter_by(concept_id=concept_id).first()
        selected_term.up_vote(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("/vote/down/<concept_id>", methods=["POST"])
@login_required
def vote_down(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        selected_term = Term.query.filter_by(concept_id=concept_id).first()
        selected_term.down_vote(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("/vote/zero/<concept_id>", methods=["POST"])
@login_required
def vote_zero(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        selected_term = Term.query.filter_by(concept_id=concept_id).first()
        selected_term.zero_vote(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("/vote/remove/<concept_id>", methods=["POST"])
@login_required
def remove_vote(concept_id):
    form = EmptyForm()
    if form.validate_on_submit():
        selected_term = Term.query.filter_by(concept_id=concept_id).first()
        selected_term.remove_vote(current_user)
        return redirect(url_for("term.display_term", concept_id=concept_id))


@term.route("/test/<concept_id>")
@login_required
def test_term(concept_id):
    term = Term.query.filter_by(concept_id=concept_id).first()
    return render_template("term/test.jinja", term=term)


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
