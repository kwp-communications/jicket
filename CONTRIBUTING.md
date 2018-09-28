# Contributing

Thank you for being interested in contributing to Jicket!
Please read this document carefully to avoid creating unnecessary work.

# Project structure
This project is structured like a basic python project.
The root folder contains some files necessary for packaging, the docs folder and jicket itself.

## Project files
* `setup.py`

  Python setup file

* `requirements.txt`

  List of all python requirements that need to be installed for development. Install with `pip install -r requirements.txt`

## docs
The docs folder contains the documentation hosted on [readthedocs](https://docs.readthedocs.io/en/latest/getting_started.html).

## jicket
Jicket package root. It contains the script in `bin`, unit tests in `tests` and the actual jicket module in `jicket`.
