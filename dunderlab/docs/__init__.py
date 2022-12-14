import os
import sys
import subprocess

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
def run_command(command):
    """This post save function creates a thumbnail for the commentary PDF"""
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.communicate()[0]


# ----------------------------------------------------------------------
def build_index(app, *args, **kwargs):
    """"""
    notebooks_dir = 'notebooks'
    notebooks_path = os.path.abspath(os.path.join(app.srcdir, notebooks_dir))

    if not os.path.exists(notebooks_path):
        os.makedirs(notebooks_path)

        readme_file = os.path.join(notebooks_path, '01-getting_started.ipynb')
        if not os.path.exists(readme_file):
            with open(readme_file, 'w') as file:
                file.write(EMPTY_NOTEBOOK.format('# Getting started'))

    readme_file = os.path.join(notebooks_path, 'readme.ipynb')
    if not os.path.exists(readme_file):
        with open(readme_file, 'w') as file:
            file.write(EMPTY_NOTEBOOK.format(f'# {app.config.project}'))

    notebooks_list = os.listdir(notebooks_path)
    notebooks_list = filter(lambda s: not s.startswith('__'), notebooks_list)

    notebooks = []
    for notebook in notebooks_list:
        if notebook not in [
            'readme.ipynb',
            # 'footer.ipynb',
            'license.ipynb',
        ] and notebook.endswith('.ipynb'):
            notebooks.append(f"{notebooks_dir}/{notebook.replace('.ipynb', '')}")

    if notebooks:
        navigation_title = """
Navigation
==========
        """
    else:
        navigation_title = ''

    notebooks = '\n   '.join(sorted(notebooks))

    with open(os.path.join(app.srcdir, 'index.rst'), 'w') as file:
        file.write(
            f"""
.. include:: {notebooks_dir}/readme.rst

{navigation_title}

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

..
  .. include:: {notebooks_dir}/footer.rst
        """
        )

    run_command(
        f'jupyter-nbconvert --to rst {os.path.join(notebooks_path, "readme.ipynb")}'
    )

    # if os.path.exists(os.path.join(notebooks_path, "footer.ipynb")):
    # run_command(
    # f'jupyter-nbconvert --to rst {os.path.join(notebooks_path, "footer.ipynb")}'
    # )

    run_command(
        f'jupyter-nbconvert --to markdown {os.path.join(notebooks_path, "readme.ipynb")} --output ../../../README.md'
    )


# ----------------------------------------------------------------------
def setup(app):
    """"""
    app.config.html_theme_options['page_width'] = '1280px'
    app.config.html_theme_options['sidebar_width'] = '300px'

    notebooks_dir = 'notebooks'
    notebooks_path = os.path.abspath(os.path.join(app.srcdir, notebooks_dir))
    notebooks = filter(lambda f: f.endswith('.ipynb'), os.listdir(notebooks_path))
    notebooks = filter(
        lambda f: not f
        in [
            'readme.ipynb',
            # 'footer.ipynb',
            'license.ipynb',
        ],
        notebooks,
    )
    app.config.html_theme_options['nosidebar'] = bool(notebooks)
    app.config.html_theme_options['page_width'] = '980px'

    app.config.extensions += [
        'sphinx.ext.todo',
        'sphinx.ext.viewcode',
        'sphinx.ext.autodoc',
        'sphinx.ext.napoleon',
        'sphinx.ext.coverage',
        'sphinx.ext.autosectionlabel',
        'sphinx.ext.mathjax',
        # 'sphinxcontrib.bibtex',
    ]
    app.config.extensions = list(set(app.config.extensions))

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

    # app.connect('config-inited', lambda *args, **kargs: build_index(app))
    # app.connect('config-inited', build_index)
    app.connect('builder-inited', build_index)

    # app.config.bibtex_bibfiles = ['refs.bib']

    app.add_css_file(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static', 'dunderlab_custom.css'
        )
    )

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 4,
    }
