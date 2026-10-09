"""Import optional packages when a command first needs them."""

import importlib
import logging
import sys

from booleannet import logger


def load(name: str):
    """Import ``name``. Exit if that package is not installed."""
    root = name.partition(".")[0]
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        logger.error(f"{root} is not installed. See the docs.")
        logger.error(f"{exc}.")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"Error: {exc}")
        sys.exit(1)


def interaction_graph():
    """Callables that turn Boolean functions into a styled Graphviz graph."""
    pyboolnet = load("pyboolnet")
    forms = load("pyboolnet.boolean_normal_forms")
    graphs = load("pyboolnet.interaction_graphs")
    pyboolnet.log.setLevel(logging.INFO)
    return (
        forms.functions2primes,
        graphs.primes2igraph,
        graphs.add_style_interactionsigns,
        graphs.igraph2dot,
    )


def succession():
    """pyboolnet, pystablemotifs, and the succession-diagram exporter."""
    return (
        load("pyboolnet"),
        load("pystablemotifs"),
        load("pystablemotifs.export"),
    )
