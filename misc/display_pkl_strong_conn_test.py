import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# 10 nodes
# fname = 'figure_journal/graph2_dist'
# fname = 'figure_journal/graph2_min'
# 20 nodes
# fname = 'figure_journal/graph3_dist'
# fname = 'figure_journal/graph3_min'
# 50 nodes
# fname = 'figure_journal/graph5_dist'
# fname = 'figure_journal/graph5_min'
# 1000 nodes
# fname = 'figure_journal/graph1000_dist'
fname = 'figure_journal/graph1000_min'

# widthSizeMul, heightSizeMul = 0.5, 0.6
# widthSizeMul, heightSizeMul = 0.5, 1.2
# widthSizeMul, heightSizeMul = 1, 1
widthSizeMul, heightSizeMul = 2, 2

windowSize = [widthSizeMul*6.4, heightSizeMul*4.8]
USE_SMALL_NODE = True


SHOW_ORIGINAL_GRAPH = False
SHOW_MODIFIED = True

with open(fname+'.pkl', 'rb') as f: 
    import pickle
    n, ori_A, A, G, Gpos, dummyLines, labels = pickle.load(f)
    print(n)
    # remapping
    mapping = {i:str(i+1) for i in range(n)}

    if SHOW_ORIGINAL_GRAPH:
        # Draw the network
        # Adding Identity to force display of individual isolated node
        rows, cols = np.where(ori_A == 1)
        edges = zip(rows.tolist(), cols.tolist())
        ori_G = nx.from_numpy_array(np.zeros((n,n)), create_using=nx.MultiDiGraph)        
        ori_G.add_edges_from(edges, color='k',weight=1)
        
        ori_dummyLines = [Line2D([0], [0], color='k', linewidth=1)]
        ori_labels = ['Original Edges']

        colors = nx.get_edge_attributes(ori_G,'color').values()
        weights = nx.get_edge_attributes(ori_G,'weight').values()

        plt.figure(1,figsize=windowSize) 
        if USE_SMALL_NODE:
            nx.draw(ori_G, Gpos, edge_color=colors, width=list(weights),\
                connectionstyle='arc3, rad = 0.1', node_size=10)
        else:
            nx.draw(ori_G, Gpos, edge_color=colors, width=list(weights),\
                   with_labels=True, connectionstyle='arc3, rad = 0.1')
        plt.legend(ori_dummyLines, ori_labels)
        plt.savefig(fname+'_ori.pdf')

    if SHOW_MODIFIED:
        colors = nx.get_edge_attributes(G,'color').values()
        weights = nx.get_edge_attributes(G,'weight').values()

        plt.figure(2,figsize=windowSize) 
        if USE_SMALL_NODE:
            nx.draw(G, Gpos, edge_color=colors, width=list(weights),\
                connectionstyle='arc3, rad = 0.1', node_size=10)
        else:
            nx.draw(G, Gpos, labels=mapping, edge_color=colors, width=list(weights),\
                   with_labels=True, connectionstyle='arc3, rad = 0.1')
        plt.legend(dummyLines, labels)
        plt.savefig(fname+'.pdf')
        plt.show()
