import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

#fname = 'temp/test_20220627_022420_PM' # 200 nodes Iterative Link
fname = 'temp/test_20220627_023609_PM' # 200 nodes Minimum Link
SHOW_ORIGINAL_GRAPH = True
SHOW_MODIFIED = True

with open(fname+'.pkl', 'rb') as f: 
    import pickle
    n, ori_A, A, G, Gpos, dummyLines, labels = pickle.load(f)

    if SHOW_ORIGINAL_GRAPH:
        # Draw the network
        # Adding Identity to force display of individual isolated node
        rows, cols = np.where(ori_A == 1)
        edges = zip(rows.tolist(), cols.tolist())
        ori_G = nx.from_numpy_array(np.zeros((n,n)), create_using=nx.MultiDiGraph)        
        ori_G.add_edges_from(edges, color='k',weight=1)
        #Gpos = nx.nx_agraph.pygraphviz_layout(self.G) # require pygraphviz 
        
        ori_dummyLines = [Line2D([0], [0], color='k', linewidth=1)]
        ori_labels = ['Original Edges']

        colors = nx.get_edge_attributes(ori_G,'color').values()
        weights = nx.get_edge_attributes(ori_G,'weight').values()

        nx.draw(ori_G, Gpos, edge_color=colors, width=list(weights),\
            connectionstyle='arc3, rad = 0.1', node_size=10)
        plt.legend(ori_dummyLines, ori_labels)
        plt.show()

    if SHOW_MODIFIED:
        colors = nx.get_edge_attributes(G,'color').values()
        weights = nx.get_edge_attributes(G,'weight').values()

        nx.draw(G, Gpos, edge_color=colors, width=list(weights),\
            connectionstyle='arc3, rad = 0.1', node_size=10)
        plt.legend(dummyLines, labels)
        plt.show()