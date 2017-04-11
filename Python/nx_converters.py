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
    ctree = []
    helper = {}
    while queue:
        clique = queue.popleft()
        queue.extend(clique.children)
        is_valid_clique = add_clique_networx(graph, clique.cliqueList, seen)

        if is_valid_clique:
            newnode = TreeNode(clique.uid)
            newnode.cliqueList = clique.cliqueList
            ctree.append(newnode)
            helper[clique.uid] = newnode
            if clique.parent != None:
                # if this is not the root fix parent and children pointers
                p = clique.parent
                while p != None and p.uid not in helper:
                    # go up the tree until a valid parent is found
                    p = p.parent
                if p != None:
                    # in rare cases the root of the tree is not valid(empty) and a forest is created
                    newnode.parent = helper[p.uid]
                    newnode.parent.children.append(newnode)

    return graph, ctree


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


def add_clique_networx(graph, node, seen):
    O, N = [], []
    for c in node:
        if seen[c] == False:
            N.append(c)
            seen[c] = True
        else:
            O.append(c)
    if len(N):
        for i in range(len(N)):
            for j in range(i + 1, len(N)):
                graph.add_edge(N[i], N[j])

            for node2 in O:
                graph.add_edge(N[i], node2)
        return True
    return False


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
