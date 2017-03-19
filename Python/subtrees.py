from randomizer import *

class TreeNode:
    """ A class representing a tree node """
    def __init__(self, id):
        self.id = id
        self.Ax = []
        self.Rx = []
        self.cliqueList = []
        # helper attributes for tree form
        self.children = []
        self.parent = None
        self.marked = False

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)


def sub_tree_gen(T, k, i):
    Ti = [random_element(T, 0)[0]]

    # the Ti tree contains this node
    Ti[0].cliqueList.append(i)

    if k <= 1:
        return Ti

    k_i = R.randint(1, 2 * k - 1)
    sy = 0
    for j in range(1, k_i):
        # after sy we have nodes with neighbors outside
        y, yi = random_element(Ti, sy)
        # after y.s in y.Ax there is a neighbor of y outside
        z, zi = random_element(y.Ax, y.s)

        # add z to Ti
        Ti.append(z)
        z.cliqueList.append(i)   # add to the z node of T the {i} number of Ti

        # fix y.Ax
        y.Ax[zi], y.Ax[y.s] = y.Ax[y.s], y.Ax[zi]
        y.s += 1

        # now fix z
        # this is the slow part
        yzi = z.Ax.index(y)
        z.Ax[yzi], z.Ax[z.s] = z.Ax[z.s], z.Ax[yzi]
        z.s += 1

        # if degree of y equals the seperation index on adjacency list, y
        # cannot be selected any more
        if y.s > len(y.Ax) - 1:
            Ti[sy], Ti[yi] = Ti[yi], Ti[sy]
            sy += 1

        if len(z.Ax) == 1:
            Ti[sy], Ti[-1] = Ti[-1], Ti[sy]
            sy += 1

    for node in Ti:
        node.s = 0

    return Ti


def SubTreeGen(T, k, i):
    Ti = [random_element(T, 0)[0]]

    # the Ti tree contains this node
    Ti[0].cliqueList.append(i)

    if k == 1:
        return Ti

    k_i = R.randint(1, 2 * k - 1)
    # seperation index for Ti: all nodes before "sy" have no neigbor in T-Ti
    sy = 0
    for j in range(1, k_i):
        # after sy we have nodes with neighbors outside
        y, yi = random_element(Ti, sy)
        # after y.s in y.Ax there is a neighbor of y outside
        z, zi = random_element(y.Ax, y.s)

        # add z to Ti
        Ti.append(z)
        z.cliqueList.append(i)   # add to the z node of T the {i} number of Ti

        # move z to the first part of y.Ax:
        # swap z with w: the vertex at y.s
        w = y.Ax[y.s]
        # 1. find the position of y in z
        zyi = y.Rx[zi]
        # 2. find the position of y in w
        wyi = y.Rx[y.s]
        # 3. update the positions of y in z.Rx and w.Rx
        z.Rx[zyi] = y.s
        w.Rx[wyi] = zi
        # 4. do the real swap in y.Ax, positions of y.s and zi
        y.Ax[zi], y.Ax[y.s] = y.Ax[y.s], y.Ax[zi]
        # 5. do the swap in y.Rx
        y.Rx[zi], y.Rx[y.s] = y.Rx[y.s], y.Rx[zi]

        # move y to the first part of z.Ax
        # swap y with w: the vertex at z.s
        w = z.Ax[z.s]
        # 1. find the position of z in y
        # used to be zi, now it is y.s
        yzi = y.s
        # 2. find the position of z in w
        wzi = z.Rx[z.s]
        # 3. update the positions of z in y.Rx and w.Rx
        y.Rx[yzi] = z.s
        w.Rx[wzi] = zyi  # the "old" position of y in z
        # 4. do the real swap in z.Ax, positions of z.s and zyi
        z.Ax[zyi], z.Ax[z.s] = z.Ax[z.s], z.Ax[zyi]
        # 5. do the swap in z.Rx
        z.Rx[zyi], z.Rx[z.s] = z.Rx[z.s], z.Rx[zyi]

        # Update y.s and z.s
        y.s += 1
        z.s += 1  # or z.s = 1

        # update every neighbour of z that z is now in Ti, y is among them
        # TODO: not needed (?)
#        for node in z.Ax:
#            ni = node.Ax.index(z)
#            node.Ax[node.s], node.Ax[ni] = node.Ax[ni], node.Ax[node.s]
#            node.s += 1

        # if degree of y equals the seperation index on adjacency list, y
        # cannot be selected any more
        if y.s > len(y.Ax) - 1:
            #            if sy != yi:
            Ti[sy], Ti[yi] = Ti[yi], Ti[sy]
            sy += 1

        # do the same for z:
        if z.s > len(z.Ax) - 1:
            #            if sy != zi:
            Ti[sy], Ti[len(Ti) - 1] = Ti[len(Ti) - 1], Ti[sy]
            sy += 1

        # check if leaf i.e. has degree 1, then it cannot be selected any more
        # TODO: is it needed? (i guess not needed....)
        # OR: perhaps this is only needed and the two previous cases are not needed...
 #       if len(z.Ax) == 1:
 #           if sy != len(Ti) - 1:
 #               Ti[sy], Ti[zi] = Ti[zi], Ti[sy] # why "-1" ?
 #           sy += 1

    for node in Ti:
        node.s = 0

    return Ti
