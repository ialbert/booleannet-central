"""
Bordetella Bronchiseptica  simulation

- plotting the results

"""

from pylab import *
from boolean2 import util

def skip( data, step=10):
    "Takes every Nth point from a list or dictionary values"
    if type(data) == type([]):
        return data[::step]
    
    out = dict()
    for key, values in list(data.items()):
        values = values[::step]
        out[key] = values
    return out

def make_plot():
    run1, run2, t = util.bload( 'Bb-run.bin' )
    
    # take every 10th point
    step = 20
    run1 = skip(run1, step=step)
    run2 = skip(run2, step=step)
    t = skip(t, step=step)

    nodes = "EC PIC C PH IL12I IL12II".split()
    
    subplot(121)

    # drawing these first so that the symbols are under the other ones
    p1 = plot(t, run2['EC'], 'r^-', ms=7 )
    p2 = plot(t, run2['PIC'], 'r^-', ms=7 )
    
    p7 = plot(t, run1['EC'], 'b.-', ms=5 )
    p8 = plot(t, run1['PIC'], 'b--', ms=5 )
    
    xlabel( 'Time' )
    ylabel( 'Concentration' )
    title ( 'Innate Immune Response' )
    legend( [p1, p2, p7, p8], 'DEL-EC DEL-PIC WT-EC WT-PIC'.split(), loc='best')
    
    subplot(122)
   
    p3 = plot(t, run2['C'], 'r^-', ms=7 )
    p4 = plot(t, run2['PH'], 'ro-', ms=7 )
    p5 = plot(t, run2['IL12I'], 'r.-', ms=7 )
    p6 = plot(t, run2['IL12II'], 'rs-', ms=7 )
    
    p9 = plot(t, run1['C'], 'bo-', ms=5 )
    p10 = plot(t, run1['PH'] , 'bD-', ms=5 )
    p11 = plot(t, run1['IL12I'], 'b.-', ms=5 )
    p12 = plot(t, run1['IL12II'], 'b^-', ms=5 )
    
    xlabel( 'Time' )
    ylabel( 'Concentration' )
    title ( 'Adaptive Immune Response' )
    legend( [p3, p4, p5, p6, p9, p10, p11, p12], 'DEL-C DEL-PH DEL-IL12I DEL-IL12II WT-C WT-PH WT-IL12I WT-IL12II'.split(), loc='best')
    
if __name__ == '__main__':
    figure(num = None, figsize=(14, 7), dpi=80, facecolor='w', edgecolor='k')
    make_plot()
    savefig('Figure3.png')
    show()