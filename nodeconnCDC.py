import numpy as np

class NodeConn(object):

    """docstring for NodeConn"""
    def __init__(self, v_num, n, in_LapCol, out_LapRow):
        super(NodeConn, self).__init__()

        self.isDebug = False #Turned off by default

        self.verificationState = ['x', 'f']
        self.estimateSCCState = ['x', 'c', ['s', 'o'] ]
        self.currState = 0

        # Total number of iterations, and running status
        self.it = 0
        self.isRunning = True
        # this node's vertex number (0 to n-1)
        self.v_num = v_num 

        # total vertices number in graph 
        self.n = n 
        # array of in-neighbours
        self.in_neigh = np.where(in_LapCol == 1)[0]
        # array of out-neighbours
        self.out_neigh = np.where(out_LapRow == 1)[0]

        self.initState('x') # All process always start with state x

    # To allow running several procedure in series without resetting iteration number
    def initializeNewProcedure(self):
        self.currState = 0
        self.isRunning = True
        self.initState('x') # All process always start with state x

    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 1: Distributed Algorithm for Solving Problem 1
    #     Problem 1: Verify in a distributed manner if the directed graph 
    #                is strongly connected
    # -------------------------------------------------------------------------------
    def updateVerifyStrongConn (self, buffTo):

        processState = self.verificationState[self.currState]

        # Process the incoming messages
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, processState):
                # process message information
                if processState == 'x': 
                    # Update each element of x
                    self.x = [max(val) for val in zip(self.x, dictMsg['msg'])]
                    
                elif processState == 'f': 
                    # Update information of f
                    self.f = max(self.f, dictMsg['msg'])
                
                else:
                    print('Node {}: Unusual processState {}'.format(self.v_num, processState))

            else:
                if not (dictMsg['msg_type'] == 'la'): 
                    print('Node {} inValidMsg: {}'.format(self.v_num, dictMsg))
                    print('Node {} expecting {} from {}'.format(self.v_num, processState, self.in_neigh))

        self.it += 1
        # Procedure to check for switching between Verification State
        if self.it % self.n == 0:
            # increment the current state
            self.currState += 1

            if self.currState >= len(self.verificationState):

                # Prohibit to run in the next turn
                self.isRunning = False
                print('Node {} finished Algorithm 1 in iterations {}'.format( \
                    self.v_num, self.it ))

                # Show the Final Verification Status
                final_status = 'IS'
                if self.f == 1:
                    final_status = 'is NOT'
                print('Node {}: The communication graph {} strongly connected'.format( \
                    self.v_num, final_status ))

            else: 
                # Set into the new processState
                processState = self.verificationState[self.currState]

                # Initialize the new state
                self.initState(processState)


        # Return the current state information towards out Neighbors
        return self.constructOutMsg(processState)

    # END of Main Procedure for Algorithm 1
    # -------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 2: Distributed Estimation of SCC
    # -------------------------------------------------------------------------------
    def updateEstimateSCC (self, buffTo, allowAllPrint = True):
        # setting allowAllPrint to False, only suppress part of printing (nonessential)

        processState = self.estimateSCCState[self.currState]

        # Process the incoming messages
        for dictMsg in buffTo:
            # Check message information
            if self.isValidMsg(dictMsg, processState):
                # process message information
                if processState == 'x': 
                    # Update each element of x
                    self.x = [max(val) for val in zip(self.x, dictMsg['msg'])]
                    
                elif processState == 'c': 
                    # Update each element of c
                    self.c = [max(val) for val in zip(self.c, dictMsg['msg'])]

                elif processState == ['s', 'o']:
                    if dictMsg['msg_type'] == 'o':
                        # Update each element of o
                        self.o = [max(val) for val in zip(self.o, dictMsg['msg'])]
                    else: #dictMsg['msg_type'] == 's':
                        # Update each element of s
                        self.s = [max(val) for val in zip(self.s, dictMsg['msg'])]
                
                else:
                    print('Node {}: Unusual processState {}'.format(self.v_num, processState))

            else:
                if not (dictMsg['msg_type'] == 'la'): 
                    print('Node {} inValidMsg: {}'.format(self.v_num, dictMsg))
                    print('Node {} expecting {} from {}'.format(self.v_num, processState, self.in_neigh))

        self.it += 1
        # Procedure to check for switching between Verification State
        if self.it % self.n == 0:
            # increment the current state
            self.currState += 1

            if self.currState >= len(self.estimateSCCState):

                # Prohibit to run in the next turn
                self.isRunning = False
                if allowAllPrint:
                    print('Node {} finished Algorithm 2 in iterations {} '.format( \
                        self.v_num, self.it ))

                # Show the Final Verification Status
                status = ''
                
                isOut_SCC = sum(np.take(self.o, self.SCC_elem)) > 0
                isIn_SCC = sum(np.take(self.s, self.SCC_elem)) == 0 

                # Theorem 3
                self.isSinkSCC = isIn_SCC and not isOut_SCC
                self.isSourceSCC = not isIn_SCC and isOut_SCC
                self.isStronglyConnected = len(self.SCC_elem) == self.n

                if self.isSinkSCC:
                    if len(self.preSCC_elem)==0: # Safety check
                        print('Node {}: weird SCC incoming edge determination'\
                            .format(self.v_num))
                    else:
                        status = '- Sink-SCC'
                elif self.isSourceSCC:
                    status = '- Source-SCC'
                elif self.isStronglyConnected: 
                    if (isOut_SCC or isIn_SCC): # Safety check
                        print('Node {}: weird Strongly connected determination'\
                            .format(self.v_num))
                    else:
                        status = '- strongly connected graph'

                # inform status
                if allowAllPrint:
                    print('Node {}: own SCC {} {}'.format( \
                        self.v_num, self.SCC_elem , status))

            else: 
                # Set into the new processState
                processState = self.estimateSCCState[self.currState]

                if processState == ['s', 'o']:
                    # Estimate SCC_elem and preSCC_elem before initialize state o and s
                    c_ii = self.c[self.v_num] # This node's information number
                    temp = np.array(self.c)
                    self.SCC_elem = np.where(temp == c_ii)[0]
                    self.preSCC_elem = np.where((temp > 0) & (temp < c_ii))[0]

                # Initialize the new state
                self.initState(processState)

        # Return the current state information towards out Neighbors
        return self.constructOutMsg(processState)

    # END of Main Procedure for Algorithm 2
    # -------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------
    # Main Procedure for Algorithm 3: Distributed Algorithm for Solving Problem 2
    #     Problem 2: Add additional edges in a distributed manner to strongly connect 
    #                the original graph
    # -------------------------------------------------------------------------------
    def updateEnsureStrongConn (self, buffTo):

        # Keep Running Algorithm 2 until it finished
        outMsg = self.updateEstimateSCC(buffTo, False) # suppress some print output

        if not self.isRunning:
            if not self.isStronglyConnected :
                # Reset outMsg information
                request_edge = []

                if self.isSinkSCC :
                    # Determine representative node
                    # Here: consider largest vertex number in sink-scc
                    if self.v_num == max(self.SCC_elem):
                        # this node is representative node
                        # Estimate the sources set
                        est_sources = np.where(np.array(self.s) == 1)[0]
                        print('Node {}: Estimated source {} from s {}'\
                            .format(self.v_num, est_sources, self.s))

                        selected_source = np.random.choice(est_sources)
                        # append selected source to out-neighbor
                        self.out_neigh = np.append(self.out_neigh, selected_source)

                        print('Node {}: sending requested new edge to node {}. Out-neighbor {}'\
                            .format(self.v_num, selected_source, self.out_neigh))

                        # link addition sending message
                        request_edge = [{'sender':self.v_num, 'dest':selected_source, \
                            'msg_type':'la', 'msg':''}]


                #else: do nothing

                # Reset Algorithm 2 for next link addition
                self.initializeNewProcedure() # Only reset state x at this point
                # Resend new information state
                outMsg = request_edge + self.constructOutMsg('x')

            else: # Already strongly connected
                print('Node {} finished Algorithm 3 in iterations {}. Graph is strongly connected.'.format( \
                    self.v_num, self.it ))

        return outMsg
    # END of Main Procedure for Algorithm 3
    # -------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------
    # Supporting Procedures
    # -------------------------------------------------------------------------------
    # State Initialization
    def initState (self, processState):
        if processState == 'x': 
            # Initialize each element of x
            self.x = [0] * self.n
            self.x[self.v_num] = 1
        
        elif processState == 'f': 
            # Initialize element of f
            self.f = 1
            if sum(self.x) == self.n :
                self.f = 0

        elif processState == 'c': 
            # Initialize each element of c
            self.c = [0] * self.n
            self.c[self.v_num] = sum(self.x)

        elif processState == ['s', 'o']: 
            # Initialize each element of o
            self.o = [0] * self.n
            outSCC = np.setdiff1d(self.out_neigh,self.SCC_elem)
            if len(outSCC) > 0 :
                self.o[self.v_num] = 1

            # Initialize each element of s
            self.s = [0] * self.n
            if len(self.preSCC_elem) == 0 :
                self.s[self.v_num] = 1

        else:
            print('Node {}: Unusual Init processState {}'.format(self.v_num, processState))


    # Construct Out Message
    def constructOutMsg(self, processState):
        # Formulate outgoing messages
        out_message = [] # Initiate empy list

        if processState == 'x': 
            # send state x to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':'x', 'msg':self.x})
        
        elif processState == 'f': 
            # send state f to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':'f', 'msg':self.f})

        elif processState == 'c': 
            # send state c to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':'c', 'msg':self.c})
        
        elif processState == ['s', 'o']: 
            # send state s to all out-neighbors
            # send state o to all out-neighbors
            for j in self.out_neigh:
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':'o', 'msg':self.o})
                out_message.append({'sender':self.v_num, 'dest':j, 'msg_type':'s', 'msg':self.s})

        else:
            print('Node {}: Unusual Init processState {}'.format(self.v_num, processState))

        return out_message


    # Check Validity of Messages & Accepting Link Addition
    def isValidMsg(self, dictMsg, processState):
        # check the destination
        isValid = (dictMsg['dest'] == self.v_num)
        # Check the expected information
        if isValid & (dictMsg['msg_type'] == 'la'): # Request for Link Addition
            # Add the requester node to the in-neighbor
            self.in_neigh = np.append(self.in_neigh, dictMsg['sender'])
            print('Node {}: Accepting requested new edge from node {}. In-neighbor {}'\
                .format(self.v_num, dictMsg['sender'], self.in_neigh))
            isValid = False
        else:
            # check the sender
            isValid = isValid and (dictMsg['sender'] in self.in_neigh)
            isValid = isValid and any(item == dictMsg['msg_type'] for item in processState)

        return isValid

    # END of Supporting Procedures
    # -------------------------------------------------------------------------------
