"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import ConfigError
from .runner import Runner

__version__ = "0.2.0"
__all__ = ["ConfigError", "Runner"]
