import os
import shutil
import tempfile
import zipfile
from html.parser import HTMLParser
from flask import (
    Flask, request, session, g, redirect, url_for, abort, render_template,
    render_template_string, flash, send_file)


app = Flask(__name__)
app.config.update(dict(DEBUG=True, SECRET_KEY=b'iamsecret'))


class MetaHTMLParser(HTMLParser):
    """Retrieve the name of theme in the file meta.html."""
    def __init__(self, *args, **kwargs):
        super(MetaHTMLParser, self).__init__(*args, **kwargs)
        self.theme = []

    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and dict(attrs).get('name') == 'theme':
            meta_theme = dict(attrs).get('content')
            self.theme.append(meta_theme)


def parser_theme(presentation):
    """Get the contents of meta.html and the theme of the presentation."""
    presentations_path = os.path.join(app.config.root_path, 'presentations')
    presentation_path = os.path.join(presentations_path, presentation)
    with open(os.path.join(presentation_path, 'meta.html'), 'r') as fd:
        meta = fd.read()
    parser = MetaHTMLParser()
    parser.feed(meta)
    meta_theme = parser.theme[-1]
    return (meta, meta_theme)


def list_themes():
    """Create a list of themes"""
    themes = []
    path = os.path.join(app.config.root_path, 'themes')
    for folder in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder)):
            if folder != "reveal.js":
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
    if request.method =='POST':
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
            with open(
                os.path.join(path, name, 'presentation.html'), 'w') as fd:
                fd.write('<section><h1>' + name + '</h1></section>')
            with open(os.path.join(path, name, 'meta.html'), 'w') as fd:
                fd.write(
                    '<title>%s</title>\n<meta name="theme" content="%s" />\n' %
                    (name, request.form['theme']))
            flash('This presentation has been created!')
            return redirect(url_for('presentations'))
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
    meta, meta_theme = parser_theme(presentation)
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

        with open('static/control.html', 'r') as fd:
            control = render_template_string(fd.read(), control=action)

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
            with open('static/section.js', 'r') as fd:
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
    sections = request.form['sections']
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)
    with open(os.path.join(presentation_path, 'presentation.html'), 'w') as fd:
        fd.write(sections)


@app.route('/add/<presentation>', methods=['POST'])
def add(presentation):
    """Add a slide to the presentation."""
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)
    with open(os.path.join(presentation_path, 'presentation.html'), 'a') as fd:
        fd.write('<section>Write here</section>')


@app.route('/remove/<presentation>', methods=['POST'])
def remove(presentation):
    """Remove a slide of the presentation."""
    section = request.form['section']
    slide_number = request.form['slide']
    presentation_path = os.path.join(
        app.config.root_path, 'presentations', presentation)


if __name__ == '__main__':
    app.run()
