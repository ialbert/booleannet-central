
import sys, os
from itertools import *
from collections import OrderedDict 

from boolean2.boolmodel import BoolModel
from boolean2 import util, tokenizer
from . import helper
import imp

try:
    import pylab
    from pylab import arange, rk4
except ImportError:
    util.error( "matplotlib is missing, install it from: http://matplotlib.sourceforge.net/")

def default_override( node, indexer, tokens ):
    """
    Gets called before the generating each equation.
    If this function returns anything other than None 
    it will override the equation
    """
    return None

def default_equation( tokens, indexer ):
    """
    Default equation generator, override this to generate
    other equations without explicit overrides
    """
    node = tokens[1].value
    text = helper.change(node, indexer) + ' = ' + helper.piecewise(tokens, indexer)
    return text

def boolmapper (value):
    if type(value) == tuple:
        return value
    else:
        return util.bool_to_tuple(value)

class PldeModel( BoolModel ):
    """
    This class generates python code that will be executed inside 
    the Runge-Kutta integrator.
    """
    def __init__(self, text, mode='plde'):
        
        # run the regular boolen engine for one step to detect syntax errors
        model = BoolModel(text=text, mode='sync')
        model.initialize( missing=util.randbool )
        model.iterate( steps=1 )

        # onto the main initialization
        self.INIT_LINE  = helper.init_line
        self.OVERRIDE   = default_override
        self.DEFAULT_EQUATION = default_equation
        self.EXTRA_INIT = ''

        # setting up this engine
        BoolModel.__init__(self, text=text, mode=mode)
        self.dynamic_code = '*** not yet generated ***'
        self.lazy_data = {}
    
    @property
    def data(self):
        "For compatibility with the async engine"
        return self.lazy_data

    def initialize(self, missing=None, defaults={} ):
        "Custom initializer"
        BoolModel.initialize( self, missing=missing, defaults=defaults )
        
        # will also maintain the order of insertion
        self.mapper  = OrderedDict() 
        self.indexer = {}
        
        # this will maintain the order of nodes
	
        self.nodes = list(self.nodes)
        self.nodes.sort()
        for index, node in enumerate(self.nodes):
            triplet = self.first[node]
            self.mapper[node] = ( index, node, triplet )
            self.indexer[node] = index
        
        # a sanity check
        assert self.nodes == list(self.mapper.keys())

    def generate_init( self, localdefs ):
        """
        Generates the initialization lines
        """
        init = [ ]
        
        init.extend( self.EXTRA_INIT.splitlines() )
        init.append( '# dynamically generated code' )
        init.append( '# abbreviations: c=concentration, d=decay, t=threshold, n=newvalue' )
        init.append( '# %s' % list(self.mapper.values()) )

        for index, node, triplet in list(self.mapper.values()):
            conc, decay, tresh = boolmapper(triplet)
            #assert decay > 0, 'Decay for node %s must be larger than 0 -> %s' % (node, str(triplet))   
            store = dict( index=index, conc=conc, decay=decay, tresh=tresh, node=node)
            line = self.INIT_LINE( store )
            init.append( line )
        
        if localdefs:
            init.extend( [ '# custom imports', 'import %s' % localdefs, 'reload(%s)' % localdefs, 'from %s import *' % localdefs ]   )

        init_text = '\n'.join( init )
        return init_text
    
    def create_equation( self, tokens ):
        """
        Creates a python equation from a list of tokens.
        """
        original = '#' + tokenizer.tok2line(tokens)
        node  = tokens[1].value
        lines = [ '', original ]
        
        line  = self.OVERRIDE(node, indexer=self.indexer, tokens=tokens)
        if line is None:
            line = self.DEFAULT_EQUATION( tokens=tokens, indexer=self.indexer )
        
        if isinstance(line, str):
            line = [ line ]

        lines.extend( [ x.strip() for x in line ] )
        return lines  

    def generate_function(self ):
        """
        Generates the function that will be used to integrate
        """
        sep = ' ' * 4

        indices = [ x[0] for x in list(self.mapper.values()) ]
        assign  = [ 'c%d' % i for i in indices ]
        retvals = [ 'n%d' % i for i in indices ]
        zeros   = ['0.0' for x in indices] 
        assign  = ', '.join(assign)
        retvals = ', '.join(retvals)
        zeros   = ', '.join( zeros )

        body = []
        body.append( 'x0 = %s' % assign )
        body.append( 'def derivs( x, t):' )
         
        body.append( '    %s = x' % assign )
        body.append( '    %s = %s' % (retvals, zeros) )
        for tokens in self.update_tokens:
            equation = self.create_equation( tokens )
            equation = [ sep + e for e in equation ]
            body.append( '\n'.join( equation)  )
        body.append( '' )
        body.append( "    return ( %s ) " % retvals )
        text = '\n'.join( body )
        
        return text

    def iterate( self, fullt, steps, autogen_fname=None, localdefs=None, autogen='autogen'  ):
        """
        Iterates over the system of equations 
        """
        if autogen_fname is not None:
            autogen = autogen_fname
            del autogen_fname
            util.warn("parameter 'autogen_fname' is deprecated. Use 'autogen' instead." )
        
        # setting up the timesteps
        dt = fullt/float(steps)
        self.t  = [ dt * i for i in range(steps) ]

        # generates the initializator and adds the timestep
        self.init_text  = self.generate_init( localdefs=localdefs )
        self.init_text += '\ndt = %s' % dt

        #print init_text
        
        # generates the derivatives
        self.func_text = self.generate_function()
        #print func_text
       
        self.dynamic_code = self.init_text + '\n' + self.func_text             
        
        try:
            fp = open( '%s.py' % autogen, 'wt')
            fp.write( '%s\n' % self.init_text )
            fp.write( '%s\n' % self.func_text )
            fp.close()
            autogen_mod = __import__( autogen )
            try:
                os.remove( '%s.pyc' % autogen )
            except OSError:
                pass # must be a read only filesystem
            imp.reload( autogen_mod )
        except Exception as exc:
            msg = "'%s' in:\n%s\n*** dynamic code error ***\n%s" % ( exc, self.dynamic_code, exc )
            util.error(msg)

        # x0 has been auto generated in the initialization
        self.alldata = rk4(autogen_mod.derivs, autogen_mod.x0, self.t) 
        
        for index, node in enumerate( self.nodes ):
            self.lazy_data[node] = [ row[index] for row in self.alldata ]
    
if __name__ == '__main__':
    text = """
    #
    # this is a comment
    #
    # conc, decay, treshold
    # 100%
    A = (1, 1, 0.5)
    B = (1, 1, 0.5)
    C = (1, 1, 0.5 )
    1: A* = not A 
    2: B* = A and B
    3: C* = C
    """
    
    model = PldeModel( text=text )
    model.initialize()
    model.iterate( fullt=5, steps=100 )

    from pylab import *
    plot( model.data['A'] ,'o-' )
    plot( model.data['B'] ,'o-' )
    plot( model.data['C'] ,'o-' )
    show()
