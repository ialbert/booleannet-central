"""
Bordetella Bronchiseptica  simulation

- contains the node overrides

"""
import math
from boolean2.plde import helper

# the localdefs module contains reusable function definitions
from localdefs import *

def override( node, indexer, tokens, param ):
    
    if node == 'Th1t2':
        newval = helper.conc( node, indexer )
        thr    = helper.threshold(node, indexer)
        conc   = helper.conc( 'Th1I', indexer )
        expr = "%s = int( %s > %s)" % (newval, conc, thr)
        return expr
                
    if node == 'PIC':
        newval = helper.newval(node, indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = "%s = ( %s ) * 3" % (newval, piece)
        return expr
                
    elif node == 'Oag':        
        newval = helper.newval(node, indexer)
        newBb = helper.newval('Bb', indexer)
        expr = "%s = %s" %(newval,newBb)
        return expr	
		        
    elif node == 'MPII':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'MPI', indexer, param)
        decayMPII = helper.decay(node, indexer)
        expr = '%s = %s - c%s * %s' % (newval, hill, indexer['MPII'], decayMPII)
        return expr
        
    elif node == 'MPI':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'MPI', indexer, param)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = '%s = %s - %s' % (newval, piece, hill)
        return expr
        
    elif node == 'DCII':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'DCI', indexer, param)
        decayDCII = helper.decay(node, indexer)
        expr = '%s = %s - c%s * %s' % (newval, hill, indexer['DCII'], decayDCII)
        return expr
        
    elif node == 'DCI':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'DCI', indexer, param)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = '%s = %s - %s' % (newval, piece, hill)
        return expr
        
    elif node == 'Th1I':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'Th1II', indexer, param)
        decayTh1I = helper.decay(node, indexer)
        expr = '%s = %s - c%s * %s' % (newval, hill, indexer['Th1I'], decayTh1I)
        return expr
        
    elif node == 'Th1II':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'Th1II', indexer, param)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = '%s = %s - %s' % (newval, piece, hill)
        return expr        
    
    elif node == 'Th2I':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'Th2II', indexer, param)
        decayTh2I = helper.decay(node, indexer)
        expr = '%s = %s - c%s * %s' % (newval, hill, indexer['Th2I'], decayTh2I)
        return expr
        
    elif node == 'Th2II':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'Th2II', indexer, param)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = '%s = %s - %s' % (newval, piece, hill)
        return expr        
    
    elif node == 'TrI':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'TrII', indexer, param)
        decayTrI = helper.decay(node, indexer)
        expr = '%s = %s - c%s * %s' % (newval, hill, indexer['TrI'], decayTrI)
        return expr
        
    elif node == 'TrII':
        newval = helper.newval(node, indexer)
        hill = helper.hill_func( 'TrII', indexer, param)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        expr = '%s = %s - %s' % (newval, piece, hill)
        return expr        
                                                
    elif node == 'IL10I':
        newIL101 = helper.newval('IL10I' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        prop_text = make_slow_prop( node='IL10I', indexer=indexer, param=param) 
        step1 = 'PROP = %s' % prop_text
        step2 = '%s = (PROP * %s)*2' % ( newIL101, piece)
        expr = [ step1, step2 ]
        return expr
     
    elif node == 'IL10II':
        newIL102 = helper.newval('IL10II' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        step2 = '%s = ((1-PROP) * %s)*2' % ( newIL102, piece)
        expr = [ step2 ]
        return expr
    
    elif node == 'IFNgI':
        newIFNg1 = helper.newval('IFNgI' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        prop_text = make_slow_prop( node='IFNgI', indexer=indexer, param=param) 
        step1 = 'PROP = %s' % prop_text
        step2 = '%s = (PROP * %s) * 0.5' % ( newIFNg1, piece)
        expr = [ step1, step2 ]
        return expr
     
    elif node == 'IFNgII':
        newIFNg2 = helper.newval('IFNgII' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        step2 = '%s = ((1-PROP) * %s)*0.5' % ( newIFNg2, piece)
        expr = [ step2 ]
        return expr
            
    elif node == 'IL4II':
        newIL42 = helper.newval('IL4II' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        step2 = '%s = (PROP * %s)*2' % ( newIL42, piece)
        expr = [ step2 ]
        return expr
             
    elif node == 'IL4I':
        newIL41 = helper.newval('IL4I' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        prop_text = make_slow_prop( node='IL4I', indexer=indexer, param=param) 
        step1 = 'PROP = %s' % prop_text
        step2 = '%s = ((1-PROP) * %s)*2' % ( newIL41, piece)
        expr = [ step1, step2 ]
        return expr
            
    elif node == 'IL12II':
        newIL122 = helper.newval('IL12II' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        step2 = '%s = PROP * %s' % ( newIL122, piece)
        expr = [ step2 ]
        return expr
             
    elif node == 'IL12I':
        newIL121 = helper.newval('IL12I' , indexer)
        piece  = helper.piecewise( tokens=tokens, indexer=indexer )
        prop_text = make_slow_prop( node='IL12I', indexer=indexer, param=param) 
        step1 = 'PROP = %s' % prop_text
        step2 = '%s = (1-PROP) * %s' % ( newIL121, piece)
        expr = [ step1, step2 ]
        return expr
                                                
    elif node == 'Bb':
        newval = helper.newval(node, indexer)
        conc   = helper.conc( node, indexer)
        concPH = helper.conc( 'PH', indexer)
        expr   = '%s = ( %s * ( 1 - %s) ) - %s*%s' % ( newval, conc, concPH, conc, conc)
        return expr
        
    elif node == 'PH':
        newval = helper.newval(node, indexer)
        concMP = helper.conc( 'MPI', indexer)
        concRP = helper.conc( 'RP', indexer)
        concAgAb = helper.conc( 'AgAb', indexer)
        concC = helper.conc( 'C', indexer)
        concBb = helper.conc( 'Bb', indexer)                
        expr = '%s = ((%s + %s) * (%s * 0.4 + %s * 0.2 + 0.02)) * %s' % (newval, concMP, concRP, concAgAb, concC, concBb)
        return expr
        
    return None
