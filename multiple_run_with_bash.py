import testGraphs as tg
from strong_connectedness_test import single_run
import csv
from datetime import datetime
import sys

if __name__ == '__main__':
    it = int(sys.argv[1])
    testName = sys.argv[2]
    graph_num = int(sys.argv[3])

    with open( (testName + '.csv'), mode='a', newline='') as fd: # append existing file
        # Load graph
        if   graph_num == 2: A = tg.graph2['A'] # Weakly connected digraph with 10 nodes
        elif graph_num == 3: A = tg.graph3['A'] # Weakly connected digraph with 10 nodes
        elif graph_num == 5: A = tg.graph5['A'] # Weakly connected digraph with 10 nodes
        else: raise AssertionError('unknown graph number')

        n = A.shape[0] # A should always be a square matrix
        # CALL THE FUNCTION TO TEST
        iterNum, addedLink, minLink = single_run(A, print_step = False, display_graph = False, save_data = False)

        # Store data to csv
        csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([iterNum, len(addedLink), addedLink, len(minLink), minLink])

        # Simple Progress Bar 
        print(".", end =" ", flush=True)
        if (it % n) == 0: print((str(it) + ' ' + datetime.now().strftime("%Y%m%d_%H%M%S")), flush=True)
        # increase iteration number
