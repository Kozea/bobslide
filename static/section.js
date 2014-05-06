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

  $.post( "{{ url_for('save', presentation=presentation) }}", { sections: sections } );
});

$('#add').click(function() {
  $('section.present').after('<section contenteditable="true">Write here!</section>');
});

$('#remove').click(function() {
  $('section.present').remove();
});
