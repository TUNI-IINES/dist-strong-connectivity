import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

class MsgForwarder(object):
    """
    Simulate the process of sending message from one node to another
    The message is a dictionary constructed in NodeConn Object
    consisting of: sender, dest, msgType, and msg
    """
    def __init__(self, A):
        super(MsgForwarder, self).__init__()
        self.A = A.copy()
        self.original_A = A.copy()
        self.n = self.A.shape[0] # A should always be a square matrix

        # Initiate empty list (buffer)
        self.buffFrom = [ [] for _ in range(self.n) ]
        self.buffTo = [ [] for _ in range(self.n) ]
        
        self.init_drawCommNetwork()
        self.k = 0 # Counter for link addition

        self.reconfigure_A = None
        self.reconfigure_newEdges = []
        self.recorded_reconfigure = [{'number':0, 'links':[]}]

    # Visualize the network
    def init_drawCommNetwork(self):
        # Draw the network
        rows, cols = np.where(self.A == 1)
        edges = zip(rows.tolist(), cols.tolist())
        self.G = nx.MultiDiGraph()
        self.G.add_edges_from(edges, color='k',weight=1)
        # self.Gpos = nx.circular_layout(self.G)
        self.Gpos = nx.kamada_kawai_layout(self.G)
        
        self.colorList = ['r','g','b','c','m','y']
        self.dummyLines = [Line2D([0], [0], color='k', linewidth=1)]
        self.labels = ['Original Edges']
                
    def drawCommNetwork(self):
        colors = nx.get_edge_attributes(self.G,'color').values()
        weights = nx.get_edge_attributes(self.G,'weight').values()
        nx.draw(self.G, self.Gpos, edge_color=colors, width=list(weights),\
                with_labels=True, connectionstyle='arc3, rad = 0.1')
        plt.legend(self.dummyLines, self.labels)
        plt.show(block=False)
                
    # Process outgoing message into buffer to be read for each node i
    def processBuffer(self):
        # input is a list of dictionary of messages
        #------------------------------------------------------------------
        # Message is being encapsulated as a dict, consisting of :
        #    sender, dest (both in vertex number)
        #     msg_type and the msg itself (just to be clear, msg is message)

        # reset buffTo to be filled with new messages in msg_in
        self.buffTo = [ [] for _ in range(self.n) ]

        # Flag for link addition
        isLinkAdded = False

        for i in range(self.n):
            for dictMsg in self.buffFrom[i]:
                # Error Trap
                if dictMsg['sender'] != i:
                    print('MsgForwarder: unusual package: from {} with id {}. Should be the same' \
                        .format(i, dictMsg['sender']))
                
                # Check whether it is listed in Adjacency matrix
                if (self.A[i][dictMsg['dest']] == 1) :
                    # Forward the message to the correct destination buffer 
                    self.buffTo[dictMsg['dest']].append(dictMsg)
                    
                    # Check out for reconfiguration broadcast and save
                    if dictMsg['msg_type'] == 'bcR':
                        ReconfigureLink = dictMsg['msg']
                        if ReconfigureLink not in self.recorded_reconfigure:
                            # Prepare for new configuration to be implemented                            
                            self.recorded_reconfigure.append(ReconfigureLink)

                            if ReconfigureLink['number'] > 0:
                                self.reconfigure_A = self.original_A.copy()
                                
                                for link in ReconfigureLink['links']:
                                    self.reconfigure_A[link['sender']][link['dest']] = 1
                                    self.reconfigure_newEdges += [(link['sender'], link['dest'])]
                                    
                                print('MsgForwarder: Detecting Reconfiguration package, saved.')


                else:
                    # Draw additional edges, when the requested edge passed
                    if (dictMsg['msg_type'] == 'la'):
                        # update into adjacency matrix
                        print('MsgForwarder: New connection request detected and updated to matrix A[{}][{}]' \
                              .format(i, dictMsg['dest']) )
                        self.A[i][dictMsg['dest']] = 1
                        # Add link addition counter only once per all addition
                        if not isLinkAdded:
                            isLinkAdded = True
                            self.k += 1
                            # Assign color and weight for new edges here
                            temp = (self.k-1) % len(self.colorList)
                            selCol = self.colorList[temp]
                            selWeight = np.ceil(self.k / len(self.colorList))*2
                            # The variables will remains during this session
                            
                            # Add variables for Legend Description
                            self.dummyLines.append(Line2D([0], [0], color=selCol, linewidth=selWeight))
                            self.labels.append('Added Edges #'+str(self.k))
                        
                        # Forward the message to the correct destination buffer 
                        self.buffTo[dictMsg['dest']].append(dictMsg)
                        
                        # Add information for drawing
                        self.G.add_edges_from([(dictMsg['sender'], dictMsg['dest'])],\
                                              color=selCol, weight=selWeight)
                    
                    # Same Destination with msg_type RN >> Network Reconfiguration
                    elif (dictMsg['dest'] == i) and (dictMsg['msg_type'] == 'RN'):
                        if self.reconfigure_A is not None:                            
                            # DRAW the previous network
                            self.drawCommNetwork()
                                                        
                            # Initialize new drawing for the new network
                            self.A = self.original_A.copy()
                            self.init_drawCommNetwork()

                            self.k += 1
                            # Assign color and weight for new edges here
                            temp = (self.k-1) % len(self.colorList)
                            selCol = self.colorList[temp]
                            selWeight = np.ceil(self.k / len(self.colorList))*2
                            # Add variables for Legend Description
                            self.dummyLines.append(Line2D([0], [0], color=selCol, linewidth=selWeight))
                            self.labels.append('Minimum Link Edges')

                            self.G.add_edges_from(self.reconfigure_newEdges,\
                                                  color=selCol, weight=selWeight)                            

                            # Reconfigure New Network
                            self.A = self.reconfigure_A.copy()
                            self.reconfigure_A = None # to skip next similar message
                            print('MsgForwarder: Activating past recorded Reconfiguration Network.')

                    else:
                        print('MsgForwarder: Deleting unauthorized message from {} to {}: {} {}' \
                              .format(i, dictMsg['dest'], dictMsg['msg_type'], dictMsg['msg']) )

        # reset buffFrom to be filled in the next iteration
        self.buffFrom = [ [] for _ in range(self.n) ]        