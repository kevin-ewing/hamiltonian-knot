'''
Procedural generation of a citycape

By Kevin Ewing
Spring 2022
Middlebury Animation Studio Independent project
'''


from colorsys import hsv_to_rgb
from dataclasses import dataclass
from random import randint, uniform
from os import getcwd
from site import addpackage
from sys import argv
from time import time
import math as m
from pprint import pprint
import re
import threading
from concurrent.futures import ThreadPoolExecutor


# To render or not to render that is the question
RENDER = True

# Render global variables
RENDER_SIZE_FACTOR = 1
RENDER_SAMPLE_FACTOR = 1


#  Detect  hamiltonian path exists in this graph or not
def findSolution(graph, visited, result, node, counter, n, start) :
    if (counter == n and node == start) :
        result[counter] = node
        print(result)
        return True
    
    if (visited[node] == True) :
        return False
    
    #  indicates visiting node
    visited[node] = True
    #  Store path result
    result[counter] = node
    i = 0
    while (i < n) :
        if (graph[node][i] == 1) :
            if findSolution(graph, visited, result, i, counter + 1, n, start):
                return True
        
        i += 1
    
    #  reset the status of visiting node
    visited[node] = False

def setDefault(visited, n) :
    i = 0
    while (i < n) :
        visited[i] = False
        i += 1
    

#  Handles the request of find and display hamiltonian path
def hamiltonianCycle_single(graph, num_cycles):
    n = len(graph)
    #  Indicator of visited node
    visited = [False] * (n)
    #  Used to store path information
    result = [0] * (n + 1)
    i = 0
    cycles_found = 0
    while (i < n) and cycles_found < num_cycles:
        setDefault(visited, n)
        if findSolution(graph, visited, result, i, 0, n, i):
            cycles_found += 1
        i += 1

def hamiltonianCycle_multi(graph, num_cycles, start_vert):
    n = len(graph)
    #  Indicator of visited node
    visited = [False] * (n)
    #  Used to store path information
    result = [0] * (n + 1)
    setDefault(visited, n)
    findSolution(graph, visited, result, start_vert, 0, n, start_vert)
    
def make_adjacency(edge_list):
    size = len(set([n for e in edge_list for n in e])) 
    # make an empty adjacency list  
    adjacency = [[0]*size for _ in range(size)]
    # populate the list for each edge
    for sink, source in edge_list:
        adjacency[sink][source] = 1
        
    return adjacency


# Blender will update the view with each primitive addition, we do not want that, instead
# lets block it from updating the view until the end
# https://blender.stackexchange.com/questions/7358/python-performance-with-blender-
# operators
def run_ops_without_view_layer_update(func):
    '''
    Workaround function as mentioned above to only update the meshes after everything
    has been generated, severely shortens the amount of time building generation takes
    '''

    from bpy.ops import _BPyOpsSubModOp
    view_layer_update = _BPyOpsSubModOp._view_layer_update

    def dummy_view_layer_update(context):
        pass
    try:
        _BPyOpsSubModOp._view_layer_update = dummy_view_layer_update
        func()
    finally:
        _BPyOpsSubModOp._view_layer_update = view_layer_update


def main():
    '''
    Main function
        clears scene, sets conditions, generates building plan then starts generation
        does not do the rendering
    '''

    edge_list = [[12, 0], [13, 1], [14, 2], [15, 1], [16, 5], [17, 0], [18, 3], [19, 0], [20, 4], [21, 5], [22, 1], [23, 10], [24, 2], [25, 6], [26, 3], [27, 7], [28, 4], [29, 8], [30, 5], [31, 9], [32, 6], [33, 7], [34, 8], [35, 9], [36, 10], [37, 6], [38, 11], [39, 7], [40, 8], [41, 9], [2, 12], [0, 13], [1, 14], [5, 15], [0, 16], [3, 17], [2, 18], [4, 19], [3, 20], [4, 21], [10, 22], [5, 23], [6, 24], [1, 25], [7, 26], [2, 27], [8, 28], [3, 29], [9, 30], [4, 31], [10, 32], [6, 33], [7, 34], [8, 35], [9, 36], [11, 37], [10, 38], [11, 39], [11, 40], [11, 41], [38, 41], [38, 36], [41, 36], [41, 40], [41, 35], [40, 35], [40, 39], [40, 34], [39, 34], [39, 37], [39, 33], [37, 33], [37, 38], [37, 32], [38, 32], [23, 36], [23, 30], [36, 30], [31, 35], [31, 28], [35, 28], [29, 34], [29, 26], [34, 26], [27, 33], [27, 24], [33, 24], [25, 32], [25, 22], [32, 22], [30, 31], [30, 21], [31, 21], [28, 29], [28, 20], [29, 20], [26, 27], [26, 18], [27, 18], [24, 25], [24, 14], [25, 14], [22, 23], [22, 15], [23, 15], [16, 21], [16, 19], [21, 19], [19, 20], [19, 17], [20, 17], [17, 18], [17, 12], [18, 12], [15, 16], [15, 13], [16, 13], [12, 14], [12, 13], [14, 13]]
    
    adj_list = make_adjacency(edge_list)
    num_cycles = 1000
    vert_count = len(adj_list)

    checkpoint = time()
    hamiltonianCycle_single(adj_list, num_cycles)

    check_1 = time() - checkpoint
    print("Single Thread")
    print("--- %s seconds ---\n" % check_1)


    checkpoint = time()
    with ThreadPoolExecutor() as executor:
       for thread in range(vert_count):
           executor.submit(hamiltonianCycle_multi, adj_list, num_cycles, thread)
    
    check_2 = time() - checkpoint
    print("Multi Thread")
    print("--- %s seconds ---\n" % check_2)

    print("Multi was %s seconds faster" % (check_1 - check_2))
    
    
    print("Done")

if __name__ == "__main__":
    main()