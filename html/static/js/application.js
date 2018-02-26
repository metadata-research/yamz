$(document).ready(function attachListeners () {
  expandCommentsListener();
});

var expandCommentsListener = function() {
  $('.expandComments').on('click', function(e){
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
