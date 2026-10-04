"""
Absicis Acid Signaling - simulation

- plotting saved data

"""
import sys
from pylab import *
from boolean2 import util
import numpy

def make_plot( fname ):
    obj  = util.bload( fname )
    data = obj['data']
    muts = obj['muts']
    genes=['WT','pHc','PA']
    
    # standard deviations
    def limit (x):
        if x>1:
            return 1
        elif x<0:
            return 0
        else:
            return x
    subplot(122)
    color=['b','c','r']
    plots=[]
    for gene,color in zip(genes,color):
        means, std = data[gene]
        plots.append(plot( means , linestyle = '-',color = color ))
        upper = list(map(limit, means+std))
        lower = list(map(limit, means-std))
        plot( upper , linestyle = '--',color = color, lw=2 )
        plot( lower , linestyle = '--', color = color , lw=2 )
    
    legend( plots, "WT pHc PA".split(), loc='best' )
    title( 'Variability of Closure in WT and knockouts' )
    xlabel( 'Time Steps' )
    ylabel( 'Percent' )
    ylim( (0.0, 1.1) )
    # 
    # Plots the effect of mutations on Closure
    #
    subplot(121)
    coll = []
    knockouts = 'WT S1P PA pHc ABI1'.split()

    for target in knockouts:
        p = plot( muts[target]['Closure'], 'o-')
        coll.append( p )

    legend( coll, knockouts, loc='best' )
    title( 'Effect of mutations on Closure' )
    xlabel( 'Time Steps' )
    ylabel( 'Percent' )
    ylim( (0, 1.1) )

if __name__ == '__main__':
    figure(num = None, figsize=(14, 7), dpi=80, facecolor='w', edgecolor='k')

    fname='ABA-run.bin'
    make_plot( fname )
    show()