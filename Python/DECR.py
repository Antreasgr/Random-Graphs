from MVA import *
from math import sqrt, ceil


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

    def calculate_tree_edges(self):
        self.edges_list = []
        visited = set()
        all_cliques = [c for c in self.cliques if c != None]
        for i, clique in enumerate(all_cliques):
            if clique is None:
                continue
            for n in clique.neighbours.keys():
                if n not in visited:
                    self.edges_list.append(n.neighbours[clique])
            visited.add(clique)

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
        if not is_subset_u and kx_with_u.issubset(y.vertex_set):
            is_subset_u = True
            x_1 = y

        if not is_subset_v and kx_with_v.issubset(y.vertex_set):
            is_subset_v = True
            x_2 = y

        if is_subset_u and is_subset_v:
            break

    if not is_subset_u:
        x_1 = clique_tree.add_node(kx_with_u)

    if not is_subset_v:
        x_2 = clique_tree.add_node(kx_with_v)

    for y in clique_node.neighbours.keys():
        add_x1_y = y != x_1
        add_x2_y = y != x_2
        if u in y.vertex_set:
            # y \in N_u add {x1, y} i.e. modify {x, y}
            add_x1_y &= True
        elif v in y.vertex_set:
            # y \in N_v add {x2, y}
            add_x2_y &= True
        else:
            # y \notin N_uv  add {x1 or x2, y}
            if rand.random() < 0.5:
                add_x1_y &= True
            else:
                add_x2_y &= True

        old_edge = clique_node.neighbours[y]

        if add_x1_y:
            x_1.neighbours[y] = (x_1, y, old_edge[2], old_edge[3])
            y.neighbours[x_1] = (x_1, y, old_edge[2], old_edge[3])
        elif add_x2_y:
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
            if key[0] != u and key[0] != v and key[1] != u and key[1] != v:
                if key in clique_tree.good_edges:
                    clique_tree.good_edges[key].difference_update([clique_node])
                    clique_tree.good_edges[key].update([x_1, x_2])
            if key[0] != v and key[1] != v:
                clique_tree.good_edges[key].difference_update([clique_node])
                clique_tree.good_edges[key].update([x_1])
            if key[0] != u and key[1] != u:
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

    for u in range(1, num_vertices - k):
        i = rand.next_random(0, len(ct_tree.cliques))
        y = rand.next_random(0, len(ct_tree.cliques[i].vertex_set))

        sep = [x for ii, x in enumerate(ct_tree.cliques[i].vertex_set) if ii != y]

        new_node = ct_tree.add_node(set(sep + [u + k]))
        ct_tree.num_edges += k

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


def get_next_edge(clique_tree):
    for key in clique_tree.good_edges.keys():
        if len(clique_tree.good_edges[key]) == 1:
            return key

    return None


def DECR(clique_tree, edges_bound, rand, stream):
    r_key = get_next_edge(clique_tree)

    while r_key and edges_bound < clique_tree.num_edges:
        r_node = list(clique_tree.good_edges[r_key])[0]
        # print("Deleting edge:", r_key, "in node:", r_node)
        delete_edge(clique_tree, r_node, r_key[0], r_key[1], rand)
        r_key = get_next_edge(clique_tree)

        if stream:
            stream.write(", ")
            clique_tree.toJson(stream)


def Run_DECR(num_vertices, edge_density, algorithm_name):
    edges_bound = int(edge_density * (num_vertices * (num_vertices - 1) / 2))
    k = 1 / 2 * (2 * num_vertices - 1 - sqrt(((2 * num_vertices - 1) * (2 * num_vertices - 1)) - (8 * edges_bound)))
    k = int(ceil(k))
    k_edges = (num_vertices - k - 1) * k + (k * (k + 1) / 2)

    if k_edges < edges_bound:
        raise Exception("Wrong k autodetected, too few edges")

    runner = runner_factory(
        num_vertices, algorithm_name, None, edges_bound=edges_bound, edge_density=edge_density, k=k, edges_removed=int(k_edges - edges_bound))
    randomizer = Randomizer(2 * num_vertices, runner["Parameters"]["seed"])

    with Timer("t_init_k_tree", runner["Times"]):
        clique_tree = init_k_tree(num, k, randomizer)

    with Timer("t_edges_remove", runner["Times"]):
        DECR(clique_tree, edges_bound, randomizer, None)

    runner["Stats"]["total"] = runner["Times"]["t_init_k_tree"] + runner["Times"]["t_edges_remove"]
    # with open("graph.json", "w") as stream:
    #     stream.write("[")
    #     clique_tree.toJson(stream)
    #     try:
    #         DECR(clique_tree, edges_bound, randomizer, stream)
    #         clique_tree.calculate_tree_edges()
    #     finally:
    #         stream.write("]")

    # print(clique_tree)

    # convert to MVA form for statistics calculation
    with Timer("t_stats", runner["Times"]):
        clique_tree.calculate_tree_edges()
        stats = calculate_mva_statistics(clique_tree, runner, randomizer, num_vertices)
    return stats


NUM_VERTICES = [
    50,
    100,
    500,
    1000,
    2500,
    5000,
    10000,  # 50000, 100000, 500000, 1000000
]
EDGES_DENSITY = [0.1, 0.33, 0.5, 0.75, 0.99]
NAME = "DECR"

if __name__ == '__main__':
    mva_data = []
    for num in NUM_VERTICES:
        for ed in EDGES_DENSITY:
            Runners = []
            for _ in range(10):
                Runners.append(Run_DECR(num, ed, NAME))

                # filename = "Results/" + NAME + "/Run_{}_{}_{}.yml".format(num, edge_density, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

                # if not os.path.isdir(os.path.dirname(filename)):
                #     os.makedirs(os.path.dirname(filename))

                # with io.open(filename, 'w') as file:
                #     print_statistics(Runners, file)

                print("Done")

            mva_data.append(merge_runners(Runners))

    run_reports_data(NAME, mva_data)
