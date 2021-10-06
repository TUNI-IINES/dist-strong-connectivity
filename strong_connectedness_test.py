import testGraphs as tg
from msgForwarder import MsgForwarder
# from nodeconnCDC import NodeConn
from nodeconnJournal import NodeConn
import networkx as nx
import numpy as np

# Admittance matrix to ease assigning for in-neighbor and out-neighbor
# G = tg.graph1 # Strongly connected digraph with 8 nodes 
# G = tg.graph2 # Weakly connected digraph with 10 nodes
G = tg.graph3 # Disconnected digraph with 20 nodes
# G = tg.graph4 # Disconnected digraph with 20 nodes
#G = tg.graph5 # Disconnected digraph with 50 nodes

A = G['A']
n = A.shape[0] # A should always be a square matrix

# # Random Graph
# n = 50 # number of nodes
# p = 1/n # probability of edge
# G = nx.gnp_random_graph(n, 1/n, directed=True)
# Amat = nx.adjacency_matrix(G).todense()
# A = np.squeeze(np.asarray(Amat))
# print(A)

def main():    
    # Initialize message forwarder (simulate sending message from one node to the other)
    msg = MsgForwarder(A)
    msg.drawCommNetwork() # draw original graph
    # Initialize a list of NodeConn objects
    Node = [NodeConn(i, n, A[:,i], A[i]) for i in range(n)]

    anyRunning = True
    outnode_it = 0
    # Keep looping as long as one node keep running
    while anyRunning:

        # Re-initialized anyRunning
        anyRunning = False

        # Update running node
        for i in range(n):
            if Node[i].isRunning:
                # Collect incoming message (retrieved from MsgForwarder)
                inMessage = msg.buffTo[i]
                
                # --------------------------------------------------------------------
                # Process the incoming messages, update states and output new messages
                # --------------------------------------------------------------------
                
                # Algorithms in CDC paper version
                # use "from nodeconnCDC import NodeConn" in line 3
                # --------------------------------------------------------------------
                # outMessage = Node[i].updateVerifyStrongConn(inMessage) # Algorithm 1
                # outMessage = Node[i].updateEstimateSCC(inMessage) # Algorithm 2
                # outMessage = Node[i].updateEnsureStrongConn(inMessage) # Algorithm 3
                

                # Algorithms in Journal version (under preparation)
                # use "from nodeconnJournal import NodeConn" in line 4
                # --------------------------------------------------------------------                
                # outMessage = Node[i].updateVerifyStrongConn(inMessage) # Algorithm 1
                # outMessage = Node[i].updateEstimateSCC(inMessage) # Algorithm 2
                # outMessage = Node[i].updateEnsureStrongConn_Weak(inMessage)
                outMessage = Node[i].updateEnsureStrongConn_MinLink(inMessage, suppressPrint = True)

                # --------------------------------------------------------------------

                # Sending message to other nodes (to be processed later by MsgForwarder)
                msg.buffFrom[i] = outMessage
                
                # Accumulate this node running status into anyRunning
                anyRunning = anyRunning or Node[i].isRunning

        # Forward messages to the correct respondent for next iteration
        msg.processBuffer()
        
        outnode_it += 1
        if outnode_it > 10*n*n:
            anyRunning = False
            print('quitting the program, infinite loop. Current iterations: {}'.format(outnode_it))

    print('Centralized counter: All nodes finished in iterations {}'.format(outnode_it))
    msg.drawCommNetwork()

if __name__ == '__main__':
    main()