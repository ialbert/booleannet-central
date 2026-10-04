#!/usr/bin/env python3
"""List models or print one model in a chosen format.

    bnet models                 one summary row per model
    bnet models 1               bnet for model 001
    bnet models CORTICAL        model whose name contains CORTICAL
    bnet models 1 -f aeon       aeon for model 001
    bnet models -d models.json  read a chosen JSON database
"""

import gzip
import json
import sys
from importlib.resources import files
from pathlib import Path

import click

DATA = files("booleannet").joinpath("data", "models.json.gz")
FORMATS = (
    "bnet",
    "booleannet",
    "sbml",
    "aeon",
    "bma",
    "inferred_graph",
    "metadata",
    "readme",
)
JSON_FORMATS = {"bma", "metadata"}


def load_models(path: Path | None):
    if path is None:
        with DATA.open("rb") as raw, gzip.open(raw, "rt") as f:
            return json.load(f)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return json.load(f)


def list_summaries(models):
    rows = []
    for model_id, model in models.items():
        summary = model["summary"]
        rows.append((
            model_id,
            summary["name"],
            summary["variables"],
            summary["inputs"],
            summary["regulations"],
        ))
    rows.sort(key=lambda row: (row[2], row[0]))
    name_w = max(len(name) for _, name, _, _, _ in rows)
    click.echo(f"{'id':3}  {'name':<{name_w}}  {'var':>5}  {'in':>4}  {'reg':>5}")
    for model_id, name, variables, inputs, regulations in rows:
        click.echo(f"{model_id}  {name:<{name_w}}  {variables:5}  {inputs:4}  {regulations:5}")


def find_models(models, key: str) -> list[str]:
    """Match a number to an id, or text to an id or name."""
    if key.isdigit():
        model_id = key.zfill(3)
        return [model_id] if model_id in models else []
    needle = key.casefold()
    return [
        model_id
        for model_id, model in models.items()
        if needle in model_id.casefold() or needle in model["summary"]["name"].casefold()
    ]


def emit(model, fmt):
    value = model[fmt]
    if fmt in JSON_FORMATS:
        click.echo(json.dumps(value, ensure_ascii=False))
        return
    click.echo(value, nl=not value.endswith("\n"))


@click.command()
@click.argument("key", required=False)
@click.option(
    "-d",
    "--database",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="JSON or JSON.gz database. Default: packaged data/models.json.gz.",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    default="booleannet",
    show_default=True,
    type=click.Choice(FORMATS),
    help="Model file to print when KEY is given.",
)
def main(key, database, fmt):
    """List model summaries, or print one model in the chosen format.

    KEY is a number (1 or 001) or text matched against the id or name.
    """
    models = load_models(database)
    if key is None:
        list_summaries(models)
        return

    hits = find_models(models, key)
    if not hits:
        raise click.ClickException(f"no model {key}")
    if len(hits) > 1:
        lines = [f"{i}  {models[i]['summary']['name']}" for i in sorted(hits)]
        raise click.ClickException("several models match:\n" + "\n".join(lines))
    emit(models[hits[0]], fmt)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.stdout.close()
        sys.exit(0)
