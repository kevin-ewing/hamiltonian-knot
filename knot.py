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
from sys import argv
from time import time
import math as m
from pprint import pprint
import re
import bpy
import bmesh

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
def hamiltonianCycle(graph, num_cycles):
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

    # Checkpoint before everyting is cleared
#    checkpoint = time()
#    print("Clearing everything...")
#    
#    bpy.ops.object.mode_set(mode = 'OBJECT')

#    # Clearing all objects and materials from the prior scene
#    bpy.ops.object.select_all(action='SELECT')
#    bpy.ops.object.delete()
#    bpy.context.scene.render.engine = 'CYCLES'
#    for material in bpy.data.materials:
#        bpy.data.materials.remove(material)

#    # Checkpoint after everything is cleared
#    print("--- %s seconds ---\n" % (time() - checkpoint))
#    checkpoint = time()
#    
#    
#    #Add monkey
#    bpy.ops.mesh.primitive_monkey_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
#    
##    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
##    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    
    #Gets to bmesh representation
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    vert_list = []
    index_list = []
    bm.faces.active = None
    for v in bm.verts:
        vert_list.append(re.search(r'\((.*?)\)',str(v)).group(1))
        index_list.append(re.search(r'index\s*=\s*([\S\s]+)',str(v)).group(1))
        
    verts_lookup = dict( zip(index_list,vert_list))
    
    edge_list = []
    edge_num = 0
    for e in bm.edges:
        edge_list.append([int(x) for x in re.findall(r'\/(\d+)',str(e))])
        edge_num += 1
    

    # nodes must be numbers in a sequential range starting at 0 - so this is the
    # number of nodes. you can assert this is the case as well if desired 
    
    adj_list = make_adjacency(edge_list)
    num_cycles = 2

    hamiltonianCycle(adj_list, num_cycles)
    
#    print(edge_num)
    
    
    print("Done")
    
#    # Modify the BMesh, can do anything here...
#    for v in bm.verts:
#        v.co.z += 1.0
#        

    # Show the updates in the viewport
    # and recalculate n-gon tessellation.
#    bmesh.update_edit_mesh(me, loop_triangles=True)

#    bpy.ops.object.mode_set(mode = 'EDIT') 
    

if __name__ == "__main__":
    start_checkpoint = time()
    run_ops_without_view_layer_update(main)
#    if RENDER:
#        print("Rendering...")
#        checkpoint = time()

#        working_dir = getcwd()
#        bpy.context.scene.render.filepath = (working_dir + "/output/output_" + argv[7])
#        bpy.context.scene.cycles.samples = int(256 * RENDER_SAMPLE_FACTOR)
#        bpy.context.scene.render.resolution_x = 3840 * RENDER_SIZE_FACTOR
#        bpy.context.scene.render.resolution_y = 1644 * RENDER_SIZE_FACTOR
#        bpy.context.scene.cycles.device = 'GPU'
#        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)

#        print("--- %s seconds ---\n" % (time() - checkpoint))
#        print("Total Time: %s seconds \n" % (time() - start_checkpoint))


# This example assumes we have a mesh object in edit-mode