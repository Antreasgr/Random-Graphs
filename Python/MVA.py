# -*- coding: utf-8 -*-
import os
import collections
from datetime import datetime

from randomizer import *
from numpy import core
from UnionFind import UnionFind
from nx_converters import *
from clique_tree import TreeStatistics
from Runners import *
"""
    Implements the markenzon algorithm version 2 as described in paper
    @param l holds the number of maximal cliques generated
        (l < n, since the graph isconnected).
    @param m The number of edges
    @param Q stores the contents of the maximal cliques generated.
    @param S is an array of integers, such that Si is the cardinality of Qi, 1≤i<n.
    @param L The list of triples L contains the edges of the clique-tree
        along with their weights; each edge is given by a pair of integers (i, j),
        which are the positions of its endpoints in the array Q
"""


class MVAParameters(object):
    __slots__ = ["num_maximal_cliques", "num_edges", "edges_list", "cardinality_array", "cliques"]

    def __init__(self, l, m, L, S, Q):
        self.num_maximal_cliques = l
        self.num_edges = m
        self.edges_list = L
        self.cardinality_array = S
        self.cliques = Q

    def __str__(self):
        return "\t#: {}\n\tedges: {}\n\tedges_list: {}\n\tcardinalities: {}\n\tcliques: {}".format(
            self.num_maximal_cliques, self.num_edges, "Not printed for speed", "Not printed for speed", "Not printed for speed")

    def __repr__(self):
        return self.__str__()


def split_edges(m_parameters, upper_bound, rand):
    """
        Split clique tree edges
    """
    dis_set = UnionFind()
    [dis_set[i] for i in range(m_parameters.num_maximal_cliques)]

    final_edges = []
    while m_parameters.edges_list and m_parameters.num_edges < upper_bound:
        (x, y, sep, omega), index = rand.next_element(m_parameters.edges_list)
        i = dis_set[x]
        j = dis_set[y]

        edges_x = m_parameters.cardinality_array[i] - omega
        edges_y = m_parameters.cardinality_array[j] - omega

        x_sep, y_sep = m_parameters.cliques[i] - set(sep), m_parameters.cliques[j] - set(sep)
        if m_parameters.num_edges + 1 > upper_bound:
            break

        if len(x_sep) == 0 and len(y_sep) == 0:
            # no other vertices what to do?
            print("all vertices common case")
            continue
        elif len(x_sep) == 1 and len(y_sep) == 1:
            # merge {x,y}
            dis_set.union(x, y)
            m_parameters.cliques[i].update(m_parameters.cliques[j])
            m_parameters.cardinality_array[i] = edges_y + edges_x + omega
            m_parameters.cliques[j] = set()
            m_parameters.cardinality_array[j] = 0
            m_parameters.num_edges += edges_y * edges_x
            m_parameters.num_maximal_cliques -= 1
            # delete old edge
            del m_parameters.edges_list[index]
        elif len(x_sep) == 1:
            # merge {x,z}
            y_random, _ = rand.next_element(list(y_sep))

            m_parameters.cliques[i].update([y_random])
            m_parameters.cardinality_array[i] += 1
            # update the edge min-seperator
            m_parameters.edges_list[index] = (x, y, [y_random] + sep, omega + 1)

            # update num of edges
            m_parameters.num_edges += 1
        elif len(y_sep) == 1:
            # merge {y,z}
            x_random, _ = rand.next_element(list(x_sep))

            m_parameters.cliques[j].update([x_random])
            m_parameters.cardinality_array[j] += 1
            # update the edge min-seperator
            m_parameters.edges_list[index] = (x, y, [x_random] + sep, omega + 1)

            # update num of edges
            m_parameters.num_edges += 1
        else:
            # make new z node
            x_random, _ = rand.next_element(list(x_sep))
            y_random, _ = rand.next_element(list(y_sep))
            z = set([x_random, y_random] + sep)

            # add node to list
            m_parameters.cliques.append(z)
            m_parameters.cardinality_array.append(len(z))

            # fix union find structure
            dis_set[m_parameters.num_maximal_cliques]

            # add x-z edge
            m_parameters.edges_list.append((x, m_parameters.num_maximal_cliques, [x_random] + sep, omega + 1))
            # add y-z edge
            m_parameters.edges_list.append((y, m_parameters.num_maximal_cliques, [y_random] + sep, omega + 1))

            m_parameters.num_maximal_cliques += 1
            # update num of edges
            m_parameters.num_edges += 1

            # delete old edge
            del m_parameters.edges_list[index]


def merge_cliques(m_parameters, upper_bound, rand):
    """
        Merge cliques
    """
    dis_set = UnionFind()
    [dis_set[i] for i in range(m_parameters.num_maximal_cliques)]

    final_edges = []

    m_parameters.edges_list.sort(key=lambda e: -e[3])

    while m_parameters.edges_list and m_parameters.num_edges < upper_bound:
        # (a, b, sep, omega), index = rand.next_element(m_parameters.edges_list)
        (a, b, sep, omega), index = m_parameters.edges_list[0], 0
        del m_parameters.edges_list[index]
        i = dis_set[a]
        j = dis_set[b]
        delta = m_parameters.cardinality_array[i] - omega
        Delta = m_parameters.cardinality_array[j] - omega
        if m_parameters.num_edges + (delta * Delta) <= upper_bound:
            dis_set.union(a, b)
            m_parameters.cliques[i].update(m_parameters.cliques[j])
            m_parameters.cardinality_array[i] = Delta + delta + omega
            m_parameters.cliques[j] = set()
            m_parameters.cardinality_array[j] = 0
            m_parameters.num_edges += Delta * delta
            m_parameters.num_maximal_cliques -= 1
        else:
            final_edges.append((a, b, sep, omega))

    m_parameters.edges_list.extend(final_edges)
    for i, (start, end, sep, weight) in enumerate(m_parameters.edges_list):
        m_parameters.edges_list[i] = (dis_set[start], dis_set[end], sep, weight)


def expand_cliques(n, rand):
    """
       Expand a clique
    """
    Q, S, L, m, l = [set([0])], [1], [], 0, 0
    for u in range(1, n):
        i = rand.next_random(0, l + 1)
        t = rand.next_random(0, S[i] + 1)
        if t == S[i]:
            # expand old clique
            Q[i].add(u)
            S[i] += 1
        else:
            # create new clique
            q_subset = rand.sample(Q[i], t)
            l += 1
            Q.append(set([u] + q_subset))
            S.append(t + 1)
            if len(Q) != len(S) and len(Q) != l:
                raise Exception("invalid l")

            L.append((i, l, q_subset, t))
        m += t

    return MVAParameters(l + 1, m, L, S, Q)


def expand_tree(n, rand):
    # we use lists instead of set because set is not indexable
    # and we cannot select a random element easily

    Q, S, L, m, l = [[0, 1]], [2], [], 1, 1
    for u in range(2, n):
        i = rand.next_random(0, l)
        x, _ = rand.next_element(Q[i])

        Q.append([x, u])
        S.append(2)
        l += 1
        L.append((i, l - 1, 1))
        m += 1

    # convert to set for the rest of the algorithm
    for i, n in enumerate(Q):
        Q[i] = set(Q[i])

    return MVAParameters(l, m, L, S, Q)


def dfs_mva_width_height(parameters):
    """
        Calculates the width and height of the MVA clique tree using dfs
    """
    dfs_dict = {}
    for (i, j, sep, w) in parameters.edges_list:
        if i not in dfs_dict:
            dfs_dict[i] = TreeNode(i)
        if j not in dfs_dict:
            dfs_dict[j] = TreeNode(j)
        dfs_dict[i].children.append(dfs_dict[j])

    dfs_stats = dfs_tree(None, next(iter(dfs_dict.values())))
    return (dfs_stats.width, dfs_stats.height)


def calculate_mva_statistics(p_mva, runner, randomizer, num_vertices):
    # calculate statistics
    stats = TreeStatistics()
    stats.num = p_mva.num_maximal_cliques
    stats.max_size = max(p_mva.cardinality_array)
    stats.min_size = min(s for s in p_mva.cardinality_array if s > 0)
    stats.sum_size = sum(s for s in p_mva.cardinality_array if s > 0)
    stats.avg_size = stats.sum_size / stats.num
    stats.num_edges = len(p_mva.edges_list)

    # distribution of size
    stats.distribution_size = collections.Counter((s for s in p_mva.cardinality_array if s > 0))

    if p_mva.edges_list:
        stats.sum_weight = sum(w for (_, _, sep, w) in p_mva.edges_list)
        stats.min_weight = min(w for (_, _, sep, w) in p_mva.edges_list)
        stats.max_weight = max(w for (_, _, sep, w) in p_mva.edges_list)
        stats.avg_weight = stats.sum_weight / stats.num_edges
        # distribution of weight
        stats.distribution_weight = collections.Counter((w for _, _, sep, w in p_mva.edges_list))

    # dfs for width and height
    stats.width, stats.height = dfs_mva_width_height(p_mva)

    stats.max_clique_edge_distribution = (stats.max_size * (stats.max_size - 1) / 2) / p_mva.num_edges

    runner["Stats"]["randoms"] = randomizer.total_count
    runner["Output"]["nodes"] = num_vertices
    runner["Stats"]["edges"] = p_mva.num_edges
    runner["Output"]["clique_trees"] = [stats]

    print_statistics([runner])

    # nx_export_json([nx_chordal])
    return runner


def Run_MVA(num_vertices, edge_density, algorithm_name):
    """
        Initialize and run the MVA algorithm
    """

    edges_bound = edge_density * ((num_vertices * (num_vertices - 1)) / 2)
    runner = runner_factory(num_vertices, algorithm_name, None, edges_bound=edges_bound, edge_density=edge_density)

    randomizer = Randomizer(2 * num_vertices, runner["parameters"]["seed"])
    with Timer("t_expand_cliques", runner["Times"]):
        p_mva = expand_cliques(runner["parameters"]["n"], randomizer)
        # p_mva = expand_tree(runner["parameters"]["n"], randomizer)

    print("- Expand cliques:")
    print(p_mva)

    with Timer("t_merge_cliques", runner["Times"]):
        merge_cliques(p_mva, runner["parameters"]["edges_bound"], randomizer)

    # with Timer("t_merge_cliques", runner["Times"]):
    #     split_edges(p_mva, runner["parameters"]["edges_bound"], randomizer)

    print("- Merge cliques:")
    # print("- Split edges:")
    print(p_mva)

    runner["Stats"]["total"] = runner["Times"]["t_merge_cliques"] + \
        runner["Times"]["t_expand_cliques"]

    # with Timer("t_convert_nx", runner["Times"]):
    #     nx_chordal = convert_markenzon_clique_tree_networkx2(
    #         p_mva.cliques, num_vertices)

    # with Timer("t_chordal", runner["Times"]):
    #     runner["Verify"]["is_chordal"] = Chordal(nx_chordal)

    return calculate_mva_statistics(p_mva, runner, randomizer, num_vertices)


NUM_VERTICES = [
    500,
    100,
    500,
    1000,
    2500,
    5000,
    10000,  # 50000, 100000, 500000, 1000000
]
EDGES_DENSITY = [0.1, 0.33, 0.5, 0.75, 0.99]

NAME = "SortedMinSepReverseMVA"

if __name__ == '__main__':
    for num in NUM_VERTICES:
        for edge_density in EDGES_DENSITY:
            Runners = []
            for _ in range(10):
                Runners.append(Run_MVA(num, edge_density, NAME))

            filename = "Results/" + NAME + "/Run_{}_{}_{}.yml".format(num, edge_density, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))

            with io.open(filename, 'w') as file:
                print_statistics(Runners, file)

            print("Done")
