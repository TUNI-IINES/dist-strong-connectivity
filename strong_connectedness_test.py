import testGraphs as tg
from msgForwarder import MsgForwarder
from nodeconnCDC import NodeConn
#from nodeconnJournal import NodeConn


# Admittance matrix to ease assigning for in-neighbor and out-neighbor
# A = tg.A1 # Strongly connected digraph with 8 nodes 
A = tg.A2 # Weakly connected digraph with 10 nodes
# A = tg.A3 # Disconnected digraph with 20 nodes

n = A.shape[0] # A should always be a square matrix

def main():    
    # Initialize message forwarder (simulate sending message from one node to the other)
    msg = MsgForwarder(A)
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
                outMessage = Node[i].updateEnsureStrongConn(inMessage) # Algorithm 3
                
                # --------------------------------------------------------------------

                # Sending message to other nodes (to be processed later by MsgForwarder)
                msg.buffFrom[i] = outMessage
                
                # Accumulate this node running status into anyRunning
                anyRunning = anyRunning or Node[i].isRunning

        # Forward messages to the correct respondent for next iteration
        msg.processBuffer()
        
        outnode_it += 1
        if outnode_it > 3*n*n:
            anyRunning = False
            print('quitting the program, infinite loop. Current iterations: {}'.format(outnode_it))

    print('Centralized counter: All nodes finished in iterations {}'.format(outnode_it))
    msg.drawCommNetwork()

if __name__ == '__main__':
    main()