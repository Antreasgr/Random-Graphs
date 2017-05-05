from subtrees import *
import unittest
from LexBFS import LexBFS


def truecliqueListGenChordal(graph, subtrees):
    """
        Converts the output of the sub-tree generation algorithm to clique_tree
    """
    final_graph = [TreeNode(n.uid) for n in graph]

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
                # next is this parent if not marked
                if not node.parent.marked:
                    stack.append(node.parent)
                # check node.cliqueList is subset of node.parent.cliqueList
                if is_subset(node.parent.cliqueList, node.cliqueList):
                    for child in node.children:
                        child.parent = node.parent
                else:
                    node.marked = True
            else:
                # check node.parent.cliqueList is subset of node.cliqueList
                if is_subset(node.cliqueList, node.parent.cliqueList):
                    # parent.parent could be None if node.parent is root
                    p = node.parent.parent
                    for child in node.parent.children:
                        child.parent = p
                    node.parent = p
                    # node need rechecking with new parent
                    stack.append(node)
                else:
                    node.marked = True
                    # bug ??? why and when is this needed???
                    if not node.parent.marked:
                        stack.append(node.parent)
        else:
            node.marked = True

    # TODO: maybe return new nodes and not reference
    # to the originals, fix children arrays
    clique_tree = [x for x in graph if x.marked]
    return clique_tree


def is_subset(list1, list2):
    """
        Returns whether the list1 is subset of list2
        list1 MUST BE largest than list2
    """
    if len(list2) > len(list1):
        raise Exception("is subset called with largest list 2")
        # list1, list2=list2, list1

    i, j = 0, 0
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
            stack.extend(
                (neighbour for neighbour in vertex.Ax if not neighbour.dfs_visited))
    return visited


def dfs_tree(tree, root):
    """
        Goes through a tree using DFS, and compute max children, its depth, and the level of each node 
    """
    visited, stack = set(), [root]

    width, height = float("-inf"), float("-inf")
    # root.height = 0
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            new_c = set(vertex.children) - visited
            num_children = 0
            for c in new_c:
                # weight = is_subset(c.cliqueList, vertex.cliqueList)
                # if weight:
                #     print(weight)
                # else:
                #     raise Exception("No sublist")


                c.height = vertex.height + 1
                num_children += 1
            if num_children > width:
                width = num_children
            if vertex.height > height:
                height = vertex.height
            stack.extend(new_c)
    return width, height


def dfs_forest(forest):
    """
        Goes through a forest using DFS, and compute max children, its depth, and the level of each node 
    """
    width, height = float("-inf"), float("-inf")
    for tree in forest.ctree:
        w, h = dfs_tree(tree, tree[0])
        if w > width:
            width = w
        if h > height:
            height = h
    return width, height


def check_clique(vlist, graph):
    for i in range(0, len(vlist)):
        for j in range(i + 1, len(vlist)):
            if not graph.has_edge(vlist[i], vlist[j]):
                return False
    return True


def common_notincluded(list1, list2):
    if not list1:
        return False
    if not list2:
        return False
    if len(list1) > len(list2):
        l1, l2 = list1, list2
    else:
        l1, l2 = list2, list1
    if is_subset(l1, l2):
        return False
    return True


def is_cliqueforest(forest, graph):
    """
        Checks whether forest is indeed a forest of clique trees:
        1. cliqueList induce a clique in G
        2. cliqueList is neither empty, nor subset or superset of each of its children         
        3. the induced subtree Tv of each v in cliqueList must be connected
    """
    seen = [[] for v in graph.nodes()]
    for tree in forest.ctree:
        stack = [tree[0]]
        while stack:
            u = stack.pop()
            # 1. cliqueList induce a clique in G
            a1 = check_clique(u.cliqueList, graph)
            # 2. cliqueList is neither empty, nor subset or superset of each of
            # its children
            a2 = True
            for c in u.children:
                a2 = a2 and common_notincluded(u.cliqueList, c.cliqueList)
            # 3. the induced subtree Tv of each v in cliqueList must be
            # connected
            a3 = True
            for v in u.cliqueList:
                if len(seen[v]):
                    i = 0
                    connected = False
                    while not connected and i < len(seen[v]):
                        utree = seen[v][i]
                        if u in utree.children or utree in u.children:
                            connected = True
                        i += 1
                else:
                    connected = True
                seen[v].append(u)
                a3 = a3 and connected
            if not (a1 and a2 and a3):
                # print(a1,a2,a3)
                return False
            stack.extend(u.children)
    return True


def PerfectEliminationOrdering(G):
    """Return a perfect elimination ordering, or raise an exception if not chordal.
    G should be represented in such a way that "for v in G" loops through
    the vertices, and "G[v]" produces a list of the neighbors of v; for
    instance, G may be a dictionary mapping each vertex to its neighbor set.
    Running time is O(n+m) and additional space usage over G is O(n+m).
    """
    alreadyProcessed = set()
    B = list(LexBFS(G))
    position = {B[i]: i for i in range(len(B))}
    leftNeighbors = {}
    parent = {}
    for v in B:
        leftNeighbors[v] = set(G[v]) & alreadyProcessed
        alreadyProcessed.add(v)
        if leftNeighbors[v]:
            parent[v] = B[max([position[w] for w in leftNeighbors[v]])]
            if not leftNeighbors[v] - {parent[v]} <= leftNeighbors[parent[v]]:
                raise ValueError(
                    "Input to PerfectEliminationOrdering is not chordal")
    B.reverse()
    return B


def Chordal(G):
    """Test if a given graph is chordal."""
    try:
        PerfectEliminationOrdering(G)
    except:
        return False
    return True
