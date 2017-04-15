from subtrees import *


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
        w , h = dfs_tree(tree, tree[0])
        if w > width:
            width = w
        if h > height:
            height = h
    return width, height
