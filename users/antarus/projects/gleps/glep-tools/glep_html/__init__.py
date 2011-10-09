
"""
PEP HTML Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import os.path
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import pep_html


class Writer(pep_html.Writer):

    default_stylesheet = 'glep.css'

    default_stylesheet_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_stylesheet))

    default_template = 'template.txt'

    default_template_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_template))

    settings_default_overrides = {
        'stylesheet_path': default_stylesheet_path,
        'template': default_template_path,
        'python_home': 'http://www.gentoo.org',
        'pep_home': 'http://www.gentoo.org/proj/en/glep/',
        'pep_base_url': 'http://www.gentoo.org/proj/en/glep/',
        'no_random': '1',
        'generator': '1',
        'datestamp': '%Y-%m-%d %H:%M UTC',
        'source_link': '1',
        }
