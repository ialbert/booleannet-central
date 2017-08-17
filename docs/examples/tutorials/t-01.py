from boolean2 import Model

text = """
# initial values
A = B = C = True

# updating rules

A* = A and C
B* = A and B
C* = not A
"""

model = Model( text=text, mode='sync')
model.initialize()
model.iterate( steps=5 )

for state in model.states:
    print state.A, state.B, state.C


