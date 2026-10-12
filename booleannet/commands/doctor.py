"""Report whether optional packages used by the commands are installed."""

import os
import shutil
import subprocess
from pathlib import Path

import click

from booleannet.verify import PYBOOLNET_READY, READY

# Tools that read a model from stdin exit once stdin is closed.
RUN_TIMEOUT = 2


def _spawn(argv: list[str]) -> str:
    try:
        subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=RUN_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return "hangs"
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "failed"
    return "runs"


def _run_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    if not os.access(path, os.X_OK):
        return "not executable"
    state = _spawn([str(path)])
    return "failed" if state == "missing" else state


# mark, color. Yellow means the file is present but not usable as-is.
_STATUS = {
    "installed": ("✓", "green"),
    "runs": ("✓", "green"),
    "missing": ("✗", "red"),
    "failed": ("✗", "red"),
    "not executable": ("✗", "yellow"),
    "hangs": ("✗", "yellow"),
}


def _report(name: str, state: str, width: int, detail: str = "") -> None:
    mark, color = _STATUS[state]
    status = click.style(f"{mark} {state}", fg=color)
    tail = click.style(f"  {detail}", dim=True) if detail else ""
    click.echo(f"{name:<{width}}  {status}{tail}")


@click.command()
def cli() -> None:
    """Prints which packages are installed."""

    click.echo("#\n# Checking python packages ...\n#")

    width = max(len(name) for name in READY)
    for name, ready in READY.items():
        _report(f"# {name}", "installed" if ready else "missing", width)

    if not PYBOOLNET_READY:
        return

    click.echo("#\n# Checking pyboolenet executables ...\n#",nl=False)
    import pyboolnet

    names = list(pyboolnet.EXECUTABLES)
    width = max(width, *(len(name) for name in names))
    click.echo()
    for name in names:
        # Same path pyboolnet will execute, including ":" commands and binaries.
        target = pyboolnet.find_command(name)
        path = Path(target)
        if path.is_absolute():
            state = _run_status(path)
        else:
            # execvp would run whatever PATH names, so report that file.
            located = shutil.which(target) if target else None
            if located:
                state = _spawn([located])
                target = located
            else:
                state = "missing"
        _report(name, state, width, target)
    settings_file = Path(pyboolnet.ROOT_DIR, "binaries", "settings.cfg")
    click.echo(f"#\n# settings file: {settings_file}")


if __name__ == "__main__":
    cli()
