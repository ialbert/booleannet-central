"""Edit Boolean rules and draw the succession diagram."""

import base64
import threading
import traceback
import tkinter as tk
from tkinter import filedialog
from tkinter import font as tkfont
from tkinter import scrolledtext

import click
import networkx as nx
import pyboolnet
import pystablemotifs as sm
import pystablemotifs.export as ex

MAX_SIMULATE_SIZE = 100
NODE_FONT = "20"
MONO_SIZE = 16
WIDTH = 1200
HEIGHT = 600
SPLIT = 2 / 5
VSPLIT = 1 / 2


def ui_font():
    face = tkfont.nametofont("TkDefaultFont").copy()
    face.configure(size=16)
    return face


def mono_font(root):
    families = set(tkfont.families(root))
    for name in ("Menlo", "DejaVu Sans Mono", "Monaco", "Courier New", "Courier"):
        if name in families:
            return (name, MONO_SIZE)
    return ("Courier", MONO_SIZE)

RULES = """
A* = A
B* = not C and not D or A and not C
C* = not A and not B
D* = A and D
"""


def trap_spaces(primes):
    found = pyboolnet.trap_spaces.compute_trap_spaces(primes, "min")
    spaces = []
    for space in found:
        for node in primes:
            if node not in space:
                space[node] = "?"
            else:
                space[node] = str(space[node])
        spaces.append(dict(sorted(space.items())))
    return spaces


def report(ar, primes):
    lines = [f"{len(ar.attractors)} attractors"]
    for attractor in ar.attractors:
        lines.append(str(attractor.attractor_dict))
    spaces = trap_spaces(primes)
    lines.append("")
    lines.append("minimal trap spaces")
    for space in spaces:
        lines.append(str(space))
    lines.append(f"number of minimal trapspaces: {len(spaces)}")
    return "\n".join(lines)


def render(graph):
    labels = {str(n): str(data.get("label", n)) for n, data in graph.nodes(data=True)}
    drawn = nx.DiGraph()
    drawn.add_nodes_from(labels)
    drawn.add_edges_from(graph.edges())
    A = nx.nx_agraph.to_agraph(drawn)
    for node in A.nodes():
        node.attr["shape"] = "box"
        node.attr["fontsize"] = NODE_FONT
        node.attr["label"] = labels.get(str(node), str(node))
    A.layout(prog="dot")
    return A.draw(format="png")


def write_graphml(graph, path):
    out = graph.copy()
    for node in out.nodes():
        for key, value in list(out.nodes[node].items()):
            out.nodes[node][key] = str(value)
    for edge in out.edges():
        for key, value in list(out.edges[edge].items()):
            out.edges[edge][key] = str(value)
    nx.write_graphml(out, path)


def analyze(rules, limit):
    primes = sm.format.create_primes(rules)
    ar = sm.AttractorRepertoire.from_primes(primes, max_simulate_size=limit)
    graph = ex.networkx_succession_diagram(ar, include_attractors_in_diagram=True)
    return report(ar, primes), render(graph), graph


class App:
    def __init__(self, root):
        self.root = root
        self.photo = None
        self.graph = None
        self.busy = False
        root.title("Succession diagram")
        root.geometry(f"{WIDTH}x{HEIGHT}")

        face = ui_font()
        self.status = tk.Label(root, text="", anchor="w", font=face)
        self.status.pack(side="bottom", fill="x", padx=8, pady=4)

        pane = tk.PanedWindow(root, orient="horizontal", sashwidth=6)
        pane.pack(fill="both", expand=True)
        self.pane = pane
        root.after_idle(self._split)

        left = tk.Frame(pane)
        right = tk.Frame(pane)
        pane.add(left, minsize=360)
        pane.add(right, minsize=320)

        vpane = tk.PanedWindow(left, orient="vertical", sashwidth=6)
        vpane.pack(fill="both", expand=True)
        self.vpane = vpane
        top = tk.Frame(vpane)
        bottom = tk.Frame(vpane)
        vpane.add(top, minsize=80)
        vpane.add(bottom, minsize=80)

        mono = mono_font(root)
        self.rules = scrolledtext.ScrolledText(top, wrap="word", font=mono, undo=True)
        self.rules.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.rules.insert("1.0", RULES.strip() + "\n")
        self.rules.bind("<Control-Return>", self._shortcut)

        limit_row = tk.Frame(bottom)
        limit_row.pack(anchor="w", fill="x", padx=8, pady=(4, 0))
        tk.Label(limit_row, text="Simulate size", font=face).pack(side="left")
        self.limit = tk.Entry(limit_row, width=8, font=mono)
        self.limit.insert(0, str(MAX_SIMULATE_SIZE))
        self.limit.pack(side="left", padx=(8, 0))

        row = tk.Frame(bottom)
        row.pack(anchor="w", fill="x", padx=8, pady=4)
        self.button = tk.Button(row, text="Draw", command=self.draw, font=face)
        self.button.pack(side="left")
        tk.Label(row, text="(shortcut: Ctrl-Enter)", font=face).pack(side="left", padx=(12, 0))

        self.out = scrolledtext.ScrolledText(bottom, wrap="none", font=mono, state="disabled")
        self.out.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.canvas = tk.Canvas(right, background="white", highlightthickness=0)
        ys = tk.Scrollbar(right, orient="vertical", command=self.canvas.yview)
        xs = tk.Scrollbar(right, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.save = tk.Button(right, text="Save", command=self.save_graph, font=face, state="disabled")
        self.save.grid(row=2, column=0, sticky="w", padx=8, pady=4)

    def _split(self):
        self.root.update_idletasks()
        width = self.pane.winfo_width()
        height = self.vpane.winfo_height()
        if width <= 1 or height <= 1:
            self.root.after(50, self._split)
            return
        self.pane.sash_place(0, int(width * SPLIT), 1)
        self.vpane.sash_place(0, 1, int(HEIGHT * VSPLIT))

    def _shortcut(self, _event):
        self.draw()
        return "break"

    def draw(self):
        if self.busy:
            return
        try:
            limit = int(self.limit.get().strip())
        except ValueError:
            self.status.configure(text="simulate size must be an integer")
            return
        self.busy = True
        self.button.configure(state="disabled")
        self.status.configure(text="Computing...")
        rules = self.rules.get("1.0", "end-1c")
        threading.Thread(target=self._work, args=(rules, limit), daemon=True).start()

    def _work(self, rules, limit):
        try:
            text, png, graph = analyze(rules, limit)
        except Exception as exc:
            traceback.print_exc()
            msg = str(exc).strip().splitlines()
            line = msg[0] if msg else type(exc).__name__
            self.root.after(0, self._fail, line)
            return
        print(text)
        self.root.after(0, self._show, text, png, graph)

    def _fail(self, line):
        if not self._alive():
            return
        self.status.configure(text=line)
        self._ready()

    def _show(self, text, png, graph):
        if not self._alive():
            return
        self._set_out(text)
        self.graph = graph
        self.save.configure(state="normal")
        self.photo = tk.PhotoImage(data=base64.b64encode(png))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, self.photo.width(), self.photo.height()))
        self.status.configure(text="")
        self._ready()

    def save_graph(self):
        if self.graph is None:
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".graphml",
            filetypes=[("GraphML", "*.graphml")],
            initialfile="diagram.graphml",
        )
        if not path:
            return
        try:
            write_graphml(self.graph, path)
        except Exception as exc:
            traceback.print_exc()
            msg = str(exc).strip().splitlines()
            self.status.configure(text=msg[0] if msg else type(exc).__name__)
            return
        print(path)
        self.status.configure(text=path)

    def _set_out(self, text):
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        self.out.insert("1.0", text)
        self.out.configure(state="disabled")

    def _ready(self):
        self.busy = False
        self.button.configure(state="normal")

    def _alive(self):
        try:
            return bool(self.root.winfo_exists())
        except tk.TclError:
            return False


@click.command()
def cli() -> None:
    """Open the succession diagram editor."""
    root = tk.Tk()
    App(root)
    root.mainloop()
