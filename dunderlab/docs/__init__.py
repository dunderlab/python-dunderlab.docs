import os

__version__ = '0.1'

EMPTY_NOTEBOOK = """
{{
 "cells": [
   {{
   "cell_type": "markdown",
   "id": "0",
   "metadata": {{}},
   "source": [
    "{0}"
   ]
  }}
 ],
 "metadata": {{}},
 "nbformat": 4,
 "nbformat_minor": 5
}}
"""

# ----------------------------------------------------------------------
def update(lista, listb):
    """"""
    return list(set(lista + listb))


# ----------------------------------------------------------------------
def build_index(app):
    """"""
    notebooks_dir = 'notebooks'
    notebooks_path = os.path.join(app.srcdir, notebooks_dir)

    if not os.path.exists(notebooks_path):
        os.makedirs(notebooks_path)

    readme_file = os.path.join(notebooks_path, 'readme.ipynb')
    if not os.path.exists(readme_file):
        with open(readme_file, 'w') as file:
            file.write(EMPTY_NOTEBOOK.format(f'# {app.config.project}'))

    readme_file = os.path.join(notebooks_path, '01-getting_started.ipynb')
    if not os.path.exists(readme_file):
        with open(readme_file, 'w') as file:
            file.write(EMPTY_NOTEBOOK.format('# Getting started'))

    notebooks_list = os.listdir(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), notebooks_path)
    )
    notebooks_list = filter(lambda s: not s.startswith('__'), notebooks_list)

    notebooks = []
    for notebook in notebooks_list:
        if notebook not in ['readme.ipynb', 'license.ipynb'] and notebook.endswith(
            '.ipynb'
        ):
            notebooks.append(f"{notebooks_dir}/{notebook.replace('.ipynb', '')}")

    notebooks = '\n   '.join(sorted(notebooks))

    with open(os.path.join(app.srcdir, 'index.rst'), 'w') as file:
        file.write(
            f"""
.. include:: {notebooks_dir}/readme.rst

.. toctree::
   :maxdepth: 2
   :name: mastertoc

   {notebooks}

.. only:: html

    Docstrings
    ==========

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

        """
        )


# ----------------------------------------------------------------------
def html_page_context(app, pagename, templatename, context, doctree):
    """Add CSS string to HTML pages that contain code cells."""

    # style = """

    #

    # """
    context['body'] = '\n<style>a {color: #ff0000;}</style>\n' + context['body']

    # print('*' * 70)
    # print(context['body'])


# ----------------------------------------------------------------------
def setup(app):
    """"""

    app.add_config_value('dunderlab_accent', '#00acc1', rebuild='html')
    # app.add_config_value('html_style', None, 'html', [list, str])

    app.config.html_theme_options = {
        'page_width': '1280px',
        'sidebar_width': '300px',
    }

    app.config.extensions = update(
        app.config.extensions,
        [
            'sphinx.ext.autodoc',
            'sphinx.ext.napoleon',
            'sphinx.ext.coverage',
            'sphinx.ext.viewcode',
            'sphinx.ext.autosectionlabel',
            'sphinx.ext.todo',
            'sphinx.ext.mathjax',
            # 'sphinxcontrib.bibtex',
        ],
    )

    app.config.naoleon_google_docstring = False
    app.config.napoleon_numpy_docstring = True
    app.config.napoleon_include_init_with_doc = True
    app.config.napoleon_include_private_with_doc = True
    app.config.napoleon_include_special_with_doc = True
    app.config.napoleon_use_admonition_for_examples = False
    app.config.napoleon_use_admonition_for_notes = False
    app.config.napoleon_use_admonition_for_references = False
    app.config.napoleon_use_ivar = False
    app.config.napoleon_use_param = True
    app.config.napoleon_use_rtype = True
    app.config.todo_include_todos = True

    app.config.autodoc_mock_imports = [
        'IPython',
        'matplotlib',
        'numpy',
    ]

    app.config.highlight_language = 'none'
    app.config.html_sourcelink_suffix = ''
    app.config.nbsphinx_execute = 'never'
    # app.config.nbsphinx_input_prompt = ' '
    # app.config.nbsphinx_output_prompt = ' '
    app.config.nbsphinx_kernel_name = 'python3'
    app.config.nbsphinx_prompt_width = '0'

    app.config.nbsphinx_prolog = """
    .. raw:: html

        <style>
            .nbinput .prompt,
            .nboutput .prompt {
                display: none;
        }
        </style>


    """

    app.connect('config-inited', lambda *args, **kargs: build_index(app))
    app.connect('html-page-context', html_page_context)

    # app.config.bibtex_bibfiles = ['refs.bib']

    # app.config.html_static_path = ['_static']
    # app.add_css_file('custom.css')

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 4,
    }
