"""bnet command line."""

import click

from booleannet.commands.diagram import cli as diagram
from booleannet.commands.gviz import cli as gviz
from booleannet.commands.models import main as models
from booleannet.commands.simulate import cli as simulate

# Subcommand name -> click command. Add a new tool here.
COMMANDS = {
    "models": models,
    "graphviz": gviz,
    "simulate": simulate,
    "diagram": diagram,
}

HELP = {"help_option_names": ["-h", "--help"]}


@click.group("bnet", no_args_is_help=True, context_settings=HELP)
def main() -> None:
    """BooleanNet command line tools."""


for name, cmd in COMMANDS.items():
    main.add_command(cmd, name=name)
