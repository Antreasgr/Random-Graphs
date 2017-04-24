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


def chordal_generation(run, rand):
    """
        Generate a random chordal graph with n vertices, k is the algorithm parameter
    """
    k = run["parameters"]["k"]
    n = run["parameters"]["n"]
    version = run["parameters"]["version"]

    if 2 * k - 1 > n:
        raise Exception("chordal gen parameter k must be lower than n/2")

    print("- Begin Run ")
    print("\tParameters: ")
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format("n", "k", "seed", "version"))
    print('{0:>10} |{1:>10} |{2:>10} |{3:>10}'.format(n, k, rand.Seed, version))

    print("- Times: ")
    with Timer("t_real_tree", run["Times"]):
        tree = tree_generation(n, rand)

    with Timer("t_subtrees_2", run["Times"]):
        for node in tree:
            node.s = 0
        for subtree_index in range(0, n):
            if version == AlgorithmVersion.ReverseLookup:
                SubTreeGen(tree, k, subtree_index, rand)
            else:
                sub_tree_gen(tree, k, subtree_index, rand, version)

    # convert to networkx, our main algorithm
    with Timer("t_ctree", run["Times"]):
        nx_chordal, final_cforest = convert_clique_tree_networkx2(tree, n)

    ncc = nx.number_connected_components(nx_chordal)

    with Timer("t_chordal", run["Times"]):
        graph_chordal = Chordal(nx_chordal)

    with Timer("t_forestverify", run["Times"]):
        tree_cliqueforest = is_cliqueforest(final_cforest, nx_chordal)

    run["Output"]["tree"] = tree
    run["Output"]["nx_chordal"] = nx_chordal
    run["Output"]["final_cforest"] = final_cforest
    run["Output"]["graph_chordal"] = graph_chordal
    run["Output"]["ncc"] = ncc
    run["Output"]["tree_cliqueforest"] = tree_cliqueforest

    print("- End Run")
    sys.stdout.flush()


def post_process(run):
    out = run["Output"]
    times = run["Times"]

    print("- Verify:")
    print("\t is_chordal:      ", out["graph_chordal"])
    print("\t clique forest:   ", out["tree_cliqueforest"])
    print("- Stats:")
    t_total = times["t_real_tree"] + times["t_subtrees_2"] + times["t_ctree"]
    print('\t{0:20} {1:.15f}'.format("t_total:", t_total))

    ratiochordal = t_total / float(times["t_chordal"])
    ratioforest = t_total / float(times["t_forestverify"])
    ratioboth = t_total / float(times["t_forestverify"] + times["t_chordal"])

    print('\t{0:20} {1:.15f}'.format("ratio[total/chordal]:", ratiochordal))
    print('\t{0:20} {1:.15f}'.format("ratio[total/forest]:", ratioforest))
    print('\t{0:20} {1:.15f}'.format("ratio[total/[chordal+forest]]:", ratioboth))

    print("- Ouput:")
    print('\t{0} {1:,d}'.format("nodes:", len(out["nx_chordal"].nodes())))
    print('\t{0} {1:,d}'.format("edges:", len(out["nx_chordal"].edges())))

    print('\t{0} {1:,d}'.format("cc:", out["ncc"]))
    print('\t{0:20} {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}'.format(
        "clique tree:", "#", "min", "max", "average", "width", "height"))
    temp_forest = cForest(1)
    temp_forest.ctree.append(out["tree"])
    print_clique_tree_statistics(temp_forest)
    print_clique_tree_statistics(out["final_cforest"])

    nx_ctrees = [convert_tree_networkx(tree) for tree in out["final_cforest"].ctree]
    nx_ctrees.insert(0, convert_tree_networkx(out["tree"]))

    return nx_ctrees

def print_clique_tree_statistics(forest):
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

    print('\t{0:20} {1:>10} {2:>10} {3:>10} {4:>10.3f} {5:>10} {6:>10}'.format(
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
    num_of_vertices = 10
    parameter_k = 4

    RUNNER = {"parameters":
                {
                    "n": num_of_vertices, "k": parameter_k, "version": AlgorithmVersion.Index, 'seed': None 
                },
                'Times': {},
                'Verify': {},
                'Stats': {},
                'Output':{}
            }

    for i in range(254, 255):
        randomizer = Randomizer(2 * num_of_vertices, i)

        RUNNER["parameters"]["seed"] = i
        RUNNER["parameters"]["version"] = AlgorithmVersion.Dict
        chordal_generation(RUNNER, randomizer)
        trees1 = post_process(RUNNER)

        randomizer.local_index = 0
        RUNNER["parameters"]["version"] = AlgorithmVersion.Index
        chordal_generation(RUNNER, randomizer)
        trees3 = post_process(RUNNER)

    # nx_export_json(trees1 + trees2)

    print(".....Done")

    """
        Todo:
        - clean the code
        - Randomizer(): we should keep it with linear parameter
                        what happens for small/large parameter?
                        does it affect on the quality of the random graph?
                        does it affect on the running time?
    """
