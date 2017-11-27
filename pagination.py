def getPaginationDetails(dbConnector=None, page=1, listing=None, browse=True, search_words=None):
  details = {}

  if browse:
    details['terms'] = dbConnector.getChunkTerms(sortBy="term_string", page=page) #issue with defaults? thoughts?
    details['termCount'] = dbConnector.getLengthTerms()
  else:
    details['terms'] = dbConnector.searchPage(search_words, page)
    details['termCount'] = dbConnector.searchLength(search_words)

  print details['termCount']

  if details['termCount'] > 0:
    details['page'] = page
    details['listing'] = listing
    details['start'] = 1
    details['end'] = ((details['termCount']//2) + (0 if details['termCount']%2 == 0 else 1)) #2 should change to whatever page size will be in the long term
    details['first'] = page - 5 if page - 5 > 0 else 1
    details['last'] = page + 6 if page + 6 < details['end'] else details['end'] + 1
    details['dots_left'] = details['first'] > details['start']
    details['dots_right'] = details['last'] < details['end']
    details['next_ten'] = (page + 10) <= details['end']
    details['prev_ten'] = (page - 10) >= details['start']
    print details['end']
  return details
