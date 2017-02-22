"""
    Create a random chordal graph
"""
import random
import json
import io
import time
import timeit
import functools
import networkx as nx
from networkx.readwrite import json_graph

# initialize global random seed
R = random.Random(501)


class TreeNode:
    """ A class representing a tree node """

    def __init__(self, id):
        self.id = id
        self.Ax = []
        self.cliqueList = []
        # helper attributes for tree form
        self.children = []
        self.parent = None
        self.marked = False

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)


def truecliqueListGenChordal(graph, subtrees):
    """
        Converts the output of the sub-tree generation algorithm to clique_tree
    """
    final_graph = [TreeNode(n.id) for n in graph]

    for i in range(0, len(graph)):
        for j in range(i + 1, len(graph)):
            if not set(subtrees[i]).isdisjoint(subtrees[j]):
                final_graph[i].Ax.append(final_graph[j])

    return final_graph


def cliqueListGenChordal(graph):
    stack = []
    for node in graph:
        # find all leaf nodes
        if len(node.children) == 0:
            stack.append(node)

    while len(stack) > 0:
        node = stack.pop()
        if node.parent != None:
            if len(node.parent.cliqueList) >= len(node.cliqueList):
                # check node.cliqueList is subset of node.parent.cliqueList
                # next is this parent if not marked
                if not node.parent.marked:
                    stack.append(node.parent)
                if is_subset(node.parent.cliqueList, node.cliqueList):
                    for child in node.children:
                        child.parent = node.parent
                else:
                    node.marked = True
            else:
                # check node.parent.cliqueList is subset of node.cliqueList
                if is_subset(node.cliqueList, node.parent.cliqueList):
                    # parent.parent could be None if node.parent is root
                    for child in node.parent.children:
                        child.parent = node.parent.parent
                    node.parent = node.parent.parent
                    # node need rechecking with new parent
                    stack.append(node)
                else:
                    node.marked = True
        else:
            # TODO: is this ok?
            node.marked = True

    clique_tree = [x for x in graph if x.marked]
    return clique_tree


def ChordalGen(n, k):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    if 2 * k - 1 > n:
        raise Exception("ChordalGen parameter k must be lower than n/2")

    tree = TreeGen(n)
    # convert to networx before cliquelistgen, that function may alter the
    # children attribute -- not yet
    nx_tree = convert_tree_networkx(tree)
    # nx_export_json(nx_tree)
    print(dfs(tree, tree[0]))
    print(dfs_list(tree, tree[0]))
    subtrees = [SubTreeGen(tree, k, i) for i in range(0, n)]

    # print("subtrees: ", subtrees)
    # print("cliqueList: ", [t.cliqueList for t in tree])
    chordal = cliqueListGenChordal(tree)
    true_chordal = truecliqueListGenChordal(tree, subtrees)

    # func = functools.partial(truecliqueListGenChordal, tree, subtrees)
    # times = timeit.timeit(func, number=num)
    # print("Slow convert took {0} s".format(times * 1000 / num))

    # convert to networkx, export to json
    nx_chordal = convert_clique_tree_networkx(chordal)
    nx_true_chordal = convert_adjacency_list_networkx(true_chordal)
    # for nx_g in [nx_tree, nx_chordal]:
    #     print("is Chordal: {0} ".format(nx.is_chordal(nx_g)))
    #     print("is Tree: {0} ".format(nx.is_tree(nx_g)))
    #     print("is Connected: {0} ".format(nx.is_connected(nx_g)))
    print("is isomophic: {0} ".format(
        nx.is_isomorphic(nx_chordal, nx_true_chordal)))
    #     print("-------------------")
    nx_export_json([nx_tree, nx_chordal, nx_true_chordal])

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

        # update helper, children list, parent pointer
        selection.children.append(newnode)
        newnode.parent = selection

        # append to tree
        tree.append(newnode)

    return tree


def convert_tree_networkx(tree):
    """
        Converts a list of TreeNodes to networkx graph(using children nodes)
    """
    graph = nx.Graph(graph_type="tree")
    for treenode in tree:
        for child in treenode.children:
            graph.add_edge(treenode.id, child.id)

    return graph


def convert_clique_tree_networkx(clique_tree):
    """
        Converts a clique tree to a networkx graph
    """
    graph = nx.Graph(graph_type="fast")
    for node in clique_tree:
        for i in range(len(node.cliqueList)):
            for j in range(i + 1, len(node.cliqueList)):
                graph.add_edge(node.cliqueList[i], node.cliqueList[j])

    return graph


def convert_adjacency_list_networkx(adj_list_graph):
    """
        Converts an adjacency list graph to a networkx graph
    """
    graph = nx.Graph(graph_type="true")
    for node in adj_list_graph:
        for neighbour in node.Ax:
            graph.add_edge(node.id, neighbour.id)

    return graph


def nx_export_json(graphs, filename="graph.json"):
    """
        Exports a list of networkx graphs to json
    """
    if not isinstance(graphs, list):
        graphs = [graphs]

    json_data = []
    for graph in graphs:
        json_data.append(json_graph.node_link_data(graph))

    with io.open(filename, 'w') as file:
        json.dump(json_data, file, indent=4)


def is_subset(list1, list2):
    """
        Returns whether the list1 is subset of list2
        list1 MUST BE largest than list2
    """
    if len(list2) > len(list1):
        raise Exception("is subset called with largest list 2")
        # list1, list2=list2, list1

    i = 0
    j = 0
    # list1 should be the largest list
    while i < len(list2):
        while (j < len(list1)) and (list1[j] != list2[i]):
            j += 1
        if j == len(list1):
            return False
        i += 1

    return True


def dfs(graph, root):
    """
        Goes through a graph using DFS, using sets not returning in order
    """
    visited, stack = set(), [root]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(set(vertex.Ax) - visited)
    return visited


def dfs_list(graph, root):
    """
        Goes through a graph using DFS,using lists(should be faster)
    """
    for node in graph:
        node.dfs_visited = False

    visited, stack = [], [root]
    while stack:
        vertex = stack.pop()
        if not vertex.dfs_visited:
            visited.append(vertex)
            vertex.dfs_visited = True
            stack.extend((neighbour for neighbour in vertex.Ax if not neighbour.dfs_visited))
    return visited


def random_element(array, index=0):
    """
        Get a random element, and index from given array starting from index to end
    """
    i = R.randint(index, len(array) - 1)
    return array[i], i


ChordalGen(50, 14)
print(".....Done")
