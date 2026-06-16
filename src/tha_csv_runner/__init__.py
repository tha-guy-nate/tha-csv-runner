"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import ConfigError
from .runner import ThaCSV

__version__ = "0.2.7"
__all__ = ["ConfigError", "ThaCSV"]
