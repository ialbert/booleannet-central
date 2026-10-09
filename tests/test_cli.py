"""Smoke tests: each bnet command runs and exits without error."""

from pathlib import Path

import tkinter as tk
from click.testing import CliRunner

from booleannet.cli import main

RULES = Path(__file__).parent / "rules" / "model01.txt"
RUNNER = CliRunner()


def invoke(*args):
    result = RUNNER.invoke(main, args)
    assert result.exit_code == 0, result.output
    return result


def test_help():
    # no_args_is_help prints usage and exits 2. That is the help path, not a crash.
    bare = RUNNER.invoke(main, [])
    assert isinstance(bare.exception, SystemExit)
    assert "Commands:" in bare.output
    invoke("--help")
    for name in ("models", "show", "simulate", "diagram"):
        invoke(name, "--help")


def test_models():
    invoke("models")
    invoke("models", "7")


def test_simulate():
    args = ("simulate", str(RULES), "A=1", "B=?", "-n", "3")
    invoke(*args, "-m", "sync")
    invoke(*args, "-m", "async")


def test_show(tmp_path):
    rules = tmp_path / "rules.txt"
    rules.write_text("A* = B\nB* = A\n")
    image = tmp_path / "graph.png"
    invoke("show", "-i", str(rules), "-o", str(image), "-e", "circo")
    assert image.is_file()
    assert image.stat().st_size > 0


def test_diagram(monkeypatch):
    monkeypatch.setattr(tk.Tk, "mainloop", lambda self: self.destroy())
    invoke("diagram")
