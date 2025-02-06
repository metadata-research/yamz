from app.term import term_blueprint as term
from app.term.models import Term, Tag
from app.term.forms import EmptyForm
from app import db
from flask import render_template, request, current_app, session
from app.utilities import Pager
from sqlalchemy import desc


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
                .paginate(page=page, per_page=per_page, error_out=False)
        )
    else:
        term_list = (
            Term.query.filter_by(status="published")
            .order_by(Term.term_string.asc())
                .paginate(page=page, per_page=per_page, error_out=False)
        )

    pager = Pager(term_list, page, per_page, Term.query.count())

    return render_template(
        "term/list_terms.jinja",
        term_list=term_list.items,
        sort_type=sort_type,
        sort_order=sort_order,
        pager=pager,
    )

# @term.route("/list/alphabetical/<letter>")")


@term.route("/list/alphabetical/top")
def list_top_terms_alphabetical():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]

    if session.get("portal_tag"):
        query_result = (
            db.session.query(Term.term_string, db.func.count(Term.term_string))
            .join(Term.tags)
            .filter(Tag.value == session.get("portal_tag"))
            .group_by(Term.term_string)
            .order_by(Term.term_string.asc())
        )
    else:
        query_result = (
            db.session.query(Term.term_string, db.func.count(Term.term_string))
            .filter_by(status="published")
            .group_by(Term.term_string)
            .order_by(Term.term_string.asc())
        )

    pager = query_result.paginate(
        page=page, per_page=per_page, error_out=False)
    term_list = pager.items

    tag_list = Tag.query.order_by(Tag.value.asc())
    return render_template(
        "term/list_top_terms.jinja", term_list=term_list, pager=pager, tag_list=tag_list, portal_tag=session.get("portal_tag")
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
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    term_list = pager.items

    return render_template(
        "term/terms_by_tag.jinja",
        term_list=term_list,
        pager=pager,
        tag_id=tag_id,
        tag=tag.value,
    )


@term.route("/list/tag/value/<tag_value>")
def terms_by_tag_value(tag_value):
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["TERMS_PER_PAGE"]
    tag = Tag.query.filter_by(value=tag_value).first()
    term_list = Term.query.filter(Term.tags.any(value=tag_value)).order_by(
        Term.term_string
    )
    tag_list = Tag.query.order_by(Tag.value.asc())
    return render_template(
        "term/terms_by_tag_value.jinja",
        term_list=term_list,
        tag=tag,
        tag_list=tag_list,
    )


@term.route("/list/tag/value/<tag_value>/detail")
def terms_by_tag_value_detail(tag_value):
    tag = Tag.query.filter_by(value=tag_value).first()
    selected_terms = Term.query.filter(Term.tags.any(value=tag_value)).order_by(
        Term.term_string
    )
    return render_template("term/terms_by_tag_value_detail.jinja", tag=tag, selected_terms=selected_terms, form=EmptyForm())


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
