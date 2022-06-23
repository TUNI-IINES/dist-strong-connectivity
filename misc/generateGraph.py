import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

n = 50 # number of nodes
p = 1/n # probability of edge

# Generate random graph
G = nx.gnp_random_graph(n, p, directed=True)

# extract Adjacency matrix to numpy array
A = nx.to_numpy_array(G)
# A = np.squeeze(np.asarray(Amat))

# Save A matrix to txt file
np.savetxt('generatedA_test.txt', A, fmt='%d', delimiter=',')

# Display graph
Gpos = nx.kamada_kawai_layout(G)
# Gpos = nx.nx_pydot.graphviz_layout(G)
nx.draw(G, Gpos, with_labels=True, connectionstyle='arc3, rad = 0.1')
plt.show()

