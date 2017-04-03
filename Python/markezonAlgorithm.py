from randomizer import *
from numpy import core
import random
from UnionFind import UnionFind

def merge_cliques(num_maximal_cliques, m, L, S, Q, upper_bound):

    dis_set = UnionFind()
    [dis_set[i] for i in range(num_maximal_cliques)]

    while L and m < upper_bound:
        (a, b, omega), index = random_element(L)
        del L[index]
        i = dis_set[a]
        j = dis_set[b]
        delta = S[i] - omega
        Delta = S[j] - omega
        if m + (delta * Delta) <= upper_bound:
            dis_set.union(i, j, i)
            Q[i] = Q[i] + Q[j]
            S[i] = Delta + delta + omega
            Q[j] = []
            S[j] = 0
            m += Delta * delta




def expand_cliques(n):
    Q = [[0]]
    S = [0]
    L = []
    m = 0
    l = 0
    for u in range(1, n):
        i = R.randint(0, l + 1, dtype=core.uint32)
        t = R.randint(0, S[i] + 1, dtype=core.uint32)
        if t == S[i]:
            # expand old clique
            Q[i].append(u)
            S[i] += 1
        else:
            # create new clique
            q_subset = random.sample(Q[i], t)
            l += 1
            Q.append([u] + q_subset)
            S.append(t + 1)
            if len(Q) != len(S) and len(Q) != l:
                raise Exception("invalid l")

            L.append((i, l, t))
        m += t

    return l, m, L, S, Q


cliques = expand_cliques(10)
merge_cliques(*cliques, 100)
print(cliques)
