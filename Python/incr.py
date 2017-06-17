from MVA import *
from report_generator import *


def split_edges_k(m_parameters, upper_bound, rand, k=1):
    """
        INCR Algorithm. Split clique tree edges
    """
    dis_set = UnionFind()
    [dis_set[i] for i in range(m_parameters.num_maximal_cliques)]
    loops = 0
    while m_parameters.edges_list and m_parameters.num_edges < upper_bound:
        loops += 1
        (x, y, sep, omega), index = rand.next_element(m_parameters.edges_list)
        i = dis_set[x]
        j = dis_set[y]

        x_sep, y_sep = m_parameters.cliques[i] - set(sep), m_parameters.cliques[j] - set(sep)

        if len(x_sep) == 0 or len(y_sep) == 0:
            raise Exception("Not valid clique tree")
        elif len(x_sep) <= k or len(y_sep) <= k:
            # merge {x,y}
            edges_added = len(x_sep) * len(y_sep)
            dis_set.union(x, y)
            m_parameters.cliques[i].update(m_parameters.cliques[j])
            m_parameters.cardinality_array[i] += len(y_sep)
            m_parameters.cliques[j] = set()
            m_parameters.cardinality_array[j] = 0
            m_parameters.num_edges += edges_added
            m_parameters.num_maximal_cliques -= 1
            # delete old edge
            del m_parameters.edges_list[index]
        elif len(x_sep) <= k:
            # merge {x,z}
            ylen = rand.next_random(1, len(y_sep))
            y_random = list(y_sep)[0:ylen]

            m_parameters.cliques[i].update(y_random)
            m_parameters.cardinality_array[i] += ylen
            # update the edge min-seperator
            m_parameters.edges_list[index] = (x, y, y_random + sep, omega + ylen)

            # update num of edges
            m_parameters.num_edges += ylen * len(x_sep)
        elif len(y_sep) <= k:
            # merge {y,z}
            xlen = rand.next_random(1, len(x_sep))
            x_random = list(x_sep)[0:xlen]

            m_parameters.cliques[j].update(x_random)
            m_parameters.cardinality_array[j] += xlen
            # update the edge min-seperator
            m_parameters.edges_list[index] = (x, y, x_random + sep, omega + xlen)

            # update num of edges
            m_parameters.num_edges += xlen * len(y_sep)
        else:
            # make new z node
            xlen = rand.next_random(1, len(x_sep))
            ylen = rand.next_random(1, len(y_sep))

            x_random = list(x_sep)[0:xlen]
            y_random = list(y_sep)[0:ylen]

            z = set(x_random + y_random + sep)
            edges_added = xlen * ylen
            # print(str(edges_added) + " / " + str(len(x_sep) * len(y_sep)))

            # add node to list
            m_parameters.cliques.append(z)
            m_parameters.cardinality_array.append(len(z))

            # add x-z edge
            m_parameters.edges_list.append((x, len(m_parameters.cliques) - 1, x_random + sep, omega + edges_added))
            # add y-z edge
            m_parameters.edges_list.append((y, len(m_parameters.cliques) - 1, y_random + sep, omega + edges_added))

            m_parameters.num_maximal_cliques += 1
            # update num of edges
            m_parameters.num_edges += edges_added

            # delete old edge
            del m_parameters.edges_list[index]

    return loops


def Run_INCR(num_vertices, edge_density, algorithm_name, k, init_tree=None):
    """
        Initialize and run the MVA algorithm
    """

    edges_bound = edge_density * ((num_vertices * (num_vertices - 1)) / 2)
    k = max(1, k * edges_bound)
    runner = runner_factory(num_vertices, algorithm_name, None, edges_bound=edges_bound, edge_density=edge_density, k=k)

    randomizer = Randomizer(2 * num_vertices, runner["parameters"]["seed"])
    with Timer("t_expand_cliques", runner["Times"]):
        if init_tree:
            p_mva = expand_tree(runner["parameters"]["n"], randomizer)
            print("- Expand tree:")
        else:
            p_mva = expand_cliques(runner["parameters"]["n"], randomizer)
            print("- Expand cliques:")

    print(p_mva)

    with Timer("t_split_edges", runner["Times"]):
        loops = split_edges_k(p_mva, runner["parameters"]["edges_bound"], randomizer, k)
        print("- Split edges:")
    runner["Stats"]["total"] = runner["Times"]["t_split_edges"] + runner["Times"]["t_expand_cliques"]
    runner["Stats"]["loops%"] = loops / edges_bound
    print("    loops:", runner["Stats"]["loops%"])
    print(p_mva)

    return calculate_mva_statistics(p_mva, runner, randomizer, num_vertices)


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

NAME = "INCR_k_1e-5"
if __name__ == '__main__':
    for num in NUM_VERTICES:
        for edge_density in EDGES_DENSITY:
            Runners = []
            for _ in range(10):
                Runners.append(Run_INCR(num, edge_density, NAME, 1e-5, True))

            filename = "Results/" + NAME + "/Run_{}_{}_{}.yml".format(num, edge_density, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))

            with io.open(filename, 'w') as file:
                print_statistics(Runners, file)

            print("Done")
