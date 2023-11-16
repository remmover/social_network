import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'Social Network'
copyright = '2023, remover'
author = 'remover'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
