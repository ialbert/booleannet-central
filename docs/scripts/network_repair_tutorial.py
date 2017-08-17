'''
This is an example script that makes use of the edge modification repair
methodology introduced in Campbell and Albert (2014), BMC Syst. Biol.

Please feel free to contact me with questions and/or comments.

Colin Campbell
Contact: colin.campbell@psu.edu
Python Version: 2.7.x
Date: April 2014
'''

import networkx as nx
import network_repair_functions as nr

# First, we load in network update rules. See sample_network.txt for details on
# format
f = open(r'sample_network.txt','Urt')
lines = f.readlines()
f.close()

# We construct a network based on these rules
G,nodes = nr.form_network(lines)

# We can determine an attractor by iteratively evaluating from a random or
# specified network state. Here we choose the 'all ON' state.
# A is a list of the form [next state,eventual attractor]
A = nr.find_attractor(G,state='11111')                                          # Omit 'state' parameter for random selection of initial state (randomly identifies attractor with preference for those with larger basins)
print 'Attractor states:'
for x in A[1]: print ''.join(x)

# 'A' from above is a limit cycle. We can form its superset: a single state
# where nodes that are always OFF are OFF, others are ON.
A_s = nr.superset(A)
print 'Attractor superset:\n%s'%(''.join(A_s))

# We knockout the node at index 1 (node B)
G_d = nr.damage_network(G,force=1,force_type='knockout')                        # If we instead do [ nr.damage_network(G,a=A_s) ], a node is randomly chosen and fixed to its opposite state from A_s

# We examine the initial limit cycle to see what state pairs collapse due to
# the damage, and what portion of the LC we can actually stabilize, given the
# damage. A_d maintains format of A:
# [next state (as in A), surviving_attractor (new)]
cut,A_d = nr.compare_attractors(G_d,A)                                          # 'cut' is True if a collapse of the attractor occurs, False otherwise. A_d is the damaged version of the attractor.
print 'Desired stable attractor after knocking out node B:'
for x in A_d[1]: print ''.join(x)

# We now want to check the stability of A_d as a result of this damage.
stable = nr.check_stability(G_d,A_d)

# If stable == True, we'd be done. Here, stable == False, so we proceed to
# evaluate ways by which we can modify interactions to make A_d stable.
# The approach differs based on the parameter 'method'; it must be 'LC_repair'
# or 'fix_to_SS' For the former, the attractor will be modified so as to
# preserve its LC dynamics. For the latter, the LC superset will be stabilized
# as a SS.'
G_r_LC,choice_dict_LC = nr.evaluate_repair(G_d,A_d,A_s,method='LC_repair')      # First, we attempt to preserve the limit cycle in it's damage-modified form. The output here is a string indicating this is not possible
print 'Preservation of LC failed because: %s'%(G_r_LC)

print 'Attempting Superset Repair...'
G_r_SS,choice_dict_SS = nr.evaluate_repair(G_d,A_d,A_s,method='fix_to_SS')      # Next, we make the superset of A_d a steady state of the network

# Finally, we write choice_dict_SS to file in a readable format. This lists all
# possible edge modifications for every node that preserve it as specified
# above. Nodes that are omitted require no modification.
# Set console_dump to True/False to write contents to console or not
nr.write_dict_to_file(choice_dict_SS,nodes,fname='sample_output_dict.txt',console_dump=True)







