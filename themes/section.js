list = document.querySelectorAll('#controls a');
for (var i=0; i<list.length ;i++) {
  list[i].addEventListener("click", function(event) {
    role = this.getAttribute('data-role');
    if ([
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote'
    ].indexOf(role) >= 0) {
        document.execCommand('formatBlock', false, role);
    } else {
        document.execCommand(role, false, null);
    }
    return false;
  });
}

for (var i=0; document.getElementsByTagName('section').length > i; i++) {
  document.getElementsByTagName('section')[i].setAttribute('contenteditable', 'true');
};

document.getElementById('save').addEventListener("click", function(event) {
  var sections = '';
  for (var i=0; document.getElementsByTagName('section').length > i; i++) {
    sections += document.getElementsByTagName('section')[i].outerHTML;
  };

  var request = new XMLHttpRequest();
  request.open('POST', "{{ url_for('save', index=index, presentation=presentation) }}", true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  request.send('sections=' + sections);
  event.preventDefault();
  return false;
});

document.getElementById('add').addEventListener("click", function(event) {
  var parent = document.querySelector('div.slides');
  var section = document.createElement("section");
  var text = document.createTextNode("Write Here!");
  section.appendChild(text);
  section.setAttribute('contenteditable', 'true');
  event.target = parent.insertBefore(section, document.querySelector('section.present').nextSibling);
  Reveal.next();
  event.preventDefault();
  return false;
});

document.getElementById("remove").addEventListener("click", function( event ) {
  if (Reveal.isLastSlide() && Reveal.isFirstSlide()) {
    return false;
  }
  index = Reveal.getIndices().h;
  if (Reveal.isLastSlide()) { index--; }
  event.target = document.querySelector('section.present').remove();
  Reveal.slide(index, 0, 0);
  event.preventDefault();
  return false;
});
