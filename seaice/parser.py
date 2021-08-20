import optparse

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
