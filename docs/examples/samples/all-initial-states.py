import boolean2
from boolean2 import util, state, network

# updating rules

rules = """
    CIS* = Ca
    CaATPase* = Ca
    Ca* = CIS and (not CaATPase)
"""

# create the model
model = boolean2.Model( text=rules, mode='async')

# generates all states, set limit to a value to keep only the first that many states
# when limit is a number it will take the first that many initial states
initializer = state.all_initial_states( model.nodes, limit=None )

# the data is the inital data, the func is the initializer
for data, initfunc in initializer:
    # shows the initial values
    print(data)
    model.initialize(missing=initfunc)
    model.iterate(5)
