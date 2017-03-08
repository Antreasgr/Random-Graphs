"""
    Create a random chordal graph
"""
from randomizer import *
from clique_tree import *
from subtrees import *
from nx_converters import *
import plotter

def ChordalGen(n, k):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    if 2 * k - 1 > n:
        raise Exception("ChordalGen parameter k must be lower than n/2")

    start_real_tree = Now()
    tree = TreeGen(n)
    end_real_tree = Now()

    start_subtrees = Now()
    for node in tree:
        node.s = 0
    # subtrees = [SubTreeGen(tree, k, i) for i in range(0, n)]
    subtrees = [sub_tree_gen(tree, k, i) for i in range(0, n)]
    end_subtrees = Now()
    my_end_subtrees = end_subtrees - e_rand

    # convert to networx before cliquelistgen, that function may alter the
    # children attribute -- not yet
    nx_tree = convert_tree_networkx(tree)

    start_true = Now()
    #true_chordal = truecliqueListGenChordal(tree, subtrees)
    end_true = Now()

    start_chordal = Now()
    #chordal = cliqueListGenChordal(tree)
    end_chordal = Now()

    # convert to networkx, our main algorithm
    start_ctree = Now()
    nx_chordal = convert_clique_tree_networkx(tree, n)
    end_ctree = Now()

    start_true_chordal = Now()
    ax_chordal = allnodes_alledges(nx_chordal)
    end_true_chordal = Now()

#    print("nx_chordal edges: ", nx_chordal.number_of_edges())

    # func = functools.partial(truecliqueListGenChordal, tree, subtrees)
    # times = timeit.timeit(func, number=num)
    # print("Slow convert took {0} s".format(times * 1000 / num))

    # for nx_g in [nx_tree, nx_chordal]:
    #     print("is Chordal: {0} ".format(nx.is_chordal(nx_g)))
    #     print("is Tree: {0} ".format(nx.is_tree(nx_g)))
    #     print("is Connected: {0} ".format(nx.is_connected(nx_g)))
    # print("is isomophic: {0} ".format(
    #   nx.is_isomorphic(nx_chordal, nx_true_chordal)))
    # print("is Connected: {0} ".format(nx.is_connected(nx_chordal)))

    #     print("-------------------")
#    print("is Chordal: {0} ".format(nx.is_chordal(nx_chordal)))
    print("time T: ", end_real_tree - start_real_tree)
    pl.add_time("real_tree", end_real_tree - start_real_tree)
    print("time Subtree  : ", end_subtrees - start_subtrees)
    pl.add_time("subtrees", end_subtrees - start_subtrees)
    print("time MySubtree: ", my_end_subtrees - start_subtrees)
    pl.add_time("Mysubtrees", my_end_subtrees - start_subtrees)
    # pl.add_time("cliqueListGenChordal", end_chordal - start_chordal)
    # print("time slow main: ", end_true - start_true)
    # pl.add_time("truecliqueListGenChordal", end_true - start_true)
    print("time our main : ", end_ctree - start_ctree)
    pl.add_time("convert_clique_tree_networkx", end_ctree - start_ctree)
    pl.add_time("ourtotal", end_ctree - start_ctree +
                end_real_tree - start_real_tree +
                end_subtrees - start_subtrees)
    pl.add_time("ourtotalnorandom", end_ctree - start_ctree +
                end_real_tree - start_real_tree +
                my_end_subtrees - start_subtrees)
    pl.add_time("allnodes_alledges",
                end_true_chordal - start_true_chordal)
    # check dfs running time:
    v_dfs = R.choice(nx_chordal.nodes())
    start_dfsnx = Now()
    dfstree = nx.dfs_tree(nx_chordal, v_dfs)
    end_dfsnx = Now()
    print("time nx_dfs: ", end_dfsnx - start_dfsnx)
    pl.add_time("nx_dfs", end_dfsnx - start_dfsnx)
    # check con.comp. running time:
    start_cc = Now()
    cc = nx.connected_components(nx_chordal)
    end_cc = Now()
    print("time nx_cc : ", end_cc - start_cc)
    pl.add_time("nx_cc", end_cc - start_cc)
    total_run = end_ctree - start_ctree + end_real_tree - \
        start_real_tree + end_subtrees - start_subtrees
    total_run_norandom = end_ctree - start_ctree + end_real_tree - \
        start_real_tree + my_end_subtrees - start_subtrees
    run_alledges = end_true_chordal - start_true_chordal
    run_dfs = end_dfsnx - start_dfsnx
    run_cc = end_cc - start_cc
    print("Running time overhead over Alledges:             ",
          total_run / run_alledges)
    print("Running time (no random) overhead over Alledges: ",
          total_run_norandom / run_alledges)
    print("Running time overhead over DFS:                  ", total_run / run_dfs)
    print("Running time (no random) overhead over DFS:      ",
          total_run_norandom / run_dfs)
    print("Running time overhead over CC:                   ", total_run / run_cc)
    print("Running time (no random) overhead over CC:       ",
          total_run_norandom / run_cc)

    #nx_export_json([nx_tree, nx_chordal, nx_true_chordal])
    nx_export_json([nx_tree, nx_chordal])

    return subtrees

def TreeGen(n):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode(0)]
    for i in range(0, n - 1):
        selection, _ = random_element(tree)
        newnode = TreeNode(i + 1)

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

pl = plotter.Plotter()
pl.add_label('cliqueListGenChordal', 'Generate clique tree')
pl.add_label('truecliqueListGenChordal', 'Generate clique tree(slow)')
pl.add_label('convert_clique_tree_networkx', 'Clique tree to networkx')
pl.add_label('allnodes_alledges',
             'allnodes_alledges')
pl.add_label('ourtotal', 'Our total time')
pl.add_label('ourtotalnorandom', 'Our total time without Random')
pl.add_label('truetotal', 'Slow total time')
pl.add_label('nx_dfs', 'DFS(using networkx)')
pl.add_label('nx_cc', 'CC(using networkx)')
pl.add_label('simple_dfs', 'DFS(using sets)')
pl.add_label('list_dfs', 'DFS(using lists)')
pl.add_label('real_tree', 'Real T generator')
pl.add_label('subtrees', 'SubTrees generator')
pl.add_label('Mysubtrees', 'SubTrees generator without Random')

e_rand = 0
ChordalGen(7, 4)
print(".....Done")
pl.show()
