"""
Extending the model

Implementing a value getter. It gets triggered upon retrieving the value for a node.

Note that the values for B and C after update may be different
"""

import random
from boolean2 import Model, state, util

rules = """
A = B = C = True

A* = A
B* = A
C* = B
"""

# create a custom value getter
def get_value( state, name, p ):
    "Custom value getter"

    # detect the node of interest
    if name == 'B':
        print('now getting node %s' % name) 
        return random.choice ( (True, False) )
    else:
        # returns the normal value
        return getattr( state, name )

model = Model( text=rules, mode='sync')
model.parser.RULE_GETVALUE = get_value
model.initialize()
model.iterate( steps=5 )

for state in model.states:
    print(state.A, state.B, state.C)