from numpy.random import RandomState
from numpy import core
from timeit import default_timer

# initialize global random seed
R = RandomState()
Now = default_timer


def random_element(array, index=0):
    """
        Get a random element, and index from given array starting from index to end
    """
    i = R.randint(index, len(array), dtype=core.uint32)
    return array[i], i
