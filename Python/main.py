"""
    Create a random chordal graph
"""
import random
import json
import io
import networkx as nx
from networkx.readwrite import json_graph


class TreeNode:
    """ A class representing a tree node """

    def __init__(self, id):
        self.id = id
        self.Ax = []
        self.cliqueList = []

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)


def cliqueListGenChordal(graph):
    finalGraph = [TreeNode(n.id) for n in graph]

    for i, n in enumerate(graph):
        for j in range(i + 1, len(graph)):
            for ci in n.cliqueList:
                if ci in graph[j].cliqueList:
                    finalGraph[i].Ax.append(finalGraph[j])
                    break
    convertToNetworkX(finalGraph)


def ChordalGen(n, k):
    tree = TreeGen(n)
    subtrees = [SubTreeGen(tree, k, i) for i in range(0, n)]
    # print(subtrees)
    # subTrees = SubTreeGen(t, k)
    print([t.cliqueList for t in tree])
    cliqueListGenChordal(tree)
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
        try:
            ni = node.Ax.index(Ti[0])
            node.Ax[0], node.Ax[ni] = node.Ax[ni], node.Ax[0]
            node.s += 1
        except ValueError:
            pass

    for j in range(1, k_i):
        yi = random.randint(sy, len(Ti) - 1)
        y = Ti[yi]

        zi = random.randint(y.s, len(y.Ax) - 1)
        z = y.Ax[zi]

        # update every neighbour of z that z is now in Ti, y is among them
        for node in z.Ax:
            ni = node.Ax.index(z)
            node.Ax[node.s], node.Ax[ni] = node.Ax[ni], node.Ax[node.s]
            node.s += 1

        # if degree of y equals the seperation index on adjacency list, y
        # cannot be selected any more
        if y.s > len(y.Ax) - 1:
            if sy != yi:
                Ti[sy], Ti[yi] = Ti[yi], Ti[sy]
            sy += 1

        Ti.append(z)
        z.cliqueList.append(i)
        # check if leaf i.e. has degree 1, then it cannot be selected any more
        # TODO: is it needed?
        if len(z.Ax) == 1:
            if sy != len(Ti) - 1:
                Ti[sy], Ti[-1] = Ti[-1], Ti[sy]
            sy += 1
    return Ti


def TreeGen(n):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode(0)]
    for i in range(0, n - 1):
        selection = random.choice(tree)
        newnode = TreeNode(i + 1)

        # update the adjacency lists
        newnode.Ax.append(selection)
        selection.Ax.append(newnode)

        # append to tree
        tree.append(newnode)
    convertToNetworkX(tree)
    return tree


def convertToNetworkX(graph):
    lines = []
    for n in graph:
        lines.append(str(n.id) + ' ' + ' '.join((str(nn.id) for nn in n.Ax)))

    G = nx.parse_adjlist(lines, nodetype=int)
    print(nx.is_chordal(G))
    data = json_graph.node_link_data(G)
    with io.open('graph.json', 'w') as file:
        json.dump(data, file, indent=4)


ChordalGen(10, 4)
print(".....Done")
