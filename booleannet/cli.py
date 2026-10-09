"""bnet command line."""

import click


from booleannet.commands import models, show, simulate, diagram

# Subcommand name -> click command. Add a new tool here.
COMMANDS = {
    "models": models.cli,
    "show": show.cli,
    "simulate": simulate.cli,
    "diagram": diagram.cli,
}

HELP = {"help_option_names": ["-h", "--help"]}


@click.group("bnet", no_args_is_help=True, context_settings=HELP)
def main() -> None:
    """BooleanNet command line tools."""


for name, cmd in COMMANDS.items():
    main.add_command(cmd, name=name)
