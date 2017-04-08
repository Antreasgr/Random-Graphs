from numpy.random import RandomState
from numpy import core
from timeit import default_timer
import random

# initialize global random seed
Now = default_timer


class Randomizer(object):

    def __init__(self, size, seed=None):
        self.size = size
        self.local_index = 0
        self.RState = RandomState(seed)
        self.np_random = self.RState.random_sample(size)

    def next_element(self, array, index=0):
        """
            Get the next random element, and index from given array starting from index to end
        """
        i = self.next_random(index, len(array))
        return array[i], i

    def next_random(self, low, high):
        if self.local_index >= self.size:
            self.local_index = 0

        return int(self.np_random[self.local_index] * (high - low) + low)


def random_element(array, index=0):
    """
        Get a random element, and index from given array starting from index to end
    """
    i = R.randint(index, len(array), dtype=core.uint32)
    return array[i], i
