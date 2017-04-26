from randomizer import *
from numpy import core
import random
from UnionFind import UnionFind
from nx_converters import *

"""
    Implements the markenzon algorithm version 2 as described in paper
    @param l holds the number of maximal cliques generated
        (l < n, since the graph isconnected).
    @param m The number of edges
    @param Q stores the contents of the maximal cliques generated.
    @param S is an array of integers, such that Si is the cardinality of Qi, 1≤i<n.
    @param L The list of triples L contains the edges of the clique-tree
        along with their weights; each edge is given by a pair of integers (i, j),
        which are the positions of its endpoints in the array Q
"""

class MarkenzonParameters(object):
    __slots__ = ["num_maximal_cliques", "num_edges", "edges_list", "cardinality_array", "cliques"]

    def __init__(self, l, m, L, S, Q):
        self.num_maximal_cliques = l
        self.num_edges = m
        self.edges_list = L
        self.cardinality_array = S
        self.cliques = Q

    def __str__(self):
        return "#:{}\tedges:{}\tedges_list:{}\tcardinalities:{}\tcliques:{}".format(
            self.num_maximal_cliques, self.num_edges, self.edges_list, self.cardinality_array, self.cliques)

    def __repr__(self):
        return self.__str__()


def merge_cliques(mParameters, upper_bound, rand):
    """
        Merge cliques
    """
    dis_set = UnionFind()
    [dis_set[i] for i in range(mParameters.num_maximal_cliques)]

    while mParameters.edges_list and mParameters.num_edges < upper_bound:
        (a, b, omega), index = rand.next_element(mParameters.edges_list)
        del mParameters.edges_list[index]
        i = dis_set[a]
        j = dis_set[b]
        delta = mParameters.cardinality_array[i] - omega
        Delta = mParameters.cardinality_array[j] - omega
        if mParameters.num_edges + (delta * Delta) <= upper_bound:
            dis_set.union(i, j)
            mParameters.cliques[i] = mParameters.cliques[i] + mParameters.cliques[j]
            mParameters.cardinality_array[i] = Delta + delta + omega
            mParameters.cliques[j] = []
            mParameters.cardinality_array[j] = 0
            mParameters.num_edges += Delta * delta
    


def expand_cliques(n, rand):
    Q, S, L, m, l = [[0]], [0], [], 0, 0
    for u in range(1, n):
        i = rand.next_random(0, l + 1)
        t = rand.next_random(0, S[i] + 1)
        if t == S[i]:
            # expand old clique
            Q[i].append(u)
            S[i] += 1
        else:
            # create new clique
            q_subset = rand.sample(Q[i], t)
            l += 1
            Q.append([u] + q_subset)
            S.append(t + 1)
            if len(Q) != len(S) and len(Q) != l:
                raise Exception("invalid l")

            L.append((i, l, t))
        m += t

    return MarkenzonParameters(l, m, L, S, Q)


if __name__ == '__main__':
    NUM_VERTICES = 15

    randomizer = Randomizer(2 * NUM_VERTICES)
    cliques = expand_cliques(NUM_VERTICES, randomizer)
    print("- Expand cliques:")
    print("\t", cliques)
    # keep a copy of clique tree edges L because merge_cliques is consuming it

    clique_edges = list(cliques.edges_list)

    merge_cliques(cliques, 500, randomizer)
    print("- Merge cliques:")
    print("\t", cliques)
    # print(clique_edges)

    nx_chordal = convert_markenzon_clique_tree_networkx2(cliques.cliques, NUM_VERTICES)
    print("- Stats:")
    print("\t nodes:", len(nx_chordal.nodes()))
    print("\t edges:", len(nx_chordal.edges()))
    nx_export_json([nx_chordal])
