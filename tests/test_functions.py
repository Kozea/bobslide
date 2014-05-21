import bobslide
import pytest
import os


def test_lists():
    """Test list of presentations and list of themes."""
    assert bobslide.list_presentations() == [(0, 'Bonbons'), (0, 'Bulles'), (0, 'Sweets')]
    assert bobslide.list_themes() == [(0, 'Noir'), (0, 'Rose')]


def test_parser_theme():
    """Test a parser for meta.html."""
    assert bobslide.parser_theme(os.path.join(
        bobslide.app.config['PRESENTATIONS_PATHS'][0], 'Bulles')) == (
            '<title>Bulles</title>\n<meta name="theme" content="0/Noir" />\n',
            '0/Noir', 'Bulles')
    assert bobslide.parser_theme(os.path.join(
        bobslide.app.config['PRESENTATIONS_PATHS'][0], 'Bonbons')) == (
            '<title>Bonbons</title>\n<meta name="theme" content="0/Rose" />\n',
            '0/Rose', 'Bonbons')
