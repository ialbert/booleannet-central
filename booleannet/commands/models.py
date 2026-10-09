#!/usr/bin/env python3
"""List models or print one model in a chosen format.

    bnet models                 one summary row per model
    bnet models 1               bnet for model 001
    bnet models CORTICAL        model whose name contains CORTICAL
    bnet models 1 -f aeon       aeon for model 001
    bnet models -d models.json  read a chosen JSON database
    bnet models --show          pick a model and draw its graph
"""

import gzip
import json
import sys
from pathlib import Path

import click

from booleannet import MODELS

FORMATS = (
    "bnet",
    "booleannet",
    "sbml",
    "aeon",
    "bma",
    "inferred_graph",
    "metadata",
    "readme",
)
JSON_FORMATS = {"bma", "metadata"}


def load_models(path: Path | None):
    path = MODELS if path is None else path
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return json.load(f)


def summary_rows(models):
    rows = []
    for model_id, model in models.items():
        summary = model["summary"]
        rows.append((
            model_id,
            summary["name"],
            summary["variables"],
            summary["inputs"],
            summary["regulations"],
        ))
    rows.sort(key=lambda row: (row[2], row[0]))
    return rows


def summary_line(row, name_w: int) -> str:
    model_id, name, variables, inputs, regulations = row
    return f"{model_id}  {name:<{name_w}}  {variables:5}  {inputs:4}  {regulations:5}"


def list_summaries(models):
    rows = summary_rows(models)
    name_w = max(len(name) for _, name, _, _, _ in rows)
    click.echo(f"{'id':3}  {'name':<{name_w}}  {'var':>5}  {'in':>4}  {'reg':>5}")
    for row in rows:
        click.echo(summary_line(row, name_w))


def find_models(models, key: str) -> list[str]:
    """Match a number to an id, or text to an id or name."""
    if key.isdigit():
        model_id = key.zfill(3)
        return [model_id] if model_id in models else []
    needle = key.casefold()
    return [
        model_id
        for model_id, model in models.items()
        if needle in model_id.casefold() or needle in model["summary"]["name"].casefold()
    ]


def one_model(models, key: str) -> str:
    hits = find_models(models, key)
    if not hits:
        raise click.ClickException(f"no model {key}")
    if len(hits) > 1:
        lines = [f"{i}  {models[i]['summary']['name']}" for i in sorted(hits)]
        raise click.ClickException("several models match:\n" + "\n".join(lines))
    return hits[0]


def emit(model, fmt):
    value = model[fmt]
    if fmt in JSON_FORMATS:
        click.echo(json.dumps(value, ensure_ascii=False))
        return
    click.echo(value, nl=not value.endswith("\n"))


def rules_png(text: str, engine: str = "circo") -> bytes:
    """Render BooleanNet rules to PNG the same way ``bnet show`` does."""
    import tempfile

    from booleannet.commands.show import rules2dot, write_image

    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        dot = folder / "model.dot"
        png = folder / "model.png"
        rules2dot(text, dot)
        write_image(dot, png, engine)
        return png.read_bytes()


def show_gui(models, selected: str | None = None) -> None:
    """Dropdown of model summaries. The chosen model is drawn as an interaction graph."""
    import base64
    import threading
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import ttk

    from booleannet.commands.show import ENGINES

    rows = summary_rows(models)
    name_w = max(len(name) for _, name, _, _, _ in rows)
    header = f"{'id':3}  {'name':<{name_w}}  {'var':>5}  {'in':>4}  {'reg':>5}"
    labels = [summary_line(row, name_w) for row in rows]
    by_label = dict(zip(labels, rows))

    root = tk.Tk()
    root.title("models")
    families = set(tkfont.families(root))
    face = "Courier"
    for name in ("Menlo", "DejaVu Sans Mono", "Monaco", "Courier New", "Courier"):
        if name in families:
            face = name
            break
    mono = (face, 13)
    root.option_add("*TCombobox*Listbox.font", f"{face} 13")

    bar = tk.Frame(root)
    tk.Label(bar, text=header, font=mono, anchor="w").pack(fill="x")
    choice = tk.StringVar()
    combo = ttk.Combobox(
        bar,
        textvariable=choice,
        values=labels,
        font=mono,
        state="readonly",
        height=24,
    )
    combo.pack(fill="x", pady=(2, 0))
    tools = tk.Frame(bar)
    tools.pack(fill="x", pady=(4, 0))
    tk.Label(tools, text="engine").pack(side="left")
    engine = tk.StringVar(value="circo")
    engine_box = ttk.Combobox(
        tools,
        textvariable=engine,
        values=ENGINES,
        state="readonly",
        width=8,
    )
    engine_box.pack(side="left", padx=(6, 12))
    status = tk.StringVar(value="Select a model")
    tk.Label(tools, textvariable=status, anchor="w").pack(side="left", fill="x", expand=True)

    canvas = tk.Canvas(root, background="white", highlightthickness=0)
    ys = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    xs = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
    canvas.grid(row=1, column=0, sticky="nsew")
    ys.grid(row=1, column=1, sticky="ns")
    xs.grid(row=2, column=0, sticky="ew")
    root.geometry("800x600")
    root.minsize(480, 360)

    job = {"n": 0, "busy": False, "text": "", "caption": "", "engine": "circo"}
    lock = threading.Lock()

    def finish(data, err, caption, n):
        try:
            alive = root.winfo_exists()
        except tk.TclError:
            return
        if job["n"] != n or not alive:
            return
        if err is not None:
            status.set(str(err))
            return
        try:
            photo = tk.PhotoImage(data=base64.b64encode(data).decode("ascii"))
        except tk.TclError as exc:
            status.set(str(exc))
            return
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo
        canvas.configure(scrollregion=(0, 0, photo.width(), photo.height()))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        status.set(caption)

    def worker():
        while True:
            with lock:
                n = job["n"]
                text = job["text"]
                caption = job["caption"]
                layout = job["engine"]
            data = None
            err = None
            try:
                data = rules_png(text, layout)
            except Exception as exc:
                err = exc
            with lock:
                if job["n"] != n:
                    continue
                job["busy"] = False
            try:
                root.after(0, lambda d=data, e=err, c=caption, k=n: finish(d, e, c, k))
            except RuntimeError:
                return
            return

    def draw(_event=None):
        row = by_label.get(choice.get())
        if row is None:
            return
        model_id, name, variables, inputs, regulations = row
        layout = engine.get()
        caption = f"{model_id}  {name}    var {variables}  in {inputs}  reg {regulations}    {layout}"
        status.set(f"drawing  {model_id}  {name}  {layout}")
        with lock:
            job["n"] += 1
            job["text"] = models[model_id]["booleannet"]
            job["caption"] = caption
            job["engine"] = layout
            if job["busy"]:
                return
            job["busy"] = True
        threading.Thread(target=worker, daemon=True).start()

    def wheel(event):
        step = -1 if event.delta > 0 else 1
        if event.state & 0x1:
            canvas.xview_scroll(step, "units")
        else:
            canvas.yview_scroll(step, "units")

    combo.bind("<<ComboboxSelected>>", draw)
    engine_box.bind("<<ComboboxSelected>>", draw)
    canvas.bind("<MouseWheel>", wheel)

    if selected is not None:
        for label, row in zip(labels, rows):
            if row[0] == selected:
                choice.set(label)
                root.after(0, draw)
                break

    root.mainloop()


@click.command()
@click.argument("key", required=False)
@click.option(
    "-d",
    "--database",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="JSON or JSON.gz database. Default: ~/.config/bnet/models.json.gz.",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    default="booleannet",
    show_default=True,
    type=click.Choice(FORMATS),
    help="Model file to print when KEY is given.",
)
@click.option(
    "-s",
    "--show",
    "gui",
    is_flag=True,
    help="Open a window to pick a model and draw its interaction graph.",
)
def cli(key, database, fmt, gui):
    """List model summaries, or print one model in the chosen format.

    KEY is a number (1 or 001) or text matched against the id or name.
    With --show, open a dropdown of every model and draw the one you pick.
    """
    models = load_models(database)
    if gui:
        chosen = one_model(models, key) if key else None
        show_gui(models, chosen)
        return

    if key is None:
        list_summaries(models)
        return

    emit(models[one_model(models, key)], fmt)


if __name__ == "__main__":
    try:
        cli()
    except BrokenPipeError:
        sys.stdout.close()
        sys.exit(0)
