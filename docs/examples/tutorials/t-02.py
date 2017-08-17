import pylab
from boolean2 import Model

#
# This initial condition leads to a cycle of period 4.
# If A is set to False, a steady state is obtained.
#
# 
text = """
A = True
B = False
C = False
D = True

B* = A or C
C* = A and not D
D* = B and C
"""

model = Model( text=text, mode='sync')
model.initialize()
model.iterate( steps=15 )

# the model data attribute holds the states keyed by nodes
for node in model.data:
    print node, model.data[node]

# this is a helper function that reports the cycle lengths 
# and the  index at wich the cycle started
model.report_cycles()

#
# the same thing as above but
# will not print only return the two parameters
#
print model.detect_cycles()    

#
# this is how one plots the values, delete this below
# if matplotlib is not installed
#
p1 = pylab.plot( model.data["B"] , 'ob-' )
p2 = pylab.plot( model.data["C"] , 'sr-' )
pylab.legend( [p1,p2], ["B","C"])
pylab.ylim((-0.1,1.1))
pylab.show()    


