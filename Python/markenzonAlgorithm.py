from randomizer import *
from numpy import core
import random
from UnionFind import UnionFind
from nx_converters import *
from clique_tree import TreeStatistics

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

class MarkenzonParameters(object):
    __slots__ = ["num_maximal_cliques", "num_edges", "edges_list",
                 "cardinality_array", "cliques"]

    def __init__(self, l, m, L, S, Q):
        self.num_maximal_cliques = l
        self.num_edges = m
        self.edges_list = L
        self.cardinality_array = S
        self.cliques = Q

    def __str__(self):
        return "\t#: {}\n\tedges: {}\n\tedges_list: {}\n\tcardinalities: {}\n\tcliques: {}".format(
            self.num_maximal_cliques, self.num_edges,
            self.edges_list, self.cardinality_array, self.cliques)

    def __repr__(self):
        return self.__str__()


def merge_cliques(m_parameters, upper_bound, rand):
    """
        Merge cliques
    """
    dis_set = UnionFind()
    [dis_set[i] for i in range(m_parameters.num_maximal_cliques)]

    final_edges = []

    while m_parameters.edges_list and m_parameters.num_edges < upper_bound:
        (a, b, omega), index = rand.next_element(m_parameters.edges_list)
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
            final_edges.append((a, b, omega))

    m_parameters.edges_list.extend(final_edges)
    for i, (start, end, weight) in enumerate(m_parameters.edges_list):
        m_parameters.edges_list[i] = (dis_set[start], dis_set[end], weight)


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

            L.append((i, l, t))
        m += t

    return MarkenzonParameters(l + 1, m, L, S, Q)

NUM_VERTICES = 15
EDGES_BOUND = 50
def main():
    """
        Initialize the algorithm
    """
    runner = {"Times": {}, "Output": {}}

    randomizer = Randomizer(2 * NUM_VERTICES, 4)
    with Timer("t_expand_cliques", runner["Times"]):
        p_markenzon = expand_cliques(NUM_VERTICES, randomizer)
    print("- Expand cliques:")
    print(p_markenzon)

    with Timer("t_merge_cliques", runner["Times"]):
        merge_cliques(p_markenzon, EDGES_BOUND, randomizer)

    print("- Merge cliques:")
    print(p_markenzon)
    nx_chordal = convert_markenzon_clique_tree_networkx2(p_markenzon.cliques, NUM_VERTICES)

    # calculate statistics
    stats = TreeStatistics()
    stats.num = p_markenzon.num_maximal_cliques
    stats.max_size = max(p_markenzon.cardinality_array)
    stats.min_size = min(s for s in p_markenzon.cardinality_array if s > 0)
    stats.sum_size = sum(s for s in p_markenzon.cardinality_array if s > 0)
    stats.avg_size = stats.sum_size / stats.num
    stats.num_edges = p_markenzon.num_edges

    stats.sum_weight = sum(w for (_, _, w) in p_markenzon.edges_list)
    stats.avg_weight = stats.sum_weight / stats.num_edges

    # dfs?
    stats.width = 0
    stats.height = 0

    runner["Output"]["clique_trees"] = [stats]
    runner["Output"]["nodes"] = len(nx_chordal.nodes())
    runner["Output"]["edges"] = len(nx_chordal.edges())

    print("- Output:")
    print("    nodes:", runner["Output"]["nodes"])
    print("    edges:", runner["Output"]["edges"])
    print("    clique_trees:")
    for index, slot in enumerate(stats.__slots__):
        if index == 0:
            print('    - {0:30} {1!s:>22}'.format(slot + ':', getattr(stats, slot)))
        else:
            print('      {0:30} {1!s:>22}'.format(slot + ':', getattr(stats, slot)))


    # nx_export_json([nx_chordal])

if __name__ == '__main__':
    main()
