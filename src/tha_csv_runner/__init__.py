"""tha-csv-runner: run a function over every row of a CSV."""

from .errors import ConfigError
from .runner import Runner

__version__ = "0.1.0"
__all__ = ["Runner", "ConfigError"]
