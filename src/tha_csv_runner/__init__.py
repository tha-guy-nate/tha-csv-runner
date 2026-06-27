"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import ConfigError, CsvError
from .runner import ThaCSV

__version__ = "0.3.0"
__all__ = ["ConfigError", "CsvError", "ThaCSV"]
