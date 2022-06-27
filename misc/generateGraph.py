import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pickle

n = 1000 # number of nodes
fname = 'misc/generatedA_'+str(n)
IS_GENERATE_NEW = False

if IS_GENERATE_NEW:
    p = 1/n # probability of edge

    # Generate random graph
    G = nx.gnp_random_graph(n, p, directed=True)

    # extract Adjacency matrix to numpy array
    A = nx.to_numpy_array(G)
    # A = np.squeeze(np.asarray(Amat))

    # Save A matrix to txt file
    np.savetxt(fname+'.txt', A, fmt='%d', delimiter=',')
    # Saving the objects:
    with open(fname+'.pkl', 'wb') as f: 
        pickle.dump([n, G, A], f)

else:
    # Getting back the objects:
    with open(fname+'.pkl', 'rb') as f: 
        n, G, A = pickle.load(f)

    #G = nx.from_numpy_array(A, create_using=nx.MultiDiGraph)

# Display graph
#Gpos = nx.kamada_kawai_layout(G)
Gpos = nx.nx_agraph.pygraphviz_layout(G)

#nx.draw(G, Gpos, with_labels=True, connectionstyle='arc3, rad = 0.1')
nx.draw(G, Gpos, connectionstyle='arc3, rad = 0.1', node_size=10)
plt.show()

