def getPaginationDetails(dbConnector=None, page=1, listing=None, browse=True, search_words=None):
  """ Return a dict of details used to construct pagination bar

  :param dbConnector: database connector
  :type dbConnector: obj
  :param page: Page number being served
  :type page: int
  :param listing: type of browse. used for redirects
  :type listing: str
  :param browse: is this for browse or for search
  :type browse: boolean
  :param search_words: what terms to search the database by
  :type search_words: str

  :rtype: dict
  """

  details = {}
  terms_per_page = 10

  if browse:
    details['terms'] = dbConnector.getChunkTerms(sortBy="term_string", page=page, tpp=terms_per_page) #issue with defaults? thoughts?
    details['termCount'] = dbConnector.getLengthTerms()
  else:
    details['terms'] = dbConnector.searchPage(string=search_words, page=page, tpp=terms_per_page)
    details['termCount'] = dbConnector.searchLength(search_words)

  if details['termCount'] > 0:
    # which page you are on
    details['page'] = page
    # what type of browse we are looking at
    details['listing'] = listing
    # first page
    details['start'] = 1
    # last page
    details['end'] = ((details['termCount']//terms_per_page) + (0 if details['termCount']%terms_per_page == 0 else 1))
    # first page to have a link to
    details['first'] = page - 5 if page - 5 > 0 else 1
    # last page to have a link to
    details['last'] = page + 6 if page + 6 < details['end'] else details['end'] + 1
    # are there more pages than are showing on the left?
    details['dots_left'] = details['first'] > details['start']
    # are there more pages than are showing on the right?
    details['dots_right'] = details['last'] < details['end']
    # are there more than ten more pages to the right?
    details['next_ten'] = (page + 10) <= details['end']
    # are there more than ten more pages to the left?
    details['prev_ten'] = (page - 10) >= details['start']
  return details
