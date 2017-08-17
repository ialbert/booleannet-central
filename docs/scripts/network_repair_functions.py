'''
This module contains an implementation of the  network repair methodology
introduced in Campbell and Albert (2014), BMC Syst. Biol.

The code should be straightforward to apply (see network_repair_tutorial.py).

I will be happy to respond to questions and/or comments.

Colin Campbell
Contact: colin.campbell@psu.edu
Python Version: 2.7.x
Date: April 2014 (last updated August 2014)
'''
import networkx as nx
import numpy as np
from itertools import product
from random import choice, randrange

def form_network(rules):
    '''
    Takes as input a list of rules in the format of sample_network.txt.

    Outputs a networkx DiGraph with node properties:
        'update_nodes': a list of regulating nodes
        'update_rules': a dictionary with binary strings as keys, corresponding
                        to the possible states of the update_nodes, and integers
                        as values, corresponding to the state of the node given
                        that input.

    Note that nodes are identified by their position in a sorted list of
    user-provided node names.
    '''
    def clean_states(x):
        #cleans binary representation of node input states
        out=x[2:]                                                               # Strip leading 0b
        return '0'*(len(inf)-len(out))+out                                      # Append leading 0's as needed

    stream = [x.rstrip('\n') for x in rules if x != '\n' and x[0]!='#']         # Remove comments and blank lines
    nodes = sorted([x.split(' ',1)[0][:-1] for x in stream])                    # Generate a sorted list of node names

    g = nx.DiGraph()
    g.graph['knockout'] = None                                                  # At creation, no node is flagged for knockout or overexpression
    g.graph['express'] = None

    for n in xrange(len(stream)):
        rule = stream[n].split('* = ')[1]
        rule = rule.replace(' AND ',' and ')                                    # Force decap of logical operators so as to work with eval()
        rule = rule.replace(' OR ',' or ')
        rule = rule.replace(' NOT ',' not ')
        if stream[n].find('True') >= 0 or stream[n].find('False') >= 0:         # For always ON or always OFF nodes
            g.add_node(n)                                                       # We refer to nodes by their location in a sorted list of the user-provided node names
            g.node[n]['update_nodes'] = []
            g.node[n]['update_rules'] = {'':str(int(eval(rule)))}
            continue

        inf = rule.split(' ')                                                   # Strip down to just a list of influencing nodes
        inf = [x.lstrip('(') for x in inf]
        inf = [x.rstrip(')') for x in inf]
        #The sort ensures that when we do text replacement (<node string>->'True' or 'False') below in this fn, we avoid problems where node 1 is a substring of node 2 (e.g. NODE1_phosph and NODE1)
        inf = sorted([x for x in inf if x not in ['','and','or','not']],key=len,reverse=True)

        for i in inf: g.add_edge(nodes.index(i),n)                              # Add edges from all influencing nodes to target node
        g.node[n]['update_nodes'] = [nodes.index(i) for i in inf]
        g.node[n]['update_rules'] = {}

        bool_states = map(bin,range(2**len(inf)))
        bool_states = map(clean_states,bool_states)
        for j in bool_states:
            rule_mod = rule[:]
            for k in range(len(j)):
                if j[k]=='0':
                    rule_mod=rule_mod.replace(nodes[g.node[n]['update_nodes'][k]],'False')      # Modify the rule to have every combination of True, False for input nodes
                else: rule_mod=rule_mod.replace(nodes[g.node[n]['update_nodes'][k]],'True')
            g.node[n]['update_rules'][j] = int(eval(rule_mod))                                  # Store outcome for every possible input

    return g,nodes

def find_attractor(graph,state=False):
    '''
    Takes a graph as formatted in form_network() as input.

    Chooses a random starting state (if state==False); synchronously advances
    until a SS or LC is found. Can accommodate a node knockout or overexpression
    as formed in damage_network().

    if state is not False, it must be a string of 0s and 1s, which specifies the
    starting state for the update iteration.

    The string bits must be are arranged in alphabetical (sorted) order,
    according to node names.

    Outputs a list of [next_state,attractor]. For a SS, the 'attractor' entries
    are '0's and '1's, representing the SS. For a LC, the 'attractor' is a list
    of state strings, representing every state in the LC.

    If no state is found after 1000 interations, the function returns False and
    prints a warning to the console.
    '''
    def update_state(x):
        #x is the node's index
        input_state = ''
        for i in graph.node[nodes[x]]['update_nodes']: input_state += str(trajectory[-1][nodes.index(i)])    # Acquire string of current states of node x's input nodes
        return str(graph.node[nodes[x]]['update_rules'][input_state])

    nodes = sorted(graph.nodes())
    if not state: trajectory = [list(np.random.random_integers(0,1,nx.number_of_nodes(graph)))]         # Random starting state
    else: trajectory = [state]                                                                          # Provided starting state

    while True:
        trajectory += [map(update_state,xrange(len(nodes)))]
        if graph.graph['knockout'] != None: trajectory[-1][nodes.index(graph.graph['knockout'])] = '0'  # If a node has been knocked out, it must be 0 even if it would normally be active
        elif graph.graph['express'] != None: trajectory[-1][nodes.index(graph.graph['express'])] = '1'  # "  " "    "   "    expressed,   "  "    "  1 "    "  "  "     "        "  inactive
        if trajectory[-1] in trajectory[:-1]:                                                           # Return a list of [next state, attractor], once attractor is found (attractor list length 1 in case of SS)
            return [trajectory[1],trajectory[trajectory.index(trajectory[-1]):-1]]
        if len(trajectory) == 1000:
            print 'find_attractor() was unable to find an attractor in 1000 interations; returning False.'
            return False

def superset(a):
    '''
    Takes a limit cycle (list of lists of binary strings), and collapses it into
    one state with a 1 if the node is 1 in any states in 'a', and 0 otherwise.
    '''
    transpose = [[row[i] for row in a[1]] for i in range(len(a[1][0]))]         # Turn list of states into list of time sequences for each node [[n1s1,n2s1],[n1s2,n2s2]] -> [[n1s1,n1s2],[n2s1,n2s2]]
    superset = ['1' if '1' in x else '0' for x in transpose]                    # Evaluate each entry for any 1s; generate superset
    return superset


def damage_network(graph,a=None,force=None,force_type='knockout'):
    '''
    Takes a graph and superset attractor as input. Chooses either a transiently
    active or permanently inactive node and forces it to be knocked out or
    overexpressed, respectively.

    Alternatively, if force != False, it must be an integer of a node's position
    in a sorted list of graph nodes. That node is then set to 'knockout' or
    'express' according to force_type.

    Returns the modified graph.
    '''
    g_copy = graph.copy()                                                       # Don't modify the input graph

    if force == None:
        node = randrange(len(a))                                                # Choose a random node index
        if a[node] == 0: g_copy.graph['express'] = node                         # Assign the index of an overexpressed (0 forced into 1) node
        else: g_copy.graph['knockout'] = node                                   # "      "   "     "  a knocked out (1 forced into 0)    "
    else:
        if force_type == 'knockout': g_copy.graph['knockout'] = force
        elif force_type == 'express': g_copy.graph['express'] = force

    return g_copy

def damage_state(graph,a):
    '''
    Form a damaged state (in superset form or regular form, depending on input)
    that mirrors the original attractor except for the knockout/damage.

    Called internally in other functions; likely not of direct interest to the
    end user.
    '''
    if graph.graph['knockout'] != None:
        return a[:graph.graph['knockout']]+['0']+a[graph.graph['knockout']+1:]
    else: return a[:graph.graph['express']]+['1']+a[graph.graph['express']+1:]

def compare_attractors(graph,a):
    '''
    Takes as input a damaged graph and the original, undamaged LC attractor.

    Returns (as the second value) a list where the first entry is the first
    entry of 'a' (preserving format) and the second is the largest component of
    the attractor that survives when duplicate states are collapsed (e.g. 011
    and 010 when node 3 is fixed).

    Returns (as the first value) True of False, respectively corresponding to
    if a pair of state collapsed or not.
    '''
    new_attractors = []
    valid,invalid = [],[]
    for state in a[1]:
        if graph.graph['knockout'] != None:
            if state[graph.graph['knockout']] == '1':
                switch_state = state[:graph.graph['knockout']] + ['0'] + state[graph.graph['knockout']+1:]
                if switch_state in a[1]:
                    invalid += [state]
                    valid += [switch_state]                                     # Store the 'invalid' states; inputs to them reroute to the 'valid' states
        elif graph.graph['express'] != None:
            if state[graph.graph['express']] == '0':
                switch_state = state[:graph.graph['express']] + ['1'] + state[graph.graph['express']+1:]
                if switch_state in a[1]:
                    invalid += [state]
                    valid += [switch_state]
    if len(valid)==0: return False, [a[0],[damage_state(graph,x) for x in a[1]]]# If there are no state collapses, we straightforwardly damage every state in a according to graph damage.

    positions = range(1,len(a[1]))
    cur_pos = 0
    route = []
    while True:                                                                 # We walk across the state transition map, sensitive to invalid states due to state collapse
        if a[1][cur_pos] in invalid:
            while a[1][cur_pos] in invalid:
                try: positions.remove(cur_pos)                                  # We can sometimes loop back to the same state multiple times; no need to remove it from the "points to walk across" list again
                except ValueError: pass
                cur_pos = a[1].index(valid[invalid.index(a[1][cur_pos])])       # Jump from invalid position to corresponding valid position when moving onto invalid state
            route+=[a[1][cur_pos]]
        else:
            route+=[a[1][cur_pos]]
        falsified = [x for x in route if route.count(x) > 1]
        if len(falsified) > 0:                                                  # Check to see if we've hit a node twice (found a LC)
            start = route.index(route[-1])
            new_attractors += [route[start+1:]]                                 # The last entry is always one of the repeats, so the LC runs from the first instance of the repeat to the end

            try: positions.remove(cur_pos)
            except ValueError: pass                                             # We can sometimes loop back to the same state multiple times; no need to remove it from the "points to walk across" list again
            if len(positions) == 0: break

            cur_pos = choice(positions)                                         # If we isolate an attractor and other states have yet to be walked, pick one randomly
            route = []
            continue
        else:                                                                   # If we are still progressing, simply iterate our position forward
            try: positions.remove(cur_pos)
            except ValueError: pass
            cur_pos += 1
            if cur_pos == len(a[1]):                                            # We can also walk back to 0
                cur_pos = 0

    if len(new_attractors) == 0:
        raise RuntimeError("No new attractors identified.")
    elif len(new_attractors) == 1:
        return True, [a[0],[damage_state(graph,x) for x in new_attractors[0]]]  # We now have the largest salvageable section of the LC
    else:
        new_attractor_lengths = map(len,new_attractors)
        max_index = new_attractor_lengths.index(max(new_attractor_lengths))     # We choose to look at the longest "new" attractor
        return True, [a[0],[damage_state(graph,x) for x in new_attractors[max_index]]]  # We now have the largest salvageable section of the LC


def check_stability(graph,a):
    '''
    Takes as input the damaged graph and damaged attractor.

    If the attractor reached from every state in the damaged attractor is
    identical to the damaged attractor, the damaged attractor is stable, and
    the function returns True. Otherwise, the function returns False.
    '''
    def shift(seq, n):
        n = n % len(seq)
        return seq[n:] + seq[:n]

    A_n = [find_attractor(graph,state=x) for x in a[1]]
    if [type(x) for x in A_n].count(bool) > 0:
        raise RuntimeError("Unable to find attractor in check_stability()")
    if len(A_n) == len(a[1]) == 1:                                              # If the damaged attractor is a SS and evaluates to a SS, we can directly compare them
        if A_n[0][1] == a[1]: return True
        else: return False

    for attr in A_n:                                                            # If one or both is a LC, We check to make sure that the procession of states matches
        if len(attr[1]) != len(a[1]): return False                              # Quickest check is to see if the lengths are the same
        else:
            try: asi = a[1].index(attr[1][0])                                   # See the 'starting index' of A_d relative to this attractor
            except Exception: return False                                      # If it isn't in this attractor, they obviously don't match
            rotated = shift(a[1],asi)                                           # Then see if the aligned processions are equivalent at each position (same procession)
            if [i==j for i,j in zip(rotated,attr[1])].count(False) > 0: return False
    return True


def evaluate_repair(graph,a,a_s=None,method='fix_to_SS'):
    '''
    Takes the damaged graph, damaged attractor, and original superset as input.
    method == 'LC_repair' or method == 'fix_to_SS', to determine whether or not
    we attempt to preserve LC transitions or fix its superset to a SS.

    Returns the repaired graph, or if not possible, a string explaining the
    cause of failure.
    '''
    # Define internal functions ------------------------------------------------
    def disjoint(x,y):
        '''
        Takes two lists and outputs the positions where the two don't have the
        same value.
        '''
        return [v for v in xrange(len(x)) if x[v]!=y[v]]

    def examine_modifications(g_in,a_t):
        '''
        Takes damaged network g and target attractor a_t. Looks at all possible
        edge modifications (as enumerated in the report) to force every node to
        be in its desired state.

        results are stored in g.graph['modifications'][<node>] as list of
        tuples:
        (<approach #>,<fix to 1/0>,<interacting node 1>,<interacting node 2>)

        '''
        def approach_1(x,pn,an,fix_to=1):
            '''
            adds OR <present_new> to an inactive node to make it active, or
            an AND <absent_new> to an active node to make it inactive.
            here and below:
                fix_to = 0 - we are fixing an active node to be inactive
                fix_to = 1 - we are fixing an inactive node to be active
                pn - viable_present_new_nodes
                p  - viable_present_nodes
                an - viable_absent_new_nodes
                a  - viable_absent_nodes
            '''
            if fix_to == 1:
                for j in pn:
                    g.graph['modifications'][x] += [(1,1,j)]                          #output meaning: method, fix_to, interacting node #1 (similar for other approach_# functions)
            else:
                for j in an:
                    g.graph['modifications'][x] += [(1,0,j)]
        def approach_2(x,pn,an,fix_to=1):
            '''
            adds an OR NOT <absent_new> to an inactive node to make it active,
            or an AND NOT <present_new> to an active node to make it inactive.
            '''
            if fix_to == 1:
                for j in an:
                    g.graph['modifications'][x] += [(2,1,j)]
            else:
                for j in pn:
                    g.graph['modifications'][x] += [(2,0,j)]
        def approach_3(x,p,pn,a,an,fix_to=1):
            '''
            adds an OR <pres and pres_new> to an inactive node to make it
            active, or an AND <abs or abs_new> to an active node to make it
            inactive.
            '''
            if fix_to == 1:
                for j,k in product(p,pn):
                    g.graph['modifications'][x] += [(3,1,j,k)]
            else:
                for j,k in product(a,an):
                    g.graph['modifications'][x] += [(3,0,j,k)]
        def approach_4(x,p,pn,a,an,fix_to=1):
            '''
            adds an OR <pres and not abs_new> to an inactive node to make it
            active, or an AND <abs OR NOT pres_new> to an active node to make it
            inactive.
            '''
            if fix_to == 1:
                for j,k in product(p,an):
                    g.graph['modifications'][x] += [(4,1,j,k)]
            else:
                for j,k in product(a,pn):
                    g.graph['modifications'][x] += [(4,0,j,k)]
        def approach_5(x,p,pn,a,an,fix_to=1):
            '''
            adds an OR <NOT abs AND pres_new> to an inactive node to make it
            active, or an AND <NOT pres OR abs_new> to an active node to make it
            inactive.
            '''
            if fix_to == 1:
                for j,k in product(a,pn):
                    g.graph['modifications'][x] += [(5,1,j,k)]
            else:
                for j,k in product(p,an):
                    g.graph['modifications'][x] += [(5,0,j,k)]
        def approach_6(x,p,pn,a,an,fix_to=1):
            '''
            adds an OR <NOT abs AND NOT abs_new> to an inactive node to make it
            active, or an AND <NOT pres OR NOT pres_new> to an active node to
            make it inactive.
            '''
            if fix_to == 1:
                for j,k in product(a,an):
                    g.graph['modifications'][x] += [(6,1,j,k)]
            else:
                for j,k in product(p,pn):
                    g.graph['modifications'][x] += [(6,0,j,k)]

        g=g_in.copy()
        nodes = sorted(g.nodes())
        g.graph['modifications'] = {}
        for i in g.nodes_iter():
            if g.graph['express'] == i or g.graph['knockout'] == i: continue                                                                                    # Don't attempt to modify the knocked out/overexpressed node
            g.graph['modifications'][i] = []                                                                                                                    # Set container for all viable modifications to this node (0->1 and 1->0)
            viable_present_new_nodes = [y for y in g.nodes_iter() if int(a_t[nodes.index(y)]) == 1 and y not in g.node[i]['update_nodes'] and g.graph['express'] != y and y != i]     # Possible new regulators that are present nodes (that have not been overexpressed)
            viable_absent_new_nodes = [y for y in g.nodes_iter() if int(a_t[nodes.index(y)]) == 0 and y not in g.node[i]['update_nodes'] and g.graph['knockout'] != y and y != i]     # Possible new regulators that are absent nodes (that have not been knocked out)
            viable_present_nodes = [y for y in g.node[i]['update_nodes'] if int(a_t[nodes.index(y)]) == 1 and g.graph['express'] != y and y != i]                                     # Possible existing regulators that are present nodes (that have not been overexpressed)
            viable_absent_nodes = [y for y in g.node[i]['update_nodes'] if int(a_t[nodes.index(y)]) == 0 and g.graph['knockout'] != y and y != i]                                     # Possible existing regulators that are absent nodes (that have not been overexpressed)
            if set(viable_present_new_nodes)&set(viable_absent_new_nodes)&set(viable_present_nodes)&set(viable_absent_nodes) != set(): raise RuntimeError("Algorithm halted - duplicate node assignment.")
            #go through all 6 approaches, store possible combinations of nodes as a graph property
            approach_1(i,viable_present_new_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_2(i,viable_present_new_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_3(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_4(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_5(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_6(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=int(a_t[nodes.index(i)]))
            approach_1(i,viable_present_new_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)                                                #look at both the 0->1 and 1->0 possibilities
            approach_2(i,viable_present_new_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)
            approach_3(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)
            approach_4(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)
            approach_5(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)
            approach_6(i,viable_present_nodes,viable_present_new_nodes,viable_absent_nodes,viable_absent_new_nodes,fix_to=(int(a_t[nodes.index(i)])+1)%2)
        return g

    def fix_to_SS(graph,a,node_set):
        '''
        Takes a damaged graph (that has been run through examine_modifications)
        and a desired attractor, and makes that attractor a SS of an
        edge-modified version of the network. Returns the repaired graph.

        Randomly selects a viable edge modification for every node.

        node_set is a list of the nodes with rules to be modified.

        Returns repaired graph, steady state attractor, and dictionary of
        viable modifications for each node.
        '''
        g_r = graph.copy()
        nodes = sorted(g_r.nodes())
        choice_dict = {}
        for node in node_set:
            if g_r.graph['express'] == node or g_r.graph['knockout'] == node: continue                              # Don't attempt to modify the knocked out/overexpressed node
            choice_dict[node] = [x for x in g_r.graph['modifications'][node] if x[1] == int(a[nodes.index(node)])]  # Choose only from approaches that fix it to the appropriate choice of 0 or 1
            modification = choice(choice_dict[node])                                                                # Format: (approach from the 6 listed in examine_modifications(), method 0 or 1 for the block within the method, interacting node 1[, interacting node 2])
            g_r.node[node]['update_nodes'] += [modification[-1]]                                                    # Append new interacting nodes to previously selected interacting nodes
            new_rules = {}
            bool_suffixes = ['0','1']                                                                           # We always only ever add 1 new node
            for state in g_r.node[node]['update_rules']:
                for bs in bool_suffixes:
                    new_rules[state+bs]=g_r.node[node]['update_rules'][state]       # Append the suffixes but initially with the same outputs as before; then with complete set of input possibilities, change outcomes below
            g_r.node[node]['update_rules'] = new_rules.copy()

            if len(modification) == 4: ex_index = g_r.node[node]['update_nodes'].index(modification[-2])        # Slot in 'update_rule' keys that corresponds to the existing node whose edge is being modified
            #adding an "... OR p_n". So all rules where the final entry is a 1 must have an output of 1
            if modification[0] == 1 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND a_n". So all rules where the final entry is a 0 must have an output of 0
            elif modification[0] == 1 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR NOT a_n". So all rules where the final entry is a 0 must have an output of 1
            elif modification[0] == 2 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND NOT p_n". So all rules where the final entry is a 1 must have an output of 0
            elif modification[0] == 2 and modification[1] == 0: g_r.node[node]['update_rules']  = {key:(val if key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (p AND p_n)". So all rules where the existing and new node entries are both 1 must have an output of 1
            elif modification[0] == 3 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (a OR a_n)". So all rules where the existing and new node entries are both 0 must have an output of 0
            elif modification[0] == 3 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (p AND NOT a_n)". So all rules where the existing and new node entries are '10' must have an output of 1
            elif modification[0] == 4 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (a OR NOT p_n)". So all rules where the existing and new node entries are '01' must have an output of 0
            elif modification[0] == 4 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (NOT a AND p_n)". So all rules where the existing and new node entries are '01' must have an output of 1
            elif modification[0] == 5 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (NOT p OR a_n)". So all rules where the existing and new node entries are '10' must have an output of 0
            elif modification[0] == 5 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (NOT a AND NOT a_n)". So all rules where the existing and new node entries are both 0 must have an output of 1
            elif modification[0] == 6 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (NOT p OR NOT p_n)". So all rules where the existing and new node entries are both 1 must have an output of 0
            elif modification[0] == 6 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

        a_r = find_attractor(g_r,a)
        if len(a_r[1]) > 1: raise RuntimeError('LC found in fix_to_SS()')
        return g_r,a_r[1][0],choice_dict

    def fix_to_LC(graph_list,a,d_o,node_list):
        '''
        Takes a list of graphs that has been run through examine_modifications,
        such that each graph has modification properties that enumerates all
        methods of forcing a node to be '0' or '1' after an update.

        Each entry in the list corresponds to a state in the LC attractor, a.

        d_o is the 'next state' from the corresponding LC state in 'a'
        (evaluated in the damaged network).

        node_list enumerates the nodes that don't make the desired transition,
        again in the order of every state transition in the LC.

        We enumerate all possible modifications for every state transition for
        the nodes specified, and filter according to the modifications that
        will account for all modifications.

        Returns repaired graph LC attractor, and dictionary of viable
        modifications for each node.
        '''
        g_r = graph_list[0].copy()
        nodes = sorted(g_r.nodes())
        #First, collapse node_list into one list with all nodes that ever don't make the desired transition (others don't require any modification)
        s = set(node_list[0])
        for x in node_list[1:]: s=s.union(x)
        modify_nodes = list(s)
        choice_dict = {}
        #Then search for all viable modifications (return out of fn if none exist for any node)
        #the only thing that is different b/w entries in this list are the modification rules; just use entry [0] for manipulations
        for node in modify_nodes:
            if graph_list[0].graph['express'] == node or g_r.graph['knockout'] == node: raise RuntimeError("expressed/knocked out node identified as oscillating.")
            t_01,t_10 = 0,0
            for state in range(len(node_list)):
                if node in node_list[state]:                                        #Important - we here look at the transitions where we know the node doesn't make the desired change
                    if int(d_o[state-1][nodes.index(node)]) == 0 and int(a[state][nodes.index(node)]) == 1: t_01 = 1    #(a node could fail at one transition and not another within a LC)
                    elif int(d_o[state-1][nodes.index(node)]) == 1 and int(a[state][nodes.index(node)]) == 0: t_10 = 1
            if t_01 + t_10 == 2: return False,'a',False                             #If it actively fails via both 0->1 and 1->0, we can't repair the network using this methodology.
            # Otherwise, we need to find a rule that works at every transition,
            # for either 1+ 0->1 correction(s) or 1+ 1->0 correction(s). Either
            # possibility could additionally have 1+ 1->1 and/or 1+ 0->0
            # transitions (i.e. the rule change must preserve 'correct' state
            # transitions). We do this by set-intersecting the appropriate list
            # of modifications at every primary (1->0 or 0->1) state transition
            # for the nodes in the modify_nodes list. From there, we compare to
            # the other (secondary) transitions, which are more flexible
            primary_transitions = [];secondary_1_transitions = [];secondary_0_transitions = []
            for state in range(len(a)):
                if int(d_o[state-1][nodes.index(node)]) !=  int(a[state][nodes.index(node)]):
                    primary_transitions += [[x for x in graph_list[state-1].graph['modifications'][node] if x[1] == int(a[state][nodes.index(node)])]]     #All the valid transitions where we need a 1->0 or 0->1 modification
                elif int(a[state][nodes.index(node)]) == 0:
                    secondary_0_transitions += [[x for x in graph_list[state-1].graph['modifications'][node] if x[1] == int(a[state][nodes.index(node)])]] #All the valid transitions where we need a 0->0 modification
                else:
                    secondary_1_transitions += [[x for x in graph_list[state-1].graph['modifications'][node] if x[1] == int(a[state][nodes.index(node)])]] #All the valid transitions where we need a 1->1 modification
            #These are now lists of lists, for valid modifications at each state transition
            p = set(primary_transitions[0])
            for i in primary_transitions[1:]: p=p.intersection(i)
            if len(p)==0: return False,'b',False                                    #No changes survive the primary filtering process.
            p = list(p)
            if len(secondary_0_transitions) > 0:
                s0 = set(secondary_0_transitions[0])
                for i in secondary_0_transitions[1:]: s0=s0.intersection(i)
                s0 = list(s0)
            if len(secondary_1_transitions) > 0:
                s1 = set(secondary_1_transitions[0])
                for i in secondary_1_transitions[1:]: s1=s1.intersection(i)
                s1 = list(s1)
            #Now we need to further refine this list to make sure the modification we choose preserves 0->0 and 1->1 transitions
            if len(secondary_1_transitions) > 0 and p[0][1]==0:                     #We're doing a 1->0 correction somewhere, so we're restricted to an [ .. AND <stuff> ] modification
                #0->0 aren't influenced, but we need AND <1> for 1->1 preservation.
                #We want node (or node combinations) that eval to 0 (already isolated in primary_transitions) in some states and 1 in others (here).
                #This boils down to the modification tuple matching at all indices but 1, which needs to be opposite (0 vs 1 or vice versa)
                surviving_transitions = [x for x in p if tuple([x[0]]+[(x[1]+1)%2]+list(x[2:])) in s1]
                if len(surviving_transitions) == 0: return False, 'c', False
                else:
                    modification = choice(surviving_transitions)
                    choice_dict[node] = surviving_transitions
            elif len(secondary_0_transitions) > 0:                                  #We're doing a 0->1 correction somewhere, so we're restricted to an [ ... OR <stuff> ] modification
                #1->1 aren't influenced, but we need OR <0> for 0->0 preservation.
                #As above, we want combinations that eval to 1 or 0, depending on state
                surviving_transitions = [x for x in p if tuple([x[0]]+[(x[1]+1)%2]+list(x[2:])) in s0]
                if len(surviving_transitions) == 0: return False, 'c', False
                else:
                    modification = choice(surviving_transitions)
                    choice_dict[node] = surviving_transitions
            else:
                modification = choice(p)                                          #No need for further analysis if we don't have these transitions, so just choose from what we have
                choice_dict[node] = p

            #modification variable format: (approach from the 6 listed in examine_modifications(), method 0 or 1 for the block within the method, interacting node 1[, interacting node 2])
            #Rest of this loop is copy of end of fix_to_SS()
            g_r.node[node]['update_nodes'] += [modification[-1]]                    #append new interacting nodes to previously selected interacting nodes
            new_rules = {}
            bool_suffixes = ['0','1']                                               #we always only ever add 1 new node
            for state in g_r.node[node]['update_rules']:
                for bs in bool_suffixes:
                    new_rules[state+bs]=g_r.node[node]['update_rules'][state]      #append the suffixes but initially with the same outputs as before; then with complete set of input possibilities, change outcomes below
            g_r.node[node]['update_rules'] = new_rules.copy()

            if len(modification) == 4: ex_index = g_r.node[node]['update_nodes'].index(modification[-2])     #slot in 'update_rule' keys that corresponds to the existing node whose edge is being modified

            #adding an "... OR p_n". So all rules where the final entry is a 1 must have an output of 1
            if modification[0] == 1 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND a_n". So all rules where the final entry is a 0 must have an output of 0
            elif modification[0] == 1 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR NOT a_n". So all rules where the final entry is a 0 must have an output of 1
            elif modification[0] == 2 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND NOT p_n". So all rules where the final entry is a 1 must have an output of 0
            elif modification[0] == 2 and modification[1] == 0: g_r.node[node]['update_rules']  = {key:(val if key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (p AND p_n)". So all rules where the existing and new node entries are both 1 must have an output of 1
            elif modification[0] == 3 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (a OR a_n)". So all rules where the existing and new node entries are both 0 must have an output of 0
            elif modification[0] == 3 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (p AND NOT a_n)". So all rules where the existing and new node entries are '10' must have an output of 1
            elif modification[0] == 4 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (a OR NOT p_n)". So all rules where the existing and new node entries are '01' must have an output of 0
            elif modification[0] == 4 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (NOT a AND p_n)". So all rules where the existing and new node entries are '01' must have an output of 1
            elif modification[0] == 5 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '0' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (NOT p OR a_n)". So all rules where the existing and new node entries are '10' must have an output of 0
            elif modification[0] == 5 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '1' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... OR (NOT a AND NOT a_n)". So all rules where the existing and new node entries are both 0 must have an output of 1
            elif modification[0] == 6 and modification[1] == 1: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '1' or key[-1] == '1' else 1) for key,val in g_r.node[node]['update_rules'].iteritems()}

            #adding an "... AND (NOT p OR NOT p_n)". So all rules where the existing and new node entries are both 1 must have an output of 0
            elif modification[0] == 6 and modification[1] == 0: g_r.node[node]['update_rules'] = {key:(val if key[ex_index] == '0' or key[-1] == '0' else 0) for key,val in g_r.node[node]['update_rules'].iteritems()}

        a_r = find_attractor(g_r,a[-1])                                             #Find attractor from one of the LC states

        if len(a_r[1]) == 1: raise RuntimeError('SS found in fix_to_LC()')          #Make sure we find a LC from this procedure (we check for equality to 'a' outside of this fn)
        return g_r,a_r[1],choice_dict

    # End internal functions ---------------------------------------------------


    if method == 'fix_to_SS' or (method == 'LC_repair' and len(a[1]) == 1):     # If we pass a steady state, we evaluate it as a steady state even if we call 'LC_repair'
        if len(a[1]) > 1: a_t = damage_state(graph,a_s)                         # If we do pass a LC, we are concerned with its superset
        else: a_t = a[1][0][:]
        graph = examine_modifications(graph,a_t)                                # Look at the enumerated methods of forcing each node to be a specified state after update. Output is a graph with: g.graph['modifications'][node] properties
        node_set = find_attractor(graph,state=a_t)
        node_set = disjoint(node_set[0],a_t)                                    # Those nodes that change states in the first update from A_t
        g_r,a_r,choice_dict = fix_to_SS(graph,a_t,node_set)                     # Modify edges so the target attractor is a SS of the network
        if a_r == a_t: return g_r,choice_dict                                   # The repair succeeded
        else: raise RuntimeError("evaluate_repair() failed.")                   # The repair failed (i.e. there is a bug)
    elif method == 'LC_repair':
        graph_list = [examine_modifications(graph,x) for x in a[1]]                             # Look at the enumerated methods of forcing each node to be a specified state after update (Use 'A' b/c we assume we're going to fix it to be stable!)
        node_sets = [find_attractor(graph,state=x) for x in a[1]]                               # Look at 'next state' and ultimate attractor for each state in the damaged limit cyle
        node_set_list = [disjoint(node_sets[x-1][0],a[1][x]) for x in range(len(node_sets))]    # See which nodes don't make the desired state transition at every update in the damaged LC
        damaged_outcomes = [x[0] for x in node_sets]                                            # Feed just the 'next state' values into the function in the below line
        g_r,a_r,choice_dict = fix_to_LC(graph_list,a[1],damaged_outcomes,node_set_list)         # Attempt to modify edges to recover complete LC
        if g_r == False:
            if a_r == 'a': return 'LC repair impossible (a)',False              # The repair is not possible (need to repair a 0->1 and a 1->0 transition for at least one node)
            elif a_r == 'b': return 'LC repair impossible (b)',False            # The repair is not possible (not above issue, but edge additions as considered here fail to give option to meet all req. 0->1 or 1->0 state changes)
            else: return 'LC repair impossible (c)',False                       # The repair is not possible (neither of above issues, but we can't also preserve the 0->0 or 1->1 transitions while fixing the 0->1 or 1->0 transitions)
        elif [x in a[1] for x in a_r].count(False) + [x in a_r for x in a[1]].count(False) == 0:
            return g_r,choice_dict                                              # The repair was attempted and succeeded (all states in repaired LC are in original and vice versa; we don't explicitly check order)
        else: raise RuntimeError("evaluate_repair() failed.")                   # The repair was attempted and failed, and none of the cause categories were identified
    else: raise RuntimeError('invalid value for parameter \'method\'')


def write_dict_to_file(d,n,fname=False,console_dump=False):
    '''
    The output of evaluate_repair(), if successful, includes a dictionary of all
    viable edge modifications. This function writes this dictionary (d) in a
    human-readable format to a .txt file at fname (if fname != False), and
    dumps the data to the console (if console_dump = True).

    Note that when fixing to a SS, the "adjustments" are permanent, whereas when
    fixing to a LC, the adjustments may not permanently adjust the state of the
    node, but rather ensures that is follows the prescribed oscillations.
    '''
    out = ''
    for node in d.iterkeys():
        out+='Modifications for node '+n[node]+':\n'
        for entry in d[node]:
            if entry[0] == 1 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND %s\t(absent_new)\n'%(entry[1],n[entry[-1]])
            elif entry[0] == 1 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR %s\t(present_new)\n'%(entry[1],n[entry[-1]])
            elif entry[0] == 2 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND NOT %s\t(present_new)\n'%(entry[1],n[entry[-1]])
            elif entry[0] == 2 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR NOT %s\t(absent_new)\n'%(entry[1],n[entry[-1]])
            elif entry[0] == 3 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND (%s OR %s)\t(absent, absent_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 3 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR (%s AND %s)\t(present, present_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 4 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND (%s OR NOT %s)\t(absent, present_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 4 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR (%s AND NOT %s)\t(present, absent_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 5 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND (NOT %s OR %s)\t(present, absent_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 5 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR (NOT %s AND %s)\t(absent, present_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 6 and entry[1] == 0: out+= '\tAdjust to %s via: ... AND (NOT %s OR NOT %s)\t(present, present_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
            elif entry[0] == 6 and entry[1] == 1: out+= '\tAdjust to %s via: ... OR (NOT %s AND NOT %s)\t(absent, absent_new)\n'%(entry[1],n[entry[-2]],n[entry[-1]])
        out+='\n\n'

    if fname:
        f = open(fname,'wt')
        f.write(out)
        f.close()

    if console_dump:
        print out
