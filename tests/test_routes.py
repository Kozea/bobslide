import pytest
import os
import bobslide


def test_presentations(test_app):
    """Test the home path."""
    html = test_app.get('/presentations').data.decode('utf-8')
    assert 'Bulles' in html
    assert 'Bonbons' in html
    assert 'View' in html
    assert 'Edit' in html
    assert 'Delete' in html
    assert 'Export' in html


def test_create_presentation(test_app):
    """Test the creation of a presentation."""
    form = {
        'name': 'Plop',
        'theme': 'Blue'}
    test_app.post('/create', data=form)
    html = test_app.get('/presentations').data.decode('utf-8')
    assert 'Plop' in html

    form = {
        'name': 'Plop',
        'theme': 'Blue'}
    test_app.post('/create', data=form)

    form = {
        'name': '',
        'theme': 'Blue'}
    test_app.post('/create', data=form)

    html = test_app.get('/create').data.decode('utf-8')
    assert 'Noir' in html
    assert 'Rose' in html
    assert 'Create' in html

def test_delete_presentation(test_app):
    """Test the deleting of a presentation."""
    form = {'validation': 'yes'}
    test_app.post('/delete/0/Bulles', data=form)
    html = test_app.get('/presentations').data.decode('utf-8')
    assert 'Bulles' not in html
    assert 'Bonbons' in html

    html = test_app.get('/delete/0/Bonbons').data.decode('utf-8')

def test_themes_path(test_app):
    """Test sends files from themes folder."""
    response = test_app.get('/themes/reveal.js/css/reveal.min.css')
    assert response.status_code == 200


def test_local_themes_path(test_app):
    """Test sends files from local themes folder."""
    response = test_app.get('/local_themes/0/Rose/style.css')
    assert response.status_code == 200


def test_presentations_path(test_app):
    """Test sends files from presentation folder."""
    response = test_app.get('/presentations/0/Bulles/presentation.css')
    assert response.status_code == 200


def test_view_presentation(test_app):
    """Test the view of a presentation."""
    for index, presentation in bobslide.list_presentations():
        html = test_app.get('/presentation/view/%d/%s' % (index, presentation)).data.decode('utf-8')
        assert '<h1>%s</h1>' % presentation in html
        assert 'Close' in html
        assert 'Ordered' not in html


def test_edit_presentation(test_app):
    """Test the edit of a presentation."""
    # TODO: test the javascript
    test_app.get('/presentation/edit/0/Bulles')


def test_action_presentation(test_app):
    """Test if the action exists."""
    test_app.get('/presentation/delete/0/Bulles').data.decode('utf-8')


def test_export_presentation(test_app):
    """Test sends of folder.zip."""
    response = test_app.get('/presentation/export/0/Bulles')
    assert response.status_code == 200
    assert response.content_type == 'application/zip'


def test_save_presentation(test_app):
    """Test the backup of a presentation."""
    form = {'sections': '<section><h1>Bonbons</h1></section>'}
    test_app.post('/save/0/Bonbons', data=form)
    with open(os.path.join(
        bobslide.app.config['PRESENTATIONS_PATHS'][0], 'Bonbons',
            'presentation.html'), 'r') as fd :
            html = fd.read()
    assert '<h1>Bonbons</h1>' in html
    assert 'Bulles' not in html
    assert '<p>bonbons!</p>' not in html


def test_details_presentation(test_app):
    """Test the edition of name, theme, contents, script and css of a presentation."""
    with open(os.path.join(
        bobslide.app.config['PRESENTATIONS_PATHS'][0], 'Bonbons',
            'presentation.html'), 'r') as fd:
            contents = fd.read()
    form = {
        'title': 'Haribo',
        'theme': '0/Rose',
        'contents': contents,
        'css': 'body{background-color: #ACFA58;}',
        'script': ''}
    test_app.post('/details/0/Bonbons', data=form)
    html = test_app.get('/presentations').data.decode('utf-8')
    assert 'Haribo' in html

    html = test_app.get('/details/0/Bulles').data.decode('utf-8')
    assert 'Bulles' in html
    assert 'Noir' in html
    assert 'Rose' in html
    assert 'Write your javascript here' in html
    assert 'Edit' in html
