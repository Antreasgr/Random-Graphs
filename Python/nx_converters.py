import networkx as nx
from networkx.readwrite import json_graph
import io
import json
from collections import deque
from subtrees import *
import numpy


def convert_tree_networkx(tree):
    """
        Converts a list of TreeNodes to networkx graph(using children nodes)
    """
    graph = nx.Graph(graph_type="tree")

    for treenode in tree:
        if treenode.cliqueList:
            graph.add_node(treenode.id, clique_list=str(treenode.cliqueList))

        for child in treenode.children:
            graph.add_edge(treenode.id, child.id)

    return graph


def convert_clique_tree_networkx(clique_tree, num_vertices):
    """
        Converts a clique tree to a networkx graph
    """
    graph = nx.Graph(graph_type="fast")
    graph.add_nodes_from(range(num_vertices))
    visited, queue = [], deque([c for c in clique_tree if c.parent == None])
    while queue:
        parent = queue.popleft()
        visited.append(parent)
        # TODO: children array is pointing to original tree and wrong
        # so we need to find children by parent poiner
        # fix children array for this to be faster
        childs = [c for c in clique_tree if c.parent == parent]
        queue.extend(childs)

    seen = [None] * num_vertices
    for i, node in enumerate(visited):
        O, N = [], []
        for c in node.cliqueList:
            if seen[c] == None:
                N.append(c)
                seen[c] = 0
            else:
                O.append(c)
        if len(N):
            for i in range(len(N)):
                for j in range(i + 1, len(N)):
                    graph.add_edge(N[i], N[j])

                for node2 in O:
                    graph.add_edge(N[i], node2)

    return graph


def convert_clique_tree_networkx2(clique_tree, num_vertices):
    """
        Converts a clique tree to a networkx graph
    """
    graph = nx.Graph(graph_type="fast")
    graph.add_nodes_from(range(num_vertices))
    visited, queue = [], deque([c for c in clique_tree if c.parent == None])
    seen = numpy.full(num_vertices, False, dtype=bool)
    while queue:
        parent = queue.popleft()
        # visited.append(parent)
        queue.extend(parent.children)
        add_clique_networx(graph, parent, seen)

    return graph


def add_clique_networx(graph, node, seen):
    O, N = [], []
    for c in node.cliqueList:
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
                graph.add_edge(node.id, neighbour.id)
        else:
            graph.add_node(node.id)

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
