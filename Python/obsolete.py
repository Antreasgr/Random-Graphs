
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