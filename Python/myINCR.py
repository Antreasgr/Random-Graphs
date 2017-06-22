import os

import networkx as nx
from numpy.random import RandomState

from clique_tree import *
from nx_converters import *
from randomizer import *
from subtrees import *
from datetime import datetime
from Runners import *

import yaml
from yaml import Loader, Dumper

"""
    EDGE INCREMENTAL: Create a random chordal graph
"""

class TreeEdge(object):
    """
        A class representing an edge of a clique tree
    """
    __slots__ = ('uid', 'xnode', 'ynode', 'common')

    def __init__(self, uid):
        self.uid = uid
        self.xnode = None
        self.ynode = None
        self.common = []

    def __str__(self):
        return str(self.uid)

    def __repr__(self):
        return str(self.uid)


def init_generation(n_vert, rand):
    """
        Creates a random clique tree on n nodes (edgeless graph)
        and creates the edge list of the tree
    """
    CT = [TreeNode(0)]
    CT[0].cliqueList.append(0)
    Elist = [TreeEdge(0)]        
    parent = CT[0]
    newnode = TreeNode(1)
    newnode.cliqueList.append(1)
    newnode.Ax.append(parent)
    parent.Ax.append(newnode)
    parent.Dx[newnode] = len(parent.Ax) - 1
    newnode.Dx[parent] = len(newnode.Ax) - 1
#    parent.children.append(newnode)
#    newnode.parent = parent
    CT.append(newnode)    
    Elist[0].xnode = parent
    Elist[0].ynode = newnode
    for uid in range(1, n_vert - 1):
        parent, pi = rand.next_element(CT)
        newnode = TreeNode(uid + 1)
        newnode.cliqueList.append(uid+1)

        # update the adjacency lists
        newnode.Ax.append(parent)
        parent.Ax.append(newnode)

        parent.Dx[newnode] = len(parent.Ax) - 1
        newnode.Dx[parent] = len(newnode.Ax) - 1

        # update helper, children list, parent pointer
#        parent.children.append(newnode)
#        newnode.parent = parent

        newedge = TreeEdge(uid)
        newedge.xnode = parent
        newedge.ynode = newnode

        # append to tree
        Elist.append(newedge)
        CT.append(newnode)

    return CT, Elist

def update_edges_onex_oney(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    a = xlist[0]
    b = ylist[0]
    # we have only one edge to add, put b in x:
    x.cliqueList.append(b)
    # merge X and Y and keep it into X
    x.Ax.remove(y)
    for z in y.Ax:
        if z.uid !=x.uid :
            x.Ax.append(z)
            z.Ax.append(x)
            z.Ax.remove(y)
            ## do something with the edge "xz"//replace yz by "xz"
            for e in EL:
                if (e.xnode == y and e.ynode == z) or (e.xnode == z and e.ynode == y):
                    e.xnode = x
                    e.ynode = z
                    e.common = e.common
                    break
    ## and delete Y and the edge X-Y: 
    #del CT[ect.ypos]
    CT.remove(ect.ynode)
    free_nodes.append(ect.ynode)
    #del EL[ei] 
    EL.remove(ect)
    free_edges.append(ect)    
    return 1        

def update_edges_onex_bigy_noroomy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    a = xlist[0]
    b = ylist[0]
    # we only move b in x and update ect.common:
    x.cliqueList.append(b)
    ect.common.append(b)           
    return 1

def update_edges_onex_bigy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    # add part of ylist to X: 
    # need to update: x.cliqueList, ect.common, real_m       
    i = rand.next_random(0, len(ylist)-1)  
    for j in range(0,i+1):
        x.cliqueList.append(ylist[j])
        ect.common.append(ylist[j])
    return i+1

def update_edges_bigx_oney_noroomx(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    #print("bigx-oney-noroomx",xlist,ylist)    
    a = xlist[0]
    # put a in Y and update edge X-Y
    y.cliqueList.append(a)
    ect.common.append(a)
    return 1 

def update_edges_bigx_oney(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    #print("bigx-oney",xlist,ylist)
    # we have place in X to send to Y
    i = rand.next_random(0,len(xlist)-1) 
    for j in range(0,i+1):
        y.cliqueList.append(xlist[j])
        ect.common.append(xlist[j])
    return i+1

def update_edges_bigx_bigy_noplaces(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    #print("bigx-bigy-noplaces",xlist,ylist)
    # there is no place in both (we could have checked one by one...)    
    # now we need a new Z node: X - Z - Y
    a = xlist[0]
    b = ylist[0]
    # we add only edge a-b
    newnode = TreeNode(free_nodes.pop(0))  
    if len(ect.common)>0:    
        newnode.cliqueList.extend(ect.common)  
    newnode.cliqueList.append(a)
    newnode.cliqueList.append(b)
    # edge: X - newnode
    newnode.parent = x 
    newnode.Ax.append(x)
    x.Ax.remove(y)
    x.Ax.append(newnode)
    # edge: newnode - Y               
    y.parent = newnode
    newnode.Ax.append(y)
    y.Ax.remove(x)
    y.Ax.append(newnode)
    CT.append(newnode)
    # about the tree edges:
    # ect (X-Y) now: X-newnode
    EL.remove(ect)
    free_edges.append(ect)
    new_xzedge = TreeEdge(free_edges.pop(0))
    new_yzedge = TreeEdge(free_edges.pop(0))
    if len(ect.common)>0:    
        new_xzedge.common.extend(ect.common)
    new_xzedge.common.append(a)    
    new_xzedge.xnode = x
    new_xzedge.ynode = newnode
    if len(ect.common)>0:    
        new_yzedge.common.extend(ect.common)
    new_yzedge.common.append(b)        
    new_yzedge.xnode = newnode
    new_yzedge.ynode = y
    EL.append(new_xzedge)
    EL.append(new_yzedge)
    return 1

def update_edges_bigx_bigy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    #print("bigx-bigy",xlist,ylist)
    ix = rand.next_random(0,len(xlist)-1) 
    iy = rand.next_random(0,len(ylist)-1) 
    z = TreeNode(free_nodes.pop(0)) 
    z.Ax.append(x)
    z.Ax.append(y)
    z.parent = x
    y.parent = z  
    x.Ax.remove(y)
    x.Ax.append(z)
    y.Ax.remove(x)
    y.Ax.append(z)
    EL.remove(ect)
    free_edges.append(ect)
    new_xzedge = TreeEdge(free_edges.pop(0))
    new_yzedge = TreeEdge(free_edges.pop(0))
    if len(ect.common)>0:    
        z.cliqueList.extend(ect.common)
        new_xzedge.common.extend(ect.common)
    new_xzedge.xnode = x
    new_xzedge.ynode = z
    if len(ect.common)>0:    
        new_yzedge.common.extend(ect.common)
    new_yzedge.xnode = z
    new_yzedge.ynode = y
    for j in range(0,ix+1):
        z.cliqueList.append(xlist[j])
        new_xzedge.common.append(xlist[j])
    for j in range(0,iy+1):
        z.cliqueList.append(ylist[j])
        new_yzedge.common.append(ylist[j])
    CT.append(z)    
    #del EL[ei]
    EL.append(new_xzedge)
    EL.append(new_yzedge)
    return (ix+1)*(iy+1)

def update_add_edges(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges):
    if len(xlist) == 1:
        if (len(ylist) == 1) or (len(ylist) >= (num_edges - real_m)): 
        # if x contains exactly one "outside" vertex and y the same:
            if len(ylist) == 1:
                update_edges_onex_oney(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
            else: 
                update_edges_onex_bigy_noroomy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
            real_m += 1
        else:
            # add part (i) of ylist to a: 
            i = update_edges_onex_bigy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
            real_m += i
    else:
        # x has a big list
        if (len(ylist)==1):
            if (len(xlist) >= (num_edges - real_m)):
                update_edges_bigx_oney_noroomx(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
                real_m += 1
            else:
                # we have place in X to send to Y
                i = update_edges_bigx_oney(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
                real_m += i
        else:
            # both X and Y have a big list
            # we are "very" careful and check 
            # if there is place in both (we could have checked one by one...)
            if (len(xlist)*len(ylist) >= (num_edges - real_m)):
                update_edges_bigx_bigy_noplaces(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
                real_m += 1 # we only added a-b
            else:
                ixy = update_edges_bigx_bigy(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)
                real_m += ixy
    return real_m

def add_edges_clique_tree(CT, EL, num_edges, rand):
    """
        Add num_edges edges on the chordal represented by CT
    """
    real_m = 0
    free_nodes = []
    free_edges = []
    while real_m < num_edges: 
        # pick a random clique tree edge
        ect, ei = rand.next_element(EL)
        x = ect.xnode
        y = ect.ynode
        xlist = [v for v in x.cliqueList if v not in ect.common]
        ylist = [v for v in y.cliqueList if v not in ect.common]

        #print("before:",x,y)
        #print("TreeNodes")        
        #for v in CT:
        #    print(v,v.Ax,v.cliqueList)
        #print("Tree-Edges")            
        #for e in EL:
        #    print(e, e.xnode, e.ynode, e.common)

        # slow facts: 
        # .remove() [hashtable might help]  
        # .z in update_edges_onex_oney() [could choose the smallest .Ax between x and y]
        real_m = update_add_edges(CT, EL, num_edges, rand, real_m, x, y, ect, ei, xlist, ylist, free_nodes, free_edges)

        #print("After:",x,y)
        #print("TreeNodes")        
        #for v in CT:
        #    print(v,v.Ax,v.cliqueList)
        #print("Tree-Edges")            
        #for e in EL:
        #    print(e, e.xnode, e.ynode, e.common)

    return real_m


def Run_INCR(n, edge_density, alg_name):
    """
        Generate a random chordal graph....
    """

    edges_bound = edge_density * ((n * (n - 1)) / 2)
    runner = runner_factory(n, alg_name, None, edges_bound=edges_bound, edge_density=edge_density)

    randomizer = Randomizer(2 * n, runner["Parameters"]["seed"])    

    with Timer("t_init_incr", runner["Times"]):
        CT, EL = init_generation(n, randomizer)

    #print(randomizer.total_count) 
    #print(EL)
    with Timer("t_add_edges", runner["Times"]):
        m = add_edges_clique_tree(CT, EL, edges_bound, randomizer)   
    
    #print("TreeNodes")        
    #for v in CT:
    #    print(v,v.Ax,v.cliqueList)
    #print("Tree-Edges")            
    #for e in EL:
    #    print(e, e.xnode, e.ynode, e.common)

    print(n,edge_density,edges_bound,m,":")
    print("rands:",randomizer.total_count) 
    t_total = runner["Times"]["t_init_incr"] + runner["Times"]["t_add_edges"] 
    print(t_total)    

#    with Timer("t_subtrees_2", run["Times"]):
#        for node in tree:
#            node.s = 0
#        for subtree_index in range(0, n):
#            sub_tree_gen(tree, k, subtree_index, rand, version)

    # convert to networkx, our main algorithm
#    with Timer("t_ctree", run["Times"]):
#        nx_chordal, final_cforest = convert_clique_tree_networkx2(tree, n, True)

    # with Timer("t_chordal", run["Times"]):
    #    graph_chordal = Chordal(nx_chordal)

    # with Timer("t_forestverify", run["Times"]):
    #    tree_cliqueforest = is_cliqueforest(final_cforest, nx_chordal)

#    run["Graphs"]["tree"] = tree
#    run["Graphs"]["nx_chordal"] = nx_chordal
#    run["Graphs"]["CT"] = CT
    # run["Verify"]["graph_chordal"] = graph_chordal
    # run["Verify"]["tree_cliqueforest"] = tree_cliqueforest

    print("End Run".center(70, "-"))

    return 0 #calculate_mva_statistics(CT, runner, randomizer, n)

def post_process(run):
    out = run["Output"]
    graphs = run["Graphs"]
    stats = run["Stats"]
    times = run["Times"]

    # get number of conected components
    # stats["ncc"] = nx.number_connected_components(graphs["nx_chordal"])

    # calculate time, and ratios
    stats["total"] = times["t_real_tree"] + times["t_subtrees_2"] + times["t_ctree"]
    # stats["ratio[total/chordal]"] = stats["total"] / float(times["t_chordal"])
    # stats["ratio[total/forest]"] = stats["total"] / float(times["t_forestverify"])
    # stats["ratio[total/[chordal+forest]]"] = stats["total"] / float(times["t_forestverify"] + times["t_chordal"])

    # get output parameters
    out["nodes"] = run["Parameters"]["n"]  # len(graphs["nx_chordal"].nodes())
    out["edges"] = graphs["nx_chordal"].size()  # len(graphs["nx_chordal"].edges())
    out["edge_density"] = float(out["edges"]) / (float(out["nodes"] * (out["nodes"] - 1)) / 2)

    temp_forest = cForest(1)
    temp_forest.ctree.append(graphs["tree"])

    # calculate tree output parameters
    out["clique_trees"] = [dfs_forest(temp_forest), dfs_forest(graphs["final_cforest"])]
    
    ct_stats = out["clique_trees"][1]
    ct_stats.max_clique_edge_distribution = (ct_stats.max_size * (ct_stats.max_size - 1) / 2) / out["edges"]
    
    stats["ncc"] = len(graphs["final_cforest"].ctree)

    # convert clique forest to nx for export to json
    nx_ctrees = None  # [convert_tree_networkx(tree) for tree in graphs["final_cforest"].ctree]
    # nx_ctrees.insert(0, convert_tree_networkx(graphs["tree"]))

    return nx_ctrees


if __name__ == '__main__':
    #NUM_VERTICES = [50, 100, 500, 1000, 2500, 5000, 10000]
    NUM_VERTICES = [50]    
    EDGES_DENSITY = [0.5] #[0.1, 0.33, 0.5, 0.75, 0.99]
    for num in NUM_VERTICES:
        for edge_density in EDGES_DENSITY:
            Runners = []
            for _ in range(1):
                randomizer = Randomizer(2 * num)
                Runners.append(Run_INCR(num, edge_density, "INCR"))

            print(".....Done")
            # RUNNER contains all data and statistics
            #filename = "Results/myINCR/Run_{}_{}_{}.yml".format(num, par_k, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            #if not os.path.isdir(os.path.dirname(filename)):
            #    os.makedirs(os.path.dirname(filename))

            #with io.open(filename, 'w') as file:
            #    print_statistics(Runners, file)

    # nx_export_json(trees1 + [Runners[0]["Graphs"]["nx_chordal"]])
