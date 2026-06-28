from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_csv() -> Path:
    return FIXTURES / "simple.csv"


@pytest.fixture
def error_csv() -> Path:
    return FIXTURES / "with_errors.csv"


@pytest.fixture
def simple_tsv() -> Path:
    return FIXTURES / "simple.tsv"
