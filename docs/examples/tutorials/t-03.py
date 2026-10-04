import boolean2
from boolean2 import Model

#
# Random sampling of initial conditions
#
# If A is set to False, a steady state is obtained.
#
# 
text = """
A = True
B = Random
C = Random
D = Random

B* = A or C
C* = A and not D
D* = B and C
"""

seen = {}

 
#
# the key will be the fingerprint of the first state 
#(some random inital conditions may be the same), it is fine to overwrite in this case
# as the 'sync' update rule is completely deterministic
#
for i in range(10):
    model = Model( text=text, mode='sync')
    model.initialize()
    model.iterate( steps=20 )

    # detect the cycles in the states
    size, index = model.detect_cycles() 
    
    # fingerprint of the first state
    key = model.first.fp()

    # keep only the first 10 states out of the 20
    values = [ x.fp() for x in model.states[:10] ]

    # store the fingerprinted values for each initial state
    seen [ key ] = (index, size, values )

# print out the observed states
for first, values in list(seen.items()):
    print('Start: %s -> %s' % (first, values))
