import boolean2
from boolean2 import util


#
# Modifying states within a program
#
# Knocking node B out.
#
# Instead of a cycle, now a steady state is observed.
# 
# Code is identical to tutorial 3 after the state modification steps
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


#
# these nodes will be overexpressed (initialized to True)
#
on  = []

#
# these nodes will be set to false and their corresponding updating 
# rules will be  removed
#
off = ["B"]

#
# this modifies the original states to apply to overexpressed and knockouts
#
text = boolean2.modify_states(text, turnon=on, turnoff=off)

#
# see tutorial 3 for more details on what happens below
#

seen = {}

for i in range(10):
    model = boolean2.Model( text, mode='sync')
    model.initialize()
    model.iterate( steps=20 )

    size, index = model.detect_cycles() 
    
    # fingerprint of the first state
    key = model.first.fp()

    # keep only the first 10 states out of the 20
    values = [ x.fp() for x in model.states[:10] ]

    # store the fingerprinted values for each initial state
    seen [ key ] = (index, size, values )   

# print out the observed states
for first, values in seen.items():
    print 'Start: %s -> %s' % (first, values)