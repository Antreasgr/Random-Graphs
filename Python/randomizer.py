import numpy as np
import timeit

# initialize global random seed
R = np.random.RandomState(207)
Now = timeit.default_timer


def random_element(array, index=0):
    """
        Get a random element, and index from given array starting from index to end
    """
    i = R.randint(index, len(array), dtype=np.uint32)
    return array[i], i
