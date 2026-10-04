"""bnet command line."""

import click

from booleannet.commands.gviz import cli as gviz
from booleannet.commands.models import main as models
from booleannet.commands.simulate import cli as simulate

# Subcommand name -> click command. Add a new tool here.
COMMANDS = {
    "models": models,
    "graphviz": gviz,
    "simulate": simulate,
}

HELP = {"help_option_names": ["-h", "--help"]}


class BnetGroup(click.Group):
    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        super().format_commands(ctx, formatter)
        blocks = []
        for name in self.list_commands(ctx):
            cmd = self.get_command(ctx, name)
            if cmd is None or cmd.hidden:
                continue
            sub = click.Context(cmd, info_name=name, parent=ctx)
            blocks.append(cmd.get_help(sub))
        if blocks:
            formatter.write("\n\n")
            formatter.write("\n\n".join(blocks))
            formatter.write("\n")


@click.group("bnet", cls=BnetGroup, no_args_is_help=True, context_settings=HELP)
def main() -> None:
    """BooleanNet command line tools."""


for name, cmd in COMMANDS.items():
    main.add_command(cmd, name=name)
