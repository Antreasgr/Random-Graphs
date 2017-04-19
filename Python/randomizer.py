from numpy.random import RandomState
from numpy import core
from timeit import default_timer
import random
import sys

Now = default_timer


class Timer(object):
    __slots__ = ["start", "end", "elapsed", "prefix", "output"]

    def __init__(self, prefix=None, output=True):
        self.prefix = prefix
        self.output = output
        self.start = 0
        self.end = 0
        self.elapsed = 0

    def __enter__(self):
        self.start = Now()
        return self

    def __exit__(self, *args):
        self.end = Now()
        self.elapsed = self.end - self.start
        if self.output:
            print('{0:20} ==> {1:.15f}'.format(self.prefix, self.elapsed))
            sys.stdout.flush()


class Randomizer(object):

    def __init__(self, size, seed=None):
        self.size = size
        self.local_index = 0
        self.Seed = seed
        self.Rstate = RandomState(seed)
        self.np_random = self.Rstate.random_sample(size)

    def next_element(self, array, index=0):
        """
            Get the next random element, and index from given array starting from index to end
        """
        i = self.next_random(index, len(array))
        return array[i], i

    def next_random(self, low, high):
        self.local_index += 1
        if self.local_index >= self.size:
          #  print("Run out of random, reseting")
            self.local_index = 0

        return int(self.np_random[self.local_index] * (high - low) + low)

