BooleanNet is a training tool that makes use of existing Boolean network models, methods and algorithms.

Website: https://www.booleannet.com/

## Environment setup

`booleannet` does not automatically install all of its dependencies. We recommend using [pixi][pixi] as a virtual environment manager. Here is a minimal example on how to set up a pixi enviroment:

```bash
pixi init
pixi add python=3.12 pip graphviz
pixi run pip install git+https://github.com/hklarner/pyboolnet@3.0.16
pixi shell
```

Your enviroment is now set up with the necessary dependencies to use `booleannet`.

[pixi]: https://pixi.prefix.dev/latest/

## Install booleannet

Inside the environment, install `booleannet` with:

```bash
pip install booleannet
```

It installs the `bnet` command line tool that implements a number of subcommands.

Run `bnet` with no arguments to see the available subcommands:

```
Usage: bnet [OPTIONS] COMMAND [ARGS]...

  BooleanNet command line tools.

Options:
  --help  Show this message and exit.

Commands:
  graphviz  Generates a Graphviz graph from a model.
  models    List model summaries, or print one model in the chosen format.
```

Add `--help` to any subcommand to see all available options.

## bnet models: manage known models

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

To get the rules for a specific model:

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

Get the rules in other formats:

```bash
# Get model 7 in BNet format
bnet models 7 -f bnet
```

## bnet graphviz: visualize a model

```bash
# If you have a model in a file
bnet graphviz -i model.txt
```

```bash
# You can pipe the rule to graphviz
bnet models CORTICAL-AREA-DEVELOPMENT | bnet graphviz
```

## Convert BBMB to JSON

This is used internally to transform the BBMB model repository to a single JSON file.

Skips a few large models that make the file too large.

```bash
python booleannet/bbm2json.py \
       --summary ~/src/biodivine-boolean-models/models/summary.csv 
       --models ~/src/biodivine-boolean-models/models 
       --skip 253,248,79,261,256
       --output models.json.gz
```

