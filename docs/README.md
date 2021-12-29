# Documentation Guidelines :bulb:
## Template
Currently, we use the insipid-theme. You find the docu [here](https://insipid-sphinx-theme.readthedocs.io/en/0.2.5/index.html#) and an example [here](https://github.com/mgeier/insipid-sphinx-theme/tree/master/doc).

## Docstrings
You can use sphinx-, Google, or NumPy-style docstrings. I recommend the [Numpy-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html#example-numpy) docstrings. They are easy to read/write and support type hints.

## Extending the Documentation
Look into `source/index.rst` and `source/chapters/use-case.rst` (and the other .rst files) to get a hint on how to extend the documentation.

## Build
Prerequisites
1. sphinx-build installed
2. `cd "aisscv root folder" && python -m pip install -r requirements.txt`

Steps to build
1. `cd docs`
2. You have two options to build the docs
    - `make html` (should also work under Windows via `make.bat`)
    - sphinx-build source/ build/

Just open `build/html/index.html` in your browser afterwards.

Sometimes it is necessary to <mark>delete</mark> the `doc/build` after you made changes in order for them to appear.
