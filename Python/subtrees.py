from enum import Enum


class AlgorithmVersion(Enum):
    """
        The available versions of the algorithm
    """
    Index = 0
    Dict = 1
    Hybrid = 2


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


def sub_tree_gen(T, k, i, rand, version=AlgorithmVersion.Index):
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
        z, zi = y.Ax[y.s], y.s # rand.next_element(y.Ax, y.s)

        # add z to Ti
        tree_i.append(z)
        z.cliqueList.append(i)  # add to the z node of T the {i} number of Ti

        # fix y.Ax
        if zi != y.s:
            y.Ax[zi], y.Ax[y.s] = y.Ax[y.s], y.Ax[zi]
            if version != AlgorithmVersion.Index:
                y.Dx[z] = y.s
                y.Dx[y.Ax[zi]] = zi
        y.s += 1

        # now fix z
        if z.Ax[z.s] != y:
            if version == AlgorithmVersion.Index:
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
