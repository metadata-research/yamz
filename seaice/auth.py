# auth.py - credentials and datastructures for authenticating users through
# third party accounts. So far we have Google via the Oauth2 protocol.
#
# Copyright (c) 2013, Christopher Patton, Nassib Nassar
# All rights reserved.
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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import stat
import configparser
import sys

from flask import Flask

from authlib.integrations.flask_client import OAuth

# Local PostgreSQL server configuration #


def accessible_by_group_or_world(file):
    """Verify the permissions of configuration file.
            *Contributed by Nassib Nassar*.

    :param file: File name.
    :type file: str
    :rtype: bool
    """
    st = os.stat(file)
    return bool(st.st_mode & (stat.S_IRWXG | stat.S_IRWXO))


def get_config(config_file=".seaice"):
    """Get local db configuration. *Contributed by Nassib Nassar*.

        Structure with DB connection parameters for particular
        roles. See the top-level program *ice* for example usage.

    :param config_file: File Name.
    :type config_file: str
    :rtype: dict
    """
    config = configparser.RawConfigParser()
    if os.path.isfile(config_file):
        if accessible_by_group_or_world(config_file):
            print(
                "error: config file "
                + config_file
                + " has group or world "
                + "access; permissions should be set to u=rw"
            )
            sys.exit(1)
        config.read(config_file)
    return config


app = Flask(__name__)
oauth = OAuth(app)

REDIRECT_URI_GOOGLE = "/g_authorized"
REDIRECT_URI_ORCID = "/orcid_authorized"


#: Get Google authentication. Client ID and secrets are drawn from a
#: config file which may contain multiple values for various
#: deployments. NOTE The client ID **should** never be published
#: and the secret **must** never be published.
def get_google_auth(client_id, client_secret):
    google = oauth.register(
        name="google",
        api_base_url="https://www.google.com/accounts/",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        request_token_url=None,
        request_token_params={
            "scope": "https://www.googleapis.com/auth/userinfo.email",
            "response_type": "code",
        },
        access_token_url="https://accounts.google.com/o/oauth2/token",
        access_token_method="POST",
        access_token_params={"grant_type": "authorization_code"},
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "email"},
    )
    return google


#: Get Orcid authentication. Client ID and secrets are drawn from a
#: config file which may contain multiple values for various
#: deplo9yments. NOTE The client ID **should** never be published
#: and the secret **must** never be published.
def get_orcid_auth(client_id, client_secret):
    oauth.register(
        name="orcid",
        client_id=client_id,
        client_secret=client_secret,
        access_token_url="https://sandbox.orcid.org/oauth/token",
        access_token_params=None,
        authorize_url="https://sandbox.orcid.org/oauth/authorize",
        autorize_params=None,
        api_base_url="https://api.sandbox.orcid.org/v3.0/",
        client_kwargs={"scope": "openid email"},
    )
    return oauth.orcid
