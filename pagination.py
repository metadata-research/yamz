def getBrowsePaginationDetails(dbConnector=None, page=1, listing=None):
  details = {}
  details['terms'] = dbConnector.getChunkTerms(sortBy="term_string", page=page) #issue with defaults? thoughts?
  details['termCount'] = dbConnector.getLengthTerms()
  details['page'] = page
  details['listing'] = listing
  details['start'] = 1
  details['end'] = (1 + (details['termCount']//2) + (0 if details['termCount']%2 == 0 else 1)) #2 should change to whatever page size will be in the long term
  details['first'] = page - 5 if page - 5 > 0 else 1
  details['last'] = page + 6 if page + 6 < details['end'] else details['end']
  details['dots_left'] = details['first'] > details['start']
  details['dots_right'] = details['last'] < details['end']
  details['next_ten'] = (page + 10) <= details['end']
  details['prev_ten'] = (page - 10) >= details['start']
  return details

# def paginationHTML(details={}):
#   if pagination_details['page']:
#     pagination = '<nav aria-label="Page navigation">'
#     pagination += '<ul class="pagination">'
#     if pagination_details['page'] == 1:
#       pagination += '<li class="page-item disabled">'
#       pagination += '<span class="page-link">Prev</span>'
#           </li>
#         {% else %}
#           <li class="page-item">
#             <a class="page-link" href="/browse/{{ pagination_details['listing'] }}/{{ pagination_details['page'] - 1 }}">Prev</a>
#           </li>
#         {% endif %}

#         {% for i in range(1, pagination_details['end']) %} <!-- change 2 to page size.  -->
#           {% if i == pagination_details['page'] %}
#             <li class="page-item active">
#               <span class="page-link">
#                 {{ i }}
#                 <span class="sr-only">(current)</span>
#               </span>
#             </li>
#           {% else %}
#             <li class="page-item"><a class="page-link" href="/browse/{{ pagination_details['listing'] }}/{{ i }}">{{ i }}</a></li>
#           {% endif %}
#         {% endfor %}

#         {% if pagination_details['page'] == (pagination_details['termCount']//2) + (0 if pagination_details['termCount']%2 == 0 else 1) %}
#           <li class="page-item disabled">
#             <span class="page-link">Next</span>
#           </li>
#         {% else %}
#           <li class="page-item">
#             <a class="page-link" href="/browse/{{ pagination_details['listing'] }}/{{ pagination_details['page'] + 1 }}">Next</a>
#           </li>
#         {% endif %}

#       </ul>
#     </nav>
#   {% endif %}
