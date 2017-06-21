from subtrees import *
import unittest
from LexBFS import LexBFS


class TreeStatistics(object):
    __slots__ = [
        'max_clique_edge_distribution', 'num', 'num_edges', 'min_size', 'max_size', 'avg_size', 'sum_size', 'min_weight', 'max_weight', 'avg_weight',
        'sum_weight', 'width', 'height', 'distribution_size', 'distribution_weight', 'degrees_var' , 'diameter'
    ]

    def __init__(self):
        self.num = 0
        self.min_size = float("inf")
        self.max_size = float("-inf")
        self.sum_size = 0
        self.avg_size = 0
        self.sum_weight = 0
        self.avg_weight = 0
        self.min_weight = float("inf")
        self.max_weight = float("-inf")
        self.num_edges = 0
        self.width = float("-inf")
        self.height = float("-inf")
        self.degrees_var = 0
        self.diameter = 0
        self.max_clique_edge_distribution = 0
        self.distribution_size = {}
        self.distribution_weight = {}

    def __str__(self):
        result = ''
        for slot in self.__slots__:
            result += '{0:30} {1!s:>22}\n'.format(slot + ':', getattr(self, slot))
        return result

    def __repr__(self):
        return self.__str__()


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


def common_values(list1, list2):
    """
        Returns the common values of two sorted arrays
    """
    i, j, common, len_a, len_b = 0, 0, 0, len(list1), len(list2)
    while i < len_a and j < len_b:
        if list1[i] > list2[j]:
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            common += 1
            i += 1
            j += 1
    return common


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


def dfs_tree(root, num_vertices):
    """
        Goes through a tree using DFS, and compute max children, its depth, and the level of each node
    """
    visited, stack = set(), [root]

    stats = TreeStatistics()
    avg_degree = 2 * (num_vertices - 1) / num_vertices
    # root.height = 0
    farthest_vertex = root

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            size = len(vertex.cliqueList)

            degree = len(vertex.children)
            new_c = set(vertex.children) - visited
            stats.num_edges += len(new_c)
            for c in new_c:
                c.weight = common_values(vertex.cliqueList, c.cliqueList)
                stats.sum_weight += c.weight
                c.height = vertex.height + 1

                if c.weight not in stats.distribution_weight:
                    stats.distribution_weight[c.weight] = 0
                stats.distribution_weight[c.weight] += 1

            stats.width = max(stats.width, degree)
            stats.degrees_var += (degree - avg_degree) * (degree - avg_degree)
            stats.height = max(stats.height, vertex.height)
            stats.sum_size += size
            stats.min_size = min(stats.min_size, size)
            stats.max_size = max(stats.max_size, size)

            if size not in stats.distribution_size:
                stats.distribution_size[size] = 0
            stats.distribution_size[size] += 1

            if new_c:
                stats.min_weight = min(stats.min_weight, min(c.weight for c in new_c))
                stats.max_weight = max(stats.max_weight, max(c.weight for c in new_c))

            if vertex.height > farthest_vertex.height:
                farthest_vertex = vertex

            stack.extend(new_c)

    # run a dfs from farthest_vertex to get the diameter
    farthest_vertex.height = 0
    visited, stack = set(), [farthest_vertex]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            neighbors = vertex.children
            if vertex.parent != None:
                neighbors.append(vertex.parent)

            new_c = set(neighbors) - visited
            for c in new_c:
                c.height = vertex.height + 1
            
            stats.diameter = max(stats.diameter, vertex.height)
            stack.extend(new_c)

    return stats


def dfs_forest(forest):
    """
        Goes through a forest using DFS, and compute max children, its depth, and the level of each node
    """
    stats = TreeStatistics()
    for tree in forest.ctree:
        tree_stats = dfs_tree(tree, tree[0])

        stats.num += len(tree)
        stats.min_size = min(stats.min_size, tree_stats.min_size)
        stats.max_size = max(stats.max_size, tree_stats.max_size)
        stats.sum_size += tree_stats.sum_size
        stats.width = max(tree_stats.width, stats.width)
        stats.height = max(tree_stats.height, stats.height)
        stats.sum_weight += tree_stats.sum_weight
        stats.min_weight = min(stats.min_weight, tree_stats.min_weight)
        stats.max_weight = max(stats.max_weight, tree_stats.max_weight)
        stats.num_edges += tree_stats.num_edges
        stats.distribution_size.update(tree_stats.distribution_size)
        stats.distribution_weight.update(tree_stats.distribution_weight)

    stats.avg_size = stats.sum_size / stats.num
    if stats.num_edges > 0:
        stats.avg_weight = stats.sum_weight / stats.num_edges

    return stats


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
                raise ValueError("Input to PerfectEliminationOrdering is not chordal")
    B.reverse()
    return B


def Chordal(G):
    """Test if a given graph is chordal."""
    try:
        PerfectEliminationOrdering(G)
    except:
        return False
    return True
