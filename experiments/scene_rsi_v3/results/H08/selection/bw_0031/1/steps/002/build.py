from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, estimated from the lower photograph in the collage:
# - Rear cabinet wall: approximately x=.03–.66, y=.65–.87 of the full image.
#   Its cabinet seams are near vertical and its upper edge descends slightly
#   toward the right. Square meters flank a wide horizontal ventilation grille.
# - Main console: approximately x=.03–.67, y=.78–1.00. Its light sloping
#   control face and writing ledge overlap a large dark pedestal. Its long
#   edges rise strongly toward the right.
# - Pale right wall and doorway: approximately x=.65–.94, y=.66–.88.
#   A small independent console stands at x=.77–.94, y=.77–.91.
# - Dark floor remains visible at lower right. The yellow GRID panel is shown
#   separately in the reference; its placement in the room is uncertain.
# - Ceiling and hidden room boundaries are not visible in the photograph.
#
# Comparison with the first rendered image:
# 1. The ceiling and exterior right wall cover most of the view; the reference
#    shows an interior. The main console appears at roughly x=.14–.64,
#    y=.48–.65 in the render, far smaller than the photograph's foreground.
#    Move the camera inside the room and remove the obstructing ceiling slab
#    from the camera view. This should enlarge the console and reveal the wall.
# 2. The rendered cabinet wall occupies only a narrow band near y=.46–.56;
#    the photograph has a broad, visible instrument wall behind the console.
#    Lower the camera and aim toward the cabinets; this should move their top
#    upward and expose their rows. The trial projections below check direction.
# 3. The render has a light floor and a pale pedestal; the photograph has a
#    conspicuously dark console base and floor. Use separate darker finishes,
#    while allowing lighting and surface orientation to affect their brightness.
# 4. The rendered console edge descends to the right, while the photograph's
#    edge rises to the right. Move the camera toward the left end of the desk;
#    this changes perspective and makes the left end the near foreground.
# Camera projections are geometric checks, not observed silhouette bounds.
#
# Estimated mesh count: architecture 7; rear cabinets and meter parts about
# 115; vent 10; main desk and controls about 120; right desk 20;
# GRID panel 45; fixtures 3: approximately 320 primitives plus 3 sloped faces.
# Camera parameters are independent of room and console dimensions.

scene = Scene('Historical_Dispatch_Room')

ROOM_W, ROOM_D, ROOM_H = 9.6, 6.8, 3.3
DESK_LEFT, DESK_RIGHT = -4.25, 2.0
DESK_FRONT, DESK_BACK = -0.65, 0.62
CAM_POS = (-5.9, -7.0, 2.85)
CAM_TARGET = (-0.4, 2.0, 1.55)
CAM_LENS = 25

wall_col = (.73, .72, .68)
cab_col = (.69, .68, .63)
face_col = (.79, .78, .72)
floor_col = (.25, .23, .21)
dark = (.15, .15, .14)
black = (.035, .035, .032)
white = (.85, .84, .78)
yellow = (.88, .69, .17)
red = (.68, .035, .018)
amber = (.98, .48, .025)

architecture = Asset('Architecture')
architecture.include('floor', box((ROOM_W, ROOM_D, .12),
                                  center=(0, 0, -.06), color=floor_col))
architecture.include('rear_wall', box((ROOM_W, .12, ROOM_H),
                                      center=(0, 3.4, ROOM_H/2), color=wall_col))
architecture.include('right_wall', box((.12, ROOM_D, ROOM_H),
                                       center=(4.8, 0, ROOM_H/2), color=wall_col))
# The ceiling is represented by individual fixtures. The upper room enclosure
# is outside the photographed crop, so no obstructing roof slab is added.
architecture.include('rear_baseboard', box((ROOM_W, .04, .13),
                                            center=(0, 3.31, .065), color=dark))
architecture.include('right_baseboard', box((.04, ROOM_D, .13),
                                             center=(4.72, 0, .065), color=dark))
scene.include('Architecture', architecture)

cabinets = Asset('Rear_Instrument_Wall')
cabinets.include('cabinet_body', box((7.1, .22, 2.72),
                                     center=(-1.2, 3.22, 1.39), color=cab_col))
for i in range(9):
    x = -4.7 + i * .86
    cabinets.include('cabinet_seam_%02d' % i,
                     box((.018, .018, 2.68), center=(x, 3.095, 1.40), color=dark))
cabinets.include('upper_panel_line', box((7.05, .018, .018),
                                          center=(-1.2, 3.09, 2.27), color=dark))
cabinets.include('lower_panel_line', box((7.05, .018, .018),
                                          center=(-1.2, 3.09, .39), color=dark))

# Square meter arrays on either side of the central ventilation grille.
for col in (0, 1, 2, 3, 7, 8, 9, 10):
    x = -4.52 + col * .60
    for row in range(3):
        z = .76 + row * .45
        k = '%02d_%d' % (col, row)
        cabinets.include('meter_frame_' + k,
                         box((.39, .035, .36), center=(x, 3.065, z), color=dark))
        cabinets.include('meter_face_' + k,
                         box((.32, .018, .29), center=(x, 3.038, z), color=white))
        cabinets.include('meter_needle_' + k,
                         box((.012, .009, .11), center=(x+.025, 3.024, z),
                             color=black))
cabinets.include('vent_frame', box((1.65, .035, .72),
                                    center=(-1.25, 3.06, 1.25), color=dark))
cabinets.include('vent_recess', box((1.52, .018, .59),
                                     center=(-1.25, 3.033, 1.25), color=cab_col))
for i in range(7):
    cabinets.include('vent_slot_%d' % i,
                     box((1.46, .015, .036),
                         center=(-1.25, 3.018, 1.01+i*.08), color=dark))
scene.include('Rear_Instrument_Wall', cabinets)

desk = Asset('Main_Operating_Console')
desk.include('dark_pedestal', box((DESK_RIGHT-DESK_LEFT, 1.15, .72),
                                  center=((DESK_LEFT+DESK_RIGHT)/2, -.03, .36),
                                  color=(.13, .12, .11)))
desk.include('front_base_panel', box((6.0, .025, .49),
                                     center=(-1.125, -.616, .36),
                                     color=(.20, .19, .17)))
desk.include('writing_ledge', box((6.45, .48, .075),
                                  center=(-1.125, -.78, .80), color=face_col))
desk.include('left_cheek', box((.10, 1.12, .40),
                               center=(-4.22, .02, 1.00), color=cab_col))
desk.include('right_cheek', box((.10, 1.12, .40),
                                center=(1.97, .02, 1.00), color=cab_col))
scene.include('Main_Operating_Console', desk)

small = Asset('Right_Independent_Console')
small.include('pedestal', box((1.45, .82, .74),
                              center=(3.72, 2.48, .37), color=(.22,.21,.19)))
small.include('writing_ledge', box((1.55, .28, .07),
                                   center=(3.72, 2.02, .79), color=face_col))
scene.include('Right_Independent_Console', small)

# A dark doorway is visible between the main wall and the right-hand desk.
door = Asset('Right_Wall_Doorway')
door.include('door_frame', box((.90, .055, 2.15),
                                center=(2.70, 3.28, 1.075), color=(.48,.47,.43)))
door.include('door_inset', box((.70, .025, 1.90),
                                center=(2.70, 3.235, 1.12), color=(.24,.23,.21)))
door.include('door_window', box((.47, .018, .83),
                                 center=(2.70, 3.215, 1.62), color=(.43,.43,.40)))
scene.include('Right_Wall_Doorway', door)

# The isolated yellow reference gives the panel's design, but not a reliable
# room position. Place it on the right wall, where it can be seen in a close-up.
grid = Asset('GRID_Mimic_Panel')
grid.include('yellow_board', box((.08, 1.42, 1.92),
                                 center=(4.70, .55, 1.90), color=yellow))
def grid_bar(name, y, z, sy, sz, col=black):
    grid.include(name, box((.025, sy, sz), center=(4.645, y, z), color=col))
grid_bar('main_bus', .40, 1.90, .035, 1.75)
for i, z in enumerate((1.25, 1.66, 2.08, 2.48)):
    grid_bar('horizontal_bus_%d' % i, .40, z, .66, .035)
for i, (y,z) in enumerate(((.10,1.46),(.70,1.46),(.10,1.87),(.70,1.87),
                            (.10,2.28),(.70,2.28))):
    grid_bar('branch_%d' % i, y, z, .035, .38)
for i, (y,z) in enumerate(((.1,1.66),(.4,1.66),(.7,1.66),
                            (.1,2.08),(.4,2.08),(.7,2.08))):
    grid.include('amber_lamp_%d' % i,
                 box((.035,.11,.12), center=(4.615,y,z), color=amber))
for i, z in enumerate((1.10,2.72)):
    grid.include('red_lamp_%d' % i, ball(.065, center=(4.61,.4,z), color=red))
for i, z in enumerate((1.25,1.55,1.85,2.15,2.45,2.72)):
    grid.include('selector_dial_%d' % i,
                 box((.025,.19,.19), center=(4.63,1.08,z), color=white))
    grid.include('selector_knob_%d' % i,
                 ball(.052, center=(4.59,1.08,z), color=black))
scene.include('GRID_Mimic_Panel', grid)

fixtures = Asset('Ceiling_Fluorescent_Fixtures')
for i, x in enumerate((-2.6, .4, 3.3)):
    fixtures.include('fluorescent_%d' % i,
                     box((2.0, .40, .035), center=(x, 1.3, 3.22), color=white))
scene.include('Ceiling_Fluorescent_Fixtures', fixtures)

realize(scene)

def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def material(name, color, rough=.65, metallic=0, emission=0):
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
        s = p.inputs.get('Emission Strength')
        if s:
            s.default_value = emission
    return m

surface_mat = material('Console painted metal', (.68,.67,.62), .52, .18)
mark_mat = material('Control markings', (.045,.045,.04), .72)
knob_mat = material('Bakelite knobs', (.045,.043,.038), .34)
red_mat = material('Red indicators emissive', (.65,.025,.012), .38, emission=.8)
amber_mat = material('Amber indicators emissive', (.95,.40,.015), .4, emission=.8)
lamp_mat = material('Fluorescent diffuser', (.95,.93,.82), .5, emission=1.0)

def mesh_obj(name, verts, faces, mat, group):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    get_collection(group).objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def sloped_face(name, xmin, xmax, yf, yb, zf, zb, group):
    return mesh_obj(name, [(xmin,yf,zf),(xmax,yf,zf),
                           (xmax,yb,zb),(xmin,yb,zb)],
                    [(0,1,2,3)], surface_mat, group)

sloped_face('Main inclined control surface', -4.17, 1.92, -.54, .58, .84, 1.34,
            'Main_Operating_Console_Details')
sloped_face('Small inclined control surface', 3.00, 4.44, 2.10, 2.84, .83, 1.25,
            'Right_Independent_Console_Details')

def slope_z(y, yf, yb, zf, zb):
    return zf + (y-yf)*(zb-zf)/(yb-yf)

def disk(name, loc, radius, mat, normal, group):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                       depth=.025, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = Vector(normal).to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(mat)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    get_collection(group).objects.link(obj)

normal = Vector((0,-.50,1.12)).normalized()
for i in range(11):
    x = -3.90 + i*.55
    for j, y in enumerate((-.36,-.12,.12,.36)):
        z = slope_z(y,-.54,.58,.84,1.34)+.018
        mat = red_mat if (i*3+j) % 11 == 0 else knob_mat
        disk('Main control %02d_%d' % (i,j), (x,y,z), .035, mat, normal,
             'Main_Operating_Console_Details')
    y0, y1 = -.48, .50
    z0 = slope_z(y0,-.54,.58,.84,1.34)+.012
    z1 = slope_z(y1,-.54,.58,.84,1.34)+.012
    mesh_obj('Station divider %02d' % i,
             [(x-.23,y0,z0),(x-.215,y0,z0),(x-.215,y1,z1),(x-.23,y1,z1)],
             [(0,1,2,3)], mark_mat, 'Main_Operating_Console_Details')

small_normal = Vector((0,-.42,.74)).normalized()
for i in range(5):
    for j in range(2):
        y = 2.22+j*.29
        z = slope_z(y,2.10,2.84,.83,1.25)+.018
        disk('Small control %d_%d' % (i,j), (3.15+i*.25,y,z), .035,
             red_mat if (i+j)%6 == 0 else knob_mat, small_normal,
             'Right_Independent_Console_Details')

# Use small text objects facing the room on the yellow panel.
def label(name, body, pos, size):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    get_collection('GRID_Panel_Labels').objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    obj.data.materials.append(mark_mat)

label('Panel label one', 'FERNLEITUNG', (4.60,1.20,2.75), .055)
label('Panel label two', 'SCHALTER', (4.60,1.20,1.05), .055)

# SceneAct emits semantic parent markers. Traverse their descendants and
# replace shared finish materials only on the intended panel/fixture meshes.
def descendants(root):
    result = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        stack.extend(obj.children)
        if obj.type == 'MESH':
            result.append(obj)
    return result

def assign_semantic(part_fragment, mat):
    selected = []
    for obj in bpy.data.objects:
        if part_fragment.lower() in obj.name.lower():
            if obj.type == 'MESH':
                selected.append(obj)
            selected.extend(descendants(obj))
    seen = set()
    for obj in selected:
        if obj.name in seen:
            continue
        seen.add(obj.name)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    p = mat.node_tree.nodes.get('Principled BSDF')
    print('Material selection:', part_fragment, 'meshes', len(seen),
          'material', mat.name, 'roughness', p.inputs['Roughness'].default_value,
          'metallic', p.inputs['Metallic'].default_value,
          'emission', p.inputs['Emission Strength'].default_value
          if p.inputs.get('Emission Strength') else 'unsupported')

assign_semantic('red_lamp', red_mat)
assign_semantic('amber_lamp', amber_mat)
assign_semantic('fluorescent_', lamp_mat)
p = surface_mat.node_tree.nodes['Principled BSDF']
print('Material selection: Main inclined control surface', surface_mat.name,
      'roughness', p.inputs['Roughness'].default_value,
      'metallic', p.inputs['Metallic'].default_value)

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
background.inputs['Color'].default_value = (.75,.73,.68,1)
background.inputs['Strength'].default_value = .35

# Retain the reference's portrait aspect and exceed 1920 pixels vertically.
sc.render.resolution_x = 1920
sc.render.resolution_y = 2628
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.engine = 'CYCLES'
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = 'Filmic'
except TypeError:
    pass

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
panorama = sc.camera
panorama.name = 'Camera_Panorama'
area_emitter((-2, 0, 3.10), power=550, size=4, target=(-1,1,0))
area_emitter((2, 1.5, 3.10), power=450, size=3, target=(1,2,0))

close_data = bpy.data.cameras.new('Camera_Closeup_Data')
close_cam = bpy.data.objects.new('Camera_Closeup', close_data)
get_collection('Cameras').objects.link(close_cam)
close_cam.location = (2.3,-3.3,2.2)
close_cam.rotation_euler = (Vector((3.7,.8,1.6))-close_cam.location).to_track_quat('-Z','Y').to_euler()
close_data.lens = 35
sc.camera = panorama

# Compare geometric projections for a small aim trial, then keep whichever
# direction moves the rear-wall top upward while preserving the foreground.
# Reference estimates are in a room-only crop and are not calibration.
landmarks = [
    ('rear wall upper left', (-4.70,3.09,2.72), (.03,.08)),
    ('rear wall upper right', (2.30,3.09,2.72), (.67,.12)),
    ('console front left', (-4.22,-1.02,.84), (.03,.78)),
    ('console rear right', (1.92,.58,1.34), (.67,.43)),
    ('small desk rear', (4.44,2.84,1.25), (.94,.48)),
]
def project_points():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    proj = panorama.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    out = []
    for _, pt, _ in landmarks:
        clip = proj @ panorama.matrix_world.inverted() @ Vector((*pt,1))
        out.append(None if clip.w <= 1e-8 else
                   (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w)))
    return out

base = project_points()
base_rotation = panorama.rotation_euler.copy()
trial_target = Vector(CAM_TARGET) + Vector((0,0,-.10))
panorama.rotation_euler = (trial_target - panorama.location).to_track_quat('-Z','Y').to_euler()
trial = project_points()
# A lower aim should move the rear-wall top upward; restore if it does not.
if base[0] is None or trial[0] is None or trial[0][1] >= base[0][1]:
    panorama.rotation_euler = base_rotation
chosen = project_points()
print('Landmark | reference estimate | base projection | lower-aim trial | final')
for (name, _, ref), a, b, c in zip(landmarks, base, trial, chosen):
    fmt = lambda uv: None if uv is None else tuple(round(v,3) for v in uv)
    print(name, ref, fmt(a), fmt(b), fmt(c))
