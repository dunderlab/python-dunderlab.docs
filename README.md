# DunderLab-Docs

This Python module allows to create [Sphinx Documntation](https://www.sphinx-doc.org/en/master/) from simple [Jupyter Notebooks](https://jupyter.org/). Is basically a preconfigured environment that use [nbsphinx](https://nbsphinx.readthedocs.io/) in background with a set of custom styles and preloaded modules.

## Instalation


```python
$ pip install -U dunderlab-docs
```

## Configuration

After to generate the [Sphinx documentation](https://www.sphinx-doc.org/en/master/#) via [sphinx-quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html).  
In the ```conf.py``` file (from [sphinx](https://www.sphinx-doc.org/en/master/usage/configuration.html#example-of-configuration-file)), add ```nbsphinx``` and ```dunderlab.docs``` to the list of extensions.


```python
extensions = [
    'nbsphinx',
    'dunderlab.docs',
]
```

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
