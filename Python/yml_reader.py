import os
import yaml
import statistics
import sys
from yaml import Loader, Dumper
from clique_tree import *

# with open("test.yml", 'w') as stream:
#     yaml.dump([TreeStatistics(), TreeStatistics()], stream, Dumper=Dumper)


def parse_data(path):
    report_path = path + "/Reports"
    files = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    ]

    os.makedirs(os.path.dirname(report_path + "/"), exist_ok=True)

    for f in files:
        filename = os.path.splitext(f)[0]
        out_path = os.path.join(report_path, filename)
        if os.path.exists(out_path + ".csv"):
            with open(os.path.join(path, f), 'r') as stream:
                yml_data = yaml.load(stream, Loader=Loader)
                acc = process_data(yml_data)
                # print to stdout
                print_data(yml_data, acc)

                # print csv and md format
                formats = ["csv"]
                for frmt in ["csv", "md"]:
                    with open(out_path + "." + frmt, 'w') as out_file:
                        print_data(yml_data, acc, out_file, frmt)


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
                            if not treesection in accumulative[section][t][tree_index]:
                                accumulative[section][t][tree_index][
                                    treesection] = []

                            accumulative[section][t][tree_index][
                                treesection].append(tree[treesection])
    return accumulative


def print_data(run_stats, accumulative, report_file=sys.stdout, frmt="csv"):
    if frmt == "md":
        print_header_md(run_stats, report_file)
    else:
        print_header_csv(run_stats, report_file)

    print("## Time - Output Parameters", file=report_file)
    print_mean_std_vertical(((key, value)
                             for section in accumulative
                             for key, value in accumulative[section].items()
                             if key != "clique_trees"), frmt, report_file)

    if "clique_trees" in accumulative["Output"]:
        print("\n" + "-".center(3, "-"), file=report_file)
        print("## Clique trees", file=report_file)
        for tree in accumulative["Output"]["clique_trees"]:
            print_mean_std_vertical(((o, tree[o])
                                     for o in tree), frmt, report_file)


def print_header_md(run_stats, report_file=sys.stdout):
    print("# Report\n".center(3), file=report_file)
    line1 = "|".join(run_stats["Run"][0]["parameters"])
    line1 += "|Trials"
    line2 = "|".join(("-" for _ in run_stats["Run"][0]["parameters"])) + "|-"
    line3 = "|".join([
        str(run_stats["Run"][0]["parameters"][param])
        for param in run_stats["Run"][0]["parameters"]
    ])
    line3 += "|" + str(len(run_stats["Run"]))

    print("> |" + line1 + "|", file=report_file)
    print("> |" + line2 + "|", file=report_file)
    print("> |" + line3 + "|", file=report_file)
    print("\n" + "-".center(3, "-"), file=report_file)


def print_header_csv(run_stats, report_file=sys.stdout, delimiter=";"):
    print("Report\n", file=report_file)
    delimiter += " "
    print(
        delimiter.join(run_stats["Run"][0]["parameters"]) + delimiter +
        "Trials",
        file=report_file)
    print(
        delimiter.join([
            str(run_stats["Run"][0]["parameters"][param])
            for param in run_stats["Run"][0]["parameters"]
        ]) + delimiter + str(len(run_stats["Run"])),
        file=report_file)
    print("\n" + "-".center(3, "-"), file=report_file)


def print_mean_std_vertical(list_values,
                            frmt="csv",
                            report_file=sys.stdout,
                            delimiter=";"):
    columns = ['', 'mean', 'std']
    prefix = ''
    if frmt == "md":
        delimiter = "|"
        prefix = delimiter
    else:
        delimiter += " "

    print(prefix + delimiter.join(columns) + prefix, file=report_file)
    if frmt == "md":
        print(
            prefix + delimiter.join(("-" for _ in columns)) + prefix,
            file=report_file)

    for key, value in list_values:
        mean = "{:>22.15f}".format(statistics.mean(value))
        stddev = "{:>22.15f}".format(statistics.stdev(value))
        p_key = "**" + key + "**" if frmt == "md" else key
        print(
            prefix + delimiter.join([p_key, mean, stddev]) + prefix,
            file=report_file)


def print_mean_std(list_values,
                   frmt="csv",
                   report_file=sys.stdout,
                   delimiter=";"):
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


if __name__ == '__main__':
    parse_data("Results/MVA")
