"""
Bordetella Bronchiseptica  simulation

Takes about 30 seconds to run
"""
import boolean2
from boolean2 import Model, util 
from boolean2.plde import helper


# the overrides.py module contains all node overrides
import overrides

# setting up simulation parameters
FULLT = 50
STEPS = FULLT*50

#
# the helper functions allow for easy parameter extraction from a csv files
#

# parameters for concentration, decay and treshold for various nodes
CONC_PARAMS = helper.read_parameters( 'Bb-concentration.csv' )

# parameters for compartment ratios and fluctuations
COMP_PARAMS = helper.read_parameters( 'Bb-compartmental.csv' )

# use data from the sixth row (it is zero based counting!) in the file
CONC = CONC_PARAMS[5]
COMP = COMP_PARAMS[5]

# helper function that Binds the local override to active COMP parameter
def local_override( node, indexer, tokens ):
    return overrides.override( node, indexer, tokens, COMP )

#
# there will be two models, one for WT and the other for a BC knockout
#
wt_text = file('Bb.txt').read()
bc_text = boolean2.modify_states( text=wt_text, turnoff= [ "BC"  ] )

model1 = Model( text=wt_text, mode='plde' )
model2 = Model( text=bc_text, mode='plde' )

model1.OVERRIDE = local_override
model2.OVERRIDE = local_override

model1.initialize( missing = helper.initializer( CONC )  )
model2.initialize( missing = helper.initializer( CONC )  )

# see localdefs for all function definitions
model1.iterate( fullt=FULLT, steps=STEPS, localdefs='localdefs' )
model2.iterate( fullt=FULLT, steps=STEPS, localdefs='localdefs' )

# saves the simulation resutls into a file
data = [ model1.data, model2.data, model1.t ]

# it is a binary save ( pickle )
util.bsave(data, 'Bb-run.bin' )
