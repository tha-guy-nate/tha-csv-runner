import importlib
import sys
from collections.abc import Callable
from pathlib import Path

import click

from .errors import ConfigError
from .runner import Runner


def _load_processor(spec: str) -> Callable[[dict], None]:
    try:
        module_name, func_name = spec.rsplit(":", 1)
    except ValueError:
        raise click.BadParameter(f"Expected format 'module:function', got: {spec!r}") from None

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise click.BadParameter(f"Cannot import module {module_name!r}") from None

    if not hasattr(module, func_name):
        raise click.BadParameter(f"Module {module_name!r} has no attribute {func_name!r}")

    return getattr(module, func_name)


@click.group()
def main() -> None:
    """Run a Python function over every row of a CSV."""


@main.command()
@click.option("--input", "input_path", required=True, help="Path to the input CSV file")
@click.option("--header", "required_headers", multiple=True, help="Required CSV header (repeatable)")  # noqa: E501
@click.option(
    "--processor", "processor_spec", default=None,
    help="Processor in 'module:function' format (optional)",
)
@click.option("--sample", default=None, type=int, help="Process only the first N rows")
@click.option(
    "--output", "output_path", default=None, help="Output CSV path (auto-named if omitted)",
)
def run(
    input_path: str,
    processor_spec: str | None,
    required_headers: tuple[str, ...],
    sample: int | None,
    output_path: str | None,
) -> None:
    """Run a processor function over every row of a CSV."""
    if not Path(input_path).exists():
        click.echo(f"Error: input file not found: {input_path}", err=True)
        sys.exit(1)

    processor = None
    if processor_spec is not None:
        try:
            processor = _load_processor(processor_spec)
        except click.BadParameter as exc:
            click.echo(f"Error: {exc}", err=True)
            sys.exit(1)

    try:
        runner = Runner(
            input_path=input_path,
            required_headers=list(required_headers),
            processor=processor,
            sample=sample,
        )
        runner.run()
        out = runner.write(output_path=output_path)
        click.echo(f"Wrote {out}")
    except ConfigError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
