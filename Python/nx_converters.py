import networkx as nx
from networkx.readwrite import json_graph
import io
import json
from collections import deque
from subtrees import *
import numpy
import sys


def convert_tree_networkx(tree):
    """
        Converts a list of TreeNodes to networkx graph(using children nodes)
    """
    graph = nx.Graph(graph_type="tree")

    for treenode in tree:
        if treenode.cliqueList:
            graph.add_node(treenode.uid, clique_list=str(treenode.cliqueList))

        for child in treenode.children:
            graph.add_edge(treenode.uid, child.uid)

    return graph


def convert_clique_tree_networkx2(clique_tree, num_vertices):
    """
        Converts a clique tree to a networkx graph
    """
    graph = nx.Graph(graph_type="fast")
    graph.add_nodes_from(range(num_vertices))
    seen = numpy.full(num_vertices, False, dtype=bool)

    if clique_tree[0].parent != None:
        raise Exception("Invalid tree first node is not root")

    queue = deque([clique_tree[0]])
    forest = cForest(0)
    helper = {}
    parent_queue = deque([clique_tree[0]])
    while queue:
        clique = queue.popleft()
        queue.extend(clique.children)
        is_valid_clique = add_clique_networx(graph, clique.cliqueList, seen)
        if is_valid_clique == "valid":
            newnode = TreeNode(clique.uid)
            newnode.cliqueList = clique.cliqueList
            parent = parent_queue.popleft()
            # here we need to be careful:
            # "parent" now may be a subset of "newnode"
            if len(newnode.cliqueList) >= len(parent.cliqueList) and is_subset(newnode.cliqueList, parent.cliqueList):
                # we have to kill "parent" and replace it by "newnode"
                # insted, we replace parent.cliqueList by newnode.cliqueList and update appropriately
                parent.cliqueList = newnode.cliqueList

            else:       
                newnode.parent = parent
                parent.children.append(newnode)
                newnode.cc = parent.cc
                for c in clique.children:
                    parent_queue.append(newnode)
                ctree = forest.ctree[newnode.cc]    
                ctree.append(newnode)
        if is_valid_clique == "newcc": 
            newnode = TreeNode(clique.uid)
            newnode.cliqueList = clique.cliqueList
            parent = parent_queue.popleft()
            newnode.parent = newnode
            newnode.cc = len(forest.ctree) # parent.cc + 1
            ctree = []
            ctree.append(newnode)
            forest.ctree.append(ctree)
            for c in clique.children:
                parent_queue.append(newnode)
           # forest.ctree.append(newnode)
        if is_valid_clique == "empty": 
            parent = parent_queue.popleft()
            for c in clique.children:
                parent_queue.append(c)
        if is_valid_clique == "dummy": 
            parent = parent_queue.popleft()
            for c in clique.children:
                parent_queue.append(parent)                

    return graph, forest


def convert_markenzon_clique_tree_networkx2(clique_tree, num_vertices):
    """
        Converts a list of cliques in RIP ordering to a networkx graph.
        Only the data initialization is different from `convert_clique_tree_networkx2`
    """
    graph = nx.Graph(graph_type="fast")
    graph.add_nodes_from(range(num_vertices))
    visited, queue = [], deque((c for c in clique_tree))
    seen = numpy.full(num_vertices, False, dtype=bool)
    while queue:
        parent = queue.popleft()
        add_clique_networx(graph, parent, seen)

    return graph


def add_clique_networx(graph, node, seen, add=True):
    """
        Add edges to "graph" depending on the Old and New nodes from the list of already "seen" nodes. 
        Returns "valid" if N != [] and O != []
        Returns "newcc" if N != [] and O = []
        Returns "dummy" if N = [] and O != []
        Returns "empty" if N = [] and O = []                        
    """    
    O, N = [], []
    for c in node:
        if seen[c] == False:
            N.append(c)
            seen[c] = True
        else:
            O.append(c)
    if len(N):
        if add:
            for i in range(len(N)):
                for j in range(i + 1, len(N)):
                    graph.add_edge(N[i], N[j])

                for node2 in O:
                    graph.add_edge(N[i], node2)
        if len(O):
            return "valid"
        else:
            return "newcc"
    if len(O):
        return "dummy"
    return "empty"


def allnodes_alledges(nx_graph):
    """
        Iterates over the adjacency list of a networkx graph and returns a graph with .Ax
    """
    Adj = [TreeNode(0)]
    for node in nx_graph.nodes():
        newnode = TreeNode(0)
        for neighbor in nx_graph.neighbors(node):
            newnode.Ax.append(neighbor)
        Adj.append(newnode)

    return Adj


def convert_adjacency_list_networkx(adj_list_graph):
    """
        Converts an adjacency list graph to a networkx graph
    """
    graph = nx.Graph(graph_type="true")
    for node in adj_list_graph:
        if len(node.Ax):
            for neighbour in node.Ax:
                graph.add_edge(node.uid, neighbour.uid)
        else:
            graph.add_node(node.uid)

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
