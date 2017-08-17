#
# Demo script that displays the basic usage
#

# put the boolean library on the path
from boolean2 import Model, util

def start_iteration(index, model):
    if index < 5:
        state = True
    else:
        state = False

    model.last['A'] = state


#
# run the simulation
#
model = Model( mode='sync', text='demo-rules.txt')
model.initialize()
#model.RULE_START_ITERATION = start_iteration
model.iterate( steps=5 )

# all the states are now computed and stored internally

# you can print the states
for state in model.states:
    print state

print '-' * 20

# save states into a file
model.save_states( 'states.txt' )

# two ways to access nodes for a state
for state in model.states:
    print state['A'], state.A