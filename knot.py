'''
Hamiltonian Path

By Kevin Ewing
Spring 2022
Middlebury Animation Studio Independent Project 2
'''

from colorsys import hsv_to_rgb
from random import uniform
import math as m
import copy
import re
import bpy
import bmesh

# To render or not to render that is the question
RENDER = True

# Render global variables
RENDER_SIZE_FACTOR = 1
RENDER_SAMPLE_FACTOR = 1

# Stylization options:
CURVED = True
TRANSP = True
TRANSLUCENCE = 0.1
ROTATE = True
SYMMETRIC_X = True
SYMMETRIC_Y = True
SYMMETRIC_Z = True

CYCLE_COUNT = 10

# Function constants
MULTI = False
CYCLES = []


#  Detect hamiltonian path exists in this graph or not
def find_solution(graph, visited, result, node, counter, n, start):
    '''
    Organizing function for determining if there is a hamiltonian path or not
    '''
    if (counter == n and node == start):
        result[counter] = node
        CYCLES.append(copy.deepcopy(result))
        return True

    if visited[node]:
        return False

    #  indicates visiting node
    visited[node] = True
    #  Store path result
    result[counter] = node
    i = 0
    while i < n:
        if graph[node][i] == 1:
            if find_solution(graph, visited, result, i, counter + 1, n, start):
                return True
        i += 1

    #  reset the status of visiting node
    visited[node] = False


def set_default(visited, n):
    '''
    Clears the visited nodes up until the point it was at
    '''
    i = 0
    while i < n:
        visited[i] = False
        i += 1


#  Handles the request of find and display hamiltonian path
def hamiltonian_cycle_single(graph, num_cycles):
    '''
    Actually does the finding of the path
    '''
    n = len(graph)
    #  Indicator of visited node
    visited = [False] * (n)
    #  Used to store path information
    result = [0] * (n + 1)
    i = 0
    cycles_found = 0
    while (i < n) and cycles_found < num_cycles:
        set_default(visited, n)
        if find_solution(graph, visited, result, i, 0, n, i):
            cycles_found += 1
        i += 1

# def hamiltonian_cycle_multi(graph, num_cycles, start_vert):
#     n = len(graph)
#     #  Indicator of visited node
#     visited = [False] * (n)
#     #  Used to store path information
#     result = [0] * (n + 1)
#     set_default(visited, n)
#     find_solution(graph, visited, result, start_vert, 0, n, start_vert)


def make_adjacency(edge_list):
    '''
    Makes adjacency list from the edge list. Non directed.
    '''
    size = len(set([n for e in edge_list for n in e]))
    # make an empty adjacency list
    adjacency = [[0] * size for _ in range(size)]
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

    def dummy_view_layer_update():
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

    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Clearing all objects and materials from the prior scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        bpy.context.scene.render.engine = 'CYCLES'
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    except RuntimeError:
        print("There were no objexts in the scene")

    # Add primative
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, radius=1, enter_editmode=False, align='WORLD', location=(
            0, 0, 0), scale=(
            1, 1, 1))

    obj = bpy.context.active_object
    obj.name = "base_mesh"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action='DESELECT')

    # Gets to bmesh representation
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    vert_list = []
    index_list = []
    bm.faces.active = None
    for v in bm.verts:
        vert_list.append(re.search(r'\((.*?)\)', str(v)).group(1))
        index_list.append(re.search(r'index\s*=\s*([\S\s]+)', str(v)).group(1))

    edge_list = []
    edge_num = 0
    for e in bm.edges:
        edge_list.append([int(x) for x in re.findall(r'\/(\d+)', str(e))])
        edge_num += 1

    adj_list = make_adjacency(edge_list)
    num_cycles = CYCLE_COUNT

    if MULTI:
        pass
        # with ThreadPoolExecutor() as executor:
        #    for thread in range(vert_count):
        #        executor.submit(hamiltonian_cycle_multi, adj_list, num_cycles, thread)
    else:
        hamiltonian_cycle_single(adj_list, num_cycles)

    print("Done")

    if len(CYCLES) == 0:
        print("No hamiltonian cycles found")
    else:
        for k in range(len(CYCLES)):
            ham_path = []
            bm.edges.ensure_lookup_table()

            for i in range(len(CYCLES[k]) - 1):

                for j in range(len(edge_list)):
                    if edge_list[j] == [CYCLES[k][i], CYCLES[k][i + 1]]:
                        ham_path.append(bm.edges[j])

            for e in range(len(ham_path)):
                ham_path[e].select_set(True)
            bpy.ops.mesh.duplicate()

            for i in bm.edges:
                i.select = False

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        bpy.data.objects[0].select_set(True)
        bpy.context.view_layer.objects.active = bpy.context.window.scene.objects[0]
        bpy.ops.object.delete()

        if not TRANSP:
            mat = bpy.data.materials.new(name="gold")
            mat.use_nodes = True
            for n in mat.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    n.inputs["Metallic"].default_value = 0.9
                    n.inputs["Roughness"].default_value = 0.3
                    n.inputs["Base Color"].default_value = (
                        0.8, 0.582169, 0.218687, 1)

        # Making curves of all of the paths
        for k in range(len(CYCLES)):
            bpy.data.objects[k].select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.window.scene.objects[k]
            bpy.ops.object.convert(target='CURVE')

            if CURVED:
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subdivision"].levels = 4
                bpy.context.object.modifiers["Subdivision"].render_levels = 5

            # Giving the curves depth
            bpy.context.object.data.bevel_depth = 0.018
            bpy.ops.object.shade_smooth()

            # If it is allowed to rotate it we rotate it only in the specified
            # directions
            if ROTATE:
                if SYMMETRIC_X:
                    bpy.ops.transform.rotate(
                        value=uniform(0, 2 * m.pi),
                        orient_axis='X',
                        orient_type='GLOBAL',
                        orient_matrix=(
                            (1, 0, 0),
                            (0, 1, 0),
                            (0, 0, 1)),
                        orient_matrix_type='GLOBAL',
                        constraint_axis=(True, False, True),
                        mirror=False,
                        use_proportional_edit=False,
                        proportional_edit_falloff='SMOOTH',
                        proportional_size=1,
                        use_proportional_connected=False,
                        use_proportional_projected=False)
                if SYMMETRIC_Y:
                    bpy.ops.transform.rotate(
                        value=uniform(0, 2 * m.pi),
                        orient_axis='Y',
                        orient_type='GLOBAL',
                        orient_matrix=(
                            (1, 0, 0),
                            (0, 1, 0),
                            (0, 0, 1)),
                        orient_matrix_type='GLOBAL',
                        constraint_axis=(False, True, False),
                        mirror=False,
                        use_proportional_edit=False,
                        proportional_edit_falloff='SMOOTH',
                        proportional_size=1,
                        use_proportional_connected=False,
                        use_proportional_projected=False)
                if SYMMETRIC_Z:
                    bpy.ops.transform.rotate(
                        value=uniform(
                            0, 2 * m.pi),
                        orient_axis='Z',
                        orient_type='GLOBAL',
                        orient_matrix=(
                            (1, 0, 0),
                            (0, 1, 0),
                            (0, 0, 1)),
                        orient_matrix_type='GLOBAL',
                        constraint_axis=(False, False, True),
                        mirror=False,
                        use_proportional_edit=False,
                        proportional_edit_falloff='SMOOTH',
                        proportional_size=1,
                        use_proportional_connected=False,
                        use_proportional_projected=False)

            # If it is transparent we want to vary the color slightly on every
            # material made
            if TRANSP:
                mat = bpy.data.materials.new(name=("transp" + str(k)))
                mat.use_nodes = True
                for n in mat.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED':
                        n.inputs["Roughness"].default_value = 0.3
                        n.inputs["Base Color"].default_value = (
                            hsv_to_rgb(
                                uniform(
                                    0, 1), TRANSLUCENCE, 1.0)[0], hsv_to_rgb(
                                uniform(
                                    0, 1), TRANSLUCENCE, 1.0)[1], hsv_to_rgb(
                                uniform(
                                    0, 1), TRANSLUCENCE, 1.0)[2], 1.0)
                        n.inputs["Transmission"].default_value = 1.0
                        n.inputs["IOR"].default_value = 1.33

            # Append either transparent or gold material
            bpy.context.object.data.materials.append(mat)

        # Adding light, makes slightly brighter when using transparent shaders
        bpy.ops.mesh.primitive_plane_add(
            size=100, enter_editmode=False, align='WORLD', location=(0, 0, -1), scale=(1, 1, 1))
        bpy.ops.object.light_add(
            type='POINT', align='WORLD', location=(
                2, 2, 2), scale=(
                1, 1, 1))
        if TRANSP:
            bpy.context.object.data.energy = 200
        else:
            bpy.context.object.data.energy = 100

        # Adding camera
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(
            -1.56, 5.82, 1.12), rotation=(1.4154, 0, 3.43113), scale=(1, 1, 1))

        # Adding background
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (
            0, 0, 0, 1)


if __name__ == "__main__":
    run_ops_without_view_layer_update(main)
    if RENDER:
        print("Rendering...")
        bpy.context.scene.cycles.samples = int(256 * RENDER_SAMPLE_FACTOR)
        bpy.context.scene.render.resolution_x = 2048 * RENDER_SIZE_FACTOR
        bpy.context.scene.render.resolution_y = 2048 * RENDER_SIZE_FACTOR
        bpy.context.scene.cycles.device = 'GPU'
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=False)
