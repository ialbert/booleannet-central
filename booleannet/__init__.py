"""Boolean network modeling."""
import os

from . import util
from . import ruleparser, boolmodel, timemodel, tokenizer
from .tokenizer import modify_states

__version__ = "2.0"


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
