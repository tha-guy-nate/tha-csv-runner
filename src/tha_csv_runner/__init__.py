"""tha-csv-runner: run a function over every row of a CSV."""

from importlib.metadata import version

from .errors import CsvError
from .runner import ThaCSV

__version__ = version("tha-csv-runner")
__all__ = ["CsvError", "ThaCSV"]
