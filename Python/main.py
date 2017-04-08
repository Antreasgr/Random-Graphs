"""
    Create a random chordal graph
"""
from randomizer import *
from clique_tree import *
from subtrees import *
from nx_converters import *
import networkx as nx
from numpy.random import RandomState
# import plotter

def ChordalGen(n, k, pl):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    if 2 * k - 1 > n:
        raise Exception("ChordalGen parameter k must be lower than n/2")

    t_real_tree = Now()
    tree = TreeGen(n)
    t_real_tree = Now() - t_real_tree
    print('{0:20} ==> {1:.15f}'.format("t_real_tree", t_real_tree))

    t_subtrees = Now()
    for node in tree:
         node.s = 0
    for i in range(0, n):
        SubTreeGen(tree, k, i)         
    t_subtrees = Now() - t_subtrees
    print("t_subtrees:      ", t_subtrees)    
    sys.stdout.flush()

    t_subtrees_2 = Now()        
    for node in tree:
        node.s = 0
    for i in range(0, n):
        sub_tree_gen(tree, k, i)
    t_subtrees_2 = Now() - t_subtrees_2
    print('{0:20} ==> {1:.15f}'.format("t_subtrees_2", t_subtrees_2))

    # convert to networx before cliquelistgen, that function may alter the
    # children attribute -- not yet
    # t_nx_tree = Now()    
    # nx_tree = convert_tree_networkx(tree)
    # t_nx_tree = Now() - t_nx_tree    
    # print("t_nx_tree:       ", t_nx_tree)

    # start_true = Now()
    # true_chordal = truecliqueListGenChordal(tree, subtrees)
    # nx_true_chordal = convert_adjacency_list_networkx(true_chordal)
    # end_true = Now()

    # start_chordal = Now()
    # chordal = cliqueListGenChordal(tree)
    # end_chordal = Now()

    # convert to networkx, our main algorithm
    t_ctree = Now()
    nx_chordal = convert_clique_tree_networkx2(tree, n)
    t_ctree = Now() - t_ctree
    print('{0:20} ==> {1:.15f}'.format("t_ctree", t_ctree))

    # t_allnodes_alledges = Now()
    # ax_chordal = allnodes_alledges(nx_chordal)
    # t_allnodes_alledges = Now() - t_allnodes_alledges

    # print("is isomophic: {0} ".format(nx.is_isomorphic(nx_chordal, nx_true_chordal)))
    ## pl.add_time("real_tree", t_real_tree, output=True)
    # pl.add_time("subtrees", t_subtrees, output=True)
    ## pl.add_time("subtrees2", t_subtrees_2, output=True)
    ## pl.add_time("convert_clique_tree_networkx", t_ctree, output=True)
    ## pl.add_time("ourtotal", t_ctree + t_real_tree + t_subtrees_2, output=True)
    # pl.add_time("allnodes_alledges", t_allnodes_alledges, output=True)

    # check dfs running time:
    v_dfs = R.choice(nx_chordal.nodes())
    t_dfsnx = Now()
    dfstree = nx.dfs_tree(nx_chordal, v_dfs)
    t_dfsnx = Now() - t_dfsnx
    print("t_dfsnx: ", t_dfsnx)
    sys.stdout.flush()

    # check con.comp. running time:
    t_cc = Now()
    ncc = nx.number_connected_components(nx_chordal)
    t_cc = Now() - t_cc
    print("ncc: ", ncc)
    sys.stdout.flush()
    t_total = t_real_tree + t_subtrees_2 + t_nx_tree + t_ctree
    print("t_total: ", t_total)
    sys.stdout.flush()
    
    # pl.add_time("nx_cc", t_cc, output=True)
    # total_run = t_ctree + t_real_tree + t_subtrees

    # print("Running time overhead over Alledges:             ", total_run / t_allnodes_alledges)
    # print("Running time overhead over DFS:                  ", total_run / t_dfsnx)
    # print("Running time overhead over CC:                   ", total_run / t_cc)

    # nx_export_json([nx_tree, nx_chordal, nx_true_chordal])
    # t_nx_export = Now()    
    # # nx_export_json([nx_tree, nx_chordal])
    # t_nx_export = Now() - t_nx_export
    # print("t_nx_export:     ", t_nx_export)

    # return subtrees


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

#from joblib import Parallel, delayed
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

#    for kk in range(0, 1):
#        r1 = R.randint(15, 20)
#        r2 = R.randint(1, r1 / 2)
#        print(r1, r2)
#        ChordalGen(r1, r2, plter)

    # Parallel(n_jobs=4)(delayed(ChordalGen)(500, 47, plotter) for i in range(10))

    num_of_vertices = 10000
    parameter_k = 200

    ChordalGen(num_of_vertices, parameter_k, -1)
    print(".....Done")
    # # plter.show()
