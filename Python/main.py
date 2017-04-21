"""
    Create a random chordal graph
"""
from randomizer import *
from clique_tree import *
from subtrees import *
from nx_converters import *
import networkx as nx
from numpy.random import RandomState
import statistics
# from joblib import Parallel, delayed
# import plotter


def chordal_generation(n, k, rand, version="index"):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    if 2 * k - 1 > n:
        raise Exception("chordal gen parameter k must be lower than n/2")

    print(" Begin Run ".center(50, "-"))
    print(" Parameters ".center(50, "-"))
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format(
        "n", "k", "seed", "version"))
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format(n, k, rand.Seed, version))

    print(" Time ".center(50, "-"))
    with Timer("t_real_tree") as t_real_tree:
        tree = tree_generation(n, rand)

    with Timer("t_subtrees_2") as t_subtrees_2:
        for node in tree:
            node.s = 0
        t_all1 = 0    
        for subtree_index in range(0, n):
            if version == "index":
                t_all1 = sub_tree_gen(tree, k, subtree_index, rand, t_all1)
            elif version == "Rx":
                t_all1 = SubTreeGen(tree, k, subtree_index, rand, t_all1)
            else:
                t_all1 = sub_tree_gen_new(tree, k, subtree_index, rand, t_all1)
    print("t_all1: ", t_all1)                

    # convert to networkx, our main algorithm
    with Timer("t_ctree") as t_ctree:
        nx_chordal, final_cforest = convert_clique_tree_networkx2(tree, n)

    #with Timer("t_dfsnx") as t_dfsnx:
    #    cc = nx.connected_components(nx_chordal)
    #    for c in cc:
    #        v_dfs = next(iter(c))
    #        dfstree = nx.dfs_tree(nx_chordal, v_dfs)

    # with Timer("t_cc") as t_cc:
    ncc = nx.number_connected_components(nx_chordal)

    with Timer("t_chordal") as t_chordal:
        graph_chordal = Chordal(nx_chordal)

    with Timer("t_forestverify") as t_forestverify:
        tree_cliqueforest = is_cliqueforest(final_cforest, nx_chordal)

    print(" Verify ".center(50, "-"))
    print("is_chordal:      ", graph_chordal)
    print("clique forest:   ", tree_cliqueforest)
    print(" Stats ".center(50, "-"))
    t_total = t_real_tree.elapsed + t_subtrees_2.elapsed + t_ctree.elapsed
    print('{0:20} ==> {1:.15f}'.format("t_total", t_total))
    #ratiodfs = float(str(t_total)) / float(str(t_dfsnx.elapsed))
    #print('{0:20} ==> {1:.15f}'.format("ratio[total/dfs]", ratiodfs))
    ratiochordal = float(str(t_total)) / float(str(t_chordal.elapsed))
    print('{0:20} ==> {1:.15f}'.format("ratio[total/chordal]", ratiochordal))
    ratioforest = float(str(t_total)) / float(str(t_forestverify.elapsed))
    print('{0:20} ==> {1:.15f}'.format("ratio[total/forest]", ratioforest))
    ratioboth = float(str(t_total)) / (float(str(t_forestverify.elapsed))+float(str(t_chordal.elapsed)))
    print('{0:20} ==> {1:.15f}'.format("ratio[total/[chordal+forest]]", ratioboth))
    print(" ".center(50, "-"))
    print('{0:20} ==> {1:,d}'.format("nodes", len(nx_chordal.nodes())))
    print('{0:20} ==> {1:,d}'.format("k", k))
    print('{0:20} ==> {1:,d}'.format("edges", len(nx_chordal.edges())))

    print('{0:20} ==> {1:,d}'.format("cc", ncc))
    print('{0:20} ==> {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}'.format(
        "cliques", "#", "min", "max", "average", "width", "height"))
    temp_forest = cForest(1)
    temp_forest.ctree.append(tree)
    print_clique_tree_statistics(temp_forest)
    print_clique_tree_statistics(final_cforest)

    nx_ctrees = [convert_tree_networkx(tree) for tree in final_cforest.ctree]
    nx_ctrees.insert(0, convert_tree_networkx(tree))

    print("End Run".center(50, "-"))
    sys.stdout.flush()

    return nx_ctrees


def print_clique_tree_statistics(forest):
    """
        Print statistics for a given clique tree
    """
    max_clique_size, min_clique_size, sum_clique_size, num_c = float(
        "-inf"), float("inf"), 0, 0
    for tree in forest.ctree:
        cliques = (len(c.cliqueList) for c in tree)
        for c in cliques:
            max_clique_size = max(max_clique_size, c)
            min_clique_size = min(min_clique_size, c)
            sum_clique_size += c
        num_c += len(tree)

    avg_clique_size = sum_clique_size / num_c

    width, height = dfs_forest(forest)

    print('{0:20} ==> {1:>10} {2:>10} {3:>10} {4:>10.3f} {5:>10} {6:>10}'.format(
        "", num_c, min_clique_size, max_clique_size, avg_clique_size, width, height))


def tree_generation(n, rand):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode(0)]
    for uid in range(0, n - 1):
        parent, _ = rand.next_element(tree)
        newnode = TreeNode(uid + 1)

        # update the adjacency lists
        newnode.Ax.append(parent)
        parent.Ax.append(newnode)

        # also make: x.Ax[i] = y
        #            x.Rx[i] = length(y.Ax) so that
        # if x.Ax[i] = y then
        #    y.Ax[x.Rx[i]] = x
        newnode.Rx.append(len(parent.Ax) - 1)
        parent.Rx.append(len(newnode.Ax) - 1)

        parent.Dx[newnode] = len(parent.Ax) - 1
        newnode.Dx[parent] = len(newnode.Ax) - 1

        # update helper, children list, parent pointer
        parent.children.append(newnode)
        newnode.parent = parent

        # append to tree
        tree.append(newnode)

    return tree


if __name__ == '__main__':
    num_of_vertices = 1000
    parameter_k = 400

    for i in range(100, 101):
        randomizer = Randomizer(2 * num_of_vertices, i)
        trees3 = chordal_generation(
            num_of_vertices, parameter_k, randomizer, version="Dx")
        randomizer.local_index = 0
        trees1 = chordal_generation(num_of_vertices, parameter_k, randomizer)
        randomizer.local_index = 0
        # trees2 = chordal_generation(num_of_vertices, parameter_k, randomizer, version="Rx")
        # randomizer.local_index = 0

    # nx_export_json(trees1 + trees2)

    print(".....Done")

    """
        Todo:
        - clean the code
        - Randomizer(): we should keep it with linear parameter
                        what happens for small/large parameter?
                        does it affect on the quality of the random graph?
                        does it affect on the running time?
        - SubTreeGen() and sub_tree_gen():
            what is the practical difference?
            when we should use the one against the other?
    """
