"""
    Create a random chordal graph
"""
import random


class TreeNode:
    """ A class representing a tree node """

    def __init__(self):
        self.id = None
        self.Ax = []
        self.cliqueList = []


def ChordalGen(n, k):
    tree = TreeGen(n)
    subtrees = [SubTreeGen(tree, k, i) for i in range(0, n + 1)]
    # subTrees = SubTreeGen(t, k)
    print([t.cliqueList for t in tree])
    return subtrees


def SubTreeGen(T, k, i):
    Ti = [random.choice(T)]
    # the Ti tree contains this node
    Ti[0].cliqueList.append(i)

    k_i = random.randint(1, 2 * k - 1)
    # seperation index for y
    sy = 0
    # seperation indices for each node
    for node in T:
        node.s = 0

    for j in range(1, k_i):
        yi = random.randint(sy, len(Ti) - 1)
        y = Ti[yi]

        zi = random.randint(y.s, len(y.Ax) - 1)
        z = y.Ax[zi]
        if y.s != zi:
            y.Ax[y.s], y.Ax[zi] = y.Ax[zi], y.Ax[y.s]
            y.s += 1

        # if degree of y equals the seperation index on adjacency list , y
        # cannot be selected any more
        if y.s > len(y.Ax) - 1:
            print("y.s: " + str(y.s) + " degree:" + str(len(y.Ax)))
            if sy != yi:
                print("swap " + str(sy) + " with " + str(yi))
                Ti[sy], Ti[yi] = Ti[yi], Ti[sy]
                sy += 1
            if sy > len(Ti):
                print("lathos apo y, sy:" + str(sy) + " len: " + str(len(Ti)))

        Ti.append(z)
        z.cliqueList.append(i)
        # check if leaf i.e. has degree 1, then it cannot be selected any more
        if len(z.Ax) == 1:
            if sy != len(Ti) - 1:
                print("leaf swap " + str(sy) + " with " + str(len(Ti) - 1))
                Ti[sy], Ti[-1] = Ti[-1], Ti[sy]
                sy += 1
            if sy > len(Ti) - 1 and j != k_i - 1:
                print("lathos apo z, sy:" + str(sy) + " len: " + str(len(Ti)))
    return Ti


def TreeGen(n):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode()]
    for i in range(0, n):
        selection = random.choice(tree)
        newnode = TreeNode()

        # update the adjacency lists
        newnode.Ax.append(selection)
        selection.Ax.append(newnode)

        # append to tree
        tree.append(newnode)
    return tree

ChordalGen(10, 4)
print(".....Done")
