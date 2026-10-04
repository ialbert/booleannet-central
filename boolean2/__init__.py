"""Compatibility shim. The simulator lives in booleannet."""
import sys

import booleannet
import booleannet.plde.defs
import booleannet.plde.helper
import booleannet.plde.model
import booleannet.plde.rk4
from booleannet import Model, all_nodes, modify_states
from booleannet import boolmodel, network, odict, plde, ruleparser, state, timemodel, tokenizer, util

__version__ = booleannet.__version__

_subs = {
    'boolmodel': boolmodel,
    'network': network,
    'odict': odict,
    'plde': plde,
    'ruleparser': ruleparser,
    'state': state,
    'timemodel': timemodel,
    'tokenizer': tokenizer,
    'util': util,
    'plde.defs': booleannet.plde.defs,
    'plde.helper': booleannet.plde.helper,
    'plde.model': booleannet.plde.model,
    'plde.rk4': booleannet.plde.rk4,
}
for _name, _mod in _subs.items():
    sys.modules[__name__ + '.' + _name] = _mod
