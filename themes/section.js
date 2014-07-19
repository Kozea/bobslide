for (var i = 0; i < document.querySelectorAll('aside.buttons a').length; i++) {
  var link = document.querySelectorAll('aside.buttons a')[i];
  link.setAttribute('title', link.innerHTML);
  link.addEventListener('click', function(event) {
    event.preventDefault();
    role = this.getAttribute('data-role');
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote'].indexOf(role) >= 0) {
      document.execCommand('formatBlock', false, role);
    } else if (role == 'createLink') {
      var a = document.createElement('a');
      a.appendChild(window.getSelection().getRangeAt(0).extractContents());
      document.execCommand(role, false, a.innerHTML);
    } else {
      document.execCommand(role, false, null);
    }
  });
}

for (var i = 0; i < document.querySelectorAll('nav.buttons a').length; i++) {
  var link = document.querySelectorAll('nav.buttons a')[i];
  link.setAttribute('title', link.innerHTML);
}

for (var i = 0; document.getElementsByTagName('section').length > i; i++) {
  document.getElementsByTagName('section')[i].setAttribute('contenteditable', 'true');
};

document.getElementById('save').addEventListener('click', function(event) {
  var sections = '';
  for (var i = 0; document.getElementsByTagName('section').length > i; i++) {
    sections += document.getElementsByTagName('section')[i].outerHTML;
  };

  var request = new XMLHttpRequest();
  request.open('POST', '{{ url_for("save", index=index, presentation=presentation) }}', true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  request.send('sections=' + sections);
  event.preventDefault();
  return false;
});

document.getElementById('add').addEventListener('click', function(event) {
  var parent = document.querySelector('div.slides');
  var section = document.createElement('section');
  section.setAttribute('contenteditable', 'true');
  section.innerHTML = '<h2>Title</h2><p>Content</p>';
  event.target = parent.insertBefore(section, document.querySelector('section.present').nextSibling);
  Reveal.next();
  event.preventDefault();
  return false;
});

document.getElementById('remove').addEventListener('click', function(event) {
  if (Reveal.isLastSlide() && Reveal.isFirstSlide()) {
    return false;
  }
  index = Reveal.getIndices().h;
  if (Reveal.isLastSlide()) {
    index--;
  }
  event.target = document.querySelector('section.present').remove();
  Reveal.slide(index, 0, 0);
  event.preventDefault();
  return false;
});
