def getBrowsePaginationDetails(dbConnector=None, page=1, listing=None):
  details = {}
  details['terms'] = dbConnector.getChunkTerms(sortBy="term_string", page=page)
  details['termCount'] = dbConnector.getLengthTerms()
  details['page'] = page
  details['listing'] = listing
  details['start'] = 1
  details['end'] = (1 + (details['termCount']//2) + (0 if details['termCount']%2 == 0 else 1))
  details['first'] = page - 5 if page - 5 > 0 else 0
  return details
# think more about what we want here. see notes.
