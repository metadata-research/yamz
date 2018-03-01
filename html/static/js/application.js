$(document).ready(function attachListeners () {
  expandCommentsListener();
  logoutOrcidListener();
});

var expandCommentsListener = function () {
  $('.expandComments').on('click', function (e) {
    e.preventDefault();
    var link = $(this);
    var divSuffix = link.data('id');
    $('.comments-' + divSuffix).toggle();
    if(link.data('direction') === 'down'){
      link.html("Comments &#x25B2;");
      link.data('direction', 'up');
    } else {
      link.html("Comments &#x25BC;");
      link.data('direction', 'down');
    }
  })
}

var logoutOrcidListener = function () {
  $('.orcid-login').on('click', function (e) {
    var loginLink = $(this);
    e.preventDefault();
    $.ajax({
        url: 'https://sandbox.orcid.org/userStatus.json?logUserOut=true',
        dataType: 'jsonp',
        success: function(result,status,xhr) {
          window.location = loginLink.attr('href');
        },
        error: function (xhr, status, error) {
          console.warn('failure')
        }
    });

  })
}
