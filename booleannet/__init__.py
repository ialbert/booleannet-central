"""Boolean network modeling."""

from .about import __version__

import os
import shutil
import logging
from importlib.resources import files
from pathlib import Path

# ~/.config/bnet holds the models database and other local data.
# The packaged database is copied once; an existing file is left in place.
CONFIG = Path.home() / ".config" / "bnet"
TMP = CONFIG / "tmp"
MODELS = CONFIG / "models.json.gz"

# Configure the logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def prepare() -> None:
    """Create ~/.config/bnet and copy the default models database if it is missing."""
    CONFIG.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    if MODELS.exists():
        return
    packaged = files("booleannet").joinpath("data", "models.json.gz")
    partial = MODELS.with_suffix(".partial")
    with packaged.open("rb") as src, partial.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    partial.replace(MODELS)


prepare()

from . import util
from . import ruleparser, boolmodel, timemodel, tokenizer
from .tokenizer import modify_states


def Model(text, mode):
    "Factory function that returns the proper class based on the mode"

    # the text parameter may be a file that contains the rules
    if os.path.isfile(text):
        with open(text, 'rt') as fp:
            text = fp.read()

    if mode not in ruleparser.VALID_MODES:
        util.error('mode parameter must be one of %s' % ruleparser.VALID_MODES)

    if mode == ruleparser.TIME:
        return timemodel.TimeModel(mode='time', text=text)
    elif mode == ruleparser.PLDE:
        # matplotlib may not be installed
        # so defer import to allow other modes to be used
        from .plde import model
        return model.PldeModel(mode='plde', text=text)
    else:
        return boolmodel.BoolModel(mode=mode, text=text)


def all_nodes(text):
    "Returns all the nodes in the text"
    tokens = tokenizer.tokenize(text)
    return tokenizer.get_nodes(tokens)
