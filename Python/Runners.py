# from __future__ import print_function
import sys

def print_statistics(runners, file=sys.stdout):
    """
        Print all statistics in pretty format
    """
    s_all = {'parameters': {}, 'Times': {}, 'Verify': {}, 'Stats': {}, 'Output': {}}

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
                                if i_ctree == 0:
                                    print('    - {0:30} {1!s:>22}'.format(c_value + ':', getattr(ctree, c_value)), file=file)
                                else:
                                    print('      {0:30} {1!s:>22}'.format(c_value + ':', getattr(ctree, c_value)), file=file)


def runner_factory(num_of_vertices, parameter_k, algorithm="", seed=None, **kwargs):
    """
        Creates a new runner object to initiliaze the algorithm
    """
    run_dict = {
        "parameters": {
            "n": num_of_vertices,
            "k": parameter_k,
            'seed': seed,
            'Algorithm': algorithm
        },
        'Times': {},
        'Verify': {},
        'Stats': {},
        'Graphs': {},
        'Output': {}
    }

    run_dict["parameters"].update(kwargs)

    return run_dict
