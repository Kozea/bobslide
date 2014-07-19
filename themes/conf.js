reveal_conf = {
  controls: true,
  progress: true,
  history: true,
  center: true,

  theme: Reveal.getQueryHash().theme, // available themes are in /css/theme
  transition: Reveal.getQueryHash().transition || 'linear', // default/cube/page/concave/zoom/linear/fade/none

  // Optional libraries used to extend on reveal.js
  dependencies: [
    { src: '{{ reveal_path }}/lib/js/classList.js', condition: function() { return !document.body.classList; } },
    { src: '{{ reveal_path }}/plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
    { src: '{{ reveal_path }}/plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
    { src: '{{ reveal_path }}/plugin/highlight/highlight.js', async: true, callback: function() { hljs.initHighlightingOnLoad(); } },
    { src: '{{ reveal_path }}/plugin/zoom-js/zoom.js', async: true, condition: function() { return !!document.body.classList; } },
    { src: '{{ reveal_path }}/plugin/notes/notes.js', async: true, condition: function() { return !!document.body.classList; } }
  ]
};
