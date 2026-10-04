"""Run a BooleanNet simulation."""

import re
import sys
from pathlib import Path

import click

from booleannet import Model, util
from booleannet.boolmodel import parse_state
from booleannet.util import BooleanError

MODES = ("sync", "async")
# Same node names as the lexer. A value is only 1, 0, or ?.
_STATE = re.compile(r"^[A-Za-z_+\-][A-Za-z0-9_+\-]*=[01?]$")


def bit(value) -> str:
    return "1" if value else "."


def warn_random(nodes) -> None:
    "Nodes with no initial value are filled at random."
    names = ", ".join(sorted(nodes))
    if names:
        click.echo(f"# Random initial state for {names}", err=True)


def check_states(states: tuple[str, ...]) -> list[str]:
    "Split positional states and require each piece to be NAME=0, NAME=1, or NAME=?."
    tokens = [tok for arg in states for tok in arg.split()]
    bad = [tok for tok in tokens if not _STATE.fullmatch(tok)]
    if bad:
        listed = ", ".join(bad)
        raise click.ClickException(f"initial state must look like A=1, A=0, or A=?: {listed}")
    return tokens


def rules_and_states(args: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    "Text on stdin is the rules, so every positional is an initial state. Otherwise the first is the file."
    piped = "" if sys.stdin.isatty() else sys.stdin.read()
    if piped.strip():
        return piped, args
    path = Path(args[0]) if args else Path("input.txt")
    states = args[1:] if args else ()
    if not path.is_file():
        raise click.ClickException(f"rules file not found: {path}")
    return path.read_text(), states


def selected(nodes: list[str], limit: str | None) -> list[str]:
    "Keep every node, or only the comma-separated names in limit, in that order."
    if not limit:
        return nodes
    wanted = [name.strip() for name in limit.split(",")]
    if any(not name for name in wanted):
        raise click.ClickException("empty name in --limit")
    known = set(nodes)
    bad = [name for name in wanted if name not in known]
    if bad:
        raise click.ClickException(f"unknown node in --limit: {', '.join(bad)}")
    return wanted


def run(text: str, mode: str, steps: int, state: str | None = None, limit: str | None = None) -> None:
    "Initialize a model, step it, and print each state."
    try:
        model = Model(text=text, mode=mode)
        if state is None:
            warn_random(model.uninit_nodes)
            model.initialize(missing=util.randbool)
        else:
            listed = set(parse_state(state))
            warn_random(model.update_nodes - listed)
            model.initialize(state=state)
        model.iterate(steps=steps)
    except BooleanError as exc:
        raise click.ClickException(str(exc)) from exc
    nodes = selected(list(model.first.keys()), limit)
    click.echo(" ".join(nodes))
    for state in model.states:
        click.echo(" ".join(bit(state[node]) for node in nodes))


@click.command()
@click.option("-m", "--mode", default="sync", show_default=True, type=click.Choice(MODES), help="Update mode.")
@click.option("-n", "--steps", default=5, show_default=True, type=click.IntRange(min=1), help="Number of update steps.")
@click.option("-l", "--limit", help="Comma-separated nodes to print, e.g. A,C,D.")
@click.option("--init", "init_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Initial conditions file. Assignments separated by spaces or newlines, e.g. A=1 B=0 C=?.")
@click.argument("args", nargs=-1, metavar="[FILE] [NODE=VALUE]...")
def cli(mode: str, steps: int, limit: str | None, init_path: Path | None, args: tuple[str, ...]) -> None:
    """Run a synchronous or asynchronous simulation.

    If stdin has data it reads that instead of a file.

    When stdin has data, every positional is an initial state.

    NODE=VALUE is NAME=0, NAME=1, or NAME=?. These override --init and init lines in the rules.
    """
    text, states = rules_and_states(args)
    tokens = check_states(states)
    parts = []
    if init_path is not None:
        parts.append(init_path.read_text())
    parts.extend(tokens)
    state = "\n".join(parts) if parts else None
    run(text, mode, steps, state, limit)
