#!/usr/bin/python

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

from flask import (
    Flask, request, redirect, url_for, abort, render_template,
    render_template_string, flash, send_file)


app = Flask(__name__)
app.config.update(dict(DEBUG=True, SECRET_KEY=b'iamsecret'))


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

    def handle_endtag(self, tag):
        self._active_tag = None


def parser_theme(presentation):
    """Get the contents of meta.html and the theme of the presentation."""
    presentations_path = os.path.join(app.config.root_path, 'presentations')
    presentation_path = os.path.join(presentations_path, presentation)
    with open(os.path.join(presentation_path, 'meta.html'), 'r') as fd:
        meta = fd.read()
    parser = MetaHTMLParser()
    parser.feed(meta)
    return (meta, parser.theme, parser.title)


def list_themes():
    """Create a list of themes"""
    themes = []
    path = os.path.join(app.config.root_path, 'themes')
    for folder in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder)):
            if folder != 'reveal.js':
                themes.append(folder)
    themes.sort()
    return themes


@app.route('/')
@app.route('/presentations')
def presentations():
    """Display all the presentations."""
    presentations = sorted(
        os.listdir(os.path.join(app.config.root_path, 'presentations')))
    return render_template('presentations.html', presentations=presentations)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a presentation."""
    themes = list_themes()
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            path = os.path.join(app.config.root_path, 'presentations')
            if os.path.exists(os.path.join(path, name)):
                flash('This presentation already exists!')
                return redirect(url_for('create'))
        else:
            flash('Please, enter a name for the new presentation!')
            return redirect(url_for('create'))
        if request.form['theme'] in themes:
            os.mkdir(os.path.join(path, name))
            for file_ in ('presentation.css', 'conf.js'):
                open(os.path.join(path, name, file_), 'w')
            with open(os.path.join(
                    path, name, 'presentation.html'), 'w') as fd:
                fd.write('<section><h1>' + name + '</h1></section>')
            with open(os.path.join(path, name, 'meta.html'), 'w') as fd:
                fd.write(
                    '<title>%s</title>\n<meta name="theme" content="%s" />\n' %
                    (name, request.form['theme']))
            flash('This presentation has been created!')
            return redirect(
                url_for('presentation', action='edit', presentation=name),
                code=303)
    return render_template('create.html', themes=themes)


@app.route('/delete/<presentation>', methods=['GET', 'POST'])
def delete(presentation):
    """Delete a presentation."""
    if request.method == 'POST':
        if request.form['validation'] == 'yes':
            shutil.rmtree(os.path.join(
                app.config.root_path, 'presentations', presentation))
            flash('The presentation has been deleted.')
        return redirect(url_for('presentations'))
    return render_template('delete.html', presentation=presentation)


@app.route('/themes/<path:path>')
def themes_path(path):
    """Return scripts and css of reveal."""
    return send_file(os.path.join(app.config.root_path, 'themes', path))


@app.route('/presentations/<path:path>')
def presentations_path(path):
    """Return css of the presentation."""
    return send_file(os.path.join(app.config.root_path, 'presentations', path))


@app.route('/presentation/<action>/<presentation>', methods=['GET'])
def presentation(action, presentation):
    if action not in ('view', 'edit', 'export'):
        abort(404)

    configs = []
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)
    meta, meta_theme, title = parser_theme(presentation)
    themes = os.path.join(app.config.root_path, 'themes')
    theme = os.path.join(themes, meta_theme)

    for path in (presentation_path, theme, themes):
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
            meta_theme + '/style.css', 'presentation.css']
        scripts = [
            'reveal.js/lib/js/head.min.js', 'reveal.js/js/reveal.min.js']
        dir_temp = tempfile.mkdtemp()
        theme_temp = os.path.join(dir_temp, meta_theme)

        if os.path.exists(os.path.join(presentation_path, 'presentation.css')):
            shutil.copy(os.path.join(
                presentation_path, 'presentation.css'), dir_temp)

        for path in (presentation_path, theme, themes):
            if os.path.exists(os.path.join(path, 'reveal.js')):
                shutil.copytree(
                    os.path.join(path, 'reveal.js'),
                    os.path.join(dir_temp, 'reveal.js'))

        shutil.copytree(theme, os.path.join(dir_temp, meta_theme))

        for path in (presentation_path, theme):
            if os.path.exists(os.path.join(path, 'style.css')):
                shutil.copy(os.path.join(path, 'style.css'), theme_temp)
                break
    else:
        if os.path.exists(os.path.join(presentation_path, 'reveal.js')):
            route = 'presentations_path'
            path = presentation
        else:
            route = 'themes_path'
            path = (
                meta_theme if os.path.exists(os.path.join(theme, 'reveal.js'))
                else '.')
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

        with open('themes/control.html', 'r') as fd:
            control = render_template_string(
                fd.read(), presentation=presentation, control=action,
                title=title, themes=list_themes(), meta_theme=meta_theme)

        if os.path.exists(os.path.join(presentation_path, 'style.css')):
            stylesheets.append(url_for(
                'presentations_path',
                path=os.path.join(presentation, 'style.css')))
        elif os.path.exists(os.path.join(theme, 'style.css')):
            stylesheets.append(url_for(
                'themes_path',
                path=os.path.join(meta_theme, 'style.css')))

        if os.path.exists(os.path.join(presentation_path, 'presentation.css')):
            stylesheets.append(url_for(
                'presentations_path',
                path=os.path.join(presentation, 'presentation.css')))

        if action == 'edit':
            with open('themes/section.js', 'r') as fd:
                configs.append(render_template_string(
                    fd.read(), presentation=presentation))

    for path in (themes, theme, presentation_path):
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


@app.route('/save/<presentation>', methods=['POST'])
def save(presentation):
    """Save a presentation."""
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)
    with open(os.path.join(presentation_path, 'presentation.html'), 'w') as fd:
        fd.write(request.form['sections'])


@app.route('/tail/<presentation>', methods=['GET', 'POST'])
def tail(presentation):
    """Edit the contents, the css and the script."""
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)
    meta, meta_theme, title = parser_theme(presentation)
    themes = list_themes()

    if os.path.join(presentation_path, 'presentation.html'):
        with open(os.path.join(
            presentation_path, 'presentation.html'), 'r') as fd:
            contents = fd.read()
    else:
        flash('presentation.html doesn\'t exists in the folder ' +
            presentation)
    if os.path.exists(os.path.join(presentation_path, 'presentation.css')):
        with open(os.path.join(
            presentation_path, 'presentation.css'), 'r') as fd:
                style_css = fd.read()
    else:
        flash('presentation.css doesn\'t exists in the folder ' + presentation)
    if os.path.exists(os.path.join(presentation_path, 'conf.js')):
        with open(os.path.join(presentation_path, 'conf.js'), 'r') as fd:
            conf_js = fd.read()
    else:
        flash('conf.js doesn\'t exists in the folder ' + presentation)

    if request.method == 'POST':
        with open(os.path.join(
            presentation_path, 'presentation.html'), 'w') as fd:
            fd.write(request.form['contents'])
        with open(os.path.join(
            presentation_path, 'presentation.css'), 'w') as fd:
            fd.write(request.form['css'])
        with open(os.path.join(presentation_path, 'conf.js'), 'w') as fd:
            fd.write(request.form['script'])
        flash('The presentation ' + presentation + ' has been modified.')
        with open(os.path.join(presentation_path, 'meta.html'), 'w') as fd:
            fd.write(
                '<title>%s</title>\n<meta name="theme" content="%s" />\n' %
                (request.form['title'], request.form['theme']))
        new_presentation = (
            request.form['title'] if request.form['title'] else presentation)
        os.rename(presentation_path, os.path.join(
            app.config.root_path, 'presentations', new_presentation))
        return redirect(url_for('presentation', action='edit',
            presentation=new_presentation))

    return render_template('tail.html', presentation=presentation,
        contents=contents, style_css=style_css, conf_js=conf_js, themes=themes,
        meta_theme=meta_theme)


if __name__ == '__main__':
    app.run()
