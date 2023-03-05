# DunderLab-Docs

This Python module allows to create [Sphinx Documntation](https://www.sphinx-doc.org/en/master/) from simple [Jupyter Notebooks](https://jupyter.org/). Is basically a preconfigured environment that use [nbsphinx](https://nbsphinx.readthedocs.io/) in background with a set of custom styles and preloaded modules.

## Installation


```python
$ pip install -U dunderlab-docs
```

After to generate the [Sphinx documentation](https://www.sphinx-doc.org/en/master/#) via [sphinx-quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html).  
In the ```conf.py``` file (from [sphinx](https://www.sphinx-doc.org/en/master/usage/configuration.html#example-of-configuration-file)), add ```nbsphinx``` and ```dunderlab.docs``` to the list of extensions.


```python
extensions = [
    'nbsphinx',
    'dunderlab.docs',
]
```

## Configuration

### ```dunderlab_custom_index```

Can be used to insert custom ReStructuredText index the ```ìndex.rst``` file, this one will be rendered after the main index, and also in the sidebar.


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

You can customize the appearance of your documentation by changing the color of the links. This can help give your documentation a bit of personality and make it more visually appealing. This will change the color of all links in your documentation to blue. You can experiment with different colors and styles to find the look that best suits your needs. Keep in mind that modifying the stylesheet will affect the appearance of your entire documentation, so make sure to test your changes thoroughly before publishing your documentation.


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

The notebook ```readme.ipynb``` is mandatory, this will be used to generate the ```README.md``` in the root of the Python package. All documentation notebooks are sortered by name, so, is recommendable to name then with numeric prefixes. Notebooks names that starts with ```__``` will not be rendered into the documentation.

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

**Index and Module Index is empty:**  
Just add the target module to the ```PATH``` in the ```conf.py``` file.
```
import os
import sys

sys.path.insert(0, os.path.abspath('relative_path_to_module'))
```


**Images in README.md are not visible:**  
The images used in the ```readme.ipynb``` notebook should be placed in a folder called ```_images```.

# Recommendations

**Add a custom command in** ```Makefile```**, to update modules from source code:**  

```
buildapi:
    rm -f source/_modules/*
    sphinx-apidoc -fMeETl -o source/_modules ../dunderlab/docs
```

Then the documentation can be entirely updated and compiled with the command:  
```
$ make clean buildapi html
```
