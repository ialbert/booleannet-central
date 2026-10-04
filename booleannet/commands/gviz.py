"""Build a Graphviz interaction graph from BooleanNet rules."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import click


def _pyboolnet():
    "Import pyboolnet when a graph is built."
    try:
        from pyboolnet import log
        from pyboolnet.boolean_normal_forms import functions2primes
        from pyboolnet.interaction_graphs import (
            add_style_interactionsigns,
            igraph2dot,
            primes2igraph,
        )
    except ImportError as exc:
        raise click.ClickException("pyboolnet is not installed. See the docs.") from exc
    return log, functions2primes, primes2igraph, add_style_interactionsigns, igraph2dot

KEYWORDS = {"and", "or", "not", "True", "False"}
ENGINES = ("dot", "neato", "fdp", "sfdp", "circo", "twopi")
IDENT = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def booleannet2functions(text: str) -> dict:
    """Turn BooleanNet update rules into callables for pyboolnet.

    Parameter names are sorted because functions2primes calls each
    function with arguments in alphabetical order.
    """
    funcs = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        lhs, rhs = line.split("=", 1)
        name = lhs.strip().removesuffix("*").strip()
        expr = rhs.strip()
        args = sorted(set(IDENT.findall(expr)) - KEYWORDS)
        params = ", ".join(args)
        src = f"lambda {params}: {expr}" if args else f"lambda: {expr}"
        funcs[name] = eval(src, {"True": True, "False": False})
    return funcs


def read_rules(path: Path | None) -> tuple[str, Path | None]:
    """Return rules text and the file output names inherit from.

    A pipe is the rules source when stdin is not a terminal. Otherwise the
    source is ``path`` or ``input.txt``. The returned path is that file, or
    ``None`` when the rules came from stdin and no input file was given.
    """
    if not sys.stdin.isatty():
        return sys.stdin.read(), path
    path = path or Path("input.txt")
    if not path.is_file():
        raise click.ClickException(f"rules file not found: {path}")
    return path.read_text(), path


def rules2dot(text: str, dot_path: Path) -> None:
    _, functions2primes, primes2igraph, add_style_interactionsigns, igraph2dot = _pyboolnet()
    primes = functions2primes(booleannet2functions(text))
    graph = primes2igraph(primes)
    # Default width is ~0.2in for one-letter names, which clips the labels.
    graph.graph["node"]["width"] = "0.55"
    graph.graph["node"]["fontsize"] = "14"
    graph.graph["node"]["color"] = "gray20"
    graph.graph["node"]["penwidth"] = "1.4"
    # width is a minimum; let longer labels expand the circle
    graph.graph["node"]["fixedsize"] = "false"
    for name in graph.nodes:
        if name.startswith("v_"):
            graph.nodes[name]["label"] = name.removeprefix("v_")
    add_style_interactionsigns(graph)
    igraph2dot(graph, str(dot_path))


def write_image(dot: Path, image: Path, engine: str = "neato") -> None:
    """Render a dot file. The image format is the output suffix, such as png or pdf.

    pyboolnet's layout lookup is hardcoded to /usr/bin, so this calls the engine on PATH.
    """
    log, *_ = _pyboolnet()
    exe = shutil.which(engine)
    if exe is None:
        raise click.ClickException(f"{engine} not found on PATH")
    fmt = image.suffix.lstrip(".").lower()
    if not fmt:
        raise click.ClickException(f"image path needs an extension such as .png or .pdf: {image}")
    subprocess.run([exe, f"-T{fmt}", str(dot), "-o", str(image)], check=True)
    log.info(f"image written to {image}")


@click.command()
@click.option("-i", "--input", "rules", type=click.Path(dir_okay=False, path_type=Path), help="BooleanNet rules file. Used when stdin is a terminal. Default: input.txt.")
@click.option("-d", "--dot", "dot", type=click.Path(dir_okay=False, path_type=Path), help="Dot output. Default: input path with a .dot suffix, or output.dot when reading stdin with no input file.")
@click.option("-o", "--output", "image", type=click.Path(dir_okay=False, path_type=Path), help="Image output. Default: input path with a .pdf suffix, or output.pdf when reading stdin with no input file. Format follows the extension (png, pdf, svg).")
@click.option("-e", "--engine", default="circo", show_default=True, type=click.Choice(ENGINES), help="Graphviz layout engine.")
def cli(rules: Path | None, dot: Path | None, image: Path | None, engine: str) -> None:
    """Generates a Graphviz graph from a model."""
    text, source = read_rules(rules)
    if source is None:
        dot = dot or Path("output.dot")
        image = image or Path("output.pdf")
    else:
        dot = dot or source.with_suffix(".dot")
        image = image or source.with_suffix(".pdf")
    rules2dot(text, dot)
    write_image(dot, image, engine)
