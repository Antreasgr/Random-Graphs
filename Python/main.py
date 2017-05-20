import os

import networkx as nx
from numpy.random import RandomState

from clique_tree import *
from nx_converters import *
from randomizer import *
from subtrees import *
from datetime import datetime
from Runners import *

import yaml
from yaml import Loader, Dumper

# from joblib import Parallel, delayed
# import plotter
"""
    Create a random chordal graph
"""


def tree_generation(n_vert, rand):
    """
        Creates a random tree on n nodes
        and create the adjacency lists for each node
    """
    tree = [TreeNode(0)]
    for uid in range(0, n_vert - 1):
        parent, _ = rand.next_element(tree)
        newnode = TreeNode(uid + 1)

        # update the adjacency lists
        newnode.Ax.append(parent)
        parent.Ax.append(newnode)

        parent.Dx[newnode] = len(parent.Ax) - 1
        newnode.Dx[parent] = len(newnode.Ax) - 1

        # update helper, children list, parent pointer
        parent.children.append(newnode)
        newnode.parent = parent

        # append to tree
        tree.append(newnode)

    return tree


def chordal_generation(run, rand):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    k = run["parameters"]["k"]
    n = run["parameters"]["n"]
    version = run["parameters"]["version"]

    if 2 * k - 1 > n:
        raise Exception("chordal gen parameter k must be lower than n/2")

    print("Begin Run ".center(70, "-"))
    print("Parameters: ")
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format("n", "k", "seed", "version"))
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format(n, k, rand.Seed if rand.Seed != None else "None", version))

    print("Times: ".center(70, "-"))
    with Timer("t_real_tree", run["Times"]):
        tree = tree_generation(n, rand)

    with Timer("t_subtrees_2", run["Times"]):
        for node in tree:
            node.s = 0
        for subtree_index in range(0, n):
            sub_tree_gen(tree, k, subtree_index, rand, version)

    # convert to networkx, our main algorithm
    with Timer("t_ctree", run["Times"]):
        nx_chordal, final_cforest = convert_clique_tree_networkx2(tree, n)

    with Timer("t_chordal", run["Times"]):
        graph_chordal = Chordal(nx_chordal)

    with Timer("t_forestverify", run["Times"]):
        tree_cliqueforest = is_cliqueforest(final_cforest, nx_chordal)

    run["Graphs"]["tree"] = tree
    run["Graphs"]["nx_chordal"] = nx_chordal
    run["Graphs"]["final_cforest"] = final_cforest
    run["Verify"]["graph_chordal"] = graph_chordal
    run["Verify"]["tree_cliqueforest"] = tree_cliqueforest

    print("End Run".center(70, "-"))


def post_process(run):
    out = run["Output"]
    graphs = run["Graphs"]
    stats = run["Stats"]
    times = run["Times"]

    # get number of conected components
    stats["ncc"] = nx.number_connected_components(graphs["nx_chordal"])

    # calculate time, and ratios
    stats["total"] = times["t_real_tree"] + times["t_subtrees_2"] + times["t_ctree"]
    stats["ratio[total/chordal]"] = stats["total"] / float(times["t_chordal"])
    stats["ratio[total/forest]"] = stats["total"] / float(times["t_forestverify"])
    stats["ratio[total/[chordal+forest]]"] = stats["total"] / float(times["t_forestverify"] + times["t_chordal"])

    # get output parameters
    out["nodes"] = len(graphs["nx_chordal"].nodes())
    out["edges"] = len(graphs["nx_chordal"].edges())
    out["edge_density"] = out["edges"] / ((out["nodes"] * (out["nodes"] - 1)) / 2)

    temp_forest = cForest(1)
    temp_forest.ctree.append(graphs["tree"])

    # calculate tree output parameters
    out["clique_trees"] = [dfs_forest(temp_forest), dfs_forest(graphs["final_cforest"])]

    # convert clique forest to nx for export to json
    nx_ctrees = None # [convert_tree_networkx(tree) for tree in graphs["final_cforest"].ctree]
    # nx_ctrees.insert(0, convert_tree_networkx(graphs["tree"]))

    return nx_ctrees


if __name__ == '__main__':
    NUM_VERTICES = [2500, 5000, 10000, 50000, 100000]
    PAR_K_FACTOR = [0.49, 0.33, 0.2, 0.1, 0.01]
    # EDGES_DENSITY = 0.1
    for num in NUM_VERTICES:
        for factor in PAR_K_FACTOR:
            Runners = []
            par_k = num // factor
            par_k = max(1, par_k)
            par_k = min(num // 2, par_k)
            for i in range(10):
                randomizer = Randomizer(2 * num)

                Runners.append(runner_factory(num, par_k, "SHET", None, version=AlgorithmVersion.Index))
                chordal_generation(Runners[-1], randomizer)
                trees1 = post_process(Runners[-1])

            print(".....Done")
            # RUNNER contains all data and statistics
            filename = "Results/SHET/Run_{}_{}_{}.yml".format(num, par_k, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with io.open(filename, 'w') as file:
                print_statistics(Runners, file)

    # nx_export_json(trees1 + [Runners[0]["Graphs"]["nx_chordal"]])
    