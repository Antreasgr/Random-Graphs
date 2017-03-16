from numpy.random import RandomState
from timeit import default_timer

# initialize global random seed
R = RandomState(207)
Now = default_timer

def random_element(array, index=0):
    """
        Get a random element, and index from given array starting from index to end
    """
    # i = R.randint(index, len(array), dtype=np.uint32)
    i = R.randint(index, len(array))
    return array[i], i
