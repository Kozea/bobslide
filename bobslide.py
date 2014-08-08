#!/usr/bin/env python

"""
BobSlide
========

:copyright: (c) 2014 by Kozea and contributors.
:license: BSD, see LICENSE for more details.

"""

import os
import shutil
import tempfile
from html.parser import HTMLParser
from operator import itemgetter

from flask import (
    Flask, request, redirect, url_for, abort, render_template,
    render_template_string, flash, send_file)


app = Flask(__name__)

_THEMES_PATH = os.path.join(app.config.root_path, 'themes')

DEBUG = False
PRESENTATIONS_PATHS = [os.path.join(app.config.root_path, 'presentations')]
THEMES_PATHS = [_THEMES_PATH]
SECRET_KEY= 'secret_key_that_must_be_changed'


app.config.from_object(__name__)
app.config.from_pyfile(os.path.expanduser(
    os.path.join('~', '.config', 'bobslide')), silent=True)

# Turn relative paths into absolute for variables coming from the config file
for key in ('PRESENTATIONS_PATHS', 'THEMES_PATHS'):
    app.config[key] = [
        os.path.join(app.config.root_path, os.path.expanduser(path))
        for path in app.config[key]]


class MetaHTMLParser(HTMLParser):
    """Retrieve the name of theme in the file meta.html."""
    def __init__(self, *args, **kwargs):
        super(MetaHTMLParser, self).__init__(*args, **kwargs)
        self._active_tag = None
        self.theme = None
        self.title = None

    def handle_starttag(self, tag, attrs):
        self._active_tag = tag
        if tag == 'meta' and dict(attrs).get('name') == 'theme':
            meta_theme = dict(attrs).get('content')
            self.theme = meta_theme

    def handle_data(self, data):
        if self._active_tag == 'title':
            self.title = data.strip()

    def handle_entityref(self, name):
        self.section_content.append('&%s;' % name)

    def handle_endtag(self, tag):
        self._active_tag = None


class PresentationHTMLParser(HTMLParser):
    """Strip useless classes from editable content."""
    def __init__(self, *args, **kwargs):
        super(PresentationHTMLParser, self).__init__(*args, **kwargs)
        self.section_content = []

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            if dict(attrs).get('class') in ('past', 'present', 'future'):
                self.section_content.append('<%s>' % tag)
            else:
                self.section_content.append(
                    '<%s class="%s">' % (tag, dict(attrs).get('class')))
        else:
            self.section_content.append('<%s%s>' % (tag, ''.join(
                ' %s="%s"' % (key, value) for key, value in attrs)))

    def handle_data(self, data):
        self.section_content.append(data)

    def handle_entityref(self, name):
        self.section_content.append('&%s;' % name)

    def handle_endtag(self, tag):
        self.section_content.append('</%s>' % tag)


def parser_theme(presentation_path):
    """Get the contents of meta.html and the theme of the presentation."""
    with open(os.path.join(presentation_path, 'meta.html'), 'r') as fd:
        meta = fd.read()
    parser = MetaHTMLParser()
    parser.feed(meta)
    return (meta, parser.theme, parser.title)


def parser_presentation(content):
    """Get the contents of meta.html and the theme of the presentation."""
    parser = PresentationHTMLParser()
    parser.feed(content)
    return parser.section_content


def list_themes():
    """Return a list of themes"""
    themes = []
    for index, path in enumerate(app.config['THEMES_PATHS']):
        for folder in os.listdir(path):
            if os.path.isdir(os.path.join(path, folder)):
                if folder != 'reveal.js':
                    themes.append((index, folder))
    return sorted(themes, key=itemgetter(1))


def list_presentations():
    """Return a list of presentations"""
    presentations = []
    for index, path in enumerate(app.config['PRESENTATIONS_PATHS']):
        for presentation in os.listdir(path):
            presentations.append((index, presentation))
    return sorted(presentations, key=itemgetter(1))


@app.route('/')
@app.route('/presentations')
def presentations():
    """Display all the presentations."""
    return render_template(
        'presentations.html', presentations=list_presentations())


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a presentation."""
    themes = list_themes()
    if request.method == 'POST':
        if request.form['name']:
            index = len(app.config['PRESENTATIONS_PATHS']) - 1
            name = request.form['name']
            path = app.config['PRESENTATIONS_PATHS'][index]
            if os.path.exists(os.path.join(path, name)):
                flash('This presentation already exists!')
                return redirect(url_for('create'))
        else:
            flash('Please, enter a name for the new presentation!')
            return redirect(url_for('create'))
        os.mkdir(os.path.join(path, name))
        for file_ in ('presentation.css', 'conf.js'):
            open(os.path.join(path, name, file_), 'w')
        with open(os.path.join(path, name, 'presentation.html'), 'w') as fd:
            fd.write('<section><h1>%s</h1></section>' % name)
        with open(os.path.join(path, name, 'meta.html'), 'w') as fd:
            fd.write(
                '<title>%s</title>\n<meta name="theme" content="%s" />\n' %
                (name, request.form['theme']))
        flash('This presentation has been created!')
        url = url_for(
            'presentation', action='edit', presentation=name, index=index)
        return redirect(url, code=303)
    return render_template('create.html', themes=themes)


@app.route('/delete/<int:index>/<presentation>', methods=['GET', 'POST'])
def delete(index, presentation):
    """Delete a presentation."""
    if request.method == 'POST':
        if request.form['validation'] == 'yes':
            shutil.rmtree(os.path.join(
                app.config['PRESENTATIONS_PATHS'][index], presentation))
            flash('The presentation has been deleted.')
        return redirect(url_for('presentations'))
    return render_template(
        'delete.html', index=index, presentation=presentation)


@app.route('/themes/<path:path>')
def themes_path(path):
    """Return files from themes."""
    return send_file(os.path.join(_THEMES_PATH, path))


@app.route('/local_themes/<path:path>')
def local_themes_path(path):
    """Return files from local themes."""
    index, path = path.split('/', 1)
    return send_file(
        os.path.join(app.config['THEMES_PATHS'][int(index)], path))


@app.route('/presentations/<path:path>')
def presentations_path(path):
    """Return css of the presentation."""
    index, path = path.split('/', 1)
    return send_file(os.path.join(
        app.config['PRESENTATIONS_PATHS'][int(index)], path))


@app.route('/presentation/<action>/<int:index>/<presentation>',
           methods=['GET'])
def presentation(action, index, presentation):
    if action not in ('view', 'edit', 'export'):
        abort(404)

    configs = []
    presentation_path = os.path.join(
        app.config['PRESENTATIONS_PATHS'][index], presentation)
    meta, meta_theme, title = parser_theme(presentation_path)
    theme_index, theme_name = meta_theme.split('/')
    theme = os.path.join(
        app.config['THEMES_PATHS'][int(theme_index)], theme_name)

    for path in (presentation_path, theme, _THEMES_PATH):
        if os.path.exists(os.path.join(path, 'layout.html')):
            with open(os.path.join(path, 'layout.html'), 'r') as fd:
                layout = fd.read()
            break
    with open(os.path.join(presentation_path, 'presentation.html'), 'r') as fd:
        presentation_text = fd.read()

    if action == 'export':
        reveal_path = 'reveal.js'
        control = ''
        stylesheets = [
            'reveal.js/css/reveal.min.css', 'reveal.js/lib/css/zenburn.css',
            theme_name + '/style.css', 'presentation.css']
        scripts = [
            'reveal.js/lib/js/head.min.js', 'reveal.js/js/reveal.min.js']
        dir_temp = tempfile.mkdtemp()
        theme_temp = os.path.join(dir_temp, theme_name)

        if os.path.exists(os.path.join(presentation_path, 'presentation.css')):
            shutil.copy(os.path.join(
                presentation_path, 'presentation.css'), dir_temp)

        lock = False
        for path in (presentation_path, theme, _THEMES_PATH):
            if os.path.exists(os.path.join(path, 'reveal.js')) and not lock:
                shutil.copytree(
                    os.path.join(path, 'reveal.js'),
                    os.path.join(dir_temp, 'reveal.js'))
                lock = True

        shutil.copytree(theme, theme_temp)

        for path in (presentation_path, theme):
            if os.path.exists(os.path.join(path, 'style.css')):
                shutil.copy(os.path.join(path, 'style.css'), theme_temp)
                break
    else:
        if os.path.exists(os.path.join(presentation_path, 'reveal.js')):
            route = 'presentations_path'
            path = '%i/%s' % (index, presentation)
        elif os.path.exists(os.path.join(theme, 'reveal.js')):
            route = 'local_themes_path'
            path = meta_theme
        else:
            route = 'themes_path'
            path = '.'
        reveal_path = url_for(route, path=os.path.join(path, 'reveal.js'))
        stylesheets = [
            url_for(route, path=os.path.join(
                path, 'reveal.js', 'css', 'reveal.min.css')),
            url_for(route, path=os.path.join(
                path, 'reveal.js', 'lib', 'css', 'zenburn.css'))]
        scripts = [
            url_for(route, path=os.path.join(
                path, 'reveal.js', 'lib', 'js', 'head.min.js')),
            url_for(route, path=os.path.join(
                path, 'reveal.js', 'js', 'reveal.min.js'))]

        with open(os.path.join(_THEMES_PATH, 'control.html'), 'r') as fd:
            control = render_template_string(
                fd.read(), index=index, presentation=presentation,
                control=action, title=title, themes=list_themes(),
                meta_theme=meta_theme)

        if os.path.exists(os.path.join(presentation_path, 'style.css')):
            stylesheets.append(url_for('presentations_path', path=os.path.join(
                str(index), presentation, 'style.css')))
        elif os.path.exists(os.path.join(theme, 'style.css')):
            stylesheets.append(url_for(
                'local_themes_path',
                path=os.path.join(meta_theme, 'style.css')))

        stylesheets.append(url_for(
            'presentations_path',
            path=os.path.join(str(index), presentation, 'presentation.css')))

        stylesheets.append(url_for('static', filename='control.css'))

        if action == 'edit':
            with open(os.path.join(_THEMES_PATH, 'section.js'), 'r') as fd:
                configs.append(render_template_string(
                    fd.read(), index=index, presentation=presentation))

    for path in (_THEMES_PATH, theme, presentation_path):
        if os.path.exists(os.path.join(path, 'conf.js')):
            with open(os.path.join(path, 'conf.js'), 'r') as fd:
                configs.append(render_template_string(
                    fd.read(), reveal_path=reveal_path))

    index = render_template_string(
        layout, control=control, presentation_text=presentation_text,
        stylesheets=stylesheets, configs=configs, scripts=scripts,
        meta=meta)

    if action == 'export':
        with open(os.path.join(dir_temp, 'index.html'), 'w') as fd:
            fd.write(index)
        archive = shutil.make_archive(dir_temp, 'zip', dir_temp)
        attachment = send_file(
            archive, attachment_filename='%s.zip' % presentation)
        shutil.rmtree(dir_temp)
        os.remove(archive)
        return attachment
    else:
        return index


@app.route('/save/<int:index>/<presentation>', methods=['POST'])
def save(index, presentation):
    """Save a presentation."""
    presentation_path = os.path.join(
        app.config['PRESENTATIONS_PATHS'][index], presentation)
    contents = ''.join(parser_presentation(request.form['sections']))
    with open(os.path.join(presentation_path, 'presentation.html'), 'w') as fd:
        fd.write(contents)
    return '200 OK'


@app.route('/details/<int:index>/<presentation>', methods=['GET', 'POST'])
def details(index, presentation):
    """Edit the contents, the css and the script."""
    presentation_path = os.path.join(
        app.config['PRESENTATIONS_PATHS'][index], presentation)
    meta, meta_theme, title = parser_theme(presentation_path)
    themes = list_themes()

    with open(os.path.join(presentation_path, 'presentation.html')) as fd:
        contents = fd.read()

    with open(os.path.join(presentation_path, 'presentation.css')) as fd:
        style_css = fd.read()

    with open(os.path.join(presentation_path, 'conf.js')) as fd:
        conf_js = fd.read()

    if request.method == 'POST':
        with open(os.path.join(
                presentation_path, 'presentation.html'), 'w') as fd:
            fd.write(request.form['contents'])
        with open(os.path.join(
                presentation_path, 'presentation.css'), 'w') as fd:
            fd.write(request.form['css'])
        with open(os.path.join(presentation_path, 'conf.js'), 'w') as fd:
            fd.write(request.form['script'])
        flash('The presentation %s has been modified.' % presentation)
        with open(os.path.join(presentation_path, 'meta.html'), 'w') as fd:
            fd.write(
                '<title>%s</title>\n<meta name="theme" content="%s" />\n' %
                (request.form['title'], request.form['theme']))
        new_presentation = (
            request.form['title'] if request.form['title'] else presentation)
        os.rename(presentation_path, os.path.join(
            app.config['PRESENTATIONS_PATHS'][index], new_presentation))
        return redirect(url_for(
            'presentation', action='edit', index=index,
            presentation=new_presentation))

    return render_template(
        'details.html', presentation=presentation, contents=contents,
        style_css=style_css, conf_js=conf_js, themes=themes,
        meta_theme=meta_theme)

if __name__ == '__main__':
    app.run()  # pragma: no cover
