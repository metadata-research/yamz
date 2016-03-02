# Contributed by Greg Janee

# XXX TODO Delete persistent identifier on removal of term. 


import re
import os
import urllib
import urllib2
import ssl
import auth
import sys

REALM = "yamz"
USERNAME = "yamz"

# Be careful to use these URLs only in "production" yamz,
# as the identifiers they create are meant to last forever.
REAL_MINTER_URL = "https://n2t.net/a/yamz/m/ark/99152/h"
REAL_BINDER_URL = "https://n2t.net/a/yamz/b"

# The identifiers created with these URLs are meant to be thrown away.
TEST_MINTER_URL = "https://n2t.net/a/yamz/m/ark/99152/fk2"
TEST_BINDER_URL = "https://n2t.net/a/yamz_test/b"

# FIXME Location for `minter_password` is needlessly hardcoded. 
deploy = 'heroku' 
CONFIG = auth.get_config('.seaice_auth')
if CONFIG.has_option(deploy, 'minter_password'):
    PASSWORD = CONFIG.get(deploy, 'minter_password')
else:
    PASSWORD = os.environ.get('MINTER_PASSWORD')

# xxx change this host to match our actual hostname
# xxx use non-real minter/binder for ANY non-"yamz" host
# xxx turn off certificate check
TARGET_URL_TEMPLATE = "http://yamz.net/term/concept=%s"

_opener = None
_minter = None
_binder = None

def minderOpener (prod_mode):
  # Note that exceptions are not handled here but passed to the caller.
  ctxt = ssl.create_default_context()
  ctxt.check_hostname = False
  ctxt.verify_mode = ssl.CERT_NONE

  global _opener, _minter, _binder
  if not _minter:
    if prod_mode == "enable":
      _minter = REAL_MINTER_URL
      _binder = REAL_BINDER_URL
    else:
      _minter = TEST_MINTER_URL
      _binder = TEST_BINDER_URL
  if not _opener:
    m = urllib2.HTTPPasswordMgr()
    m.add_password(REALM, _minter, USERNAME, PASSWORD)
    m.add_password(REALM, _binder, USERNAME, PASSWORD)
    _opener = urllib2.build_opener(
      urllib2.HTTPSHandler(debuglevel=0, context=ctxt),
      urllib2.HTTPBasicAuthHandler(m))
    _opener.addheaders = [("Content-Type", "text/plain")]
    return _opener

def mintArkIdentifier (prod_mode):
  # Returns an ARK identifier as a string (e.g., "ark:/99152/h4232").
  global _opener, _minter
  if not _opener: 
    _opener = minderOpener(prod_mode)
  c = None
  try:
    c = _opener.open(_minter + "?mint%201")
    r = c.readlines()
    assert len(r) == 3 and r[0].startswith("s:") and r[1] == "nog-status: 0\n"
    arkId = r[0][3:].strip()
    assert re.match("99152/[a-z]+\d+$", arkId)
    arkId = "ark:/" + arkId
  finally:
    if c: c.close()
  return arkId

def bindArkIdentifier (arkId, prod_mode):
  # Returns the identifier passed in as a string.
  global _opener, _binder
  if not _opener: 
    _opener = minderOpener(prod_mode)
  c = None
  try:
    concept_id = arkId.split('/')[-1]
    #c = _opener.open(_binder + "?" +
    #  urllib.quote(("%s.set _t " + TARGET_URL_TEMPLATE) % (arkId, concept_id)))
    d = urllib.quote(("%s.set _t " + TARGET_URL_TEMPLATE + "\n") % (arkId, concept_id))
    c = _opener.open(_binder + "?-", d)
    r = c.readlines()
    print "r is %s, d is %s\n" % (r, d)
    sys.stdout.flush()
    assert len(r) == 2 and r[0] == "egg-status: 0\n"
  finally:
    if c: c.close()
  return arkId

def mint_persistent_id(prod_mode):
    arkId = 'http://n2t.net/' + mintArkIdentifier(prod_mode)
    bindArkIdentifier(arkId, prod_mode)
    return arkId

