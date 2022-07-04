import testGraphs as tg
import numpy as np
import math
import matplotlib.pyplot as plt


# def plot3D_data(Data):


def plotData(Data, fname = 'benchmarktest.png', 
    xlim = None, ylim = None, widthSizeMul = 1, heightSizeMul = 1):

    plt.rcParams.update({'font.size': 13})

    windowSize = [widthSizeMul*6.4, heightSizeMul*4.8]
    ax = plt.figure(figsize=windowSize).gca()

    nMinIter = MinIter/n
    nMaxIter = MaxIter/n
    if nMinIter == nMaxIter:
        nMinIter -= 1
        nMaxIter += 1

    xoffset = (MaxAddedLink - ValMinLink)/(10*widthSizeMul)
    yoffset = (nMaxIter - nMinIter)/(10*heightSizeMul)

    plt.scatter(Data[:,1],Data[:,0]/n,s=0*Data[:,2]+30)
    for i, txt in enumerate(Data[:,2]):
        plt.annotate(txt, (Data[i,1], (yoffset/10)+(Data[i,0]/n)))


    if xlim is None:
        xlimMin = ValMinLink-xoffset*3/2
        xlimMax = MaxAddedLink+xoffset*6/2
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

    plt.text(ValMinLink - xoffset*5/4, ylimMin + 3*yoffset, "Optimal \nNumber \nof Links", rotation=0, verticalalignment='center', fontsize='smaller')
    plt.text(MaxAddedLink + xoffset/4, ylimMin + yoffset*11/4, "Theoretical \nMaximum \nNumber of \nAugmented \nLinks", rotation=0, verticalalignment='center', fontsize='smaller')
    plt.annotate('', 
            xy=(ValMinLink, ylimMin), xytext=(ValMinLink - xoffset*2/4, ylimMin + 2*yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    plt.annotate('', 
            xy=(MaxAddedLink, ylimMin), xytext=(MaxAddedLink + xoffset*1/4, ylimMin + yoffset*5/4),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    ax.annotate('', fontsize='smaller',
            xy=(xlimMin, MaxIter/n), xytext=(xlimMin + xoffset, (MaxIter/n) + yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    ax.text(xlimMin + 1.1*xoffset, (MaxIter/n) + 1.5*yoffset, 'Theoretical \nMaximum \nNumber of \nIterations', 
        rotation=0, verticalalignment='top', fontsize='smaller') 

    plt.xlabel('Number of Augmented links')
    plt.ylabel('Number of Time Steps (times n)')

    ax.hlines(y=21, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')
    plt.text(ValMinLink, 21 + yoffset/4, "m=3", rotation=0, verticalalignment='center', fontsize='smaller', color='r')
    if any(Data[:,0] > 21*n):
        ax.hlines(y=26, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')
        plt.text(ValMinLink, 26 + yoffset/4, "m=4", rotation=0, verticalalignment='center', fontsize='smaller', color='r')

    plt.savefig(fname)
    #plt.show()


def plotData_with_break(Data, fname = 'benchmarktest.png',
    xlim = None, ylim = None, widthSizeMul = 1, heightSizeMul = 1):

    # plt.rcParams.update({'font.size': 11})

    nMinLink = min(Data[:,1]) - 0.5

    nMinIter = MinIter/n
    nMaxIter = MaxIter/n
    if nMinIter == nMaxIter:
        nMinIter -= 1
        nMaxIter += 1

    f,(ax,ax2) = plt.subplots(1,2,sharey=True, facecolor='w', gridspec_kw={'width_ratios': [1, 3]})

    xoffset1 = 1
    xoffset2 = (MaxAddedLink - nMinLink )/(10*widthSizeMul*0.75)
    yoffset = (nMaxIter - nMinIter)/(10*heightSizeMul)

    if xlim is None:
        xlimMin = ValMinLink-xoffset1*3/2
        xlimMax = MaxAddedLink+xoffset2*6/2
        xlim = [ xlimMin, xlimMax ]
    if ylim is None:
        ylimMin = nMinIter-yoffset
        ylimMax = nMaxIter+yoffset*4/2
        ylim = [ ylimMin, ylimMax ]


    # plot the same data on both axes
    ax2.scatter(Data[:,1],Data[:,0]/n,s=0*Data[:,2]+30)
    for i, txt in enumerate(Data[:,2]):
        plt.annotate(txt, (Data[i,1], (yoffset/10)+(Data[i,0]/n)))

    ax.set_xlim(xlimMin,ValMinLink+2)
    ax2.set_xlim(nMinLink,xlimMax)
    ax.set_ylim( ylim )


    ax.hlines(y=21, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')
    ax.text(ValMinLink, 21 + yoffset/4, "m=3", rotation=0, verticalalignment='center', fontsize='smaller', color='r')
    ax2.hlines(y=21, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')
    if any(Data[:,0] > 21*n):
        ax.hlines(y=26, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')
        ax.text(ValMinLink, 26 + yoffset/4, "m=4", rotation=0, verticalalignment='center', fontsize='smaller', color='r')
        ax2.hlines(y=26, xmin=ValMinLink, xmax=MaxAddedLink, linewidth=1, linestyles='--', color='r')

    ax.text(ValMinLink - xoffset1*5/4, ylimMin + 2.75*yoffset, "Optimal \nNumber \nof Links", rotation=0, verticalalignment='center', fontsize='smaller')
    ax2.text(MaxAddedLink + xoffset1*0.1, ylimMin + yoffset*11/4, "Theoretical \nMaximum \nNumber of \nAugmented \nLinks", rotation=0, verticalalignment='center', fontsize='smaller')
    ax.annotate('', 
            xy=(ValMinLink, ylimMin), xytext=(ValMinLink - xoffset1*2/4, ylimMin + 2*yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    ax2.annotate('', 
            xy=(MaxAddedLink, ylimMin), xytext=(MaxAddedLink + xoffset1*1/4, ylimMin + yoffset*5/4),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    ax.annotate('', fontsize='smaller',
            xy=(xlimMin, MaxIter/n), xytext=(xlimMin + xoffset1, (MaxIter/n) + yoffset),
            arrowprops=dict(facecolor='black', shrink=0.03) ) 
    ax.text(xlimMin + 1.1*xoffset1, (MaxIter/n) + 1.5*yoffset, 'Theoretical \nMaximum \nNumber of \nIterations', 
        rotation=0, verticalalignment='top', fontsize='smaller')


    ax.xaxis.set_ticks(np.arange(math.ceil(xlimMin), ValMinLink+2, 1.0))
    ax2.xaxis.set_ticks(np.arange(math.ceil(nMinLink), xlimMax, 1.0))
    if (ylimMax - ylimMin) > 5:
        ax.yaxis.set_ticks(np.arange(16, math.floor(ylimMax), 5))
    else:
        ax.yaxis.set_ticks(np.arange(math.ceil(ylimMin), math.ceil(ylimMax), 1.0))

    # hide the spines between ax and ax2
    ax.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax.yaxis.tick_left()
    # ax.tick_params(labelright='off')
    ax2.yaxis.tick_right()
    # ax2.set_yticks([])

    # This looks pretty good, and was fairly painless, but you can get that
    # cut-out diagonal lines look with just a bit more work. The important
    # thing to know here is that in axes coordinates, which are always
    # between 0-1, spine endpoints are at these locations (0,0), (0,1),
    # (1,0), and (1,1).  Thus, we just need to put the diagonals in the
    # appropriate corners of each of our axes, and so long as we use the
    # right transform and disable clipping.

    d = .015 # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((1-d,1+d), (-d,+d), **kwargs)
    ax.plot((1-d,1+d),(1-d,1+d), **kwargs)

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d/3,+d/3), (1-d,1+d), **kwargs)
    ax2.plot((-d/3,+d/3), (-d,+d), **kwargs)

    # What's cool about this is that now if we vary the distance between
    # ax and ax2 via f.subplots_adjust(hspace=...) or plt.subplot_tool(),
    # the diagonal lines will move accordingly, and stay right at the tips
    # of the spines they are 'breaking'

    # ax2.set_xlabel('Number of Augmented links')
    ax.set_ylabel('Number of Time Steps (times n)')
    # f.supxlabel('Number of Augmented links')
    f.text(0.5, 0.015, 'Number of Augmented links', ha='center')

    # plt.show()    
    plt.savefig(fname)


def summarize_csv_data(fname):
    import csv
    
    with open((fname + '.csv'), mode='r') as fd:
        reader = csv.reader(fd)
        for i, line in enumerate(reader):
            iterNum = int(line[0])
            NumAddedLink = int(line[1])
            addedLink = line[2]
            NumMinLink = int(line[3])
            minLink = line = line[4]
            currentMinLink = NumMinLink if NumMinLink > 0 else NumAddedLink
            # NumMinLink is 0 when the original added link (NumAddedLink) is already optimal

            if i == 0: 
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

        print('Recapping Data from ' + fname)
        print('Iteration - Added Links - Encounter')
        print(Data)
        print('Maxiter {}. MaxAddedLink {}. MinLink {}\n'.format(MaxIter, MaxAddedLink, ValMinLink))

        return Data

def main():
    
    global G, A, n, ValMinLink, MaxAddedLink, MaxIter, MinIter

    # # --------------------------------------------------------------------------------
    # # Weakly connected digraph with 10 nodes, distinct pair source-sink are 5
    # # --------------------------------------------------------------------------------
    # G = tg.graph2
    # A = G['A']
    # n = A.shape[0] # A should always be a square matrix
    
    # ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    # MaxAddedLink =  2*G['disjointGraph'] + 5
    # MaxIter = (6*n) + (10*n)
    # MinIter = (6*n) + (5*n) # assuming 2 step iteration with minimum link verification

    # testName = 'temp/benchmark_graph2'
    # Data = summarize_csv_data(testName)

    # plotData(Data, (testName + '.pdf') )


    # --------------------------------------------------------------------------------
    # Disconnected digraph with 20 nodes, distinct pair source-sink are 6
    # --------------------------------------------------------------------------------
    G = tg.graph3
    A = G['A']
    n = A.shape[0] # A should always be a square matrix
    
    ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    MaxAddedLink =  2*G['disjointGraph'] + 6
    MaxIter = (6*n) + (10*n* math.ceil( math.log2(G['disjointGraph']) ) )
    MinIter = (6*n) + (5*n) # assuming 2 step iteration with minimum link verification

    testName = 'temp/benchmark_graph3'
    Data = summarize_csv_data(testName)

    plotData(Data, (testName + '.pdf') )

    # --------------------------------------------------------------------------------
    # Disconnected digraph with 50 nodes, distinct pair source-sink are 34
    # --------------------------------------------------------------------------------
    G = tg.graph5 
    A = G['A']
    n = A.shape[0] # A should always be a square matrix

    ValMinLink = max(G['sourceSccNum'], G['sinkSccNum']) + G['isolatedSccNum']
    MaxAddedLink =  2*G['disjointGraph'] + 34
    MaxIter = (6*n) + (10*n* math.ceil( math.log2(G['disjointGraph']) ) )
    MinIter = (6*n) + (5*n) # assuming 2 step iteration with minimum link verification

    testName = 'temp/benchmark_graph5'
    Data = summarize_csv_data(testName)

    # plotData(Data, (testName + '.pdf') )
    # plotData(Data, (testName + '.pdf'), widthSizeMul = 2.2 )
    plotData_with_break(Data, (testName + '.pdf') )

if __name__ == '__main__':
    main()
    #plotOnly()
