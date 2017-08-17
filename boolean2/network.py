
from . import util
import random
from itertools import count

try:
    import networkx
    from networkx import component
except ImportError:
    util.error( "networkx is missing, install it from https://networkx.lanl.gov/")

# color constants
BLUE, RED, GREEN = "#0000DD", "#DD0000", "#00DD00"
WHITE, PURPLE, ORANGE = "#FFFFFF", "#990066", "#FF3300"
TEAL, CRIMSON, GOLD, NAVY, SIENNA = "#009999", "#DC143C",  "#FFD700", "#000080", "#A0522D"
LIGHT_GREEN, SPRING_GREEN, YELLOW_GREEN = "#33FF00", "#00FF7F", "#9ACD32"

def component_colormap(graph):
    """
    Colormap by strong compoments
    """
    # automatically color by components

    # a list of colors in hexadecimal Red/Gree/Blue notation
    colors = [ ORANGE, SPRING_GREEN, GOLD, TEAL, PURPLE, NAVY, SIENNA, CRIMSON, BLUE, ]
    
    # find the strongly connected components
    components = component.strongly_connected_components( graph )
    
    # make sure we have as many colors as components
    if len(colors) < len(components):
        util.warn( 'there are more components than colors!' )

    # create the colormap
    colormap = {}
    for color, comp in  zip(colors, components):
        for node in comp:
            colormap[node] = color
    return colormap

def write_gml( graph, fname, colormap={} ):

    
    "Custom gml exporter"
    fp = open(fname, 'wt')
    text = [ 'graph [', 'directed 1' ]

    nodepatt = 'node [ id %(node)s label "%(node)s" graphics [ fill	"%(color)s" w 40 h 30 x %(x)s y %(y)s type "ellipse" ]]'
    rnd = random.randint
    for node in graph.nodes():
        x, y = rnd(50,200), rnd(50, 200)
        color = colormap.get(node, '#CCCCFF')
        param = dict( node=node, x=x, y=y, color=color )
        text.append(  nodepatt % param)
    
    edgepatt = 'edge [ source %(source)s target %(target)s  graphics [ fill	"%(color)s" targetArrow "delta" ]]'
    for source, target in graph.edges():
        pair  = (source, target)
        color = colormap.get(pair, '#000000')
        param = dict( source=source, target=target, color=color )
        text.append( edgepatt % param)
    
    text.append( ']' )
    fp.write( util.join( text, sep="\n" ) )
    fp.close()

class TransGraph(object):
    """
    Represents a transition graph
    """
    def __init__(self, logfile, verbose=False):
        self.graph = networkx.MultiDiGraph(  )         
        self.fp = open( logfile, 'wt')
        self.verbose = verbose
        self.seen = set()
        self.store = dict()
        self.colors = dict()

    def add(self, states, times=None):
        "Adds states to the transition"
    
        # generating the fingerprints and sto
        times = times or list(range(len(states)))
        fprints = []
        for state in states:
            if self.verbose:
                fp = state.bin()
            else:
                fp = state.fp()
            fprints.append( fp )
            self.store[fp] = state

        self.fp.write( '*** transitions from %s ***\n' % fprints[0] )

        for head, tail, tstamp in zip(fprints, fprints[1:], times ):
            pair = (head, tail)
            self.fp.write('T=%s: %s->%s\n' %  (tstamp, head, tail) ) 
            if pair not in self.seen:
                self.graph.add_edge(head, tail)
                self.seen.add(pair)
        
    def save(self, fname, colormap={}):
        "Saves the graph as gml"
        write_gml(graph=self.graph, fname=fname, colormap=colormap)
    
        self.fp.write( '*** node values ***\n' )

        # writes the mapping
        first = list(self.store.values())[0]
        header = [ 'state' ] + list(first.keys())
        self.fp.write( util.join(header) )
        
        for fprint, state in sorted( self.store.items() ):
            line = [ fprint ]  + list(map(int, list(state.values()) ))
            self.fp.write( util.join(line) )

def test():
    """
    Main testrunnner
    """
    from . import boolmodel
    
    text = """
    A = True
    B = False
    C = False
    1: A* = A
    2: B* = not B
    3: C* = A and B
    """
    model = boolmodel.BoolModel( mode='sync', text=text )
    model.initialize( missing=util.true )
    model.iterate( steps = 5 )
    
    #for state in model.states:
    #    print (state)

    trans = TransGraph( logfile='states.txt' ) 
    trans.add( model.states )

    # generate the colormap based on components
    colormap = component_colormap( trans.graph )

    trans.save( fname='test.gml', colormap=colormap )

if __name__ == '__main__':
    test()
