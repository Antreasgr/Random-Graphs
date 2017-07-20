from enum import Enum
from collections import deque
from math import floor
import numpy


class SHETVersion(Enum):
    """
        The available versions of the algorithm
    """
    Index = 0
    Dict = 1
    Hybrid = 2
    PrunedTree = 3
    ConnectedNodes = 4


class SimpleGraph(object):
    """
       A class representing simple graph
    """
    __slots__ = ['nodes', 'edges']

    def __init__(self):
        self.nodes = 0
        self.edges = 0

    def add_nodes_from(self, iterable):
        # self.nodes = list(iterable)
        self.nodes = len(iterable)

    def add_edge(self, node1, node2):
        self.edges += 1
        # self.edges.append((node1, node2))

    def size(self):
        return self.edges


class cForest(object):
    """
        A class representing a clique forest
    """
    __slots__ = ('uid', 'ctree')

    def __init__(self, uid):
        self.uid = uid
        self.ctree = []

    def __str__(self):
        return str(self.uid)

    def __repr__(self):
        return str(self.uid)


class TreeNode(object):
    """
        A class representing a tree node
    """
    __slots__ = ('uid', 'Ax', 'Dx', 'cliqueList', 'children', 'parent', 'marked', 'height', 'cc', 's', 'weight')

    def __init__(self, uid):
        self.uid = uid
        self.Ax = []
        self.Dx = {}
        self.cliqueList = []
        # helper attributes for tree form
        self.children = []
        self.parent = None
        self.marked = False
        self.height = 0
        # the weight of the edge from this to his parent
        self.weight = 0
        self.cc = 0

    def __str__(self):
        return str(self.uid)

    def __repr__(self):
        return str(self.uid)

    def __hash__(self):
        return hash(self.uid)


def clone_tree(clique_tree):
    old_new_dict = {}
    new_old_dict = {}
    cloned = []
    edges_list = []
    visited = set()
    for i, node in enumerate(clique_tree):
        if node not in visited:
            visited.add(node)
            new_node = TreeNode(len(cloned))
            cloned.append(new_node)
            old_new_dict[node.uid] = new_node.uid
            new_old_dict[new_node.uid] = i

            if node.parent != None:
                # make parent edge
                new_node.parent = cloned[old_new_dict[node.parent.uid]]
                new_node.Ax.append(new_node.parent)
                new_node.Dx[new_node.parent] = len(new_node.Ax) - 1

                # from parent to children edge
                parent = cloned[new_node.parent.uid]
                parent.children.append(new_node)
                parent.Ax.append(new_node)
                parent.Dx[new_node] = len(parent.Ax) - 1

                # add to edges list
                edges_list.append((new_node.uid, parent.uid))

    return cloned, edges_list, new_old_dict


def bfs_connected_components(clique_tree):
    ccs = []  # connected components is a list of lists
    visited = set()
    for node in clique_tree:
        if node not in visited:
            # start a bfs from node
            ccs.append([])
            queue = deque([node])
            while queue:
                vertex = queue.popleft()
                if vertex not in visited:
                    visited.add(vertex)
                    ccs[-1].append(vertex)
                    nn = set(vertex.children)
                    if vertex.parent != None:
                        nn.update([vertex.parent])

                    queue.extend(nn - visited)
    sizes = [(len(cc), i) for i, cc in enumerate(ccs)]
    sizes.sort(key=lambda d: d[0])
    return ccs, sizes


def pruned_tree(clique_tree, num_vertices, subtree_index, edge_fraction, barier, rand):
    t_clone, edges, new_old_dict = clone_tree(clique_tree)
    remove_count = floor((num_vertices - 1) * edge_fraction)
    for i in range(remove_count):
        ((node1_index, node2_index), edge_index) = rand.next_element(edges)
        del edges[edge_index]
        node1, node2 = t_clone[node1_index], t_clone[node2_index]
        if node2.parent != node1:
            node1, node2 = node2, node1

        node2.parent = None
        node1.children.remove(node2)

    ccs, sizes = bfs_connected_components(t_clone)
    ((ki, index), _) = rand.next_element(sizes, (1 - barier) * len(sizes))

    # add cliquelist to original tree
    for node in ccs[index]:
        original_node = clique_tree[new_old_dict[node.uid]]
        original_node.cliqueList.append(subtree_index)

    return ccs[index], ki


def bfs_height(clique_tree, root):
    for node in clique_tree:
        node.height = 0

    max_level = 0
    visited = set()
    queue = deque([node])
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
            vertex.height = vertex.parent.height + 1
            max_level = max(vertex.height, max_level)
            nn = set(vertex.children)
            # if vertex.parent != None:
            #     nn.update([vertex.parent])

            queue.extend(nn - visited)
    return max_level


def connected_nodes(clique_tree, num_vertices, rand):
    max_level = bfs_height(clique_tree, None)
    for subtree_index in range(num_vertices):
        levels_list = [[] for subtree_index in range(max_level + 1)]
        for node in clique_tree:
            node.marked = False

        k_i = rand.next_random(0, num_vertices)

        node_copy = [node for node in clique_tree]
        seperation_index = 0
        max_d = 0
        for k in range(k_i):
            node, node_index = rand.next_element(node_copy, seperation_index)
            node_copy[seperation_index], node_copy[node_index] = node_copy[node_index], node_copy[seperation_index]
            seperation_index += 1
            node.marked = True

            node.cliqueList.append(subtree_index)
            levels_list[node.height].append(node)
            max_d = max(max_d, node.height)

        for level in range(max_d, -1, -1):
            for node in levels_list[level]:
                if node.parent != None and not node.parent.marked:
                    node.parent.cliqueList.append(subtree_index)
                    node.parent.marked = True
                    levels_list[level - 1].append(node.parent)
            levels_list[level] = []


def sub_tree_gen(T, k, i, rand, version=SHETVersion.Index):
    """
        Generates a random subtree of a given tree
        Uses .index() but runs fast for small k if version==None || "index"
        else uses .Dx
    """
    tree_i = [rand.next_element(T, 0)[0]]

    # the Ti tree contains this node
    tree_i[0].cliqueList.append(i)

    if k <= 1:
        return tree_i

    k_i = rand.next_random(1, 2 * k - 1)
    s_y = 0
    for _ in range(1, k_i):
        # after sy we have nodes with neighbors outside
        y, yi = rand.next_element(tree_i, s_y)
        # after y.s in y.Ax there is a neighbor of y outside
        z, zi = y.Ax[y.s], y.s  # rand.next_element(y.Ax, y.s)

        # add z to Ti
        tree_i.append(z)
        z.cliqueList.append(i)  # add to the z node of T the {i} number of Ti

        # fix y.Ax
        if zi != y.s:
            y.Ax[zi], y.Ax[y.s] = y.Ax[y.s], y.Ax[zi]
            if version != SHETVersion.Index:
                y.Dx[z] = y.s
                y.Dx[y.Ax[zi]] = zi
        y.s += 1

        # now fix z
        if z.Ax[z.s] != y:
            if version == SHETVersion.Index:
                yzi = z.Ax.index(y)
                z.Ax[yzi], z.Ax[z.s] = z.Ax[z.s], z.Ax[yzi]
            else:
                yzi = z.Dx[y]
                z.Ax[yzi], z.Ax[z.s] = z.Ax[z.s], z.Ax[yzi]
                z.Dx[y] = z.s
                z.Dx[z.Ax[yzi]] = yzi
        z.s += 1

        # if degree of y equals the seperation index on adjacency list, y
        # cannot be selected any more
        if y.s > len(y.Ax) - 1:
            tree_i[s_y], tree_i[yi] = tree_i[yi], tree_i[s_y]
            s_y += 1

        if len(z.Ax) == 1:
            tree_i[s_y], tree_i[-1] = tree_i[-1], tree_i[s_y]
            s_y += 1

    for node in tree_i:
        node.s = 0

    return tree_i
