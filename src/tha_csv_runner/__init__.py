"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import CsvError
from .runner import ThaCSV

__version__ = "0.3.2"
__all__ = ["CsvError", "ThaCSV"]
