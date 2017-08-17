"""
Helper functions
"""
import csv
from io import StringIO
import string
from itertools import *

# these function get injected into the generated code

helper_modules = """
try:
    from %s import *
except:
    pass
"""

from .defs import *

def change(node, indexer):
    "Returns the change for a node"
    index = indexer[node]
    return ' n%d ' % index 

def newval(node, indexer):
    """
    Returns the change for a node,
    
    chose a bad name originally still here for compatibility reasons, 
    will be deprecated
    """
    return change( node, indexer)

def conc( node, indexer):
    "Returns the concentration for a node"
    index = indexer[node]
    return ' c%d ' % index 

def decay( node, indexer):
    "Returns the decay for a node"
    index = indexer[node]
    return ' d%d ' % index 

def threshold( node, indexer):
    "Returns the threshold for a node"
    index = indexer[node]
    return ' t%d ' % index 

def default( node, indexer, tokens):
    "Default equation builder"
    newval = change( node, indexer )
    piece  = piecewise( tokens, indexer )
    return '%s = %s' % ( newval, piece )

def hill_func( node, indexer, par):
    """
    Generates a hill function call based on the parameters 
    """
    index = indexer[node]
    try:
        text = ' hill( c%d, h=%s, n=%s ) ' % ( index, par[node].h, par[node].n )
    except Exception as exc:
        msg = "error creating hill function for node %s -> %s" % (node, exc)
        raise Exception(msg)
    return text

def prop_func( node, indexer, par):
    """
    Generates a proportion function call based on the parameters        
    """
    index = indexer[node]
    try:
        nconc = conc(node, indexer)
        text = ' prop( r=%s, rc=%s ) - %s ' % ( par[node].r, par[node].rc, nconc )
    except Exception as exc:
        msg = "error creating proportion function for node %s -> %s" % (node, exc)
        raise Exception(msg)
    return text

def piecewise( tokens, indexer ):
    """
    Generates a piecewise equation from the tokens
    """
    base_node  = tokens[1].value
    base_index = indexer[base_node]
    line = []
    line.append ( 'float(' )
    nodes = [ t.value for t in tokens[4:] ]
    for node in nodes:
        # replace each node with the comparison
        if node in indexer:
            index = indexer[node]
            value = " ( c%d > t%d ) " % ( index, index )
        else:
            value = node
        line.append ( value )
    line.append ( ')' )
    
    # add decay term
    line.append ( "- d%d * c%d" % ( base_index, base_index ) )
    
    return ' '.join( line )

def init_line( store ):
    """
    Store is an incoming dictionary prefilled with parameters
    """
    patt = 'c%(index)d, d%(index)d, t%(index)d = %(conc)f, %(decay)f, %(tresh)f # %(node)s' 
    return patt % store

def init_from_conc_max_threshold( param ):
    """
    Store is an incoming dictionary prefilled with parameters
    """
    patt = 'c%(index)d, d%(index)d, t%(index)d = %(conc)f, 1.0/%(decay)f, %(tresh)f # %(node)s' 
    return patt % param

def initializer(data, labels=None, **kwds):
    """
    Function factory that returns an initializer 
    that can initialize based on a parameter row (and naming convention)

    If a node is missing the function will raise an error. If a
    default parameter is passed to the function factory the
    function will return this value upon errors
    """

    # allow to override the parameter labels, the order is important
    labels = labels or 'conc decay threshold'.split()
    
    def func( node ):
        # the extra work is to produce helpful error messages
        try:
            values = [ data[node][label] for label in labels ]
            return tuple(values) 
        except KeyError as exc:
            
            if 'default' in kwds:
                return kwds['default']
            else:
                if node not in data:
                    raise KeyError( 'could not find parameter %s' % node )
                for label in labels:
                    if label not in data[node]:
                        raise KeyError( "could not find parameter %s['%s']" % (node, label) )   

        
    return func 

class Parameter(object):
    """
    Allows attribute access to the parameters (Bunch)
    """
    def __init___(self, **kwds):
        self.__dict__.update( kwds )
    
    def __getattr__(self, attr):
        return self[attr]

    def __getitem__(self, key):
        if key not in self.__dict__:
            raise KeyError("parameter field '%s' not present" % key)
        else:
            return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    
    def __repr__(self):
        return str(self.__dict__)
    
    def __contains__(self, key):
        return key in self.__dict__

    def setdefault(self, key, default):
        return self.__dict__.setdefault(key, default)

def read_parameters( fname ):
    """
    Reads parameters from a comma separated file and 
    returns a bunch object with attributes corresponding
    to the second line in the file
    """

    #
    # needs extra error checking because files created with 
    # Excel may contain artifacts => empty columns, empty lines, invisible values (spaces)
    #

    
    def something( row ):
        # skips rows with empty elements
        return [x for x in map(string.strip, row ) if x]
    
    # load the file, skipping commented or empty rows
    lines = list(filter( something, csv.reader( CommentedFile(fname)))) 

    # check file size 
    assert len(lines) > 2, "file '%s' needs to have more than two lines" % fname
    
    # same number of columns in each line
    colnum = len( lines[0] )
    def coltest( elems ) :
        size = len(elems)
        if size != colnum:
            raise Exception( "column number mismatch expected %d, found %s, at line '%s'" % (size, colnum, ', '.join(elems)))
        return True
    
    lines = list(filter( coltest, lines ))
    
    # nodes and attributes
    nodes, attrs = lines[0:2]
    
    # tries to coerce the value into a datastructure, float tuples, float or string
    def tuple_cast( word ):
        try:
            values = list(map( float, word.split(',') ))
            if len( values ) > 1 :
                return tuple(values)
            else:
                return values[0]
        except ValueError:
            return word

    # generate the datastructure
    store  = []
    for elems in lines[2:]:
        param = Parameter()
        for index, attr, node in zip(count(), attrs, nodes):
            value = elems[index]
            param.setdefault( node, Parameter() )[attr] = tuple_cast( value )
        store.append( param )
    
    return store

class CommentedFile:
    """
    A file reader that skips comments in files
    """
    def __init__(self, fp):
        if isinstance(fp, str):
            fp = file(fp, 'rU')
        self.fp = fp

    def __next__(self):
        line = next(self.fp)
        while line.startswith('#'):
            line = next(self.fp)
        return line

    def __iter__(self):
        return self


