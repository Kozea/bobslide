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
  $.post( "{{ url_for('add', presentation=presentation) }}" );
});

$('#remove').click(function() {
  var section = [];
  var slide = null;
  $('section').each(function(){
    section = '<section>' + $( this ).html() + '</section>';
    });
  alert($('div').hasClass('slide-number'));
  $.post( "{{ url_for('remove', presentation=presentation) }}", { section: section }, { slide: slide } );
});
