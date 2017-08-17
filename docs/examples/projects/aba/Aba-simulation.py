"""
Absicis Acid Signaling - simulation

"""
import sys
import boolean2
from boolean2 import Model, util
import numpy

def find_stdev( text, node, knockouts, repeat, steps ):
    "Finds the standard deviation of a node with two modes"
    coll = {}
    fullt  = 10
    mode  = 'plde'
    step = fullt*10
    print '- start run, %s' % mode
    
    model = Model( mode=mode, text=text )
    results = {}
    values=[]
    coll={}
    for gene in knockouts:
        for i in xrange( repeat ):
            model.initialize( missing=util.randbool , defaults = {gene:(0.0,1.0,step*10)})
            model.iterate( steps=step, fullt=fullt ) 
            values = map( float,  model.data[node] )
            results.setdefault(gene,[]).append( values )
        
        resmat = numpy.array( results[gene] )  
        means  = numpy.mean( resmat , 0 )
        stdev  = numpy.std( resmat,0 )
        coll[gene]= [means, stdev]

    return coll
    
def run_plde( text, repeat, fullt ):
    "Runs the piecewise model on the text"

    steps  = fullt * 10
    model = Model( mode='plde', text=text )
    coll = []
    print '- start plde'
    for i in xrange( repeat ):
        model.initialize( missing=util.randbool )
        model.iterate( fullt=fullt, steps=steps )
        coll.append( model.data )
    
    return coll

def run_mutations( text, repeat, steps ):
    "Runs the asynchronous model with different mutations"

    # WT does not exist so it won't affect anything
    
    data = {}
    knockouts = 'WT S1P PA pHc ABI1 ROS'.split()
    for target in knockouts:
        print '- target %s' % target
        mtext  = boolean2.modify_states( text=text, turnoff=target )
        model = Model( mode='async', text=mtext )
        coll   = util.Collector()
        for i in xrange( repeat ):
            # unintialized nodes set to random
            model.initialize( missing=util.randbool )
            model.iterate( steps=steps )
            coll.collect( states=model.states, nodes=model.nodes )
        data[target] = coll.get_averages( normalize=True )

    return data

if __name__ == '__main__':
    # more repeats - better curve, this run takes about
    # plot was made with REPEAT=300, STEPS=10 it took about 5 minutes to run
    REPEAT = 300
    STEPS  = 10
    FULLT  = 10
    text = file( 'ABA.txt').read()
    data = find_stdev( text=text, node='Closure',knockouts='WT pHc PA'.split(), repeat=REPEAT, steps=STEPS)
    
    muts = run_mutations( text, repeat=REPEAT, steps=STEPS )
    obj  = dict( data=data, muts=muts )
    util.bsave( obj=obj, fname='ABA-run.bin' )
    print 'finished simulation'
