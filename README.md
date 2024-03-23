# DunderLab's Documentation Guide

This Python module facilitates the creation of [Sphinx Documentation](https://www.sphinx-doc.org/en/master/) directly from [Jupyter Notebooks](https://jupyter.org/). Essentially, it provides a preconfigured environment that utilizes [nbsphinx](https://nbsphinx.readthedocs.io/) in the background, complete with custom styles and preloaded modules.

## Installation


```python
$ pip install -U dunderlab-docs
```

To generate [Sphinx documentation](https://www.sphinx-doc.org/en/master/#), start with the [sphinx-quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html) command. Then, in the Sphinx `conf.py` file, add '[sphinx](https://www.sphinx-doc.org/en/master/usage/configuration.html#example-of-configuration-file)' and `dunderlab.docs` to the extensions list.


```python
extensions = [
    'nbsphinx',
    'dunderlab.docs',
]
```

## Configuration

### ```dunderlab_custom_index```

This setting allows you to insert a custom ReStructuredText into the `index.rst` file. This custom index will be rendered following the main index and will also appear in the sidebar.


```python
dunderlab_custom_index = f"""
.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Submodule 1

   notebooks/submodule1/*


.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Submodule 2

   notebooks/submodule2/*
    """
```

### ```dunderlab_color_links```

Customize your documentation's appearance by altering the link colors. For instance, setting `dunderlab_color_links` to `#4db6ac` changes all links to a blue shade, adding a unique touch to your documentation. Remember, changes to the stylesheet impact the entire documentation, so test thoroughly before publishing.


```python
dunderlab_color_links = '#4db6ac'
```

### ```dunderlab_code_reference```

This configuration value can be used to disable the generation of certain index inputs in Sphinx documentation. Specifically, setting to ```True``` will enable the generation of the index inputs genindex, modindex, and search, while setting it to ```False``` will disable their generation.


```python
dunderlab_code_reference = False
```

### ```dunderlab_github_repository```

This configuration specifies the project repository, which will be used to adjust the URLs of the images in the ```README.md``` file.

## Notebooks

In the first build, for example ```make clean html```, the system will create (if not yet exist) the folder ```notebooks``` with some files in it.

```
docs/
    build/
    source/
        conf.py
        index.rst
        _modules/
        _static/
        _templates/
->      notebooks/
->          01-getting_started.ipynb
->          readme.ipynb
->          __sandbox.ipynb
```

The `readme.ipynb` notebook is mandatory, as it generates the `README.md` file in the root of the Python package. Documentation notebooks should be named with numeric prefixes for sorting purposes. Notebooks named with `__` prefixes won't be rendered into the documentation.

## Special Notebooks names

### ```readme.ipynb```
This notebook is used to generate the main documentation page, which is typically the ```index.rst file```. The notebook is converted into a ReStructuredText file, which is then rendered as HTML to create the main documentation page. Additionally, the ```readme.ipynb``` notebook is also used to generate the ```README.md``` file that is typically found in the root of your project. This file can provide a brief overview of your project and its purpose, along with any relevant installation or usage instructions.


### ```license.ipynb```
This notebook is used to generate the ```LICENSE``` file that is typically found in the root of your project. This file specifies the terms under which your code is licensed and provides information about how others can use and modify your code. It is recommended that the ```license.ipynb``` notebook contain a single Markdown or plain text cell that includes the full text of your project's license. This can help ensure that the license text is accurate and up-to-date, and can simplify the process of updating the license if needed.

### ```footer.ipynb```
This notebook is used to generate a footer that appears at the bottom of the main documentation page and the project's `README.md` file. It can contain any content you want to include in the footer, such as copyright information, acknowledgments, or links to related resources. During the documentation build process, the notebook is converted into HTML and added to the bottom of the main documentation page and `README.md` file. 

## Features

 * Automatic generation of README.md
 * Automatic index in html view
 * Compatibe with [Read the Docs](https://readthedocs.org/)

# Troubleshooting

**If the Index and Module Index appear empty:**  
Resolve this by adding the target module's path to the PATH variable in the `conf.py` file
``` python
import os
import sys

sys.path.insert(0, os.path.abspath('relative_path_to_module'))
```


**If images aren't visible in the readmereadme.md file:**  
Verify their paths to ensure they're accessible from the GitHub repository. Relative paths must be correctly set relative to the `README.md` file's location.  
The images used in the `readme.ipynb` notebook should be placed in a folder called `_images`.

![test_image](https://github.com/dunderlab/python-dunderlab.docs/raw/main/docs/source/notebooks/_images/test.png)
