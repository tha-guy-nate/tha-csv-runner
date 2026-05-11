"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import ConfigError
from .runner import tha_CSV_Runner

__version__ = "0.2.0"
__all__ = ["ConfigError", "tha_CSV_Runner"]
