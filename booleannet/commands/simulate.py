"""Run a BooleanNet simulation."""

from pathlib import Path

import click

from booleannet import Model, util
from booleannet.boolmodel import parse_state
from booleannet.commands.gviz import read_rules
from booleannet.util import BooleanError

MODES = ("sync", "async")


def bit(value) -> str:
    return "1" if value else "."


def warn_random(nodes) -> None:
    "Nodes with no initial value are filled at random."
    names = ", ".join(sorted(nodes))
    if names:
        click.echo(f"# Warning: random initial state for {names}", err=True)


def run(text: str, mode: str, steps: int, state: str | None = None) -> None:
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
    nodes = list(model.first.keys())
    click.echo(" ".join(nodes))
    for state in model.states:
        click.echo(" ".join(bit(state[node]) for node in nodes))


@click.command()
@click.option("-i", "--input", "rules", type=click.Path(dir_okay=False, path_type=Path), help="BooleanNet rules file. Used when stdin is a terminal. Default: input.txt.")
@click.option("-m", "--mode", default="sync", show_default=True, type=click.Choice(MODES), help="Update mode.")
@click.option("-n", "--steps", default=5, show_default=True, type=click.IntRange(min=1), help="Number of update steps.")
@click.option("--init", "init_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Initial conditions file. Assignments separated by spaces or newlines, e.g. A=1 B=0 C=?.")
@click.argument("states", nargs=-1, metavar="NODE=VALUE")
def cli(rules: Path | None, mode: str, steps: int, init_path: Path | None, states: tuple[str, ...]) -> None:
    """Run a synchronous or asynchronous simulation.

    NODE=VALUE sets an initial state, for example A=1 B=0 C=?.
    These override --init and any init lines in the rules file.
    """
    text, _source = read_rules(rules)
    parts = []
    if init_path is not None:
        parts.append(init_path.read_text())
    parts.extend(states)
    state = "\n".join(parts) if parts else None
    run(text, mode, steps, state)
