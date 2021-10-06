import testGraphs as tg
from msgForwarder import MsgForwarder
#from nodeconnCDC import NodeConn
from nodeconnJournal import NodeConn
import numpy as np
import math
import matplotlib.pyplot as plt

from contextlib import contextmanager
import sys, os
import csv
from datetime import datetime

# Admittance matrix to ease assigning for in-neighbor and out-neighbor
# G = tg.graph1 # Strongly connected digraph with 8 nodes 
# G = tg.graph2 # Weakly connected digraph with 10 nodes
# G = tg.graph3 # Disconnected digraph with 20 nodes
# G = tg.graph4 # Disconnected digraph with 20 nodes
G = tg.graph5 # Disconnected digraph with 50 nodes
A = G['A']
n = A.shape[0] # A should always be a square matrix

ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
MaxAddedLink = G['sourceSccNum'] + G['sinkSccNum'] + G['isolatedSccNum'] + G['disjointGraph']
MaxIter = (11*n) + (5*n* math.ceil( 1 + math.log2(G['disjointGraph'] - G['isolatedSccNum']/2) ) )
MinIter = (11*n) + (5*n) # assuming 2 step iteration with minimum link verification

# Function to fully suppress print output in terminal
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def single_run():    
    # Initialize message forwarder (simulate sending message from one node to the other)
    msg = MsgForwarder(A, showDraw = False, saveFig = False)
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
                
                # Algorithms in Journal version - to be tested
                # use "from nodeconnJournal import NodeConn" in line 4
                # --------------------------------------------------------------------                
                outMessage = Node[i].updateEnsureStrongConn_MinLink(inMessage, suppressPrint = True)

                # --------------------------------------------------------------------

                # Sending message to other nodes (to be processed later by MsgForwarder)
                msg.buffFrom[i] = outMessage
                
                # Accumulate this node running status into anyRunning
                anyRunning = anyRunning or Node[i].isRunning

        # Forward messages to the correct respondent for next iteration
        msg.processBuffer()
        
        outnode_it += 1
        if outnode_it > 20*n*n:
            anyRunning = False
            print('quitting the program, infinite loop. Current iterations: {}'.format(outnode_it))

    print('Centralized counter: All nodes finished in iterations {}'.format(outnode_it))
    msg.drawCommNetwork()

    # SANITY TEST: all graph should be strongly connected
    for i in range(n):
        assert Node[i].isStronglyConnected, f"Node {i} is not strongly connected"

    # Return the number of iterations, added links, and minimum link
    ActualIteration = outnode_it - 2*n #deduct time for last verification
    return ActualIteration, msg.AddedLink, msg.reconfigure_newEdges

def main():
    it = 0
    total_it = n*n
    testName = 'temp/' + G['name'] + 'benchmark' + datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = open( (testName + '.csv'), mode='w')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    print('Testing algorithm for {} iterations and saving it into {}'.format(total_it,testName))
    while it < total_it:
        #if True:
        with suppress_stdout():
            iterNum, addedLink, minLink = single_run()
            csv_writer.writerow([iterNum, len(addedLink), addedLink, len(minLink), minLink])
            #print('Single run data: iter {}, added {} --> {}'.format(iterNum, addedLink, minLink))


        NumMinLink = len(minLink)
        NumAddedLink = len(addedLink)        
        # NumMinLink is 0 when the original added link (NumAddedLink) is already optimal
        currentMinLink = NumMinLink if NumMinLink > 0 else NumAddedLink

        if it == 0: 
            # ValMinLink = currentMinLink # get the minimum link number (first time)
            Data = np.array([iterNum, NumAddedLink, 1]).reshape(1, 3)
        else:
            idx = np.where((Data[:,0] == iterNum) & (Data[:,1] == NumAddedLink))[0]
            if len(idx) > 0: # there is already existing values
                Data[idx[0],2] += 1
            else: # append the new data
                Data = np.vstack([Data, [iterNum, NumAddedLink, 1]])

        # SANITY TEST check if minlink is the same as the beginning
        assert (currentMinLink == ValMinLink), \
            f"Weird minlink value. Expected {ValMinLink}, received {currentMinLink}. Showing addLink {addedLink} and MinLink {minLink}"
        assert (iterNum <= MaxIter), \
            f"Weird iteration number. Expected <= {MaxIter}, received {iterNum}. Showing addLink {addedLink} and MinLink {minLink}"
        assert (NumAddedLink <= MaxAddedLink), \
            f"Weird number of added link. Expected <= {MaxAddedLink}, received {NumAddedLink}. Showing addLink {addedLink} and MinLink {minLink}"

        it += 1
        # Simple Progress Bar 
        print(".", end =" ")
        if (it % n) == 0: print((str(it) + ' ' + datetime.now().strftime("%Y%m%d_%H%M%S")), flush=True)
        # increase iteration number

    print('Done')
    print(Data)
    print('Maxiter {}. MaxAddedLink {}. MinLink {}'.format(MaxIter, MaxAddedLink, ValMinLink))

    csv_writer.writerow([Data])
    csv_writer.writerow([MaxIter, MaxAddedLink, ValMinLink])
    plotData(Data, (testName + '.pdf') )

def plotData(Data, fname = 'benchmarktest.png'):
    plt.rcParams.update({'font.size': 14})
    ax = plt.figure().gca()
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)

    plt.scatter(Data[:,1],Data[:,0]/n,s=2*Data[:,2])
    for i, txt in enumerate(Data[:,2]):
        plt.annotate(txt, (Data[i,1],Data[i,0]/n))

    nMinIter = MinIter/n
    nMaxIter = MaxIter/n
    if nMinIter == nMaxIter:
        nMinIter -= 1
        nMaxIter += 1

    xoffset = (MaxAddedLink - ValMinLink)/10
    yoffset = (nMaxIter - nMinIter)/10

    ax.set_xlim( [ ValMinLink-xoffset*3/2, MaxAddedLink+xoffset*3/2 ] )
    ax.set_ylim( [ nMinIter-yoffset, nMaxIter+yoffset*5/2 ] )

    plt.hlines(MaxIter/n, ValMinLink, MaxAddedLink)
    plt.vlines(ValMinLink, nMinIter, nMaxIter)
    plt.vlines(MaxAddedLink, nMinIter, nMaxIter)

    vcenter = (nMinIter + nMaxIter)/2
    xcenter = (ValMinLink + MaxAddedLink)/2

    plt.text(ValMinLink - xoffset*3/4, vcenter, "Optimal Number of Links", rotation=90, verticalalignment='center', fontsize='smaller')

    plt.text(MaxAddedLink + xoffset/4, vcenter, "Theoretical Maximum Number", rotation=90, verticalalignment='center', fontsize='smaller')
    plt.text(MaxAddedLink + xoffset*3/4, vcenter, "of Augmented Links", rotation=90, verticalalignment='center', fontsize='smaller')

    plt.text(xcenter + 2*xoffset, (MaxIter/n)+yoffset*3/2, "Theoretical Maximum", horizontalalignment='center', fontsize='smaller')
    plt.text(xcenter + 2*xoffset, (MaxIter/n)+yoffset/2, "Number of Iterations", horizontalalignment='center', fontsize='smaller')

    plt.xlabel('Number of Augmented links')
    plt.ylabel('Number of iterations (times n)')

    plt.savefig(fname)
    plt.show()

def plotOnly():
    
    testName = 'temp/graph2WCbenchmark20211001_132431'
    Data = np.array([
        [160,   4,  35],
        [160,   3,  65]
    ])

    #testName = 'temp/graph3DCbenchmark20211001_133201'
    #Data = np.array([
    #    [320,  12, 175],
    #    [320,  11, 163],
    #    [420,  12,   4],
    #    [320,  10,  26],
    #    [320,  13,  27],
    #    [420,  13,   2],
    #    [320,   9,   2],
    #    [420,  11,   1]
    #])

    #testName = 'temp/graph5DCbenchmark20211003_003438'
    #Data = np.array([
    #    [1050,   31,  821],
    #    [1050,   32,  506],
    #    [1050,   29,  239],
    #    [1050,   30,  612],
    #    [1050,   33,  133],
    #    [1050,   34,   12],
    #    [1050,   28,   43],
    #    [ 800,   29,   45],
    #    [ 800,   31,   20],
    #    [ 800,   30,   39],
    #    [ 800,   28,   17],
    #    [ 800,   33,    1],
    #    [ 800,   32,    4],
    #    [1050,   27,    4],
    #    [ 800,   27,    4]
    #])

    plotData(Data, (testName + '.pdf') )

if __name__ == '__main__':
    main()
    #plotOnly()
