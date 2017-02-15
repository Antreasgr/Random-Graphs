"""
    Create a random chordal graph
"""
import random
import json
import io
import networkx as nx
from networkx.readwrite import json_graph

# initialize global random seed
R = random.Random()


class TreeNode:
    """ A class representing a tree node """

    def __init__(self, id):
        self.id = id
        self.Ax = []
        self.cliqueList = []
        # helper list for tree form
        self.children = []

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

    return finalGraph


def ChordalGen(n, k):
    tree = TreeGen(n)
    subtrees = [SubTreeGen(tree, k, i) for i in range(0, n)]
    print("subtrees: ", subtrees)
    # subTrees = SubTreeGen(t, k)
    print("cliqueList: ", [t.cliqueList for t in tree])
    fg = cliqueListGenChordal(tree)
    convertToNetworkX([tree, fg])
    return subtrees


def SubTreeGen(T, k, i):
    Ti = [R.choice(T)]
    # the Ti tree contains this node
    Ti[0].cliqueList.append(i)

    k_i = R.randint(1, 2 * k - 1)
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
        y, yi = random_element(Ti, sy)

        z, zi = random_element(y.Ax, y.s)

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
        selection, _ = random_element(tree)
        newnode = TreeNode(i + 1)

        # update the adjacency lists
        newnode.Ax.append(selection)
        selection.Ax.append(newnode)

        # update helper, children list
        selection.children.append(newnode)

        # append to tree
        tree.append(newnode)

    return tree


def convertToNetworkX(graphs):
    """
        Converts a list of graphs(or a single graph) to networkX format, 
        outputs json result to file `graph.json`
    """
    if not isinstance(graphs, list):
        graphs = [graphs]

    jsonData = []
    for graph in graphs:
        lines = []
        for node in graph:
            lines.append(str(node.id) + ' ' + ' '.join(str(nn.id) for nn in node.Ax))

        G = nx.parse_adjlist(lines, nodetype=int)
        print("is Chordal: {0} ".format(nx.is_chordal(G)))
        jsonData.append(json_graph.node_link_data(G))

    with io.open('graph.json', 'w') as file:
      json.dump(jsonData, file, indent=4)

def random_element(array, index=0):
    """
        get a random element, and index from given array starting from index to end
    """
    i = R.randint(index, len(array) - 1)
    return array[i], i


ChordalGen(10, 4)
print(".....Done")
