#!/usr/bin/env python3
"""
Convert BBM models files to a JSON data file.

Join models/summary.csv to each model directory and write one JSON object.

Directory names follow the summary columns (regulations is not in the name):

\b
    [id-009]__[var-60]__[in-13]__[YEAST-APOPTOSIS]

The output is a JSON object keyed by the zero-padded id from the CSV:

\b
    {
      "009": {
        "summary": {
          "name": "YEAST-APOPTOSIS",
          "variables": 60,
          "inputs": 13,
          "regulations": 114
        },
        "metadata": { ... },          # metadata.json, parsed
        "readme": "...",              # README.md
        "bnet": "...",                # model.bnet
        "aeon": "...",                # model.aeon
        "sbml": "...",                # model.sbml
        "bma": { ... },               # model.bma.json, parsed
        "booleannet": "...",          # model.booleannet.txt
        "inferred_graph": "..."       # model.inferred-graph.aeon
      }
    }

JSON files are stored as objects. The other formats stay as text.
"""

import csv
import gzip
import json
import re
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parent

DIR_RE = re.compile(
    r"^\[id-(?P<id>\d+)\]__\[var-(?P<variables>\d+)\]__\[in-(?P<inputs>\d+)\]__\[(?P<name>.+)\]$"
)

# filename -> (output field, "json" or "text")
FILES = {
    "metadata.json": ("metadata", "json"),
    "README.md": ("readme", "text"),
    "model.bnet": ("bnet", "text"),
    "model.aeon": ("aeon", "text"),
    "model.sbml": ("sbml", "text"),
    "model.bma.json": ("bma", "json"),
    "model.booleannet.txt": ("booleannet", "text"),
    "model.inferred-graph.aeon": ("inferred_graph", "text"),
}


def read_summary(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f, skipinitialspace=True))
    by_id = {}
    for row in rows:
        model_id = row["ID"].zfill(3)
        if model_id in by_id:
            raise SystemExit(f"duplicate id {model_id} in {path}")
        by_id[model_id] = {
            "name": row["name"],
            "variables": int(row["variables"]),
            "inputs": int(row["inputs"]),
            "regulations": int(row["regulations"]),
        }
    return by_id


def index_dirs(models_dir):
    by_id = {}
    for path in sorted(models_dir.iterdir()):
        if not path.is_dir():
            continue
        match = DIR_RE.match(path.name)
        if not match:
            raise SystemExit(f"directory name does not match summary pattern: {path.name}")
        model_id = match.group("id").zfill(3)
        if model_id in by_id:
            raise SystemExit(f"duplicate id {model_id}: {path.name}")
        by_id[model_id] = (path, match.groupdict())
    return by_id


def load_files(directory):
    data = {}
    for filename, (field, kind) in FILES.items():
        path = directory / filename
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        text = path.read_text()
        data[field] = json.loads(text) if kind == "json" else text
    return data


def parse_skip(ctx, param, value):
    ids = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise click.BadParameter(f"not a model id: {part}")
        ids.add(part.zfill(3))
    return ids


def drop_skipped(summary, dirs, skip):
    unknown = sorted(skip - set(summary) - set(dirs))
    if unknown:
        raise SystemExit(f"unknown skip id: {', '.join(unknown)}")
    for model_id in skip:
        summary.pop(model_id, None)
        dirs.pop(model_id, None)


def build(summary, dirs):
    missing = sorted(set(summary) - set(dirs))
    extra = sorted(set(dirs) - set(summary))
    if missing or extra:
        click.echo(
            f"warning: summary/directory mismatch missing={missing} extra={extra}",
            err=True,
        )
        for model_id in missing:
            del summary[model_id]
        for model_id in extra:
            del dirs[model_id]

    models = {}
    for model_id in sorted(summary):
        row = summary[model_id]
        print(f"Processing: {row}")
        path, parsed = dirs[model_id]
        parsed_vars = int(parsed["variables"])
        parsed_inputs = int(parsed["inputs"])
        if (
            parsed["name"] != row["name"]
            or parsed_vars != row["variables"]
            or parsed_inputs != row["inputs"]
        ):
            raise SystemExit(
                f"id {model_id} summary {row} does not match directory {path.name}"
            )
        models[model_id] = {
            "summary": row,
            **load_files(path),
        }
    return models


@click.command(help=__doc__)
@click.option(
    "--summary",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default= Path("models") / "summary.csv",
    show_default=True,
    help="Summary CSV joined onto each model.",
)
@click.option(
    "--models",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("models"),
    show_default=True,
    help="Directory of model folders.",
)
@click.option(
    "--skip",
    default="",
    show_default=True,
    callback=parse_skip,
    help="Comma-separated model ids to leave out of the JSON. Ids are zero-padded to 3 digits.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default="models.json.gz",
    show_default=True,
    help="JSON file to write.",
)
def main(summary: Path, models: Path, output: Path, skip: set[str]) -> None:
    rows = read_summary(summary)
    dirs = index_dirs(models)
    drop_skipped(rows, dirs, skip)
    data = build(rows, dirs)
    stream = gzip.open(output, "wt") if output.suffix == ".gz" else output.open("wt")
    with stream as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), indent=2)
        f.write("\n")
    note = f", skipped {len(skip)}" if skip else ""
    click.echo(f"wrote {len(data)} models to {output}{note}", err=True)


if __name__ == "__main__":
    main()
