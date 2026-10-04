"""
Extending the model

Implementing a value setter. It gets triggered upon setting the value for a node.

Note that the values for A and B after update may be different, but B and C are always the same
"""

import random
from boolean2 import Model, state, util

rules = """
A = B = C = True

A* = A
B* = A
C* = B
"""

# create a custom value setter
def set_value( state, name, value, p ):
    "Custom value setter"

    # detect the node of interest
    if name == 'B':
        print('now setting node %s' % name) 
        value = random.choice ( (True, False) )
    
    # this sets the attribute
    setattr( state, name, value )
    return value

model = Model( text=rules, mode='sync')
model.parser.RULE_SETVALUE = set_value
model.initialize()
model.iterate( steps=5 )

for state in model.states:
    print(state.A, state.B, state.C)