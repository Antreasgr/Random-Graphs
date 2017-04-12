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
# import plotter


def chordal_generation(n, k, rand, pl=None):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    if 2 * k - 1 > n:
        raise Exception("chordal gen parameter k must be lower than n/2")

    with Timer("t_real_tree") as t_real_tree:
        tree = tree_generation(n, rand)

    with Timer("t_subtrees_2") as t_subtrees_2:
        for node in tree:
            node.s = 0
        for i in range(0, n):
            sub_tree_gen(tree, k, i, rand)

    # this is only for visual purposes
    # t_nx_tree = Now()
    # nx_tree = convert_tree_networkx(tree)
    # t_nx_tree = Now() - t_nx_tree
    # print("t_nx_tree:       ", t_nx_tree)

    # convert to networkx, our main algorithm
    with Timer("t_ctree") as t_ctree:
        nx_chordal, final_ctree = convert_clique_tree_networkx2(tree, n)

    # check dfs running time:
    v_dfs = rand.Rstate.choice(nx_chordal.nodes())
    with Timer("t_dfsnx") as t_dfsnx:
        dfstree = nx.dfs_tree(nx_chordal, v_dfs)

    # check con.comp. running time:
    with Timer("t_cc") as t_cc:
        ncc = nx.number_connected_components(nx_chordal)

    t_total = t_real_tree.elapsed + t_subtrees_2.elapsed + t_ctree.elapsed
    print("----------- Stats: -----------------------")
    print('{0:20} ==> {1:.15f}'.format("t_total", t_total))

    print('{0:20} ==> {1:,d}'.format("nodes", len(nx_chordal.nodes())))
    print('{0:20} ==> {1:,d}'.format("k", k))
    print('{0:20} ==> {1:,d}'.format("edges", len(nx_chordal.edges())))

    print('{0:20} ==> {1:,d}'.format("cc", ncc))
    print('{0:20} ==> {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}'.format(
        "cliques", "#", "min", "max", "average", "width", "height"))
    print_clique_tree_statistics(tree)
    print_clique_tree_statistics(final_ctree)
    sys.stdout.flush()

    # print("Running time overhead over Alledges:             ", total_run / t_allnodes_alledges)
    # print("Running time overhead over DFS:                  ", total_run / t_dfsnx)
    # print("Running time overhead over CC:                   ", total_run /
    # t_cc)

    # nx_export_json([nx_tree, nx_chordal, nx_true_chordal])
    # t_nx_export = Now()
    # nx_export_json([nx_tree, nx_chordal])
    # t_nx_export = Now() - t_nx_export
    # print("t_nx_export:     ", t_nx_export)

    # return subtrees


def print_clique_tree_statistics(tree):
    cliques = (len(c.cliqueList) for c in tree)
    max_clique_size, min_clique_size, sum_clique_size = float(
        "-inf"), float("inf"), 0
    for c in cliques:
        max_clique_size = max(max_clique_size, c)
        min_clique_size = min(min_clique_size, c)
        sum_clique_size += c

    avg_clique_size = sum_clique_size / len(tree)

    width, height = dfs_tree(tree, tree[0])

    print('{0:20} ==> {1:>10} {2:>10} {3:>10} {4:>10.3f} {5:>10} {6:>10}'.format(
        "", len(tree), min_clique_size, max_clique_size, avg_clique_size, width, height))


def tree_generation(n, rand):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode(0)]
    for uid in range(0, n - 1):
        selection, _ = rand.next_element(tree)
        newnode = TreeNode(uid + 1)

        # update the adjacency lists
        newnode.Ax.append(selection)
        selection.Ax.append(newnode)

        # also make: x.Ax[i] = y
        #            x.Rx[i] = length(y.Ax) so that
        # if x.Ax[i] = y then
        #    y.Ax[x.Rx[i]] = x
        newnode.Rx.append(len(selection.Ax) - 1)
        selection.Rx.append(len(newnode.Ax) - 1)

        # update helper, children list, parent pointer
        selection.children.append(newnode)
        newnode.parent = selection

        # append to tree
        tree.append(newnode)

    return tree

# from joblib import Parallel, delayed
if __name__ == '__main__':
    #    plter = plotter.Plotter()
    #    plter.add_label('cliqueListGenChordal', 'Generate clique tree')
    #    plter.add_label('truecliqueListGenChordal', 'Generate clique tree(slow)')
    #    plter.add_label('convert_clique_tree_networkx', 'Clique tree to networkx')
    #    plter.add_label('allnodes_alledges', 'Base line all nodes all edges')
    #    plter.add_label('ourtotal', 'Our total time')
    #    plter.add_label('truetotal', 'Slow total time')
    #    plter.add_label('nx_dfs', 'DFS(using networkx)')
    #    plter.add_label('nx_cc', 'CC(using networkx)')
    #    plter.add_label('simple_dfs', 'DFS(using sets)')
    #    plter.add_label('list_dfs', 'DFS(using lists)')
    #    plter.add_label('real_tree', 'Real T generator')
    #    plter.add_label('subtrees', 'SubTrees generator')

    # Parallel(n_jobs=4)(delayed(ChordalGen)(500, 47, plotter) for i in
    # range(10))

    num_of_vertices = 20
    parameter_k = 2

    # initialize 10M random floats
    for i in range(4, 5):
        rand = Randomizer(2*num_of_vertices, i)
        chordal_generation(num_of_vertices, parameter_k, rand)

    print(".....Done")
    # plter.show()
