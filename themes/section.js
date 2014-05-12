$(function() {
  $('#controls a').click(function(e) {
    switch($(this).data('role')) {
      case 'h1':
      case 'h2':
      case 'h3':
      case 'h4':
      case 'h5':
      case 'h6':
      case 'p':
      case 'blockquote':
      case 'a':
        document.execCommand('formatBlock', false, $(this).data('role'));
        break;
      default:
        document.execCommand($(this).data('role'), false, null);
        break;
    }
    return false;
  });
});

$('section').each(function(){
  $(this).attr('contenteditable', 'true');
});

$('#save').click(function() {
  var sections = '';
  $('section').each(function(){
    sections += '<section>' + $( this ).html() + '</section>';
  });
  $.post("{{ url_for('save', index=index, presentation=presentation) }}", {sections: sections});
  return false;
});

$('#add').click(function() {
  $('section.present').after('<section contenteditable="true">Write here!</section>');
  Reveal.next();
  return false;
});

$('#remove').click(function() {
  if (Reveal.isLastSlide() && Reveal.isFirstSlide()) {
    return false;
  }
  index = Reveal.getIndices().h;
  if (Reveal.isLastSlide()) { index--; }
  $('section.present').remove();
  Reveal.slide(index, 0, 0);
  return false;
});

$('#title').change(function() {
  $('title').text($('#title').val());
});
