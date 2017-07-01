from MVA import *


class DECRCliqueTree(object):
    """
        Each edge in edge list is a tuple (node 1, node 2, seperator, length of seperator) ie. node is pointer to CliqueNode
        `edges_list` and `cardinality_array` are only for running mva_stats. MAYBE remove and write another dfs stats function
        Each edge good_edges is a dict 
    """
    __slots__ = ["num_maximal_cliques", "num_edges", "edges_list", "cardinality_array", "cliques", "good_edges"]

    class CliqueNode(object):
        """
            https://wiki.python.org/moin/TimeComplexity for sets
            index: is the index in the parent clique tree list. Must be UNIQUE and HASHABLE as it is used as key in neighbours dict
            vertex_set: is the set with the vertices contained in this clique tree node
            neighbours: is the dict of edges attached to this node. Each edge is a tuple (i, j, sep, len(sep))
        """
        __slots__ = ['index', 'vertex_set', 'neighbours']

        def __init__(self, index):
            self.index = index
            self.vertex_set = set()
            self.neighbours = {}

        def add_edge(self, node, edge):
            self.neighbours[node] = edge

        def __str__(self):
            return "\tindex: {}\n\tvertex_set: {}\n\tneighbours: {}".format(self.index, self.vertex_set, "")

        def __repr__(self):
            return self.__str__()

        def __hash__(self):
            return hash(self.index)

    def __init__(self):
        self.num_maximal_cliques = 0
        self.num_edges = 0
        self.edges_list = []
        self.cardinality_array = []
        self.cliques = []
        self.good_edges = dict()

    def add_node(self, vertex_set):
        new_node = DECRCliqueTree.CliqueNode(len(self.cliques))
        new_node.vertex_set = vertex_set
        self.cliques.append(new_node)
        self.cardinality_array.append(len(vertex_set))
        self.num_maximal_cliques += 1
        return new_node

    def add_edge(self, node1, node2, sep, weight):
        edge = (node1, node2, sep, weight)
        node1.neighbours[node2] = edge
        node2.neighbours[node1] = edge
        self.edges_list.append(edge)
        return edge

    def delete_node(self, node):
        self.cliques[node.index] = None
        self.cardinality_array[node.index] = 0
        self.num_maximal_cliques -= 1
        del node

    def __str__(self):
        return "\t#: {}\n\tedges: {}\n\tedges_list: {}\n\tcardinalities: {}\n\tcliques: {}\n\tgood edges: {}".format(
            self.num_maximal_cliques, self.num_edges, "Not printed for speed", self.cardinality_array, "Not printed for speed",
            "Not printed for speed")

    def __repr__(self):
        return self.__str__()

    def toJson(self, stream=None):
        d = {"directed": False, "multigraph": False, "graph": {"graph_type": "tree"}, "nodes": [], "links": []}
        visited = set()
        all_cliques = [c for c in self.cliques if c != None]
        for i, clique in enumerate(all_cliques):
            if clique is None:
                continue
            d["nodes"].append({"id": clique.index, "clique_list": ",".join([str(s) for s in clique.vertex_set])})
            for n in clique.neighbours.keys():
                if n not in visited:
                    visited.add(n)
                    d["links"].append({"source": i, "target": all_cliques.index(n)})
            visited.add(clique)

        if stream != None:
            json.dump(d, stream)
        else:
            return json.dumps(d)


def delete_edge(clique_tree, clique_node, u, v, rand):
    """
        Deletes the edge from u to v contained in clique tree Node clique_node (x)
    """
    kx_with_u = clique_node.vertex_set - set([v])  # O(len(vertex_set))
    kx_with_v = clique_node.vertex_set - set([u])  # O(len(vertex_set))

    x_1, x_2 = None, None
    # check if soon to be created nodes are maximal
    # if not there is no reason to create them
    is_subset_u = False
    is_subset_v = False
    for y in clique_node.neighbours.keys():
        if not is_subset_u and kx_with_u.issubset([y]):
            is_subset_u = True
            x_1 = y

        if not is_subset_v and kx_with_v.issubset([y]):
            is_subset_v = True
            x_2 = y

        if not is_subset_u and not is_subset_v:
            break

    if not is_subset_u:
        x_1 = clique_tree.add_node(kx_with_u)

    if not is_subset_v:
        x_2 = clique_tree.add_node(kx_with_v)

    for y in clique_node.neighbours.keys():
        if u in y.vertex_set:
            # y \in N_u
            # add {x1, y} i.e. modify {x, y}
            old_edge = clique_node.neighbours[y]
            x_1.neighbours[y] = (x_1, y, old_edge[2], old_edge[3])
            y.neighbours[x_1] = (x_1, y, old_edge[2], old_edge[3])
            del y.neighbours[clique_node]
        elif v in y.vertex_set:
            # y \in N_v
            # add {x2, y}
            old_edge = clique_node.neighbours[y]
            x_2.neighbours[y] = (x_2, y, old_edge[2], old_edge[3])
            y.neighbours[x_2] = (x_2, y, old_edge[2], old_edge[3])
            del y.neighbours[clique_node]
        else:
            # y \notin N_uv
            # add {x1 or x2, y}
            if rand.random() < 0.5:
                old_edge = clique_node.neighbours[y]
                x_1.neighbours[y] = (x_1, y, old_edge[2], old_edge[3])
                y.neighbours[x_1] = (x_1, y, old_edge[2], old_edge[3])
            else:
                old_edge = clique_node.neighbours[y]
                x_2.neighbours[y] = (x_2, y, old_edge[2], old_edge[3])
                y.neighbours[x_2] = (x_2, y, old_edge[2], old_edge[3])
            del y.neighbours[clique_node]

    # add-edge x1-x2, w = k - 2
    sep = clique_node.vertex_set - set([u, v])
    clique_tree.add_edge(x_1, x_2, sep, len(sep))
    clique_tree.delete_node(clique_node)
    clique_tree.num_edges -= 1

    # edges gone bad
    vertex_list = list(clique_node.vertex_set)
    for ii in range(len(vertex_list)):
        for jj in range(ii + 1, len(vertex_list)):
            key = (min(vertex_list[ii], vertex_list[jj]), max(vertex_list[ii], vertex_list[jj]))
            if ii != u and ii != v and jj != u and jj != v:
                if key in clique_tree.good_edges:
                    # remove from list is slow
                    clique_tree.good_edges[key].difference_update([clique_node])
                    clique_tree.good_edges[key].update([x_1, x_2])
            if ii != v and jj != v:
                clique_tree.good_edges[key].difference_update([clique_node])
                clique_tree.good_edges[key].update([x_1])
            if ii != u and jj != u:
                clique_tree.good_edges[key].difference_update([clique_node])
                clique_tree.good_edges[key].update([x_2])

    # remove u, v edge
    clique_tree.good_edges[(min(u, v), max(u, v))].difference_update([clique_node])


def init_k_tree(num_vertices, k, rand):
    ct_tree = DECRCliqueTree()
    root = ct_tree.add_node(set([i for i in range(k + 1)]))
    ct_tree.num_edges = int(k * (k + 1) / 2)

    vertex_list = list(root.vertex_set)
    for ii in range(len(vertex_list)):
        for jj in range(ii + 1, len(vertex_list)):
            key = (min(vertex_list[ii], vertex_list[jj]), max(vertex_list[ii], vertex_list[jj]))
            if key not in ct_tree.good_edges:
                ct_tree.good_edges[key] = set([root])

    for u in range(1, num_vertices - k + 1):
        i = rand.next_random(0, len(ct_tree.cliques))
        y = rand.next_random(0, len(ct_tree.cliques[i].vertex_set))

        sep = [x for ii, x in enumerate(ct_tree.cliques[i].vertex_set) if ii != y]

        new_node = ct_tree.add_node(set(sep + [u + k]))
        ct_tree.num_edges += 1

        ct_tree.add_edge(ct_tree.cliques[i], new_node, sep, k)

        # remove edges gone bad, this is probably too slow
        for ii in range(len(sep)):
            for jj in range(ii + 1, len(sep)):
                key = (min(sep[ii], sep[jj]), max(sep[ii], sep[jj]))
                ct_tree.good_edges[key].update([new_node])

        # add good edges between u+k node and every other node in clique
        for s in sep:
            key = (s, u + k)
            if key not in ct_tree.good_edges:
                ct_tree.good_edges[key] = set()

            ct_tree.good_edges[key].update([new_node])

    return ct_tree


# def find_good_edges(clique_tree):
#     visited = set()
#     for node in clique_tree.cliques:
#         if node not in visited:
#             visited.add(node)
#             good_uvs = set(node.vertex_set)
#             for neigh, edge in node.neighbours.items():
#                 if neigh not in visited:
#                     visited.add(neigh)
#                     good_uvs.difference_update(edge[2])
#             print(good_uvs)


def get_next_edge(clique_tree):
    for key in clique_tree.good_edges.keys():
        if len(clique_tree.good_edges[key]) == 1:
            return key

    return None


def DECR(clique_tree, rand, stream):
    r_key = get_next_edge(clique_tree)

    while r_key:
        r_node = list(clique_tree.good_edges[r_key])[0]
        print("Deleting edge:", r_key, "in node:", r_node)
        delete_edge(clique_tree, r_node, r_key[0], r_key[1], rand)
        # stream.write(", ")
        # clique_tree.toJson(stream)
        r_key = get_next_edge(clique_tree)


def Run_DECR(num_vertices, k, algorithm_name):

    runner = runner_factory(num_vertices, algorithm_name, 166, k=k)
    randomizer = Randomizer(3 * num_vertices, runner["Parameters"]["seed"])

    clique_tree = init_k_tree(num, k, randomizer)
    with open("graph.json", "w") as stream:
        stream.write("[")
        clique_tree.toJson(stream)

        DECR(clique_tree, randomizer, stream)

        stream.write("]")

    # find_good_edges(clique_tree)

    # print(clique_tree)
    # return calculate_mva_statistics(clique_tree, runner, randomizer, num_vertices)


NUM_VERTICES = [
    5,
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
            Runners.append(Run_DECR(num, 2, NAME))

            # filename = "Results/" + NAME + "/Run_{}_{}_{}.yml".format(num, edge_density, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            # if not os.path.isdir(os.path.dirname(filename)):
            #     os.makedirs(os.path.dirname(filename))

            # with io.open(filename, 'w') as file:
            #     print_statistics(Runners, file)

            print("Done")

            # mva_data.append(merge_runners(Runners))

        # run_reports_data(NAME, mva_data)
