import boolean2, pylab

#
# Using Piecewise linear differential equations
#
# This initial condition leads to damped oscillations
# If A is set to False, a steady state is obtained.
#

text = """
A = True
B = False
C = False
D = True

1: B* = A or C
1: C* = A and not D
1: D* = B and C
"""

model = boolean2.Model( text, mode='plde')
model.initialize()
model.iterate( fullt=7, steps=150 )

#
# generate the plot
#
p1 = pylab.plot( model.data["B"] , 'ob-' )
p2 = pylab.plot( model.data["C"] , 'sr-' )
p3 = pylab.plot( model.data["D"] , '^g-' )
pylab.legend( [p1,p2,p3], ["B","C","D"])

pylab.show()  


