from __future__ import print_function
import sys
import collections


def print_statistics(runners, file=sys.stdout):
    """
        Print all statistics in pretty format
    """
    s_all = {'Parameters': {}, 'Times': {}, 'Verify': {}, 'Stats': {}, 'Output': {}}

    for i_run, run in enumerate(runners):
        if i_run == 0:
            print(u"Run:", file=file)

        for index, section in enumerate(s_all):
            if index == 0:
                print("- " + section + ":", file=file)
            else:
                print("  " + section + ":", file=file)
            for sub in run[section]:
                if sub not in s_all[section]:
                    if sub != "clique_trees":
                        value = run[section][sub]
                        if isinstance(value, float):
                            print('    {0:35} {1:>22.15f}'.format(sub + ":", value), file=file)
                        else:
                            print('    {0:35} {1!s:>22}'.format(sub + ":", value), file=file)
                    else:
                        print('    ' + sub + ":", file=file)
                        for ctree in run[section][sub]:
                            for i_ctree, c_value in enumerate(ctree.__slots__):
                                attr_value = getattr(ctree, c_value)
                                if i_ctree == 0:
                                    print('    - {0:30} {1!s:>22}'.format(c_value + ':', attr_value), file=file)
                                elif isinstance(attr_value, collections.Counter):
                                    print('      {0:30} {1!s:>22}'.format(c_value + ':', '!!python/object/apply:collections.Counter'), file=file)
                                    print('      - {0:}'.format(dict.__repr__(attr_value)), file=file)
                                else:
                                    print('      {0:30} {1!s:>22}'.format(c_value + ':', getattr(ctree, c_value)), file=file)


def runner_factory(num_of_vertices, algorithm="", seed=None, **kwargs):
    """
        Creates a new runner object to initiliaze the algorithm
    """
    run_dict = {
        "Parameters": {
            "n": num_of_vertices,
            'seed': seed,
            'Algorithm': algorithm
        },
        'Times': {},
        'Verify': {},
        'Stats': {},
        'Graphs': {},
        'Output': {}
    }

    run_dict["Parameters"].update(kwargs)

    return run_dict


def merge_runners(runners):
    merged_runner = runner_factory(0)
    merged_runner["Parameters"] = runners[0]["Parameters"]

    for section in ["Times", "Stats", "Output"]:
        for key in runners[0][section].keys():
            if key != 'clique_trees':
                merged_runner[section][key] = [r[section][key] for r in runners]
            else:
                # convert TreeStatistics to dict to merge
                dicts = [r[section][key][-1].__dict__ for r in runners]
                merged_runner[section][key] = [{}]
                for tree_section in dicts[0].keys():
                    merged_runner[section][key][-1][tree_section] = [d[tree_section] for d in dicts]

    return merged_runner
