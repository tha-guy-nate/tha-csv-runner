class CsvError(Exception):
    """Raised for invalid Runner configuration."""


ConfigError = CsvError  # back-compat alias
