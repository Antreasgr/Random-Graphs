from MVA import *


class DECRCliqueTree(object):
    """
        Each edge in edge list is a tuple (node 1 index, node 2 index, seperator, length of seperator) ie. index is in cliques array
        Each edge good_edges is a dict with key (x, y) and value the index of node containing edge in clique, 
        where x < y to avoid double storing
    """
    __slots__ = ["num_maximal_cliques", "num_edges", "edges_list", "cardinality_array", "cliques", "good_edges"]

    def __init__(self, l, m, L, S, Q, good_edges):
        self.num_maximal_cliques = l
        self.num_edges = m
        self.edges_list = L
        self.cardinality_array = S
        self.cliques = Q
        self.good_edges = good_edges

    def __str__(self):
        return "\t#: {}\n\tedges: {}\n\tedges_list: {}\n\tcardinalities: {}\n\tcliques: {}\n\tgood edges: {}".format(
            self.num_maximal_cliques, self.num_edges, "Not printed for speed", self.cardinality_array, "Not printed for speed", self.good_edges)

    def __repr__(self):
        return self.__str__()


def init_k_tree(num_vertices, k, rand):
    ct_tree = DECRCliqueTree(1, int(k * (k + 1) / 2), [], [k + 1], [[i for i in range(k + 1)]], dict())

    for u in range(1, num_vertices - k + 1):
        i = rand.next_random(0, len(ct_tree.cliques))
        y = rand.next_random(0, len(ct_tree.cliques[i]))

        sep = [x for ii, x in enumerate(ct_tree.cliques[i]) if ii != y]

        ct_tree.cliques.append(sep + [u + k])
        ct_tree.cardinality_array.append(k + 1)
        ct_tree.num_maximal_cliques += 1
        ct_tree.num_edges += 1

        ct_tree.edges_list.append((i, u, sep, k))

        # remove edges gone bad, this is probably too slow
        for ii in range(len(sep)):
            for jj in range(ii + 1, len(sep)):
                key = (min(sep[ii], sep[jj]), max(sep[ii], sep[jj]))
                if key in ct_tree.good_edges:
                    del ct_tree.good_edges[key]

        # add good edges between u+k node and every other node in clique
        for s in sep:
            ct_tree.good_edges[(s, u + k)] = u

    return ct_tree


def Run_DECR(num_vertices, k, algorithm_name):

    runner = runner_factory(num_vertices, algorithm_name, None, k=k)
    randomizer = Randomizer(3 * num_vertices, runner["Parameters"]["seed"])

    clique_tree = init_k_tree(num, k, randomizer)
    print(clique_tree)
    return calculate_mva_statistics(clique_tree, runner, randomizer, num_vertices)


NUM_VERTICES = [
    50,
    # 100,
    # 500,
    # 1000,
    # 2500,
    # 5000,
    # 10000,  # 50000, 100000, 500000, 1000000
]
EDGES_DENSITY = [0.1, 0.33, 0.5, 0.75, 0.99]
NAME = "DECR"

if __name__ == '__main__':
    mva_data = []
    for num in NUM_VERTICES:
        # for edge_density in EDGES_DENSITY:
        Runners = []
        for _ in range(1):
            Runners.append(Run_DECR(num, 7, NAME))

            # filename = "Results/" + NAME + "/Run_{}_{}_{}.yml".format(num, edge_density, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            # if not os.path.isdir(os.path.dirname(filename)):
            #     os.makedirs(os.path.dirname(filename))

            # with io.open(filename, 'w') as file:
            #     print_statistics(Runners, file)

            print("Done")

            # mva_data.append(merge_runners(Runners))

        # run_reports_data(NAME, mva_data)
