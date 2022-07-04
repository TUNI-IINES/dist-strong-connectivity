import numpy as np

class NodeConn(object):

    """docstring for NodeConn"""
    def __init__(self, v_num, n, in_LapCol, out_LapRow):
        super(NodeConn, self).__init__()

        # Total number of iterations, and running status
        self.it = 0
        # this node's vertex number (0 to n-1)
        self.v_num = v_num 

        # total vertices number in graph 
        self.n = n 
        # array of in-neighbours
        self.in_neigh = np.where(in_LapCol == 1)[0]
        # array of out-neighbours
        self.out_neigh = np.where(out_LapRow == 1)[0]
        
        # State for proceeding with the algorithms  
        # -------------------------------------------------------------      
        self.startingState = 'x' # path estimation

        # ALGORITHM 1 - VERIFICATION OF STRONG COONECTIVITY 
        # path estimation + strongly connected verification
        self.verificationState = [self.startingState, 'f'] 

        # ALGORITHM 3 - ESTIMATION OF STRONGLY CONNECTED COMPONENTS
        # path estimation + SCC member estimation + characterize SCC
        self.estimateSCCState = [self.startingState, 'c', 'o' ] 

        # ALGORITHM 4 or 5 - LINK ADDITION
        # Algorithm 3 + select representative + broadcast information
        # --> may be repeated several time
        self.linkAddState = ['rep', 'bc']
        self.linkAddReq = 'la' # link addition

        # ALGORITHM 6 and 7 - ENFORCING MINIMUM LINK
        # Algorithm 4 or 5 + select representative + broadcast information 
        # + broadcast minimum link result
        self.minLinkVerState = ['repL', 'bcS', 'bcR']

        # Reset the states
        self.initializeNewProcedure()
        
        # unassigned Variables
        self.linkaddIter = 0
        self.original_isSCCrep = None
        self.original_estSource = None
        self.list_newOutNeigh = []
        self.list_newInNeigh = []

        # print(str(v_num), end='_', flush=True)


    # To allow running several procedure in series without resetting iteration number
    def initializeNewProcedure(self):
        self.iterState = 0
        self.currState = self.startingState
        self.isRunning = True
        self.initState() # All process always start with state x

    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 1: Distributed Algorithm for Solving Problem 1
    #     Problem 1: Verify in a distributed manner if the directed graph 
    #                is strongly connected
    # -------------------------------------------------------------------------------
    # When (show_step == False), the result can be checked by inspecting self.f
    # Namely, 
    #   self.f == 0 --> The graph is strongly connected
    #   self.f == 1 --> The graph is NOT strongly connected
    # 
    def updateVerifyStrongConn (self, buffTo, show_step = True):
        # Process the incoming messages
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, show_step):
                # process message information - maximum consensus algorithm
                if self.currState == self.verificationState[0]: 
                    self.x = [max(val) for val in zip(self.x, dictMsg['msg'])]
                    
                elif self.currState == self.verificationState[1]: 
                    self.f = max(self.f, dictMsg['msg'])
                
                else: # unexpected state
                    raise AssertionError(
                        'Node {}: Unusual currState {}'.format(self.v_num, self.currState) )
            else: # NOT THE EXPECTED MESSAGE during this state
                if not (dictMsg['msg_type'] == self.linkAddReq): 
                    raise AssertionError(
                        'Node {} inValidMsg: {}. Expecting {} from {}'.format(
                            self.v_num, dictMsg, self.currState, self.in_neigh) )
                # ELSE --> pass message as new link is already added during isValidMsg()

        self.it += 1
        # Procedure to check for switching between States
        if self.it % self.n == 0:
            # increment the current state
            self.iterState += 1

            if self.iterState >= len(self.verificationState):
                # Prohibit to run in the next turn
                self.isRunning = False
                if show_step:
                    print('Node {} finished Algorithm 1 in iterations {}'.format( \
                        self.v_num, self.it ))

                # Show the Final Verification Status
                final_status = 'IS'
                if self.f == 1:
                    final_status = 'is NOT'
                if show_step:
                    print('Node {}: The communication graph {} strongly connected'.format( \
                        self.v_num, final_status ))

            else: 
                # Set into the new self.currState
                self.currState = self.verificationState[self.iterState]
                # Initialize the new state
                self.initState()

        # Return the current state information towards out Neighbors
        return self.constructOutMsg()

    # END of Main Procedure for Algorithm 1
    # -------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 3: Distributed Estimation of SCC (Journal Version)
    # -------------------------------------------------------------------------------
    # When (show_step == False), the result can be checked by inspecting: 
    #   self.preSCC_elem --> All accessible nodes to this node's SCC 
    #   self.SCC_elem --> All nodes with the same SCC with this node
    #   self.isSinkSCC --> True if this node belong to sink-scc
    #   self.isSourceSCC --> True if this node belong to source-scc
    #   self.isIsolatedSCC --> True if this node belong to source-scc
    #   self.isStronglyConnected --> True if the whole graph is strongly connected
    #
    def updateEstimateSCC (self, buffTo, show_step = True):
        # setting suppressPrint to True, only suppress part of printing (nonessential)

        # Process the incoming messages
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, show_step):
                # process message information - maximum consensus algorithm
                if self.currState == self.estimateSCCState[0]:
                    self.x = [max(val) for val in zip(self.x, dictMsg['msg'])]
                    
                elif self.currState == self.estimateSCCState[1]: 
                    self.c = [max(val) for val in zip(self.c, dictMsg['msg'])]

                elif self.currState == self.estimateSCCState[2]:
                    self.o = [max(val) for val in zip(self.o, dictMsg['msg'])]
                
                else: # unexpected state
                    raise AssertionError(
                        'Node {}: Unusual currState {}'.format(self.v_num, self.currState) )
            else: # NOT THE EXPECTED MESSAGE during this state
                if not (dictMsg['msg_type'] == self.linkAddReq): 
                    raise AssertionError(
                        'Node {} inValidMsg: {}. Expecting {} from {}'.format(
                            self.v_num, dictMsg, self.currState, self.in_neigh) )
                # ELSE --> pass message as new link is already added during isValidMsg()

        self.it += 1
        # Procedure to check for switching between States
        if self.it % self.n == 0:
            # increment the current state
            self.iterState += 1

            if self.iterState >= len(self.estimateSCCState):

                # Prohibit to run in the next turn
                self.isRunning = False
                if show_step:
                    print('Node {} finished Algorithm 3 in iterations {} '.format( \
                        self.v_num, self.it ))
                # print('x {}'.format(self.x))
                # print('c {}'.format(self.c))
                # print('o {}'.format(self.o))

                isOut_SCC = sum(np.take(self.o, self.SCC_elem)) > 0
                isIn_SCC = len(self.preSCC_elem) > 0 

                # -----------------------------------------------------
                # Theorem 3 - Characterization of SCC
                # -----------------------------------------------------
                self.isSinkSCC = isIn_SCC and not isOut_SCC
                self.isSourceSCC = not isIn_SCC and isOut_SCC
                self.isIsolatedSCC = not isIn_SCC and not isOut_SCC
                self.isStronglyConnected = self.isIsolatedSCC and (len(self.SCC_elem) == self.n)

                # Show the Final Verification Status
                status = ''
                if self.isSinkSCC: status = '- Sink-SCC'
                elif self.isSourceSCC: status = '- Source-SCC'
                elif self.isIsolatedSCC: status = '- Isolated-SCC'
                elif self.isStronglyConnected: status = '- strongly connected graph'

                # inform status
                if show_step:
                    print('Node {}: preSCC {} own SCC {} {}'.format( \
                        self.v_num, self.preSCC_elem, self.SCC_elem , status))

            else: 
                # Set into the new self.currState
                self.currState = self.estimateSCCState[self.iterState]

                if self.currState == self.estimateSCCState[2]: #'o'
                    # Estimate SCC_elem and preSCC_elem before initialize state o
                    c_ii = self.c[self.v_num] # This node's information number
                    temp = np.array(self.c)
                    self.SCC_elem = np.where(temp == c_ii)[0]
                    self.preSCC_elem = np.where((temp > 0) & (temp < c_ii))[0]

                # Initialize the new state
                self.initState()

        # Return the current state information towards out Neighbors
        return self.constructOutMsg()

    # END of Main Procedure for Algorithm 2
    # -------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 4 and 5: Distributed Algorithm for Solving Problem 1
    #     Problem 2: Add additional edges in a distributed manner to strongly connect 
    #                the original graph
    # -------------------------------------------------------------------------------
    # update_representatives_broadcast --> supporting procedure 
    # to select representatives and broadcast information
    def update_representatives_broadcast (self, buffTo, show_step = True): 
        # Process the incoming messages
        
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, show_step):
                # process message information
                if self.currState == self.linkAddState[0]: # communicate for representative
                    # max consensus to get other nodes information within SCC
                    self.localSCCcomm = [max(val) for val in zip(self.localSCCcomm, dictMsg['msg'])]

                elif self.currState == self.linkAddState[1]: # Process broadcast information
                    if dictMsg['msg'] not in self.retrievedbcData :
                        # New message. save and forward
                        self.retrievedbcData.append(dictMsg['msg'])
                        self.forwardbcData.append(dictMsg['msg'])
                    # else: discard data, already retrieved previously

                else: # unexpected state
                    raise AssertionError(
                        'Node {}: Unusual currState {}'.format(self.v_num, self.currState) ) 
            else: # NOT THE EXPECTED MESSAGE during this state
                # Note: no link addition message is expected during this procedure
                raise AssertionError(
                    'Node {} inValidMsg: {}. Expecting {} from {}'.format(
                        self.v_num, dictMsg, self.currState, self.in_neigh) )

        self.it += 1
        # Procedure to check for switching between States
        if self.it % self.n == 0:
            # increment the current state
            self.iterState += 1
            
            if self.currState == self.linkAddState[0]: 
                # The end of local comm for representive (before broadcast)
                # Determine the representative
                if sum(self.localSCCcomm) == 0:
                    if self.isSinkSCC or self.isSourceSCC or self.isIsolatedSCC:
                        # As a default, determine rep as the highest node number
                        self.isSCCrep = ( self.v_num == max(self.SCC_elem) )
                else:
                    # select new representative from existing node
                    if self.original_isSCCrep:
                        # Check if it remain the same scc role
                        # select itself as rep if the other rep is lower 
                        id_allrep = []
                        temp = np.array(self.localSCCcomm)
                        
                        id_isolatedrep = np.where(temp == 3)[0]
                        if (self.original_isSinkSCC or self.original_isIsolatedSCC) \
                            and (self.isSinkSCC or self.isIsolatedSCC):
                            # Sink/isolated rep is selected from sink or isolated
                            id_allrep = np.where(temp == 1)[0]
                            if len(id_isolatedrep) > 0:
                                id_allrep = np.append ( id_allrep, id_isolatedrep )
                            # print('Debug {}: candidate sink/isol rep, id_allrep_prev {} id_isolatedrep {}.'.format( \
                            #     self.v_num, id_allrep, id_isolatedrep))

                        elif (self.original_isSourceSCC or self.original_isIsolatedSCC) \
                            and self.isSourceSCC :
                            # Source rep is selected from source or isolated
                            id_allrep = np.where(temp == 2)[0]
                            if len(id_isolatedrep) > 0:
                                id_allrep = np.append ( id_allrep, id_isolatedrep )
                            # print('Debug {}: candidate source rep, id_allrep_prev {} id_isolatedrep {}.'.format( \
                            #     self.v_num, id_allrep, id_isolatedrep))

                        if len(id_allrep) > 0:
                            self.isSCCrep = ( self.v_num == max(np.take(self.SCC_elem, id_allrep)))
                        
                        # print('Node {}: comm {} id_allrep {} isSCCrep {}.'.format( \
                        #      self.v_num, self.localSCCcomm, id_allrep, self.isSCCrep))

                if show_step:
                    out = ''
                    if self.isSCCrep:
                        if self.isSinkSCC: out = 'Selected as Sink representative'
                        elif self.isSourceSCC: out = 'Selected as Source representative'
                        elif self.isIsolatedSCC: out = 'Selected as Isolated representative'
                        else: out = 'Weird exception, Selected as ???'
                    print('Node {}: from SCC {} communicating {}. {}'.format( \
                        self.v_num, self.SCC_elem, self.localSCCcomm, out ))
                    # print('Node {} finished determining SCC rep in iterations {} '.format( \
                    #     self.v_num, self.it ))

                # Save original SCC if not assigned yet
                if self.original_isSCCrep is None:
                    # Save Initial Representative
                    self.original_isSCCrep = self.isSCCrep
                    # Save Initial Role
                    self.original_isSinkSCC = self.isSinkSCC
                    self.original_isSourceSCC = self.isSourceSCC
                    self.original_isIsolatedSCC = self.isIsolatedSCC
                    
                # Switch and initiate for next process
                self.currState = self.linkAddState[1]                  
                # Initialize the new state
                self.initState()

            elif self.currState == self.linkAddState[1]: # end of broadcast
                # Prohibit to run in the next turn
                self.isRunning = False
                # if not suppressPrint:
                #     print('Node {} finished Algorithm 2 in iterations {} '.format( \
                #         self.v_num, self.it ))
                
                # Process the collected broadcasted information if sink rep
                if self.isSCCrep and self.isSinkSCC :
                    if show_step:
                        print('Node {} Processing retrieved broadcast data, est Source {} '.format( \
                            self.v_num, self.retrievedbcData ))
                    
                    self.est_sources = self.retrievedbcData
                    if (self.original_isSinkSCC) and (self.original_estSource is None):
                        self.original_estSource = self.est_sources
                    
        # Return the current state information towards out Neighbors
        return self.constructOutMsg()
    
    # linkAdditionProcedure --> suppporting procedure to select and request new links to add
    def linkAdditionProcedure (self, it_mode, show_step = True):
        request_edge = []

        if self.isSCCrep and self.isIsolatedSCC :
            # this node is representative node of isolated-scc
            # reach out to a node outside of own SCC
            temp = np.array(self.x)
            nodes_outSCC = np.where(temp == 0)[0]
            selected_node = np.random.choice(nodes_outSCC)
            
            # append selected node to out-neighbor
            self.out_neigh = np.append(self.out_neigh, selected_node)
            self.list_newOutNeigh += [selected_node]
            
            if show_step:
                print('Node {}: Reaching out, sending requested new edge to node {}. Out-neighbor {}'\
                    .format(self.v_num, selected_node, self.out_neigh))

            # link addition sending request message to selected source
            request_edge += [{'sender':self.v_num, 'dest':selected_node, \
                'msg_type':self.linkAddReq, 'msg':''}]


        if self.isSCCrep and self.isSinkSCC :
            # this node is representative node of sink-scc
            # Estimate the sources set is retrieved from broadcast data
            
            # single sink to all accessible sources
            selected_source = self.est_sources

            # append selected source to out-neighbor
            self.out_neigh = np.append(self.out_neigh, selected_source)
            self.list_newOutNeigh += selected_source

            for source in selected_source:
                if show_step:
                    print('Node {}: sending requested new edge to node {}. Out-neighbor {}'\
                        .format(self.v_num, source, self.out_neigh))
    
                # link addition sending request message to selected source
                request_edge += [{'sender':self.v_num, 'dest':source, \
                    'msg_type':self.linkAddReq, 'msg':''}]
        
        if show_step:
            print('Node {} finished linkAdditionProcedure {} in iterations {} '.format( \
                self.v_num, it_mode, self.it ))
        
        return request_edge


    # ------------------------------------------------------------------
    # ALGORITHM 4 - DISTRIBUTED LINK ADDITION FOR WEAKLY CONNECTED GRAPH
    # ------------------------------------------------------------------
    def updateEnsureStrongConn_Weak (self, buffTo, print_mode = None):
        # Default console printing mode
        show_general_step = True
        show_detailed_step = False
        # Further adjustment when needed
        if print_mode == 'silent': show_general_step = False
        elif print_mode == 'detail': show_detailed_step = True

        outMsg = []
        totalState = self.estimateSCCState + self.linkAddState
        self.currState = totalState[self.iterState]   
        
        if any(item == self.currState for item in self.estimateSCCState) and (self.linkaddIter >= 0):
            # Keep Running Algorithm 3 until it finished
            outMsg = self.updateEstimateSCC(buffTo, show_detailed_step)

            if not self.isRunning:
                # The end of updateEstimateSCC Program
                if not self.isStronglyConnected :
                    # Reset the isRunning Flag to continue with link addition
                    self.isRunning = True 
    
                    # Set the variable for Initialization to select SCC representative
                    self.currState = totalState[self.iterState] 
                    self.initState()
                    outMsg = self.constructOutMsg()
                else:
                    # Already strongly connected
                    if show_general_step:
                        print('Node {} finished Algorithm 3 in iterations {}. Graph is strongly connected.'.format( \
                            self.v_num, self.it ))
                
        elif any(item == self.currState for item in self.linkAddState) and (self.linkaddIter >= 0):
            # Keep Running update_representatives_broadcast until it is finished
            outMsg = self.update_representatives_broadcast(buffTo, show_detailed_step)

            if not self.isRunning:
                # End of update_representatives_broadcast process
                # Continue to Link addition procedures
                request_edge = self.linkAdditionProcedure(self.linkaddIter, show_detailed_step)

                # Reset Algorithm 2 for next link addition / verification
                self.initializeNewProcedure() # Only reset state x at this point
                # Resend new information state
                outMsg = request_edge + self.constructOutMsg()

                # only run once --> MODIFIED DURING REVISION
                # The main algorithm ends here
                # In essence, we need additional 1 iteration
                # to process this requested messages on the other side
                # Here, we will do it while doing verification
                self.linkaddIter = -1
                if show_general_step:
                    print('Node {} finished Algorithm 4 in iterations {}. Graph should be strongly connected.'.format( \
                        self.v_num, self.it ))
                    print('Node {}: Switching to updateVerifyStrongConn for verification (Not necessarily needed)'.format( \
                        self.v_num))
        
        elif (self.linkaddIter == -1):
            # Running Verification to Show that the resulting graph is strongly connected
            self.currState = self.verificationState[self.iterState]   
            outMsg = self.updateVerifyStrongConn(buffTo, show_detailed_step) # suppress some print output
        
        else: raise AssertionError(
            'Node {}: Unusual currState {}, linkaddIter {}'.format(self.v_num, self.currState, self.linkaddIter))
        
        return outMsg
    
    
    # ------------------------------------------------------------------
    # ALGORITHM 5 - DISTRIBUTED LINK ADDITION FOR DISCONNECTED GRAPH
    # ------------------------------------------------------------------
    def updateEnsureStrongConn (self, buffTo, print_mode = None):
        # Default console printing mode
        show_general_step = True
        show_detailed_step = False
        # Further adjustment when needed
        if print_mode == 'silent': show_general_step = False
        elif print_mode == 'detail': show_detailed_step = True
        
        outMsg = []
        totalState = self.estimateSCCState + self.linkAddState
        self.currState = totalState[self.iterState]   
        
        if any(item == self.currState for item in self.estimateSCCState):
            # Keep Running Algorithm 3 until it finished
            outMsg = self.updateEstimateSCC(buffTo, show_detailed_step) 

            if not self.isRunning:
                # The end of updateEstimateSCC Program
                if not self.isStronglyConnected :
                    # Reset the isRunning Flag to continue with link addition
                    self.isRunning = True 
    
                    # Set the variable for Initialization to select SCC representative
                    self.currState = totalState[self.iterState]  
                    self.initState()
                    outMsg = self.constructOutMsg()
                else:
                    # Already strongly connected
                    if show_general_step:
                        print('Node {} finished Algorithm 5 in iterations {}. Graph is strongly connected.'.format( \
                            self.v_num, self.it ))
                
        elif any(item == self.currState for item in self.linkAddState):
            # Keep Running update_representatives_broadcast until it finished
            outMsg = self.update_representatives_broadcast(buffTo, show_detailed_step)

            if not self.isRunning:
                # End of update_representatives_broadcast process
                # Continue to Link addition procedures
                request_edge = self.linkAdditionProcedure(self.linkaddIter, show_detailed_step)

                # Reset Algorithm 5 for next link addition / verification
                self.initializeNewProcedure() # Only reset state x at this point
                # Resend new information state
                outMsg = request_edge + self.constructOutMsg()
    
                self.linkaddIter += 1
                
        else: raise AssertionError(
            'Node {}: Unusual currState {}, linkaddIter {}'.format(self.v_num, self.currState, self.linkaddIter))
        
        return outMsg

    # END of Main Procedure for Algorithm 4 and 5
    # -------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 6 and 7: Verifying and Enforcing Minimum Link 
    # -------------------------------------------------------------------------------
    # minLinkFormulation --> supporting procedure to formulate minimum link
    def minLinkFormulation(self, show_step = True):
        # Constructing the ordering
        p = 0
        w = [] # Ordered Sink
        v = []
        for sink, sources in self.pairSinkSource.items():
            if sink in w:
                print('Weird condition, multiple sinks in pairSinkSource information')
            nonListedSources = [item for item in sources if item not in v]
            
            if len(nonListedSources) > 0:
                p += 1
                w.append(sink)
                v.append(nonListedSources[0])
        
        w += [item for item in self.listSink if item not in w]
        v += [item for item in self.listSource if item not in v]
        
        # Constructing new links
        # The index is shifted by -1 due to python indexing from 0
        newLinks = []

        q = self.listIsolated
        len_q = len(q)
        len_v = len(v)
        len_w = len(w)

        newLinks += [{'sender':w[i], 'dest':v[i+1]} for i in range(p-1)]
        newLinks += [{'sender':w[i], 'dest':v[i]} \
                     for i in range( p, min(len_v, len_w) )]
        newLinks += [{'sender':q[i], 'dest':q[i+1]} for i in range(len_q-1)]
        
        if len_v == len_w:
            if len_v > 0: # assumed normal case
                if len_q > 0:           
                    newLinks += [{'sender':w[p-1], 'dest':q[0]}]
                    newLinks += [{'sender':q[len_q-1], 'dest':v[0]}]
                else:
                    newLinks += [{'sender':w[p-1], 'dest':v[0]}]                                
            else: # (special case) all disjoint are isolated-sccs 
                newLinks += [{'sender':q[len_q-1], 'dest':q[0]}]
                
        elif len_v < len_w:
            newLinks += [{'sender':w[p-1], 'dest':w[len_v]}]
            newLinks += [{'sender':w[i], 'dest':w[i+1]} for i in range(len_v,len_w-1)]
            if len_q > 0:           
                newLinks += [{'sender':w[len_w-1], 'dest':q[0]}]
                newLinks += [{'sender':q[len_q-1], 'dest':v[0]}]
            else:
                newLinks += [{'sender':w[len_w-1], 'dest':v[0]}]
                
        elif len_v > len_w:
            newLinks += [{'sender':w[p-1], 'dest':v[len_w]}]
            newLinks += [{'sender':v[i], 'dest':v[i+1]} for i in range(len_w,len_v-1)]
            if len_q > 0:           
                newLinks += [{'sender':v[len_v-1], 'dest':q[0]}]
                newLinks += [{'sender':q[len_q-1], 'dest':v[0]}]            
            else:
                newLinks += [{'sender':v[len_v-1], 'dest':v[0]}]


        if show_step:
            print('Constructing the ordering for minimum Link')
            print('p: {}, OrderSink : {}, OrderSource : {}, OrderIsolated : {}'\
                  .format(p, w, v, q))
            print('Formulated minimum link {}'.format(newLinks))
        
        return newLinks
    
    def minLinkGuarantee (self, buffTo, show_step = True): 
        # Process the incoming messages
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, show_step):
                # process message information
                if self.currState == self.minLinkVerState[0]: # communicate for representative
                    # max consensus to get other nodes information within SCC
                    self.localSCCcomm = [max(val) for val in zip(self.localSCCcomm, dictMsg['msg'])]

                elif self.currState == self.minLinkVerState[1]:
                    # Process broadcast information
                    if dictMsg['msg'] not in self.retrievedbcData :
                        # New message. save and forward
                        self.retrievedbcData.append(dictMsg['msg'])
                        self.forwardbcData.append(dictMsg['msg'])
                    # else: discard data, already retrieved previously

                elif self.currState == self.minLinkVerState[2]:
                    # Process broadcast information
                    if dictMsg['msg'] not in self.retrievedbcData :
                        # New message. save and forward
                        self.retrievedbcData.append(dictMsg['msg'])
                        self.forwardbcData.append(dictMsg['msg'])    
                    # else: discard data, already retrieved previously
 
                else: # unexpected state
                    raise AssertionError(
                        'Node {}: Unusual currState {}'.format(self.v_num, self.currState) )
            else: # NOT THE EXPECTED MESSAGE during this state
                if not (dictMsg['msg_type'] == self.linkAddReq): 
                    raise AssertionError(
                        'Node {} inValidMsg: {}. Expecting {} from {}'.format(
                            self.v_num, dictMsg, self.currState, self.in_neigh) )
                # ELSE --> pass message as new link is already added during isValidMsg()

        self.it += 1
        # Procedure to check for switching between States
        if self.it % self.n == 0:
            # increment the current state
            self.iterState += 1
            
            if self.currState == self.minLinkVerState[0]:
                # Determine Virtual Leader to calculate minimum link
                # Here we consider the virtual leader as the node which add the most edges
                # If multiple exists, then the highest vertex number is selected
                
                max_nedge = max(self.localSCCcomm)
                idNode = np.where(np.array(self.localSCCcomm) == max_nedge)[0]
                self.isSCCrep = self.v_num == max(idNode)
                
                if self.isSCCrep and show_step:
                    print('Node {} is selected as Virtual Leader for Minimum Link Verification'.format(self.v_num))
                                        
                # Update Initialize the next state
                self.currState = self.minLinkVerState[1]
                self.initState()

            elif self.currState == self.minLinkVerState[1]:
                # If Virtual Leader, process the broadcasted information
                
                if self.isSCCrep:
                    # Start the list from own data
                    totalAddedLinks = len(self.list_newOutNeigh)
                    self.pairSinkSource = {}
                    self.listSource = []
                    self.listSink = []
                    self.listIsolated = []
                    if self.original_isSinkSCC : 
                        self.pairSinkSource[self.v_num] = self.original_estSource
                        self.listSource += self.original_estSource
                        self.listSink.append(self.v_num)
                    else :
                        if self.original_isIsolatedSCC:
                            self.listIsolated.append(self.v_num)
                        else: raise AssertionError(
                            'Node {}: Weird selection as a Virtual leader, not isolated or sink'.format(self.v_num))

                    
                    for bcData in self.retrievedbcData:
                        totalAddedLinks += len(bcData['newLinkTo'])
                        if bcData['estSource'] == None:
                            self.listIsolated.append(bcData['id'])
                        else:
                            self.listSink.append(bcData['id'])
                            self.listSource += bcData['estSource']
                            self.pairSinkSource[bcData['id']] = bcData['estSource']
                    
                    self.listSource = np.unique(np.array(self.listSource)).tolist()
                    
                    if show_step:
                        print('Node {} Processing received data'.format(self.v_num))
                        print(' - totalAddedLinks: {}'.format(totalAddedLinks))
                        print(' - Sources ({}): {}, Sinks ({}): {}, Isolateds ({}): {}'.format(
                            len(self.listSource), self.listSource,
                            len(self.listSink), self.listSink, 
                            len(self.listIsolated), self.listIsolated))
                        print(' - pairSinkSource: {}'.format(self.pairSinkSource))
                
                    minLinkNumber = max(len(self.listSource), len(self.listSink)) + len(self.listIsolated)
                    newLinks = []
                    if totalAddedLinks > minLinkNumber:
                        # COMPUTE MINIMUM LINK
                        newLinks = self.minLinkFormulation(show_step)
                        if show_step:
                            print('Number of added link ({}) is NOT minimal ({}). Proposed links reconfiguration.'.format(totalAddedLinks, minLinkNumber))
                    else:
                        if show_step:                                               
                            print('Number of added link is already minimal')
                    
                    self.proposedLinks = {'number':len(newLinks), 'links':newLinks}
                    # Broadcast Proposed link information in the next step
                
                # Update Initialize the next state
                self.currState = self.minLinkVerState[2]
                self.initState()

            elif self.currState == self.minLinkVerState[2]:
                # Prohibit to run in the next turn
                self.isRunning = False

                # Reconfigure the Network
                # Process the information (if needed to add new link)
                if len(self.retrievedbcData) == 1 :
                    # Should only run once
                    ReconfigureLink = self.retrievedbcData[0]
                    self.isAddedLinkOptimal = ReconfigureLink['number'] == 0 
                    
                    if not self.isAddedLinkOptimal :
                        if show_step:                        
                            print('Node {}: Number of added link is NOT minimal'.format(self.v_num))
                                                                                                        
                        # Remove existing added link
                        self.out_neigh = np.setdiff1d(self.out_neigh, np.array(self.list_newOutNeigh))
                        self.in_neigh = np.setdiff1d(self.in_neigh, np.array(self.list_newInNeigh))
                        
                        # for node in self.list_newOutNeigh:
                        #     self.out_neigh.remove(node)
                        # # Remove existing added link
                        # for node in self.list_newInNeigh:
                        #     self.in_neigh.remove(node)

                        if show_step:
                            if len(self.list_newOutNeigh) > 0:
                                print('Removing previously added out Neighbor {}, resulting in {}'\
                                      .format(self.list_newOutNeigh, self.out_neigh))
                            if len(self.list_newInNeigh) > 0:
                                print('Removing previously added in Neighbor {}, resulting in {}'\
                                      .format(self.list_newInNeigh, self.in_neigh))

                        self.list_newOutNeigh = []
                        self.list_newInNeigh = []
                        # Adding new link into inNeigh or OutNeigh
                        for link in ReconfigureLink['links']:
                            if link['sender'] == self.v_num:
                                self.out_neigh = np.append(self.out_neigh, link['dest'])
                                self.list_newOutNeigh += [link['dest']]

                            if link['dest'] == self.v_num:
                                self.in_neigh = np.append(self.in_neigh, link['sender'])
                                self.list_newInNeigh += [link['sender']]

                        if show_step:
                            if len(self.list_newOutNeigh) > 0:
                                print('Adding new out Neighbor {}, resulting in {}'\
                                      .format(self.list_newOutNeigh, self.out_neigh))
                            if len(self.list_newInNeigh) > 0:
                                print('Adding new in Neighbor {}, resulting in {}'\
                                      .format(self.list_newInNeigh, self.in_neigh))
                        
                    else:
                        if show_step:
                            print('Node {}: Number of added link is already minimal'.format(self.v_num))
                
                else: raise AssertionError(
                    'Node {}: Too many retrieved broadcast {}'.format(self.v_num, self.retrievedbcData))

                if show_step:
                    print('Node {} finished Algorithm Minimum Link in iterations {} '.format( \
                        self.v_num, self.it ))

        # Return the current state information towards out Neighbors
        return self.constructOutMsg()
        

    # ------------------------------------------------------------------
    # ALGORITHM 7 - VERIFYING AND ENFORCING MINIMUM LINK
    # ------------------------------------------------------------------
    def updateEnsureStrongConn_MinLink (self, buffTo, print_mode = None):
        # Default console printing mode
        show_general_step = True
        show_detailed_step = False
        # Further adjustment when needed
        if print_mode == 'silent': show_general_step = False
        elif print_mode == 'detail': show_detailed_step = True

        outMsg = []
        totalState = self.estimateSCCState + self.linkAddState + self.minLinkVerState
        self.currState = totalState[self.iterState]   
        
        if any(item == self.currState for item in (self.estimateSCCState + self.linkAddState) )\
            and (self.linkaddIter >= 0):
            # Keep Running Algorithm 3 until it is finished
            outMsg = self.updateEnsureStrongConn(buffTo, print_mode) # suppress some print output

            if not self.isRunning:
                # The end of updateEnsureStrongConn
                if self.isStronglyConnected :
                    if self.linkaddIter > 0: # no need to run if the graph is originally strongly connected
                        # Reset the isRunning Flag to continue with minimum link verification
                        self.isRunning = True 
        
                        # Set the variable for Initialization to Minimum Link Verification
                        self.iterState = len(self.estimateSCCState + self.linkAddState)
                        self.currState = totalState[self.iterState]
                        self.initState()
                        outMsg = self.constructOutMsg()
                else:
                    # Already strongly connected
                    if show_general_step:
                        print('Node {} finished Algorithm 3 in iterations {}. Graph is NOT strongly connected ???.'.format( \
                            self.v_num, self.it ))
                
        elif any(item == self.currState for item in self.minLinkVerState) and (self.linkaddIter >= 0):
            # Keep Running minLinkGuarantee until it finished
            outMsg = self.minLinkGuarantee(buffTo, show_general_step)

            if not self.isRunning:
                # End of all process
                # Reset Algorithm for next link verification
                self.initializeNewProcedure() 

                if self.isAddedLinkOptimal and show_general_step:
                    print('Node {} finished MinLink Verification in iterations {}. No configuration.'.format( \
                        self.v_num, self.it ))

                else:
                    # Resend new message to message forwarder about new network config
                    outMsg = [{'sender':self.v_num, 'dest':self.v_num, 'msg_type':'RN', 'msg':''}]

                    if show_general_step:
                        print('Node {} finished MinLink Reconfiguration in iterations {}. Graph should be strongly connected.'.format( \
                            self.v_num, self.it ))

                # Resend new information state
                outMsg += self.constructOutMsg()
                # DO Verification, regardless of optimal link or not
                self.linkaddIter = -1
                if show_general_step:
                    print('Node {}: Switching to updateVerifyStrongConn for verification (Not necessarily needed)'.format( \
                        self.v_num))
        
        elif (self.linkaddIter == -1):
            # Running Verification to Show that the resulting graph is strongly connected
            self.currState = self.verificationState[self.iterState]   
            outMsg = self.updateVerifyStrongConn(buffTo, show_detailed_step) # suppress some print output
                
        else: raise AssertionError(
            'Node {}: Unusual currState {}, linkaddIter {}'.format(self.v_num, self.currState, self.linkaddIter))
            
        return outMsg
    # END of Main Procedure for Algorithm 3
    # -------------------------------------------------------------------------------



    # -------------------------------------------------------------------------------
    # Supporting Procedures
    # -------------------------------------------------------------------------------
    # State Initialization
    def initState (self):
        if self.currState == self.startingState: 
            # Initialize each element of x
            self.x = [0] * self.n
            self.x[self.v_num] = 1
        
        elif self.currState == self.verificationState[1]: 
            # Initialize element of f
            self.f = 1
            if sum(self.x) == self.n :
                self.f = 0

        elif self.currState == self.estimateSCCState[1]: 
            # Initialize each element of c
            self.c = [0] * self.n
            self.c[self.v_num] = sum(self.x)

        elif self.currState == self.estimateSCCState[2]: 
            # Initialize each element of o
            self.o = [0] * self.n
            outSCC = np.setdiff1d(self.out_neigh,self.SCC_elem)
            if len(outSCC) > 0 :
                self.o[self.v_num] = 1

        elif self.currState == self.linkAddState[0]: 
            # Using np.where in SCC estimation,
            # the list of nodes in own SCC should be in order from smallest 
            self.localSCCcomm = [0] * len(self.SCC_elem)
            
            # Assign identifier
            temp = 0
            if self.original_isSCCrep is not None:
                if self.original_isSCCrep:
                    if self.original_isSinkSCC:
                        temp = 1
                    elif self.original_isSourceSCC:
                        temp = 2
                    elif self.original_isIsolatedSCC:
                        temp = 3
                    else: raise AssertionError(
                        'Node {}: Weird original_SCCrole'.format(self.v_num ))
                # else do nothing
            
            idPos_ndarray = np.where(self.SCC_elem == self.v_num)[0]
            if len(idPos_ndarray) == 1:
                idPos = idPos_ndarray[0]
            else: raise AssertionError(
                'Node {}: weird idPos {}'.format(self.v_num, idPos_ndarray) )

            self.localSCCcomm[idPos] = temp
            self.isSCCrep = False # Reset all previous assignment

        elif self.currState == self.linkAddState[1]: 
            self.sendbcData = None
            self.retrievedbcData = []
            self.forwardbcData = []
            
            if self.isSCCrep and self.isSourceSCC :
                self.sendbcData = self.v_num


        elif self.currState == self.minLinkVerState[0]:
            # Broadcasting the total number of added links for selecting virtual leader
            # Only for original sink or original isolated
            self.localSCCcomm = [0] * self.n
            temp = len(self.list_newOutNeigh)
            self.localSCCcomm[self.v_num] = temp
            
            if temp > 0 and not (self.original_isSinkSCC or self.original_isIsolatedSCC):
                raise AssertionError('Node {}: Added links but Weird original_SCCrole'.format(self.v_num ))
            
        elif self.currState == self.minLinkVerState[1]: 
            self.sendbcData = None
            self.retrievedbcData = []
            self.forwardbcData = []
            
            if not self.isSCCrep and self.original_isSCCrep \
                and (self.original_isSinkSCC or self.original_isIsolatedSCC) :
                self.sendbcData = {'id':self.v_num, 'estSource':self.original_estSource, 'newLinkTo':self.list_newOutNeigh}        
                
        elif self.currState == self.minLinkVerState[2]: 
            self.sendbcData = None
            self.retrievedbcData = []
            self.forwardbcData = []
            
            if self.isSCCrep:
                self.sendbcData = self.proposedLinks

        else: raise AssertionError(
            'Node {}: Unusual Init currState {}'.format(self.v_num, self.currState))


    # Construct Out Message
    def constructOutMsg(self):
        # Formulate outgoing messages
        out_message = [] # Initiate empy list

        if self.currState == self.startingState: 
            # send state x to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.x})
        
        elif self.currState == self.verificationState[1]: 
            # send state f to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.f})

        elif self.currState == self.estimateSCCState[1]: 
            # send state c to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.c})
        
        elif self.currState == self.estimateSCCState[2]: 
            # send state o to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.o})

        elif self.currState == self.linkAddState[0]:
            # send state locallinkcomm to all out-neighbors within its own SCC
            for j in self.out_neigh:
                if j in self.SCC_elem:
                    out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.localSCCcomm})

        elif (self.currState == self.linkAddState[1]) \
            or (self.currState == self.minLinkVerState[1]) \
            or (self.currState == self.minLinkVerState[2]) : 
                
            if self.sendbcData is not None :
                # send the information to all out-neighbors
                for j in self.out_neigh:
                    out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.sendbcData})

            for item in self.forwardbcData :
                # forward the information to all out-neighbors
                for j in self.out_neigh:
                    out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':item})
                
        elif self.currState == self.minLinkVerState[0]: 
            # send state locallinkcomm to all out-neighbors within its own SCC
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':self.currState, 'msg':self.localSCCcomm})

        elif self.currState == self.minLinkVerState[2]: 
            pass
            
        else: raise AssertionError(
            'Node {}: Unusual Init currState {}'.format(self.v_num, self.currState))

        return out_message


    # Check Validity of Messages & Accepting Link Addition
    def isValidMsg(self, dictMsg, show_step = True):
        # check the destination
        isValid = (dictMsg['dest'] == self.v_num)
        # Check the expected information
        if isValid & (dictMsg['msg_type'] == self.linkAddReq): # Request for Link Addition
            # Add the requester node to the in-neighbor
            self.in_neigh = np.append(self.in_neigh, dictMsg['sender'])
            self.list_newInNeigh += [dictMsg['sender']]
            if show_step:
                print('Node {}: Accepting requested new edge from node {}. In-neighbor {}'\
                    .format(self.v_num, dictMsg['sender'], self.in_neigh))
            isValid = False
        else:
            # check the sender
            isValid = isValid and (dictMsg['sender'] in self.in_neigh)
            isValid = isValid and (dictMsg['msg_type'] == self.currState)
            
        return isValid

    # END of Supporting Procedures
    # -------------------------------------------------------------------------------
