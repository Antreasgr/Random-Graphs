"""
    Create a random chordal graph
"""
import statistics
import os

import networkx as nx
from numpy.random import RandomState

from clique_tree import *
from nx_converters import *
from randomizer import *
from subtrees import *
from datetime import datetime

# from joblib import Parallel, delayed
# import plotter


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
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format(n, k, rand.Seed, version))

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

    run["Output"]["tree"] = tree
    run["Output"]["nx_chordal"] = nx_chordal
    run["Output"]["final_cforest"] = final_cforest
    run["Verify"]["graph_chordal"] = graph_chordal
    run["Verify"]["tree_cliqueforest"] = tree_cliqueforest

    print("End Run".center(70, "-"))


def post_process(run):
    out = run["Output"]
    stats = run["Stats"]
    times = run["Times"]

    # get number of conected components
    stats["ncc"] = nx.number_connected_components(out["nx_chordal"])

    # calculate time, and ratios
    stats["t_total"] = times["t_real_tree"] + times["t_subtrees_2"] + times["t_ctree"]
    stats["ratio[total/chordal]"] = stats["t_total"] / float(times["t_chordal"])
    stats["ratio[total/forest]"] = stats["t_total"] / float(times["t_forestverify"])
    stats["ratio[total/[chordal+forest]]"] = stats["t_total"] / float(times["t_forestverify"] + times["t_chordal"])

    # get output parameters
    out["nodes"] = len(out["nx_chordal"].nodes())
    out["edges"] = len(out["nx_chordal"].edges())

    out["clique_trees"] = [{}, {}]

    temp_forest = cForest(1)
    temp_forest.ctree.append(out["tree"])

    # calculate tree output parameters
    calculate_clique_tree_statistics(temp_forest, out["clique_trees"][0])
    calculate_clique_tree_statistics(out["final_cforest"], out["clique_trees"][1])

    # convert clique forest to nx for export to json
    nx_ctrees = [convert_tree_networkx(tree) for tree in out["final_cforest"].ctree]
    nx_ctrees.insert(0, convert_tree_networkx(out["tree"]))

    return nx_ctrees

    
def calculate_clique_tree_statistics(forest, out):
    """
        Print statistics for a given clique tree
    """

    max_clique_size, min_clique_size, sum_clique_size, num_c = float(
        "-inf"), float("inf"), 0, 0
    for tree in forest.ctree:
        cliques = (len(c.cliqueList) for c in tree)
        for clique in cliques:
            max_clique_size = max(max_clique_size, clique)
            min_clique_size = min(min_clique_size, clique)
            sum_clique_size += clique
        num_c += len(tree)

    avg_clique_size = sum_clique_size / num_c

    width, height = dfs_forest(forest)

    out["#"], out["min"], out["max"] = num_c, min_clique_size, max_clique_size
    out["avg"], out["width"], out["height"] = avg_clique_size, width, height

    return num_c, min_clique_size, max_clique_size, avg_clique_size, width, height


def print_statistics(run, file=sys.stdout):
    """
        Print all statistics in pretty format
    """
    s_all = {'parameters':{}, 'Times':{}, 'Verify':{}, 'Stats':{},
             'Output': {"tree", "nx_chordal", "final_cforest"}}
    print("- Run:", file=file)
    for section in s_all:
        print("\t" + section + ":", file=file)
        for sub in run[section]:
            if sub not in s_all[section]:
                if sub != "clique_trees":
                    try:
                        print('\t\t{0:30} {1!s:>20}'.format(sub + ":", run[section][sub]), file=file)
                    except TypeError:
                        pass
                else:
                    print('\t\t{:30} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}'
                          .format(sub +":", "'#'", "min", "max", "average", "width", "height"), file=file)
                    for ctree in run[section][sub]:
                        print('\t\t{:30} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}'
                              .format("", ctree["#"], ctree["min"], ctree["max"], ctree["avg"],
                                      ctree["width"], ctree["height"]), file=file)

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


def runner_factory(num_of_vertices, parameter_k, seed=None, version=AlgorithmVersion.Index):
    """
        Creates a new runner object to initiliaze the algorithm
    """
    return {"parameters":
            {"n": num_of_vertices, "k": parameter_k, "version": version, 'seed': seed},
            'Times': {},
            'Verify': {},
            'Stats': {},
            'Output':{}
           }

if __name__ == '__main__':
    NUM_VERTICES = 10
    PAR_K = 4

    for i in range(254, 255):
        randomizer = Randomizer(2 * NUM_VERTICES, i)

        RUNNER = runner_factory(NUM_VERTICES, PAR_K, i, AlgorithmVersion.Dict)
        chordal_generation(RUNNER, randomizer)
        trees1 = post_process(RUNNER)

        randomizer.local_index = 0

        RUNNER2 = runner_factory(NUM_VERTICES, PAR_K, i, AlgorithmVersion.Index)
        chordal_generation(RUNNER2, randomizer)
        trees3 = post_process(RUNNER2)

    print(".....Done")
    # RUNNER contains all data and statistics
    filename = "Results/Run_{}_{}_{}.yml".format(NUM_VERTICES, PAR_K, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with io.open(filename, 'w') as file:
        print_statistics(RUNNER, file)
        print_statistics(RUNNER2, file)

    # nx_export_json(trees1 + trees2)

    """
        Todo:
        - clean the code
        - Randomizer(): we should keep it with linear parameter
                        what happens for small/large parameter?
                        does it affect on the quality of the random graph?
                        does it affect on the running time?
    """
