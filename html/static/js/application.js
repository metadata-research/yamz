$(document).ready(function attachListeners () {
  expandCommentsListener();
});

var expandCommentsListener = function() {
  $('.expandComments').on('click', function(e){
    e.preventDefault();
    var link = $(this);
    var divSuffix = link.data('id');
    $('.comments-' + divSuffix).toggle();
  })
}
