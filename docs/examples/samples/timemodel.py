#
#
# demonstrate the use of the time model
#
# generates a transition graph for all possible initial conditions
#

import boolean2
from boolean2 import state, network

def simulation( ):

    # creating the transition graph, the verbose parameter sets the nodes to 
    # either short names like 1, 2, 3 or long (binary) names like 10001
    #
    # the logfile contains the transition edges and the identity of the nodes
    trans = network.TransGraph( logfile='timemodel.log', verbose=True )

    # create the model, you may use a text string or a filename
    model = boolean2.Model( text='timemodel.txt', mode='time')

    
    # here we generates all initial states
    #
    # IMPORTANT: Only uninitialized nodes will get new values,
    # to keep a node the same in all iterations initialize it in the rules
    #
    # when the limit parameter is a number it will takes the first that 
    # many initial values, leave it to None to use all initial values
    initializer = state.all_initial_states( model.nodes, limit=None )

    # the data is a dictionary with the inital data, print it to see what it contains
    # the initfunc is the initializer function that can be used
    for data, initfunc in initializer:
        model.initialize( missing=initfunc )
        model.iterate( 12 )
        trans.add( model.states, times=range(12) )

    # saves the transition graph into a gml file
    trans.save( 'timemodel.gml' )


# this runs the simulation
if __name__ == '__main__':
    simulation()