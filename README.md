# dist-strong-connectivity

Finite-Time Distributed Algorithms for Verifying and Ensuring Strong Connectivity in Directed Networks

This repository stores the implementation of the proposed approaches in the following academic paper:

```text
@inproceedings{atman2021cdc,
  title = {Distributed Algorithms for Verifying and Ensuring Strong Connectivity in Directed Networks},
  booktitle = {2021 60th IEEE Conference on Decision and Control (CDC)},
  author = {Atman, Made Widhi Surya and Gusrialdi, Azwirman},
  year = {2021},
  note = {To be presented}
}
```

_*An extended version for journal submission is under preparation._

## Files and Usage

``` text
strong_connectedness_test.py --> main script
testGraphs.py --> several adjacency matrices for testing
msgForwarder.py --> simulate sending message over nodes and visualize graph
nodeconnCDC.py --> algorithms in CDC paper
```

### ```strong_connectedness_test.py```

Main script to execute.

To switch between algorithms in CDC paper, comment/uncomment between line 41-43 in.

```python
# outMessage = Node[i].updateVerifyStrongConn(inMessage) # Algorithm 1
# outMessage = Node[i].updateEstimateSCC(inMessage) # Algorithm 2
outMessage = Node[i].updateEnsureStrongConn(inMessage) # Algorithm 3
```

1. _Algorithm 1: Distributed verification of a directed graph's strong connectivity._  
   Each node returning their estimation (via command line output) whether the graph representation of their network communication is strongly connected or not.
2. _Algorithm 2: Distributed Estimation of Strongly Connected Component._
   Each node estimating their own strongly connected components (SCC), and determine whether their SCC is a sink-scc, source-scc, or the whole graph (the graph is originally a strongly connected graph).
3. _Algorithm 3: Distributed Link Addition Algorithm to Strongly Connect A Weakly Connected Graph._  
   Each node distributively run Algorithm 2, then a representative node in each sink-scc propose a new link toward a source-scc.
   The procedure is repeated until the graph is strongly connected.  
   _Note: running the algorithm with disconnected graph results in abnormal exit (never meet ending condition)._

### ```testGraphs.py```

List of test graph used during the testing. (to be detailed, under preparation)

### ```msgForwarder.py```

Implementation of the message passing between one node to another. (to be detailed, under preparation)

### ```nodeconnCDC.py``` and ```nodeconnJournal.py```

Implementation of the algorithms as a ```NodeConn``` class.

## Expected Results

### ```nodeconnCDC.py```

Algorithm 1  
Algorithm 2  
Algorithm 3  
(to be detailed, under preparation)

## Constributors

The algorithms in this repository is developed by Made Widhi Surya Atman and Azwirman Gusrialdi from Intelligent Networked Systems (IINES) Group,
Faculty of Engineerings and Natural Sciences, Tampere University.

## Acknowledgements

This result is part of a project that has received funding from the Academy of Finland under Academy Project decision number 330073 - Resilient distributed optimization for cyber-physical systems.
