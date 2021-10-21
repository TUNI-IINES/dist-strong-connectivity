import testGraphs as tg
import numpy as np
import math
import matplotlib.pyplot as plt


def plotData(Data, fname = 'benchmarktest.png', 
    xlim = None, ylim = None, widthSizeMul = 1, heightSizeMul = 1):

    plt.rcParams.update({'font.size': 14})

    windowSize = [widthSizeMul*6.4, heightSizeMul*4.8]
    ax = plt.figure(figsize=windowSize).gca()

    plt.scatter(Data[:,1],Data[:,0]/n,s=0*Data[:,2]+30)
    for i, txt in enumerate(Data[:,2]):
        plt.annotate(txt, (Data[i,1],Data[i,0]/n))

    nMinIter = MinIter/n
    nMaxIter = MaxIter/n
    if nMinIter == nMaxIter:
        nMinIter -= 1
        nMaxIter += 1

    xoffset = (MaxAddedLink - ValMinLink)/(10*widthSizeMul)
    yoffset = (nMaxIter - nMinIter)/(10*heightSizeMul)

    if xlim is None:
        xlimMin = ValMinLink-xoffset*3/2
        xlimMax = MaxAddedLink+xoffset*7/2
        xlim = [ xlimMin, xlimMax ]
    if ylim is None:
        ylimMin = nMinIter-yoffset
        ylimMax = nMaxIter+yoffset*4/2
        ylim = [ ylimMin, ylimMax ]

    ax.set_xlim( xlim )
    ax.set_ylim( ylim )

    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.xaxis.set_ticks(np.arange(math.ceil(xlimMin), math.ceil(xlimMax), 1.0))
    if (ylimMax - ylimMin) > 5:
        ax.yaxis.set_ticks(np.arange(16, math.floor(ylimMax), 5))
    else:
        ax.yaxis.set_ticks(np.arange(math.ceil(ylimMin), math.ceil(ylimMax), 1.0))
    #plt.grid()

    vcenter = (nMinIter + nMaxIter)/2
    xcenter = (ValMinLink + MaxAddedLink)/2

    plt.text(ValMinLink - xoffset*5/4, ylimMin + 3*yoffset, "Optimal \nNumber \nof Links", rotation=0, verticalalignment='center', fontsize='smaller')
    plt.text(MaxAddedLink + xoffset/4, ylimMin + yoffset*11/4, "Theoretical \nMaximum \nNumber of \nAugmented \nLinks", rotation=0, verticalalignment='center', fontsize='smaller')

    plt.annotate('', 
            xy=(ValMinLink, ylimMin), xytext=(ValMinLink - xoffset*2/4, ylimMin + 2*yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    plt.annotate('', 
            xy=(MaxAddedLink, ylimMin), xytext=(MaxAddedLink + xoffset*1/4, ylimMin + yoffset*5/4),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    plt.annotate('Theoretical Maximum Number of Iterations', fontsize='smaller',
            xy=(xlimMin, MaxIter/n), xytext=(xlimMin + xoffset, (MaxIter/n) + yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 

    plt.xlabel('Number of Augmented links')
    plt.ylabel('Number of Time Steps (times n)')

    plt.savefig(fname)
    #plt.show()

def main():
    
    global G, A, n, ValMinLink, MaxAddedLink, MaxIter, MinIter

    G = tg.graph2 # Weakly connected digraph with 10 nodes
    A = G['A']
    n = A.shape[0] # A should always be a square matrix
    
    ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    MaxAddedLink = G['sourceSccNum'] + G['sinkSccNum'] + G['isolatedSccNum'] + G['disjointGraph']
    MaxIter = (11*n) + (5*n* math.ceil( 1 + math.log2(G['disjointGraph'] - G['isolatedSccNum']/2) ) )
    MinIter = (11*n) + (5*n) # assuming 2 step iteration with minimum link verification

    testName = 'temp/graph2WCbenchmark20211005_103551'
    Data = np.array([
        [160,   4,  35],
        [160,   3,  65]
    ])

    plotData(Data, (testName + '.pdf') )



    G = tg.graph3 # Disconnected digraph with 20 nodes
    A = G['A']
    n = A.shape[0] # A should always be a square matrix
    
    ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    MaxAddedLink = G['sourceSccNum'] + G['sinkSccNum'] + G['isolatedSccNum'] + G['disjointGraph']
    MaxIter = (11*n) + (5*n* math.ceil( 1 + math.log2(G['disjointGraph'] - G['isolatedSccNum']/2) ) )
    MinIter = (11*n) + (5*n) # assuming 2 step iteration with minimum link verification

    testName = 'temp/graph3DCbenchmark20211005_103728'
    Data = np.array([
        [320,  12, 175],
        [320,  11, 163],
        [420,  12,   4],
        [320,  10,  26],
        [320,  13,  27],
        [420,  13,   2],
        [320,   9,   2],
        [420,  11,   1]
    ])

    plotData(Data, (testName + '.pdf') )

    G = tg.graph5 # Disconnected digraph with 50 nodes
    A = G['A']
    n = A.shape[0] # A should always be a square matrix

    ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    MaxAddedLink = G['sourceSccNum'] + G['sinkSccNum'] + G['isolatedSccNum'] + G['disjointGraph']
    MaxIter = (11*n) + (5*n* math.ceil( 1 + math.log2(G['disjointGraph'] - G['isolatedSccNum']/2) ) )
    MinIter = (11*n) + (5*n) # assuming 2 step iteration with minimum link verification

    testName = 'temp/graph5DCbenchmark20211005_105112'
    Data = np.array([
        [1050,   31,  821],
        [1050,   32,  506],
        [1050,   29,  239],
        [1050,   30,  612],
        [1050,   33,  133],
        [1050,   34,   12],
        [1050,   28,   43],
        [ 800,   29,   45],
        [ 800,   31,   20],
        [ 800,   30,   39],
        [ 800,   28,   17],
        [ 800,   33,    1],
        [ 800,   32,    4],
        [1050,   27,    4],
        [ 800,   27,    4]
    ])

    plotData(Data, (testName + '.pdf'), widthSizeMul = 2.2 )


if __name__ == '__main__':
    main()
    #plotOnly()
