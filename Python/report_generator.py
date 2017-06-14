import os
import statistics
import sys
import csv
import collections
import yaml
from yaml import Loader, Dumper
# from ruamel import yaml
from clique_tree import *


def parse_data(path, output=True):
    all_data = []
    report_path = path + "/Reports"
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    os.makedirs(os.path.dirname(report_path + "/"), exist_ok=True)

    for file in files:
        filename = os.path.splitext(file)[0]
        out_path = os.path.join(report_path, filename)
        if not output or not os.path.exists(out_path + ".csv"):
            print(filename)
            with open(os.path.join(path, file), 'r') as stream:
                yml_data = yaml.load(stream)
                acc = process_data(yml_data)
                all_data.append(acc)
                # print to stdout
                # print_data(yml_data, acc)

                # print csv and md format
                if output:
                    for frmt in ["csv", "md"]:
                        with open(out_path + "." + frmt, 'w') as out_file:
                            print_data(yml_data, acc, out_file, frmt)

    return all_data


def process_data(run_stats):
    accumulative = {"Times": {}, "Stats": {}, "Output": {}}
    for run in run_stats["Run"]:
        for section in accumulative:
            for t in run[section]:
                if not t in accumulative[section]:
                    accumulative[section][t] = []
                if t != "clique_trees":
                    accumulative[section][t].append(run[section][t])
                else:
                    for tree_index, tree in enumerate(run[section][t]):
                        while len(accumulative[section][t]) < tree_index + 1:
                            accumulative[section][t].append({})
                        for treesection in tree:
                            # if treesection == "max_clique_edge_distribution":
                            #     tree[treesection] = (tree["max_size"] * (tree["max_size"] - 1) / 2) / run["Output"]["edges"]

                            if not treesection in accumulative[section][t][tree_index]:
                                accumulative[section][t][tree_index][treesection] = []

                            accumulative[section][t][tree_index][treesection].append(tree[treesection])


    accumulative["Parameters"] = run_stats["Run"][0]["parameters"]

    return accumulative


def print_data(run_stats, accumulative, report_file=sys.stdout, frmt="csv"):
    if frmt == "md":
        print_header_md(run_stats, report_file)
    else:
        print_header_csv(run_stats, report_file)

    print("## Time - Output Parameters", file=report_file)
    print_mean_std_vertical(((key, value) for section in accumulative for key, value in accumulative[section].items()
                             if key != "clique_trees"), frmt, report_file)

    if "clique_trees" in accumulative["Output"]:
        print("\n" + "-".center(3, "-"), file=report_file)
        print("## Clique trees", file=report_file)
        for tree in accumulative["Output"]["clique_trees"]:
            print('\n', file=report_file)
            print_mean_std_vertical(((o, tree[o]) for o in tree), frmt, report_file)


def print_header_md(run_stats, report_file=sys.stdout):
    print("# Report\n".center(3), file=report_file)
    line1 = "|".join(run_stats["Run"][0]["parameters"])
    line1 += "|Trials"
    line2 = "|".join(("-" for _ in run_stats["Run"][0]["parameters"])) + "|-"
    line3 = "|".join([str(run_stats["Run"][0]["parameters"][param]) for param in run_stats["Run"][0]["parameters"]])
    line3 += "|" + str(len(run_stats["Run"]))

    print("> |" + line1 + "|", file=report_file)
    print("> |" + line2 + "|", file=report_file)
    print("> |" + line3 + "|", file=report_file)
    print("\n" + "-".center(3, "-"), file=report_file)


def print_header_csv(run_stats, report_file=sys.stdout, delimiter=";"):
    print("Report\n", file=report_file)
    delimiter += " "
    print(delimiter.join(run_stats["Run"][0]["parameters"]) + delimiter + "Trials", file=report_file)
    print(
        delimiter.join([str(run_stats["Run"][0]["parameters"][param])
                        for param in run_stats["Run"][0]["parameters"]]) + delimiter + str(len(run_stats["Run"])),
        file=report_file)
    print("\n" + "-".center(3, "-"), file=report_file)


def print_mean_std_vertical(list_values, frmt="csv", report_file=sys.stdout, delimiter=";"):
    columns = ['', 'mean', 'std']
    prefix = ''
    if frmt == "md":
        delimiter = "|"
        prefix = delimiter
    else:
        delimiter += " "

    print(prefix + delimiter.join(columns) + prefix, file=report_file)
    if frmt == "md":
        print(prefix + delimiter.join(("-" for _ in columns)) + prefix, file=report_file)

    for key, value in list_values:
        mean = "{:>22.15f}".format(statistics.mean(value))
        stddev = "{:>22.15f}".format(statistics.stdev(value))
        p_key = "**" + key + "**" if frmt == "md" else key
        print(prefix + delimiter.join([p_key, mean, stddev]) + prefix, file=report_file)


def print_mean_std(list_values, frmt="csv", report_file=sys.stdout, delimiter=";"):
    lines = ['', '', 'mean', 'std']
    if frmt == "md":
        delimiter = "|"
        lines = [delimiter + l for l in lines]
        lines[1] += "-"
    else:
        delimiter += " "

    for key, value in list_values:
        lines[0] += delimiter + str(key)
        lines[1] += delimiter + "-"
        lines[2] += delimiter + str(statistics.mean(value))
        lines[3] += delimiter + str(statistics.stdev(value))

    if frmt == "md":
        lines = [l + delimiter for l in lines]

    for i, line in enumerate(lines):
        if i != 1 or frmt == "md":
            print(line, file=report_file)


def sort_data_fn(a):
    par = a["Parameters"]
    k = par["k"] if "k" in par else par["edge_density"]
    return par["Algorithm"], par["n"], k


def generate_accumulative_report(all_data_filename, name):
    with open(all_data_filename, 'r') as stream:
        all_data = yaml.load(stream, Loader=Loader)

    mva_data = [d for d in all_data if d["Parameters"]["Algorithm"] == name]
    shet_data = [] # [d for d in all_data if d["Parameters"]["Algorithm"] == "SHET"]

    del all_data
    for d in shet_data:
        if "edge_density" in d["Output"]:
            d["Stats"]["edge_density"] = d["Output"]["edge_density"]

    mva_data.sort(key=sort_data_fn)
    shet_data.sort(key=sort_data_fn)

    lines = []

    for i, datum in enumerate(mva_data):
        ct = datum["Output"]["clique_trees"][0]
        if i == 0:
            header_lines, columns_stats, columns_times, columns_ct = accumulative_header(["n", "e.d."], datum, ct)
            lines.extend(header_lines)

        other_lines = accumulative_line(i, datum, ct, columns_stats, columns_times, columns_ct)
        lines.append(other_lines)

    for i, datum in enumerate(shet_data):
        ct = datum["Output"]["clique_trees"][1]
        if i == 0:
            header_lines, columns_stats, columns_times, columns_ct = accumulative_header(["n", "k/n."], datum, ct)
            lines.extend(header_lines)

        other_lines = accumulative_line(i, datum, ct, columns_stats, columns_times, columns_ct)
        lines.append(other_lines)

    return lines


def accumulative_header(parameters, datum, ct):
    def index_of(order_list, value):
        try:
            return order_list.index(value)
        except ValueError:
            return -1

    columns_stats = [o for o in datum["Stats"]]
    columns_times = [o for o in datum["Times"]]

    orderby = TreeStatistics.__slots__
    columns_ct = [o for o in ct if not o.startswith("distribution")]
    columns_ct.sort(key=lambda h: index_of(orderby, h))

    l_1 = [datum["Parameters"]["Algorithm"]]
    l_11 = ["" for _ in parameters] + ["Stats"] + ["" for _ in range(2 * len(columns_stats) - 1)]
    l_11 += ["Times"] + ["" for _ in range(2 * len(columns_times) - 1)]
    l_11 += ["Clique Tree"] + ["" for _ in range(2 * len(columns_ct) - 1)]

    l_2 = parameters
    l_2 += [header if not twice else "" for header in columns_stats for twice in range(2)]
    l_2 += [header if not twice else "" for header in columns_times for twice in range(2)]
    l_2 += [header if not twice else "" for header in columns_ct for twice in range(2)]

    l_3 = ["", ""]
    l_3 += [twice for header in columns_stats for twice in ["mean", "std"]]
    l_3 += [twice for header in columns_times for twice in ["mean", "std"]]
    l_3 += [twice for header in columns_ct for twice in ["mean", "std"]]

    return [l_1, l_11, l_2, l_3], columns_stats, columns_times, columns_ct


def accumulative_line(i, datum, ct, columns_stats, columns_times, columns_ct):
    par = datum["Parameters"]
    stats = datum["Stats"]
    times = datum["Times"]

    l = [par["n"], par["edge_density"] if "edge_density" in par else float(par["k"]) / par["n"]]

    l.extend([fn(stats[k]) if k in stats else "" for k in columns_stats for fn in [statistics.mean, statistics.stdev]])

    l.extend([fn(times[k]) if k in times else "" for k in columns_times for fn in [statistics.mean, statistics.stdev]])

    all_values = (ct[k] for k in columns_ct if len(ct[k]) and not isinstance(ct[k][0], dict))
    sanitize_values = []
    for array_of_values in all_values:
        col = [vv for vv in array_of_values if not isinstance(vv, str)]
        if col:
            sanitize_values.append(col)

    if sanitize_values:
        l.extend([fn(v) for v in sanitize_values for fn in [statistics.mean, statistics.stdev]])
    else:
        l.extend([0, 0])

    return l


def localize_floats(row):
    return [str(el).replace('.', ',') if isinstance(el, float) else el for el in row]


NAME = "INCR1.x"
if __name__ == '__main__':
    mva_data = parse_data("Results/" + NAME, False)
    shet_data = []# parse_data("Results/" + NAME, False)

    print("Done...")
    if mva_data or shet_data:
        with open(os.path.join("Results", "all_data_" + NAME + ".yml"), 'w') as stream:
            yaml.dump(mva_data + shet_data, stream)

    all_lines = generate_accumulative_report(os.path.join("Results", "all_data_" + NAME + ".yml"), NAME)
    print(all_lines)
    if all_lines:
        with open(os.path.join("Results", "final_report_" + NAME + ".csv"), 'w') as stream:
            writer = csv.writer(stream, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerows((localize_floats(row) for row in all_lines))
