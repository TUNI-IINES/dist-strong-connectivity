import testGraphs as tg
from msgForwarder import MsgForwarder
# from nodeconnCDC import NodeConn
from nodeconnJournal import NodeConn

def single_run(A, print_step = True, display_graph = True, save_data = True): 
    # A should always be a square matrix
    n = A.shape[0] 

    # Silent Mode without showing graph
    MsgForwarder_is_draw = False
    MsgForwarder_is_print = False
    Node_print_mode = 'silent'
    
    if display_graph: MsgForwarder_is_draw = True
    if print_step:
        print('Start main function.')
        MsgForwarder_is_print = True
        Node_print_mode = None
        
    # Initialize message forwarder (simulate sending message from one node to the other)
    msg = MsgForwarder(A, 
        showDraw = MsgForwarder_is_draw, saveFig = save_data, 
        show_step = MsgForwarder_is_print)
    # msg.drawCommNetwork() # draw original graph
    # Initialize a list of NodeConn objects
    Node = [NodeConn(i, n, A[:,i], A[i]) for i in range(n)]

    if print_step: print('Finish initiating nodes.')

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
                # outMessage = Node[i].updateEnsureStrongConn(inMessage)
                outMessage = Node[i].updateEnsureStrongConn_MinLink(inMessage, print_mode = Node_print_mode)

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
            raise AssertionError('quitting the program, infinite loop. Current iterations: {}'.format(outnode_it))

        if n > 100:
            print('-', end='', flush=True)
            if outnode_it%n == 0: 
                if outnode_it%(n*n) == 0: print('.', flush=True)
                else: print('.', end=' ', flush=True)

    if print_step:
        print('Centralized counter: All nodes finished in iterations {}'.format(outnode_it))
    msg.drawCommNetwork()

    # SANITY TEST: all graph should be strongly connected
    for i in range(n):
        assert Node[i].isStronglyConnected, f"Node {i} is not strongly connected"

    # Return the number of iterations, added links, and minimum link
    ActualIteration = outnode_it - 2*n #deduct time for last verification
    return ActualIteration, msg.AddedLink, msg.reconfigure_newEdges

if __name__ == '__main__':

    # Admittance matrix to ease assigning for in-neighbor and out-neighbor
    #A = tg.graph1['A'] # Strongly connected digraph with 8 nodes 
    # A = tg.graph2['A'] # Weakly connected digraph with 10 nodes
    #A = tg.graph3['A'] # Disconnected digraph with 20 nodes
    #A = tg.graph4['A'] # Disconnected digraph with 20 nodes
    #A = tg.graph5['A'] # Disconnected digraph with 50 nodes

    # n= 50 # sources:13, sinks:15, isolated:8
    # # n=200 # sources:46, sinks:40, isolated:34
    # # n=1000
    A = tg.extract_pickle_graph_n(1000)

    # Random graph
    # A = tg.generate_random_n(50)

    # CALLING THE MAIN FUNCTION
    # single_run(A)
    single_run(A, print_step = False, display_graph = False)
    