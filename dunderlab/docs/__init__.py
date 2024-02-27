"""
=========================
Dunderlab - Documentation
=========================

"""
import os
import shutil
import subprocess
import typing

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

REQUIREMENTS = """sphinx==7.0.0
urllib3<2.0
ipython
ipykernel
nbsphinx
sphinxcontrib-bibtex
pygments
dunderlab-docs
"""


PathLike = typing.Union[str, bytes, os.PathLike]


# ----------------------------------------------------------------------
def write_file(filename: PathLike, content: str) -> None:
    """If ```filename``` does not exist then create one with ```content``` in it."""
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write(content)


# ----------------------------------------------------------------------
def run_command(command: str) -> str:
    """Run a command."""
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.communicate()[0]


# ----------------------------------------------------------------------
def format_file(filepath, context):
    """"""

    with open(filepath, 'r') as file:
        content = file.read()

    with open(filepath, 'w') as file:
        file.write(content.format(**context))


# ----------------------------------------------------------------------
def darker_color(color, darker_factor):
    """
    Returns a darker version of a given color in hexadecimal format.
    The darker_factor parameter must be between 0 and 1, where 0 is the same color
    and 1 is black.
    """
    # Convert the color to its RGB components
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    # Calculate the new RGB values
    r_new = int(r * (1 - darker_factor))
    g_new = int(g * (1 - darker_factor))
    b_new = int(b * (1 - darker_factor))
    # Convert the new RGB values to hexadecimal format and return the new color
    return '#{:02x}{:02x}{:02x}'.format(r_new, g_new, b_new)


# ----------------------------------------------------------------------
def build_index(app, *args, **kwargs) -> None:
    """"""
    requirements = os.path.abspath(os.path.join(
        os.path.dirname(app.srcdir), 'requirements'))
    write_file(requirements, REQUIREMENTS)

    notebooks_dir = 'notebooks'
    notebooks_path = os.path.abspath(os.path.join(app.srcdir, notebooks_dir))

    if not os.path.exists(notebooks_path):
        os.makedirs(notebooks_path)
        getting_started = os.path.join(
            notebooks_path, '01-getting_started.ipynb')
        write_file(getting_started, EMPTY_NOTEBOOK.format(
            '# Getting started'))

    readme_file = os.path.join(notebooks_path, 'readme.ipynb')
    write_file(readme_file, EMPTY_NOTEBOOK.format(f'# {app.config.project}'))

    notebooks_list = os.listdir(notebooks_path)
    notebooks_list = filter(lambda s: not s.startswith('__'), notebooks_list)

    notebooks = []
    for notebook in notebooks_list:
        if notebook not in [
            'readme.ipynb',
            'footer.ipynb',
            'license.ipynb',
        ] and notebook.endswith('.ipynb'):
            notebooks.append(
                f"{notebooks_dir}/{notebook.replace('.ipynb', '')}")

    dunderlab_custom_index = app.config.dunderlab_custom_index

    if notebooks:
        navigation_title = """
Documentation Overview
======================
        """
    else:
        navigation_title = ''
    notebooks = '\n   '.join(sorted(notebooks))

    if app.config.dunderlab_code_reference:

        code_reference = """
.. only:: html

    Code Reference
    ==============

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
       """
    else:
        code_reference = ""

    if os.path.exists(os.path.join(notebooks_path, "footer.ipynb")):
        dunderlab_footer = f"""
.. container:: dunderlab-footer

    .. include:: {notebooks_dir}/footer.rst
        """
    else:
        dunderlab_footer = ''

    with open(os.path.join(app.srcdir, 'index.rst'), 'w') as file:
        file.write(
            f"""
.. include:: {notebooks_dir}/readme.rst

{navigation_title}

.. toctree::
   :maxdepth: {app.config.dunderlab_maxdepth}
   :name: mastertoc

   {notebooks}

{dunderlab_custom_index}

{code_reference}

{dunderlab_footer}
        """
        )

    run_command(
        f'jupyter-nbconvert --to rst {os.path.join(notebooks_path, "readme.ipynb")}'
    )

    if os.path.exists(os.path.join(notebooks_path, "footer.ipynb")):
        run_command(
            f'jupyter-nbconvert --to rst {os.path.join(notebooks_path, "footer.ipynb")}'
        )

    if os.path.exists(os.path.join(notebooks_path, "license.ipynb")):
        run_command(
            f'jupyter-nbconvert --to markdown {os.path.join(notebooks_path, "license.ipynb")} --output ../../../LICENSE.md'
        )
        run_command(
            f'mv ../../../LICENSE.md ../../../LICENSE'
        )

    run_command(
        f'jupyter-nbconvert --to markdown {os.path.join(notebooks_path, "readme.ipynb")} --output ../../../README.md'
    )

    if app.config.dunderlab_github_repository and os.path.exists('../README.md'):

        with open('../README.md', 'r') as file:
            content = file.read()
        content = content.replace(
            '(_images/', f'({app.config.dunderlab_github_repository}/raw/main/docs/source/notebooks/_images/')
        with open('../README.md', 'w') as file:
            file.write(content)


# ----------------------------------------------------------------------
def build_features(app, *args, **kwargs) -> None:
    """"""
    for dirname in ['static', 'templates']:
        for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)):
            target = os.path.abspath(os.path.join(
                app.srcdir, f'_{dirname}', file))
            source = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), dirname, file)

            if dirname == 'templates':
                if not os.path.exists(target):
                    shutil.copyfile(source, target)
            else:
                shutil.copyfile(source, target)
                context = {
                    'dunderlab_color_links': app.config.dunderlab_color_links,
                    'dunderlab_color_links__darker': darker_color(app.config.dunderlab_color_links, 0.3),
                }
                format_file(target, context)


# ----------------------------------------------------------------------
def setup(app) -> dict:
    """"""
    app.add_config_value('dunderlab_custom_index', '', rebuild='env')
    app.add_config_value('dunderlab_color_links', '#00acc1', rebuild='html')
    app.add_config_value('dunderlab_code_reference', True, rebuild='html')
    app.add_config_value('dunderlab_github_repository', '', rebuild='html')
    app.add_config_value('dunderlab_maxdepth', '2', rebuild='html')

    notebooks_dir = 'notebooks'
    notebooks_path = os.path.abspath(os.path.join(app.srcdir, notebooks_dir))

    if not os.path.exists(notebooks_path):
        os.makedirs(notebooks_path)

    notebooks = filter(lambda f: f.endswith(
        '.ipynb'), os.listdir(notebooks_path))
    notebooks = filter(
        lambda f: not f
        in [
            'readme.ipynb',
            'footer.ipynb',
            'license.ipynb',
        ],
        notebooks,
    )

    notebooks = list(
        filter(
            lambda f: not f.startswith('__'),
            notebooks,
        )
    )

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
    app.connect('builder-inited', build_features)

    for dirname in ['_static', '_templates']:
        if not os.path.exists(os.path.abspath(os.path.join(app.srcdir, dirname))):
            os.mkdir(os.path.abspath(os.path.join(app.srcdir, dirname)))

    app.add_css_file('dunderlab_custom.css')
    app.add_css_file('roboto_font.css')

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 4,
    }
