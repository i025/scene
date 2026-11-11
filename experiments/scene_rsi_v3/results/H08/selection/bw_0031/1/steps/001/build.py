from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory and visual anchors, estimated from the supplied collage:
# - The lower photograph occupies approximately (0.03, 0.65)–(0.94, 1.00).
#   It shows a pale back wall of instrument cabinets, a long console in the
#   foreground, a dark floor, and a smaller console against the right wall.
# - The main console runs diagonally from approximately (0.03, 0.83) to
#   (0.66, 0.77); its pale inclined face overlaps its dark lower pedestal.
# - Rear-wall meters occupy roughly (0.04, 0.73)–(0.57, 0.86), with a large
#   horizontal ventilation grille near the middle. The wall edges recede right.
# - The small right console occupies approximately (0.77, 0.80)–(0.94, 0.91).
# - The separate yellow GRID example occupies (0.03, 0.19)–(0.52, 0.64).
#   It is a reference for the requested wall-mounted mimic panel; its exact
#   placement within the room is uncertain.
# - Occluded room boundaries and hidden cabinet backs are uncertain.
# Dominant edges: long console edges rise to the right in the photograph;
# cabinet seams are nearly vertical. The foreground console hides the lower
# portion of the instrument wall.
#
# Estimated primitive count: architecture 6, back cabinets and seams 25,
# meters about 90, ventilation 10, main console 8, controls about 100,
# small console and controls 22, GRID panel and symbols about 50, ceiling
# lights 4: approximately 315 SceneAct primitives. Text and a few simple
# slanted faces are added as Blender objects after realization.

scene = Scene('1970s_Dispatch_Control_Room')

# Dimensions and camera parameters are deliberately independent.
ROOM_W, ROOM_D, ROOM_H = 9.8, 6.5, 3.45
CAM_POS = (8.9, -11.5, 6.7)
CAM_TARGET = (0.0, 1.05, 1.45)
CAM_LENS = 35

ivory = (0.70, 0.68, 0.62)
wall = (0.76, 0.75, 0.70)
ceiling = (0.82, 0.81, 0.76)
floor_col = (0.31, 0.29, 0.26)
panel = (0.67, 0.66, 0.61)
panel_light = (0.82, 0.81, 0.75)
dark = (0.13, 0.14, 0.13)
black = (0.035, 0.037, 0.034)
glass = (0.87, 0.86, 0.78)
red = (0.63, 0.045, 0.025)
amber = (0.95, 0.52, 0.055)
yellow = (0.91, 0.72, 0.22)

architecture = Asset('Architecture')
architecture.include('floor', box((ROOM_W, ROOM_D, .12),
                                 center=(0, 0, -.07), color=floor_col))
architecture.include('back_wall', box((ROOM_W, .12, ROOM_H),
                                     center=(0, 3.25, ROOM_H/2), color=wall))
architecture.include('right_wall', box((.12, ROOM_D, ROOM_H),
                                      center=(4.9, 0, ROOM_H/2), color=wall))
architecture.include('ceiling', box((ROOM_W, ROOM_D, .10),
                                    center=(0, 0, ROOM_H+.05), color=ceiling))
architecture.include('back_baseboard', box((ROOM_W, .045, .15),
                                           center=(0, 3.17, .075), color=dark))
architecture.include('right_baseboard', box((.045, ROOM_D, .15),
                                            center=(4.83, 0, .075), color=dark))
scene.include('Architecture', architecture)

# Uniform, large rear-wall instrument cabinet field.
cabinets = Asset('Rear_Instrument_Cabinets')
cabinets.include('cabinet_field', box((7.15, .24, 2.75),
                                     center=(-1.25, 3.05, 1.48), color=ivory))
for i in range(9):
    x = -4.79 + i * .88
    cabinets.include('vertical_seam_%02d' % i,
                     box((.018, .025, 2.68), center=(x, 2.915, 1.50), color=dark))
cabinets.include('upper_division', box((7.1, .025, .025),
                                      center=(-1.25, 2.912, 2.55), color=dark))
cabinets.include('lower_division', box((7.1, .025, .025),
                                      center=(-1.25, 2.912, .47), color=dark))

# Large square meters with dark frames and pale faces.
meter_positions = []
for col in range(10):
    x = -4.49 + col * .66
    # Central zone is reserved for the ventilation grille.
    if 4 <= col <= 6:
        continue
    for row in range(3):
        z = .83 + row * .47
        meter_positions.append((x, z))
for n, (x, z) in enumerate(meter_positions):
    cabinets.include('meter_frame_%02d' % n,
                     box((.40, .035, .37), center=(x, 2.888, z), color=dark))
    cabinets.include('meter_face_%02d' % n,
                     box((.33, .022, .30), center=(x, 2.864, z), color=glass))
    cabinets.include('meter_needle_%02d' % n,
                     box((.014, .012, .11), center=(x+.035, 2.848, z), color=black))
# Wide ventilation grille, visually prominent in the photo.
cabinets.include('vent_frame', box((1.80, .045, .82),
                                  center=(-1.16, 2.875, 1.43), color=dark))
cabinets.include('vent_inset', box((1.66, .020, .68),
                                  center=(-1.16, 2.844, 1.43), color=panel))
for j in range(7):
    cabinets.include('vent_slot_%02d' % j,
                     box((1.56, .018, .045),
                         center=(-1.16, 2.826, 1.17+j*.085), color=dark))
scene.include('Rear_Instrument_Cabinets', cabinets)

# Main desk: a broad, long control assembly with a dark base and overhanging
# horizontal writing ledge. Sloped control face is created after realization.
desk = Asset('Main_Operating_Console')
desk.include('pedestal', box((6.25, 1.28, .76),
                            center=(-1.00, -.15, .38), color=dark))
desk.include('front_inset', box((5.95, .035, .52),
                               center=(-1.0, -.81, .38), color=(.24,.23,.21)))
desk.include('writing_ledge', box((6.48, .56, .09),
                                 center=(-1.0, -.80, .83), color=panel_light))
desk.include('left_cheek', box((.10, 1.20, .55),
                              center=(-4.19, -.10, 1.00), color=panel))
desk.include('right_cheek', box((.10, 1.20, .55),
                               center=(2.19, -.10, 1.00), color=panel))
scene.include('Main_Operating_Console', desk)

# Smaller independent desk at the room's right rear.
small = Asset('Right_Independent_Console')
small.include('base', box((1.38, .86, .76),
                          center=(3.82, 2.25, .38), color=(.29,.28,.25)))
small.include('ledge', box((1.48, .35, .09),
                           center=(3.82, 1.78, .83), color=panel_light))
small.include('back_panel', box((1.46, .12, .55),
                                center=(3.82, 2.62, 1.07), color=panel))
scene.include('Right_Independent_Console', small)

# A yellow mimic panel is mounted on the right-hand wall. The separate
# source image establishes its front design but not its exact room location.
grid = Asset('GRID_Mimic_Panel')
grid.include('yellow_board', box((.10, 1.42, 1.95),
                                center=(4.79, .55, 1.95), color=yellow))
# Black single-line schematic: coordinates are in the wall's Y/Z plane.
def grid_bar(name, y, z, sy, sz, color=black):
    grid.include(name, box((.026, sy, sz), center=(4.72, y, z), color=color))
grid_bar('main_bus', .48, 1.95, .035, 1.78)
for i, z in enumerate((1.30, 1.70, 2.12, 2.53)):
    grid_bar('cross_bus_%d' % i, .48, z, .70, .035)
for i, (y, z) in enumerate(((.18,1.70),(.78,1.70),(.18,2.12),(.78,2.12))):
    grid_bar('branch_%d' % i, y, z, .035, .39)
for i, (y,z) in enumerate(((.48,1.25),(.48,1.67),(.48,2.10),(.48,2.53),
                           (.18,1.70),(.78,1.70),(.18,2.12),(.78,2.12))):
    grid.include('amber_indicator_%d' % i,
                 box((.035,.14,.13), center=(4.69,y,z), color=amber))
for i, (y,z) in enumerate(((.48,1.05),(.48,2.76),(-.02,2.30),(-.02,1.49))):
    grid.include('red_indicator_%d' % i,
                 ball(.065, center=(4.68,y,z), color=red))
for i, z in enumerate((1.25,1.55,1.85,2.15,2.45,2.75)):
    grid.include('selector_%d' % i,
                 ball(.065, center=(4.68,1.05,z), color=black))
scene.include('GRID_Mimic_Panel', grid)

lights = Asset('Ceiling_Fluorescent_Fixtures')
for x in (-2.8, 1.1):
    for y in (-1.0, 1.5):
        lights.include('troffer_%s_%s' % (x,y),
                       box((2.25,.48,.035), center=(x,y,3.38),
                           color=(.95,.94,.86)))
scene.include('Ceiling_Fluorescent_Fixtures', lights)

realize(scene)

# Keep semantic Blender collections for later adjustment and annotation.
def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def move_to_collection(obj, name):
    c = collection(name)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)

def material(name, color, rough=.65, metallic=0.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    if emission:
        e = p.inputs.get('Emission Color') or p.inputs.get('Emission')
        if e:
            e.default_value = (*color, 1)
        strength = p.inputs.get('Emission Strength')
        if strength:
            strength.default_value = emission
    return m

mat_surface = material('Console painted metal', (.69,.68,.62), .49, .18)
mat_border = material('Console dark markings', (.065,.065,.058), .72)
mat_knob = material('Black bakelite knobs', (.055,.055,.05), .32)
mat_red = material('Red indicator glow', (.65,.035,.015), .38, emission=.7)
mat_amber = material('Amber indicator glow', (.95,.43,.035), .4, emission=.65)
mat_text = material('Dark lettering', (.035,.035,.03), .8)

def mesh_obj(name, verts, faces, mat, group):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection(group).objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# Inclined face runs from the writing shelf to the raised rear edge.
def sloped_face(name, xmin, xmax, yfront, yback, zfront, zback, group):
    return mesh_obj(name,
        [(xmin,yfront,zfront), (xmax,yfront,zfront),
         (xmax,yback,zback), (xmin,yback,zback)],
        [(0,1,2,3)], mat_surface, group)

sloped_face('Main sloping control surface', -4.14, 2.14, -.53, .50, .88, 1.36,
            'Main_Operating_Console_Details')
sloped_face('Small sloping control surface', 3.10, 4.54, 1.92, 2.60, .88, 1.31,
            'Right_Independent_Console_Details')

def slope_z(y, yf, yb, zf, zb):
    return zf + (y-yf)*(zb-zf)/(yb-yf)

def disk(name, loc, radius, depth, mat, normal, group, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                        depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(normal).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(mat)
    move_to_collection(o, group)
    return o

# Main desk markings and controls remain legible at presentation scale.
# Approx. 11 stations, each with an outlined plate and three controls.
slope_normal = Vector((0, -.48, 1.03)).normalized()
for i in range(11):
    x = -3.86 + i*.56
    yf, yb, zf, zb = -.53, .50, .88, 1.36
    for j, y in enumerate((-.30, -.02, .27)):
        z = slope_z(y, yf, yb, zf, zb) + .014
        disk('Desk_%02d_control_%d' % (i,j), (x,y,z), .042 if j != 1 else .055,
             .025, mat_knob if (i+j)%4 else mat_red, slope_normal,
             'Main_Operating_Console_Details')
    # Thin dark station boundaries emphasize the repeated control panels.
    y0,y1 = -.45,.42
    z0 = slope_z(y0,yf,yb,zf,zb)+.012
    z1 = slope_z(y1,yf,yb,zf,zb)+.012
    mesh_obj('Desk station divider %02d' % i,
             [(x-.24,y0,z0),(x-.226,y0,z0),(x-.226,y1,z1),(x-.24,y1,z1)],
             [(0,1,2,3)], mat_border, 'Main_Operating_Console_Details')

small_normal = Vector((0,-.43,.68)).normalized()
for i in range(5):
    for j in range(2):
        x = 3.25+i*.26
        y = 2.08+j*.28
        z = slope_z(y,1.92,2.60,.88,1.31)+.015
        disk('Small desk control %d %d' % (i,j), (x,y,z), .042, .022,
             mat_red if (i+j)%5 == 0 else mat_knob, small_normal,
             'Right_Independent_Console_Details')

def text_obj(name, body, loc, rot, size, mat, group):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.extrude = .0005
    obj = bpy.data.objects.new(name, curve)
    collection(group).objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

# Letters face inward from the right wall, alongside the mimic's controls.
text_obj('GRID heading', 'GRID', (4.715,1.22,2.82),
         (math.pi/2, 0, math.pi/2), .12, mat_text, 'GRID_Panel_Labels')
text_obj('German label one', 'FERNLEITUNG', (4.715,1.25,2.61),
         (math.pi/2, 0, math.pi/2), .055, mat_text, 'GRID_Panel_Labels')
text_obj('German label two', 'SCHALTER', (4.715,1.25,1.17),
         (math.pi/2, 0, math.pi/2), .055, mat_text, 'GRID_Panel_Labels')

# SceneAct materials may be shared; copy only for the selected visible lamp
# meshes before changing their shader. Match names within semantic parts.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    n = obj.name.lower()
    chosen = None
    if 'red_indicator' in n:
        chosen = mat_red
    elif 'amber_indicator' in n:
        chosen = mat_amber
    if chosen:
        obj.data.materials.clear()
        obj.data.materials.append(chosen)
        print('Material:', obj.name, chosen.name, 'emission strength',
              chosen.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value
              if chosen.node_tree.nodes['Principled BSDF'].inputs.get('Emission Strength') else 'linked/unsupported')
print('Material: main control surface', mat_surface.name,
      'roughness', mat_surface.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value,
      'metallic', mat_surface.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value)

# Rebuild the world after realization.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.73,.72,.68,1)
background.inputs['Strength'].default_value = .45

# The original attachment is portrait; retain its aspect for the projection
# and final active camera, as requested by the reconstruction procedure.
sc.render.resolution_x = 1080
sc.render.resolution_y = 1479
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.engine = 'CYCLES'
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = 'Filmic'
except TypeError:
    pass

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
sc.camera.name = 'Camera_Panorama'
area_emitter((0,-2,3.25), power=750, size=5, target=(0,1,0))
area_emitter((-3,1,3.25), power=450, size=3, target=(-2,1,0))
area_emitter((3,1,3.25), power=400, size=3, target=(3,1,0))

# Additional editable close-up camera; the panorama remains active.
panorama = sc.camera
cam_data = bpy.data.cameras.new('Camera_Closeup_Data')
cam_obj = bpy.data.objects.new('Camera_Closeup', cam_data)
collection('Cameras').objects.link(cam_obj)
cam_obj.location = (5.5,-5.8,3.25)
cam_obj.rotation_euler = (Vector((1.6,.3,1.55))-cam_obj.location).to_track_quat('-Z','Y').to_euler()
cam_data.lens = 42
sc.camera = panorama

# Numerical projections use identifiable geometry points. Reference values
# are approximate estimates for the lower photo, remapped to a room-only view.
reference = [
    ('cabinet upper left', (-4.8,2.92,2.82), (.04,.12)),
    ('cabinet upper right', (2.3,2.92,2.82), (.68,.12)),
    ('console front left', (-4.24,-1.08,.88), (.03,.78)),
    ('console rear right', (2.14,.50,1.36), (.68,.55)),
    ('small console top', (4.54,2.60,1.31), (.94,.56)),
]
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
projection = panorama.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print('Landmark | estimated reference | projected')
for name, p, ref in reference:
    clip = projection @ panorama.matrix_world.inverted() @ Vector((*p,1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
