"""
Extending the model

Implementing a custom AND rule

It gets triggered upon hitting the AND operation and it will return the 
true result of A and B 3 times out of 4, and picks a random value for the rest.

"""

import random
from boolean2 import Model, state, util

rules = """
A = B = C = True

A* = A
B* = A and B
C* = B
"""

# create a custom value setter
def and_function( a, b, p ):
    "Custom value setter"
    
    # expected value
    good  = a and b

    # perturbed values
    guess = random.choice( (True, False) )
    
    values = [ good, good, good, guess ]
    
    # picks one
    return random.choice( values )

model = Model( text=rules, mode='sync')
model.parser.RULE_AND = and_function
model.initialize()
model.iterate( steps=5 )

for state in model.states:
    print(state.A, state.B, state.C)