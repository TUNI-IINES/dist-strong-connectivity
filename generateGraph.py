import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

n = 50 # number of nodes
p = 1/n # probability of edge
G = nx.gnp_random_graph(n, p, directed=True)
Amat = nx.adjacency_matrix(G).todense()
A = np.squeeze(np.asarray(Amat))
print(A)
Gpos = nx.nx_pydot.graphviz_layout(G)
nx.draw(G, Gpos, with_labels=True, connectionstyle='arc3, rad = 0.1')
plt.show()
