import boolean2, pylab

text = """
A = True
B = True 
C = False
1: A* = not C 
2: B* = A and B
3: C* = B
"""

model = boolean2.Model( text=text, mode='plde' )
model.initialize()
model.iterate( fullt=7, steps=100 )

p1 = pylab.plot( model.data['A'] , 'ob-' )
p2 = pylab.plot( model.data['B'] , 'sr-' )
p3 = pylab.plot( model.data['C'] , '^g-' )
pylab.legend( [p1,p2,p3], "A B C".split(), loc="best")

pylab.show()