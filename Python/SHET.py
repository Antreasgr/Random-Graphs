import os

import networkx as nx
from numpy.random import RandomState

from clique_tree import *
from nx_converters import *
from randomizer import *
from subtrees import *
from datetime import datetime
from Runners import *
from report_generator import *

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
    k = run["Parameters"]["k"]
    n = run["Parameters"]["n"]
    version = run["Parameters"]["version"]

    if 2 * k - 1 > n:
        raise Exception("chordal gen parameter k must be lower than n/2")

    print("Begin Run ".center(70, "-"))
    print("Parameters: ")
    formatstr = ''
    listvalues = [str(v) for v in run["Parameters"].values()]
    listkeys = list(run["Parameters"].keys())
    for ii, par in enumerate(listvalues):
        formatstr += '{' + str(ii) + ':>' + str(max(len(par), len(listkeys[ii])) + 1) + '} |'
    print(formatstr.format(*listkeys))
    print(formatstr.format(*listvalues))

    print("Times: ".center(70, "-"))
    with Timer("t_real_tree", run["Times"]):
        tree = tree_generation(n, rand)

    with Timer("t_subtrees_2", run["Times"]):
        if version != SHETVersion.PrunedTree:
            for node in tree:
                node.s = 0
            for subtree_index in range(0, n):
                sub_tree_gen(tree, k, subtree_index, rand, version)
        else:
            fraction = run["Parameters"]["edge_fraction"]
            barier = run["Parameters"]["barier"]
            for sub_tree_index in range(n):
                pruned_tree(tree, n, sub_tree_index, fraction, barier, rand)

    # convert to networkx, our main algorithm
    with Timer("t_ctree", run["Times"]):
        nx_chordal, final_cforest = convert_clique_tree_networkx2(tree, n, True)

    run["Graphs"]["tree"] = tree
    run["Graphs"]["nx_chordal"] = nx_chordal
    run["Graphs"]["final_cforest"] = final_cforest

    print("End Run".center(70, "-"))


def post_process(run):
    out = run["Output"]
    graphs = run["Graphs"]
    stats = run["Stats"]
    times = run["Times"]

    # get number of conected components
    # stats["ncc"] = nx.number_connected_components(graphs["nx_chordal"])

    # calculate time, and ratios
    stats["total"] = times["t_real_tree"] + times["t_subtrees_2"] + times["t_ctree"]
    # stats["ratio[total/chordal]"] = stats["total"] / float(times["t_chordal"])
    # stats["ratio[total/forest]"] = stats["total"] / float(times["t_forestverify"])
    # stats["ratio[total/[chordal+forest]]"] = stats["total"] / float(times["t_forestverify"] + times["t_chordal"])

    # get output parameters
    out["nodes"] = run["Parameters"]["n"]  # len(graphs["nx_chordal"].nodes())
    out["edges"] = graphs["nx_chordal"].size()  # len(graphs["nx_chordal"].edges())
    stats["edge_density"] = float(out["edges"]) / (float(out["nodes"] * (out["nodes"] - 1)) / 2)

    temp_forest = cForest(1)
    temp_forest.ctree.append(graphs["tree"])

    # calculate tree output parameters
    out["clique_trees"] = [dfs_forest(graphs["final_cforest"], run["Parameters"]["n"])]

    ct_stats = out["clique_trees"][0]
    ct_stats.max_clique_edge_distribution = (ct_stats.max_size * (ct_stats.max_size - 1) / 2) / out["edges"]

    stats["ncc"] = len(graphs["final_cforest"].ctree)

    # convert clique forest to nx for export to json
    nx_ctrees = None  # [convert_tree_networkx(tree) for tree in graphs["final_cforest"].ctree]
    # nx_ctrees.insert(0, convert_tree_networkx(graphs["tree"]))

    return nx_ctrees


NAME = "SHET_PRUNED"
if __name__ == '__main__':
    NUM_VERTICES = [50, 100, 500, 1000, 2500, 5000, 10000]
    PAR_K_FACTOR = [
        [0.03, 0.1, 0.2, 0.32, 0.49],  # 50
        [0.04, 0.1, 0.22, 0.33, 0.49],  # 100
        [0.02, 0.05, 0.08, 0.2, 0.40],  # 500
        [0.02, 0.05, 0.08, 0.18, 0.33],  # 1000
        [0.01, 0.04, 0.07, 0.13, 0.36],  # 2500
        [0.01, 0.04, 0.07, 0.1, 0.36],  # 5000
        [0.009, 0.03, 0.06, 0.09, 0.33]  # 10000
    ]

    shet_data = []
    for j, num in enumerate(NUM_VERTICES):
        for factor in PAR_K_FACTOR[j]:
            Runners = []
            par_k = int(num * factor)
            par_k = max(1, par_k)
            par_k = min(num // 2, par_k)
            for i in range(3):
                randomizer = Randomizer(2 * num)

                # Runners.append(runner_factory(num, NAME, None, k=par_k, version=SHETVersion.Dict))

                Runners.append(runner_factory(num, NAME, None, k=0, edge_fraction=0.1, barier=0.33, version=SHETVersion.PrunedTree))

                chordal_generation(Runners[-1], randomizer)
                trees1 = post_process(Runners[-1])
                Runners[-1]["Stats"]["randoms"] = randomizer.total_count
                # cleanup some memory
                del Runners[-1]["Graphs"]

            print(".....Done")
            # # RUNNER contains all data and statistics
            # filename = "Results/SHET/Run_{}_{}_{}.yml".format(num, par_k, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            # if not os.path.isdir(os.path.dirname(filename)):
            #     os.makedirs(os.path.dirname(filename))

            # with io.open(filename, 'w') as file:
            #     print_statistics(Runners, file)

            shet_data.append(merge_runners(Runners))

    # run_reports_data(NAME, [], shet_data)
