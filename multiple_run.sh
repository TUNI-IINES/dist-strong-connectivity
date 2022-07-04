#!/bin/bash

# # SCRIPT FOR THE 2ND GRAPH --> Weakly connected graph (for testing)
# for i in {1..100}
# do
#    python multiple_run_with_bash.py $i 'temp/benchmark_graph2' 2
# done

# SCRIPT FOR THE 3rd GRAPH --> disconnected graph 20 nodes
for i in {1..400}
do
   python multiple_run_with_bash.py $i 'temp/benchmark_graph3' 3
done

# # SCRIPT FOR THE 5th GRAPH --> disconnected graph 50 nodes
# for i in {1..2500}
# do
#    python multiple_run_with_bash.py $i 'temp/benchmark_graph5' 5
# done