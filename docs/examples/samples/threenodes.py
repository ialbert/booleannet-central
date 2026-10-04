import boolean2
from boolean2 import util, state, network

# three nodes
rules = """
CIS* = Ca
CaATPase* = Ca
Ca* = CIS and (not CaATPase)
"""

def simulation( trans ):
    "One simulation step will update the transition graph"

    # create the model
    model = boolean2.Model( text=rules, mode='async')

    # generates all states, set limit to a value to keep only the first that many states
    # when limit is a number it will take the first that many initial states
    initializer = state.all_initial_states( model.nodes, limit=None )

    # the data is the inital data, the func is the initializer
    for data, initfunc in initializer:
        model.initialize(missing=initfunc)
        model.iterate(5)
        trans.add( model.states, times=list(range(5)) )

def main():
    "This is the main code that runs the simulation many times"

    # this will hold the transition graph
    trans = network.TransGraph( logfile='threenodes.log', verbose=True )

    # will run the simulation this many times
    for num in range( 10 ):
        simulation ( trans )

    # generate the colormap based on components
    colormap = network.component_colormap( trans.graph )

    # saves the transition graph into a gml file
    trans.save( 'threenodes.gml', colormap=colormap )

main()





