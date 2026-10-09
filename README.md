# Booleannet - Boolean network simulations

`booleannet` is a training tool that makes use of existing Boolean network models, methods and algorithms.

It installs the `bnet` command line tool that implements a number of subcommands.

Additional help and documentation at: <https://www.booleannet.com/>

The software was first published as [Boolean network simulations for life scientists][1751-0473-3-16] by *István Albert*, *Juilee Thakar*, *Song Li*, *Ranran Zhang*, and *Réka Albert* in *Source Code for Biology and Medicine (2008)*. The field has moved on and developed quite a bit since the paper. The `booleannet` package is now a tool better suited for learning and exploring Boolean networks. 

[1751-0473-3-16]: https://link.springer.com/article/10.1186/1751-0473-3-16

## Environment setup

`booleannet` works with many libraries, but not everyone needs all of them, so optional dependencies are not installed automatically. We recommend [pixi][pixi] as a virtual environment manager. Here is a minimal example of how to set up a pixi environment:

```bash
pixi init
pixi add python=3.12 pip graphviz
pixi run pip install git+https://github.com/hklarner/pyboolnet@3.0.16
pixi shell
```

[pixi]: https://pixi.prefix.dev/latest/
[graphviz]: https://graphviz.org/
[pyboolnet]: https://github.com/hklarner/pyboolnet
[pystablemotifs]: https://github.com/jcrozum/pystablemotifs

## Install booleannet

Inside the environment, install `booleannet` with:

```bash
pip install --upgrade booleannet
```

Run `bnet` with no arguments to see the available subcommands:

```
Usage: bnet [OPTIONS] COMMAND [ARGS]...

  BooleanNet command line tools.

Options:
  -h, --help  Show this message and exit.

Commands:
  diagram   Open the succession diagram editor.
  models    List model summaries, or print one model in the chosen format.
  show      Generates a Graphviz graph from a model.
  simulate  Run a synchronous or asynchronous simulation.
```

Add `--help` to any subcommand to see all available options.

## models: manage known models

The `bnet models` subcommand operates on models from the [Biodivine Boolean Models (BBM) Benchmark Dataset][bbmb]. 

[bbmb]: https://bbm.sybila.fi.muni.cz/

```bash
# List all models
bnet models | head
```

prints models by increasing number of variables:

```
id   name                                                   var    in    reg
165  EGGSHELL-PATTERNING-PHENOMOENOLOGICAL                    4     4     16
170  DROSOPHILA-GAP-B                                         4     3     15
007  CORTICAL-AREA-DEVELOPMENT                                5     0     14
109  ASYMMETRIC-CELL-DIVISION-A                               5     0     15
169  DROSOPHILA-GAP-A                                         5     2     17
171  DROSOPHILA-GAP-C                                         5     2     20
172  DROSOPHILA-GAP-D                                         5     2     12
184  P53-MDM2-NETWORK                                         5     1     15
189  TRP-BIOSYNTHESIS                                         5     1     13
...
```

A key is a model number (`7` or `007`) or text matched against the id or name. The default format is BooleanNet rules:

```bash
# Get rules for model 7
bnet models 7
```

prints:

```
Coup_fti* = not (Fgf8 or Sp8) or not (Sp8 or Fgf8)
Emx2* = Coup_fti and not (Fgf8 or Sp8 or Pax6)
Fgf8* = Fgf8 and Sp8 and not Emx2
Pax6* = Sp8 and not (Emx2 or Coup_fti)
Sp8* = Fgf8 and not Emx2
```

You can also get the rules for a model by name:

```bash
# Get rules for model by name
bnet models CORTICAL-AREA-DEVELOPMENT
```

Other formats: `bnet`, `booleannet`, `sbml`, `aeon`, `bma`, `inferred_graph`, `metadata`, `readme`.

```bash
bnet models 7 -f bnet
```

The command `bnet models --show` opens a window with a dropdown of every model and draws the interaction graph of the one you pick. The window uses the same Graphviz engines as the `bnet show` command.

```bash
# Select model from dropdown menu.
bnet models --show

# Show model 7 from dropdown menu.
bnet models 7 --show
```

## simulate: run a model

Suppose your `model.txt` contains:

```
B* = A or C
C* = A and not D
D* = B and C
```

Then you can run the model with:

```bash
# Rules from a file. Sets initial state to A and B (random). Runs for 5 steps.
bnet simulate model.txt A=1 B=? -n 5
```

One row per iteration, and one column per node. The first row is the initial state. `1` is on, `.` is off. It sets a random initial state for any node that is not set explicitly.


```
# Random initial state for C, D
A B C D
1 1 . 1
1 1 . .
1 1 1 .
1 1 1 1
1 1 . 1
1 1 . .
```

You can send a file via stdin and pipe into the simulation:

```bash
bnet models CORTICAL-AREA-DEVELOPMENT | bnet simulate Pax6=0 Emx2=1 Fgf8=1 Sp8=0 Coup_fti=1 -n 4
```

prints:

```
Coup_fti Emx2 Fgf8 Pax6 Sp8
1 1 1 . .
. . . . .
1 . . . .
1 1 . . .
1 1 . . .
```

The default mode is `sync`. `-m async` uses random-order asynchronous updates. `--init` reads initial conditions from a file (`A=1 B=0 C=?`, spaces or newlines). Positional `NODE=VALUE` assignments override `--init` and any init lines in the rules. `-l` prints only the listed nodes, in that order:

```bash
bnet simulate model.txt A=1 B=? -n 5 -l A,C
```

## show: visualize a model

`bnet show` builds a signed interaction graph. Rules come from `-i` or from stdin.

```bash
# Show model from a file.
bnet show -i model.txt

# Stream model rules into the show command.
bnet models CORTICAL-AREA-DEVELOPMENT | bnet show
```

With no `-o`, it writes a temporary files. Add `-o` to write to a file and not open a window.

`-e` picks the layout engine (`dot`, `neato`, `fdp`, `sfdp`, `circo`, `twopi`; default `circo`).

```bash
bnet show -i model.txt -o model.pdf -e circo
```

## diagram: succession diagram

`bnet diagram` opens an editor for Boolean rules and their succession diagram.

The left side is a rules editor (a small example is filled in) and a simulate-size limit (default 100). Draw, or Ctrl-Enter, computes attractors and minimal trap spaces, lists them in the lower pane, and draws the succession diagram on the right. Save writes the diagram as GraphML.

This software requires [pystablemotifs][pystablemotifs].

[pystablemotifs]: https://github.com/jcrozum/pystablemotifs

```bash
bnet diagram
```

