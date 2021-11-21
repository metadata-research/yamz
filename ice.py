#! /usr/bin/env python
#
# ice - web frontend for SeaIce, based on the Python-Flask framework.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * The names of contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.# MIT License

import configparser
import re
import sys
from itertools import chain
import optparse
import flask_login as l
import psycopg2 as pgdb
import requests
from flask import Markup, flash, g, redirect, render_template, request, session, url_for

import seaice
from seaice.paginate import Pager


from pagination import getPaginationDetails


# Parse command line options. #
parser = optparse.OptionParser()

parser.description = """\
This program is a Python/Flask-based web frontend for the SeaIce metadictionary.
SeaIce is a database comprised of a set of user-defined, crowd-sourced terms and
relations. The goal of SeaIce is to develop a succinct and complete set of
metadata terms to register just about any type of file or data set. 'ice' is
distributed under the terms of the BSD license with the hope that it will be
# useful, but without warranty. You should have received a copy of the BSD
license with this program; otherwise, visit
http://opensource.org/licenses/BSD-3-Clause.
"""

parser.add_option(
    "--config",
    dest="config_file",
    metavar="FILE",
    help="User credentials for local PostgreSQL database. ",
    default=".seaice",
)

parser.add_option(
    "--credentials",
    dest="credentials_file",
    metavar="FILE",
    help="File with OAuth-2.0 credentials. (Defaults to `.seaice_auth`.)",
    default=".seaice_auth",
)

parser.add_option(
    "--deploy",
    dest="deployment_mode",
    help="Deployment mode, used to choose OAuth parameters in credentials file.",
    default="dev",
)

parser.add_option(
    "-d",
    "--debug",
    action="store_true",
    dest="debug",
    default=False,
    help="Start flask in debug mode.",
)

parser.add_option(
    "--role",
    dest="db_role",
    metavar="USER",
    help="Specify the database role to use for the DB connector pool. These roles "
    + "are specified in the configuration file (see --config).",
    default="default",
)


(options, args) = parser.parse_args()

# Figure out if we're in production mode.
config = configparser.ConfigParser()
config.read(".seaice_auth")
if config.has_option("production", "prod_mode"):
    prod_mode = config.getboolean("production", "prod_mode")
else:
    prod_mode = False  # default

# Setup flask application #
print("ice: starting ...")

db_config = None

try:
    db_config = seaice.auth.get_config(options.config_file)
    app = seaice.SeaIceFlask(
        __name__,
        db_user=db_config.get(options.db_role, "user"),
        db_password=db_config.get(options.db_role, "password"),
        db_name=db_config.get(options.db_role, "dbname"),
    )

except pgdb.DatabaseError as e:
    print("error: %s" % e, file=sys.stderr)
    sys.exit(1)


try:
    credentials = seaice.auth.get_config(options.credentials_file)

    google = seaice.auth.get_google_auth(
        credentials.get(options.deployment_mode, "google_client_id"),
        credentials.get(options.deployment_mode, "google_client_secret"),
    )

    orcid = seaice.auth.get_orcid_auth(
        credentials.get(options.deployment_mode, "orcid_client_id"),
        credentials.get(options.deployment_mode, "orcid_client_secret"),
    )

except OSError:
    print("error: config file '%s' not found" % options.config_file, file=sys.stderr)
    sys.exit(1)


app.debug = True
app.use_reloader = True
app.secret_key = credentials.get(options.deployment_mode, "app_secret")


# Session logins #

login_manager = l.LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = seaice.user.AnonymousUser

# Prescore terms #

# This will be used to check for consistency errors in live scoring
# and isn't needed until I implement O(1) scoring.

# print "ice: checking term score consistnency (dev)" TODO
# for term in db_con.getAllAuthTerms():
#     if not db_con.checkTermConsistency(term['id']):
#       print "warning: corrected inconsistent consensus score for term %d" % term['id']
#  db_con.commit()


print("ice: setup complete.")


@login_manager.user_loader
def load_user(id):
    return app.SeaIceUsers.get(int(id))


# Request wrappers (may have use for these later) #


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


# HTTP request handlers #


@app.errorhandler(404)
def pageNotFound(e):
    return (
        render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Oops! - 404",
            headline="404",
            content="The page you requested doesn't exist.",
        ),
        404,
    )


# we'll move this to pretty for consistency but here for now
@app.template_filter("tag_to_term")
def format_term(term_string):

    if term_string.startswith("#{g: xq"):
        term_string = term_string.replace("{g: xq", "")

    if "| h" in term_string:
        term_string = term_string[: term_string.find("| h")]

    return term_string


@app.template_filter("summarize_consensus")
# use pretty.summarizeConsensus
def summarize_consensus(consensus):
    """
    Return 'high', 'medium' or 'low' as a rough indicator of consensus.
    """
    cons = int(100 * consensus)
    if cons >= 70:
        return "high"
    elif cons >= 30:
        return "medium"
    else:
        return "low"


@app.template_filter("format_date")
# use pretty.prettyPrintDate
def format_date(date):
    """
    Return a human readable date string.
    """
    return date.strftime("%m/%d/%Y")


# home page
@app.route("/")
def index():
    if l.current_user.id:
        g.db = app.dbPool.getScoped()
        # TODO Store these values in class User in order to prevent
        # these queries every time the homepage is accessed.
        my = seaice.pretty.printTermsAsLinks(
            g.db, g.db.getTermsByUser(l.current_user.id)
        )
        star = seaice.pretty.printTermsAsLinks(
            g.db, g.db.getTermsByTracking(l.current_user.id)
        )
        notify = l.current_user.getNotificationsAsHTML(g.db)
        return render_template(
            "index.html",
            user_name=l.current_user.name,
            my=Markup(my) if my else None,
            star=Markup(star) if star else None,
            notify=Markup(notify) if notify else None,
        )

    return render_template("index.html", user_name=l.current_user.name)


@app.route("/about")
def about():
    return render_template("about.html", user_name=l.current_user.name)


@app.route("/guidelines")
def guidelines():
    return render_template("guidelines.html", user_name=l.current_user.name)


@app.route("/api")
def api():
    return redirect(url_for("static", filename="api/index.html"))


@app.route("/contact")
def contact():
    return render_template("contact.html", user_name=l.current_user.name)


# Login and logout #


@app.route("/login")
def login():
    if l.current_user.id:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Oops!",
            content="You are already logged in!",
        )

    form = """
        <p>
            In order to propose new terms or comment on others, you must first
            sign in.
             <li>Sign in with <a href="/login/google">Google</a>.</li>
             <li>Sign in with <a href="/login/orcid">ORCID</a>.</li>
        </p>
        """
    return render_template(
        "basic_page.html", title="Login page", headline="Login", content=Markup(form)
    )


@app.route("/login/google")
def login_google():
    redirect_uri = url_for("authorized", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route(seaice.auth.REDIRECT_URI)
def authorized():
    access_token = google.authorize_access_token()
    resp = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        if resp.status_code == 401:  # Unauthorized - bad token
            session.pop("access_token", None)
            return "l"
    g_user = resp.json()

    g.db = app.dbPool.getScoped()
    user = g.db.getUserByAuth("google", g_user["id"])
    if not user:  # not seen this person before, so create user
        g_user["authority"] = "google"
        g_user["auth_id"] = g_user["id"]
        g_user["id"] = app.userIdPool.ConsumeId()
        g_user["last_name"] = "Name"
        g_user["first_name"] = "Placeholder"
        g_user["reputation"] = "30"
        g.db.insertUser(g_user)
        g.db.commit()
        user = g.db.getUserByAuth("google", g_user["auth_id"])
        app.SeaIceUsers[user["id"]] = seaice.user.User(user["id"], user["first_name"])
        l.login_user(app.SeaIceUsers.get(user["id"]))
        return render_template(
            "account.html",
            user_name=l.current_user.name,
            email=g_user["email"],
            orcid=None,
            message="""
                According to our records, this is the first time you've logged onto
                SeaIce with this account. Please provide your first and last name as
                you would like it to appear with your contributions. Thank you!""",
        )

    l.login_user(app.SeaIceUsers.get(user["id"]))
    flash("Logged in successfully")
    return redirect(url_for("index"))


@app.route("/login/orcid")
def login_orcid():
    redirect_uri = url_for("orcid_authorized", _external=True)
    return orcid.authorize_redirect(redirect_uri)


@app.route(seaice.auth.REDIRECT_URI_ORCID)
def orcid_authorized():
    return "ORCID Authorized"


# def orcid_authorized():
#    access_token = orcid.authorize_access_token()
#    session["orcid_access_token"] = access_token, ""
#
#    orcid_user = resp
#
#    g.db = app.dbPool.getScoped()
#    g.db.setOrcid(l.current_user.id, orcid_user["orcid"])
#    g.db.commit()
#
#    flash("Logged in successfully")
#    return redirect("/account")


def get_access_token():
    return session.get("access_token")


@app.route("/logout")
@l.login_required
def logout():
    l.logout_user()
    return redirect(url_for("index"))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))


# Users #


@app.route("/account", methods=["POST", "GET"])
@l.login_required
def settings():
    g.db = app.dbPool.dequeue()
    if request.method == "POST":
        # error handling:
        if request.form["first_name"] == "" or request.form["last_name"] == "":
            user = g.db.getUser(
                l.current_user.id
            )  # fetch user for reputation and email
            return render_template(
                "account.html",
                user_name=l.current_user.name,
                email=user["email"],
                last_name_edit=request.form["last_name"],
                first_name_edit=request.form["first_name"],
                orcid=user["orcid"],
                reputation=user["reputation"] + " *" if user["super_user"] else " _",
                enotify="yes" if user["enotify"] else "no",
                message="Please don't leave any fields blank!",
            )
        # if their data is fine:
        else:
            g.db.updateUser(
                l.current_user.id,
                request.form["first_name"],
                request.form["last_name"],
                True if request.form.get("enotify") else False,
            )

            g.db.commit()
            app.dbPool.enqueue(g.db)
            l.current_user.name = request.form["first_name"]
            return getUser(str(l.current_user.id))

    # method was GET
    user = g.db.getUser(l.current_user.id)
    app.dbPool.enqueue(g.db)
    print(user["orcid"])
    return render_template(
        "account.html",
        user_name=l.current_user.name,
        email=user["email"],
        last_name_edit=user["last_name"],
        first_name_edit=user["first_name"],
        reputation=user["reputation"] + " *" if user["super_user"] else " _",
        enotify="yes" if user["enotify"] else "no",
        orcid=user["orcid"],
        message="""
                 Here you can change how your name will appear to other users.
                 Navigating away from this page will safely discard any changes.""",
    )


@app.route("/user=<int:user_id>")
def getUser(user_id=None):
    g.db = app.dbPool.getScoped()
    try:
        user = g.db.getUser(int(user_id))
        if user:
            result = """<hr>
                <table cellpadding=12>
                    <tr><td valign=top width="40%">First name:</td><td>{0}</td></tr>
                    <tr><td valign=top>Last name:</td><td>{1}</td></tr>
                    <tr><td valign=top>Email:</td><td>{2}</td></td>
                    <tr><td valign=top>Reputation:</td><td>{3}</td></td>
                    <tr><td valign=top>Receive email notifications:</td><td>{4}</td>
                </table> """.format(
                user["first_name"],
                user["last_name"],
                user["email"],
                user["reputation"] + " *" if user["super_user"] else "",
                user["enotify"],
            )

            return render_template(
                "basic_page.html",
                user_name=l.current_user.name,
                title="User - %s" % user_id,
                headline="User",
                content=Markup(result),
            )

    except IndexError:
        pass

    return render_template(
        "basic_page.html",
        user_name=l.current_user.name,
        title="User not found",
        headline="User",
        content=Markup("User <strong>#%s</strong> not found!" % user_id),
    )


@app.route("/user=<int:user_id>/notif=<int:notif_index>/remove", methods=["GET"])
@l.login_required
def remNotification(user_id, notif_index):
    try:
        assert user_id == l.current_user.id
        app.SeaIceUsers[user_id].remove(notif_index, app.dbPool.getScoped())
        return redirect("/")

    except AssertionError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Oops!",
            content="You may only delete your own notifications.",
        )

    except IndexError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Oops!",
            content="Index out of range.",
        )


# Look up terms #


@app.route("/term/concept=<term_concept_id>")
@app.route("/term=<term_concept_id>")
@app.route("/ark:/99152/<term_concept_id>")  # concept id is the same as ark for now
def getTerm(term_concept_id=None, message=""):
    # NOTE: this getTerm is called with concept_id, the other getTerm with id
    # get_info = request.args.get("info", False)

    g.db = app.dbPool.getScoped()
    term = g.db.getTermByConceptId(term_concept_id)
    if not term:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term not found",
            headline="Term",
            content=Markup("Term <strong>#%s</strong> not found!" % term_concept_id),
        )

    if "info" in request.args or request.full_path.endswith("??"):
        user = g.db.getUser(term["owner_id"])
        return render_template(
            "info.html", term=term, user=user
        )  # TODO: create a pretty.printAsErc() function for consistency

    else:
        result = (
            '<p><a href="/term/all_of_name/concept=%s">view all terms with the natural language string %s</a></p>'
            % (term_concept_id, term["term_string"])
        )
        result += seaice.pretty.printTermAsHTML(g.db, term, l.current_user.id)
        result = message + "<hr>" + result + "<hr>"
        result += seaice.pretty.printCommentsAsHTML(
            g.db, g.db.getCommentHistory(term["id"]), l.current_user.id
        )

        if l.current_user.id:
            result += """
            <form action="/term={0}/comment" method="post">
                <table cellpadding=16 width=60%>
                    <tr><td><textarea type="text" name="comment_string" rows=3
                        style="width:100%; height:100%"
                        placeholder="Add comment"></textarea></td></tr>
                    <tr><td align=right><input type="submit" value="Comment"><td>
                    </td>
                </table>
            </form>""".format(
                term["id"]
            )
        else:
            result += "<a href='/login'> Log in to comment </a>"

    return render_template(
        "basic_page.html",
        user_name=l.current_user.name,
        title="Term %s" % term["term_string"],
        headline="Term",
        content=Markup(result),
    )


# Look up terms by name and concept id (for order) #


# @app.route("/term/concept=<term_concept_id>")
@app.route("/term/all_of_name/concept=<term_concept_id>")
def getTermsOfName(term_concept_id=None, message=""):

    g.db = app.dbPool.getScoped()
    term = g.db.getTermByConceptId(term_concept_id)
    term_string = term["term_string"]
    terms = g.db.getTermsByTermString(term_string)

    # check if there are terms
    try:
        first = next(terms)
    except StopIteration:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term not found",
            headline="Terms",
            content=Markup("Term <strong>#%s</strong> not found!" % term_string),
        )

    terms = chain([first], terms)

    content = ""

    for term in terms:
        result = seaice.pretty.printTermAsHTML(g.db, term, l.current_user.id)
        result = message + "<hr style='border-top:1px solid gray;'>" + result + "<hr>"
        result += "<a class='expandComments' style='cursor: pointer' data-direction='down' data-id='"
        result += term["concept_id"]
        result += "'>Comments &#x25BC;</a> <div style='display: none' class='comments-"
        result += term["concept_id"] + "'>"
        result += seaice.pretty.printCommentsAsHTML(
            g.db, g.db.getCommentHistory(term["id"]), l.current_user.id
        )
        if l.current_user.id:
            result += """
            <form action="/term={0}/comment" method="post">
                <table cellpadding=16 width=60%>
                    <tr><td><textarea type="text" name="comment_string" rows=3
                        style="width:100%; height:100%"
                        placeholder="Add comment"></textarea></td></tr>
                    <tr><td align=right><input type="submit" value="Comment"><td>
                    </td>
                </table>
            </form>""".format(
                term["id"]
            )
        else:
            result += "<a href='/login'> Log in to comment </a>"

        result += "</div>"
        if term["concept_id"] == term_concept_id:
            content = result + content
        else:
            content += result

    return render_template(
        "basic_page.html",
        user_name=l.current_user.name,
        title="Term %s" % term_string,
        headline="Terms",
        content=Markup(content),
    )


@app.route("/browse")
@app.route("/browse/<type>")
@app.route("/browse/<type>/<int:page>")
def getList(type="alphabetical", page=None):

    if type is None:
        return redirect("/browse/alphabetical/1")
    if page is None:
        return redirect("/browse/" + type + "/1")

    g.db = app.dbPool.getScoped()

    sort_order = request.args.get("order")
    sort_token = None
    has_next = False
    has_prev = False
    pager = None

    if sort_order == "descending":
        sort_token = "DESC"
    elif sort_order == "ascending":
        sort_token = "ASC"

    terms_per_page = 20
    if page:
        pager = Pager(
            page=page, per_page=terms_per_page, total_count=g.db.getLengthTerms()
        )
        has_next = pager.has_next
        has_prev = pager.has_prev

    if type == "score":
        if not sort_token:
            sort_token = "DESC"
        if page:
            terms = g.db.getChunkTerms(
                sortBy="up- down " + sort_token, page=page, tpp=terms_per_page
            )
        else:
            terms = g.db.getAllAuthTerms(sortBy="up - down " + sort_token)

    elif type == "consensus":
        if not sort_token:
            sort_token = "DESC"
        if page:
            terms = g.db.getChunkAuthTerms(
                sortBy="consensus " + sort_token, page=page, tpp=terms_per_page
            )
        else:
            terms = g.db.getAllAuthTerms(sortBy="consensus " + sort_token)

    elif type == "class":
        if not sort_token:
            sort_token = "ASC"
        if page:
            terms = g.db.getChunkAuthTerms(
                sortBy="class " + sort_token, page=page, tpp=terms_per_page
            )
        else:
            terms = g.db.getAllAuthTerms(sortBy="class " + sort_token)

    elif type == "modified":
        if not sort_token:
            sort_token = "DESC"
        if page:
            terms = g.db.getChunkAuthTerms(
                sortBy="modified " + sort_token, page=page, tpp=terms_per_page
            )
        else:
            terms = g.db.getAllAuthTerms(sortBy="modified " + sort_token)

    elif type == "contributor":
        if not sort_token:
            sort_token = "ASC"
        if page:
            terms = g.db.getChunkAuthTerms(
                sortBy="u.last_name " + sort_token + ", u.first_name " + sort_token,
                page=page,
                tpp=terms_per_page,
            )
        else:
            terms = g.db.getAllAuthTerms(
                sortBy="u.last_name " + sort_token + ", u.first_name " + sort_token
            )

    else:  # type is alphabetical
        if not sort_token:
            sort_token = "ASC"
        if page:
            terms = g.db.getChunkAuthTerms(
                sortBy="term_string " + sort_token, page=page, tpp=terms_per_page
            )
        else:
            terms = g.db.getAllAuthTerms(sortBy="term_string " + sort_token)

    return render_template(
        "list/index.html",
        user_name=l.current_user.name,
        title="List of terms",
        headline="Terms",
        terms=terms,
        page=page,
        sort_order=sort_order,
        type=type,
        pager=pager,
        has_next=has_next,
        has_prev=has_prev,
    )


@app.route("/xbrowse")
@app.route("/xbrowse/<listing>")
@app.route("/xbrowse/<listing>/<int:page>")
def browse(listing=None, page=None):
    if listing is None:
        return redirect("/browse/recent")
    if page is None:
        return redirect("/browse/" + listing + "/1")

    g.db = app.dbPool.getScoped()
    pagination_details = getPaginationDetails(
        dbConnector=g.db, page=page, listing=listing
    )
    terms = pagination_details["terms"]
    letter = "~"
    result = "<h5>{0} | {1} | {2} | {3} | {4}</h5><hr>".format(
        '<a href="/browse/score">high score</a>'
        if listing != "score"
        else "high score",
        '<a href="/browse/recent">recent</a>' if listing != "recent" else "recent",
        '<a href="/browse/volatile">volatile</a>'
        if listing != "volatile"
        else "volatile",
        '<a href="/browse/stable">stable</a>' if listing != "stable" else "stable",
        '<a href="/browse/alphabetical">alphabetical</a>'
        if listing != "alphabetical"
        else "alphabetical",
    )
    # xxx alpha ordering of tags is wrong (because they start '#{g: ')

    if listing == "recent":  # Most recently added listing
        result += seaice.pretty.printTermsAsBriefHTML(
            g.db,
            sorted(terms, key=lambda term: term["modified"], reverse=True),
            l.current_user.id,
        )

    elif listing == "score":  # Highest consensus
        terms = sorted(terms, key=lambda term: term["consensus"], reverse=True)
        result += seaice.pretty.printTermsAsBriefHTML(
            g.db,
            sorted(terms, key=lambda term: term["up"] - term["down"], reverse=True),
            l.current_user.id,
        )

    elif (
        listing == "volatile"
    ):  # Least stable (Frequent updates, commenting, and voting)
        terms = sorted(
            terms, key=lambda term: term["t_stable"] or term["t_last"], reverse=True
        )
        result += seaice.pretty.printTermsAsBriefHTML(g.db, terms, l.current_user.id)

    elif listing == "stable":  # Most stable, highest consensus
        terms = sorted(terms, key=lambda term: term["t_stable"] or term["t_last"])
        result += seaice.pretty.printTermsAsBriefHTML(g.db, terms, l.current_user.id)

    elif listing == "alphabetical":  # Alphabetical listing
        result += "<table>"
        for term in terms:
            # skip if term is empty
            if not term["term_string"]:
                print("error: empty term string in alpha listing", file=sys.stderr)
                continue
            # firstc = term['term_string'][0].upper()
            firstc = term["term_string"][0].upper() if term["term_string"] else " "
            if firstc != "#" and firstc != letter:
                # letter = term['term_string'][0].upper()
                letter = firstc
                result += "</td></tr><tr><td width=20% align=center valign=top><h4>{0}</h4></td><td width=80%>".format(
                    letter
                )
            result += "<p><a %s</a>" % seaice.pretty.innerAnchor(
                g.db,
                term["term_string"],
                term["concept_id"],
                term["definition"],
                tagAsTerm=True,
            )
            orcid = g.db.getOrcidById(term["owner_id"])
            if orcid:
                result += (
                    " <i>contributed by <a target='_blank' href='https://sandbox.orcid.org/%s'>%s</a></i></p>"
                    % (orcid, g.db.getUserNameById(term["owner_id"], full=True))
                )
            else:
                result += " <i>contributed by %s</i></p>" % g.db.getUserNameById(
                    term["owner_id"], full=True
                )
        result += "</table>"
        # yyy temporary proof that this code is running
        print("note: end alpha listing", file=sys.stderr)

    return render_template(
        "browse.html",
        user_name=l.current_user.name,
        title="Browse",
        headline="Browse dictionary",
        content=Markup(result),
        pagination_details=pagination_details,
    )


hash2uniquerifier_regex = re.compile("(?<!#)#(\w[\w.-]+)")
# xxx is " the problem (use ' below)?
# token_ref_regex = re.compile("(?<!#\{g: )([#&]+)([\w.-]+)")


@app.route("/search", methods=["POST", "GET"])
def returnQuery():
    g.db = app.dbPool.getScoped()
    if request.method == "POST":
        #     is totally different from term_string as used in the database!
        # search_words = hash2uniquerifier_regex.sub(
        #     seaice.pretty.ixuniq + '\\1',
        #     request.form['term_string'])
        # terms = g.db.search(search_words)
        # #terms = g.db.search(request.form['term_string'])
        # if len(terms) == 0:
        #   return render_template("search.html", user_name = l.current_user.name,
        #     term_string = request.form['term_string'])
        # else:
        #   result = seaice.pretty.printTermsAsBriefHTML(g.db, terms, l.current_user.id)
        #   return render_template("search.html", user_name = l.current_user.name,
        #     term_string = request.form['term_string'],
        #     result = Markup(result.decode('utf-8')))
        if request.form["term_string"] == "":
            return render_template(
                "search.html",
                user_name=l.current_user.name,
                term_string="",
                pagination_details={},
            )
        else:
            return redirect("/search/" + request.form["term_string"] + "/1")
    else:  # GET
        return render_template(
            "search.html", user_name=l.current_user.name, pagination_details={}
        )


@app.route("/search/<search_term>/<int:page>")
def returnQueryPaginated(search_term=None, page=1):
    g.db = app.dbPool.getScoped()
    search_words = hash2uniquerifier_regex.sub(
        seaice.pretty.ixuniq + "\\1", search_term
    )
    pagination_details = getPaginationDetails(
        dbConnector=g.db, page=page, browse=False, search_words=search_words
    )
    terms = pagination_details["terms"]
    # terms = g.db.search(request.form['term_string'])
    if len(terms) == 0:
        return render_template(
            "search.html",
            user_name=l.current_user.name,
            term_string=search_term,
            pagination_details=pagination_details,
        )
    else:
        result = seaice.pretty.printTermsAsBriefHTML(g.db, terms, l.current_user.id)
        return render_template(
            "search.html",
            user_name=l.current_user.name,
            term_string=search_term,
            result=Markup(result),
            pagination_details=pagination_details,
        )


# yyy to do: display tag definition at top of search results
# when user clicks on community tag (searches for all terms bearing the tag)
@app.route("/tag/<tag>")
def getTag(tag=None):
    g.db = app.dbPool.getScoped()
    terms = g.db.search(seaice.pretty.ixuniq + tag)
    if len(terms) == 0:
        return render_template(
            "tag.html", user_name=l.current_user.name, term_string=tag
        )
    else:
        result = seaice.pretty.printTermsAsBriefHTML(g.db, terms, l.current_user.id)
        return render_template(
            "tag.html",
            user_name=l.current_user.name,
            term_string=tag,
            result=Markup(result),
        )


# Propose, edit, or remove a term #


@app.route("/contribute", methods=["POST", "GET"])
@l.login_required
def addTerm():

    if request.method == "POST":
        g.db = app.dbPool.dequeue()
        # xxx add check for non-empty term_string before consuming new 'id'
        # xxx add check for temporary, test term_string and then only consume
        #     a test 'id'

        term = {
            # 'term_string' : request.form['term_string'],
            "term_string": seaice.pretty.refs_norm(g.db, request.form["term_string"]),
            "definition": seaice.pretty.refs_norm(g.db, request.form["definition"]),
            "examples": seaice.pretty.refs_norm(g.db, request.form["examples"]),
            "owner_id": l.current_user.id,
            "id": app.termIdPool.ConsumeId(),
        }

        (id, concept_id) = g.db.insertTerm(term, prod_mode)

        # Special handling is needed for brand new tags, which always return
        # "(undefined/ambiguous)" qualifiers at the moment of definition.
        #
        if term["term_string"].startswith("#{g:"):  # if defining a tag
            # term['term_string'] = '#{g: %s | %s}' % (      # correct our initial
            term["term_string"] = "%s%s | %s}" % (  # correct our initial
                seaice.pretty.tagstart,
                seaice.pretty.ixuniq + request.form["term_string"][1:],
                concept_id,
            )  # guesses and update
            g.db.updateTerm(term["id"], term, None, prod_mode)

        g.db.commit()
        app.dbPool.enqueue(g.db)
        return getTerm(
            concept_id, message="Your term has been added to the metadictionary!"
        )

    else:  # GET
        return render_template(
            "contribute.html",
            user_name=l.current_user.name,
            title="Contribute",
            headline="Add a dictionary term",
        )


@app.route("/term=<term_concept_id>/edit", methods=["POST", "GET"])
@l.login_required
def editTerm(term_concept_id=None):

    try:
        g.db = app.dbPool.dequeue()
        term = g.db.getTermByConceptId(term_concept_id)
        # user = g.db.getUser(l.current_user.id)
        # yyy not checking if term was found?
        assert l.current_user.id and term["owner_id"] == l.current_user.id

        if request.method == "POST":

            assert request.form.get("examples") is not None
            updatedTerm = {
                # 'term_string' : request.form['term_string'],
                "term_string": seaice.pretty.refs_norm(
                    g.db, request.form["term_string"]
                ),
                "definition": seaice.pretty.refs_norm(g.db, request.form["definition"]),
                "examples": seaice.pretty.refs_norm(g.db, request.form["examples"]),
                "owner_id": l.current_user.id,
            }

            g.db.updateTerm(term["id"], updatedTerm, term["persistent_id"], prod_mode)

            # Notify tracking users
            notify_update = seaice.notify.TermUpdate(
                term["id"], l.current_user.id, term["modified"]
            )

            for user_id in g.db.getTrackingByTerm(term["id"]):
                app.SeaIceUsers[user_id].notify(notify_update, g.db)

            g.db.commit()
            app.dbPool.enqueue(g.db)

            return getTerm(
                term_concept_id,
                message="Your term has been updated in the metadictionary.",
            )

        else:  # GET
            app.dbPool.enqueue(g.db)
            if term:
                return render_template(
                    "contribute.html",
                    user_name=l.current_user.name,
                    title="Edit - %s" % term_concept_id,
                    headline="Edit term",
                    edit_id=term_concept_id,
                    term_string_edit=term["term_string"],
                    definition_edit=term["definition"],
                    examples_edit=term["examples"],
                )

    except ValueError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term not found",
            headline="Term",
            content=Markup("Term <strong>#%s</strong> not found!" % term_concept_id),
        )

    except AssertionError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term - %s" % term_concept_id,
            content="""Error! You may only edit or remove terms and definitions that
                 you've contributed. However, you may comment or vote on this term.
     assert term['owner_id'] (%s) == l.current_user.id (%s)"""
            % (term["owner_id"], l.current_user.id),
        )


@app.route("/term=<int:term_id>/remove", methods=["POST"])
@l.login_required
def remTerm(term_id):

    try:
        g.db = app.dbPool.getScoped()
        term = g.db.getTerm(int(request.form["id"]))
        assert term and term["owner_id"] == l.current_user.id
        assert term["class"] == "vernacular"

        tracking_users = g.db.getTrackingByTerm(term_id)

        id = g.db.removeTerm(int(request.form["id"]), term["persistent_id"], prod_mode)
        app.termIdPool.ReleaseId(id)

        # Notify tracking users
        notify_removed = seaice.notify.TermRemoved(
            l.current_user.id, term["term_string"], g.db.getTime()
        )

        for user_id in tracking_users:
            app.SeaIceUsers[user_id].notify(notify_removed, g.db)

        g.db.commit()

        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Remove term",
            content=Markup(
                "Successfully removed term <b>%s (%s)</b> from the metadictionary."
                % (term["term_string"], term["concept_id"])
            ),
        )

    except AssertionError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term - %s" % term_id,
            content="""Error! You may only remove terms that are in the vernacular class and
                                 that you've contributed. However, you may comment or vote on this term. """,
        )


# Comments #


@app.route("/term=<int:term_id>/comment", methods=["POST"])
@l.login_required
def addComment(term_id):

    try:
        assert l.current_user.id

        term_id = int(term_id)
        g.db = app.dbPool.getScoped()
        comment = {
            "comment_string": seaice.pretty.refs_norm(
                g.db, request.form["comment_string"]
            ),
            "term_id": term_id,
            "owner_id": l.current_user.id,
            "id": app.commentIdPool.ConsumeId(),
        }

        comment_id = g.db.insertComment(comment)

        # Notify owner and tracking users
        notify_comment = seaice.notify.Comment(
            term_id,
            l.current_user.id,
            comment["comment_string"],
            g.db.getComment(comment_id)["created"],
        )

        tracking_users = [user_id for user_id in g.db.getTrackingByTerm(term_id)]
        tracking_users.append(g.db.getTerm(term_id)["owner_id"])
        for user_id in tracking_users:
            if user_id != l.current_user.id:
                app.SeaIceUsers[user_id].notify(notify_comment, g.db)

        g.db.commit()

        return redirect("/term=%s" % g.db.getTermConceptId(term_id))

    except AssertionError:
        return redirect(url_for("login"))


@app.route("/comment=<int:comment_id>/edit", methods=["POST", "GET"])
@l.login_required
def editComment(comment_id=None):

    try:
        g.db = app.dbPool.dequeue()
        comment = g.db.getComment(int(comment_id))
        assert l.current_user.id and comment["owner_id"] == l.current_user.id

        if request.method == "POST":
            updatedComment = {
                "comment_string": seaice.pretty.refs_norm(
                    g.db, request.form["comment_string"]
                ),
                "owner_id": l.current_user.id,
            }

            g.db.updateComment(int(comment_id), updatedComment)
            g.db.commit()
            app.dbPool.enqueue(g.db)
            return getTerm(
                g.db.getTermConceptId(comment["term_id"]),
                message="Your comment has been updated.",
            )
        else:  # GET
            app.dbPool.enqueue(g.db)
            if comment:
                form = """
                <form action="/comment={0}/edit" method="post">
                    <table cellpadding=16 width=60%>
                        <tr><td><textarea type="text" name="comment_string" rows=3
                            style="width:100%; height:100%"
                            placeholder="Add comment">{1}</textarea></td></tr>
                        <tr><td align=right><input type="submit" value="Comment"><td>
                        </td>
                    </table>
                 </form>""".format(
                    comment_id, comment["comment_string"]
                )
                return render_template(
                    "basic_page.html",
                    user_name=l.current_user.name,
                    title="Edit comment",
                    headline="Edit your comment",
                    content=Markup(form),
                )

    except ValueError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Comment not found",
            content=Markup("Comment <strong>#%s</strong> not found!" % comment_id),
        )

    except AssertionError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Term - %s" % term_id,
            content="""Error! You may only edit or remove terms and definitions that
                                 you've contributed. However, you may comment or vote on this term. """,
        )


@app.route("/comment=<int:comment_id>/remove", methods=["POST"])
def remComment(comment_id):

    try:
        g.db = app.dbPool.getScoped()
        comment = g.db.getComment(int(request.form["id"]))
        assert comment and comment["owner_id"] == l.current_user.id

        g.db.removeComment(int(request.form["id"]))
        g.db.commit()

        return redirect("/term=%s" % g.db.getTermConceptId(comment["term_id"]))

    except AssertionError:
        return render_template(
            "basic_page.html",
            user_name=l.current_user.name,
            title="Oops!",
            content="""Error! You may only edit or remove your own comments.""",
        )

    # Voting! #


@app.route("/term=<int:term_id>/vote", methods=["POST"])
@l.login_required
def voteOnTerm(term_id):
    g.db = app.dbPool.getScoped()
    p_vote = g.db.getVote(l.current_user.id, term_id)
    if request.form["action"] == "up":
        if p_vote == 1:
            g.db.castVote(l.current_user.id, term_id, 0)
        else:
            g.db.castVote(l.current_user.id, term_id, 1)
    elif request.form["action"] == "down":
        if p_vote == -1:
            g.db.castVote(l.current_user.id, term_id, 0)
        else:
            g.db.castVote(l.current_user.id, term_id, -1)
    else:
        g.db.castVote(l.current_user.id, term_id, 0)
    g.db.commit()
    print(
        "User #%d voted %s term #%d"
        % (l.current_user.id, request.form["action"], term_id)
    )
    return redirect("/term=%s" % g.db.getTermConceptId(term_id))


@app.route("/term=<int:term_id>/track", methods=["POST"])
@l.login_required
def trackTerm(term_id):
    g.db = app.dbPool.getScoped()
    if request.form["action"] == "star":
        g.db.trackTerm(l.current_user.id, term_id)
    else:
        g.db.untrackTerm(l.current_user.id, term_id)
    g.db.commit()
    print(
        "User #%d %sed term #%d" % (l.current_user.id, request.form["action"], term_id)
    )
    return redirect("/term=%s" % g.db.getTermConceptId(term_id))


# Start HTTP server. (Not relevant on Heroku.) ##
if __name__ == "__main__":
    app.debug = True
    app.run("0.0.0.0", 5000, use_reloader=False)
