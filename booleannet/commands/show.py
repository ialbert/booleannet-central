"""Build a Graphviz interaction graph from BooleanNet rules."""

import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from booleannet import logger

import click

try:
    from pyboolnet import log
    from pyboolnet.boolean_normal_forms import functions2primes
    from pyboolnet.interaction_graphs import (
        add_style_interactionsigns,
        igraph2dot,
        primes2igraph,
    )
    log.setLevel(logging.INFO)
    PYBOOLNET_READY = True
except ImportError:
    PYBOOLNET_READY = False

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


def read_rules(path: Path | None) -> tuple[str, Path | None] | None:
    """Return rules text and the file they were read from.

    Stdin is the source when it is not a terminal and has text. Otherwise
    the source is ``path``. Returns ``None`` when no file was given and
    stdin is a terminal or empty, so the caller can show help.
    """
    if not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            return text, path
    if path is None:
        return None
    if not path.is_file():
        raise click.ClickException(f"rules file not found: {path}")
    return path.read_text(), path


def _graphml_value(value):
    """GraphML stores scalars. A sign set such as {1, -1} becomes "1,-1"."""
    if isinstance(value, (str, int, float)):
        return value
    if isinstance(value, (set, frozenset)):
        return ",".join(str(item) for item in sorted(value))
    return str(value)


def write_graphml(graph, path: Path) -> None:
    """Write the interaction graph as GraphML next to the dot file."""
    import networkx as nx

    out = nx.DiGraph()
    for node, data in graph.nodes(data=True):
        out.add_node(node, **{key: _graphml_value(val) for key, val in data.items()})
    for src, tgt, data in graph.edges(data=True):
        out.add_edge(src, tgt, **{key: _graphml_value(val) for key, val in data.items()})
    nx.write_graphml(out, path)


def rules2dot(text: str, dot_path: Path) -> None:
    if not PYBOOLNET_READY:
        print("pyboolnet is not installed properly.")
        sys.exit(1)
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
    graphml = dot_path.with_suffix(".graphml")
    write_graphml(graph, graphml)
    logger.debug(f"created {graphml}")


def write_image(dot: Path, image: Path, engine: str = "neato") -> None:
    """Render a dot file. The image format is the output suffix, such as png or pdf.

    pyboolnet's layout lookup is hardcoded to /usr/bin, so this calls the engine on PATH.
    """
    exe = shutil.which(engine)
    if exe is None:
        raise click.ClickException(f"{engine} not found on PATH")
    fmt = image.suffix.lstrip(".").lower()
    if not fmt:
        raise click.ClickException(f"image path needs an extension such as .png or .pdf: {image}")
    subprocess.run([exe, f"-T{fmt}", str(dot), "-o", str(image)], check=True)
    logger.debug(f"image written to {image}")


def temp_output() -> Path:
    """Empty PDF in ~/.config/bnet/tmp. Dot and GraphML are written beside it."""
    import os
    import tempfile

    from booleannet import TMP

    fd, name = tempfile.mkstemp(prefix="bnet-", suffix=".pdf", dir=TMP)
    os.close(fd)
    return Path(name)


def png_for(image: Path) -> Path:
    """PNG sibling of ``image``. The path itself when it is already PNG."""
    if image.suffix.lower() == ".png":
        return image
    return image.with_suffix(".png")


def show_png(path: Path) -> None:
    """Open ``path`` in a scrollable Tk window. Blocks until the window closes."""
    import tkinter as tk

    root = tk.Tk()
    root.title(path.name)
    photo = tk.PhotoImage(file=str(path))
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    view_w = min(photo.width(), int(screen_w * 0.9))
    view_h = min(photo.height(), int(screen_h * 0.85))

    canvas = tk.Canvas(root, width=view_w, height=view_h, background="white", highlightthickness=0)
    ys = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    xs = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.configure(scrollregion=(0, 0, photo.width(), photo.height()))
    canvas.image = photo

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    canvas.grid(row=0, column=0, sticky="nsew")
    ys.grid(row=0, column=1, sticky="ns")
    xs.grid(row=1, column=0, sticky="ew")
    root.mainloop()


@click.command()
@click.option("-i", "--input", "rules", type=click.Path(dir_okay=False, path_type=Path), help="BooleanNet rules file. Required unless rules are streamed via standard input.")
@click.option("-o", "--output", "image", type=click.Path(dir_okay=False, path_type=Path), help="Image output. Format follows the extension (png, pdf, svg). A .dot and a .graphml file with the same name are written beside it. When omitted, a temporary PDF and PNG are written in ~/.config/bnet/tmp and the PNG is shown in a window.")
@click.option("-e", "--engine", default="circo", show_default=True, type=click.Choice(ENGINES), help="Graphviz layout engine.")
@click.pass_context
def cli(ctx: click.Context, rules: Path | None, image: Path | None, engine: str) -> None:
    """Generates a Graphviz graph from a model."""
    found = read_rules(rules)
    if found is None:
        click.echo(ctx.get_help())
        ctx.exit()
    text, _source = found
    given = image is not None
    image = image or temp_output()
    dot = image.with_suffix(".dot")
    rules2dot(text, dot)
    write_image(dot, image, engine)
    if given:
        return
    png = png_for(image)
    if png != image:
        write_image(dot, png, engine)
    show_png(png)
