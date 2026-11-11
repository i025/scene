from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and approximate normalized image coordinates:
# - Back wall with vertical dark-brown wood slats: (0, .11)-(.46, .76).
# - White door and frame on that wall: (.31, .29)-(.45, .77).
# - Low black-and-white cabinet, cropped at left: (0, .65)-(.20, .80).
# - Pale tiled floor: foreground below approximately y=.76 on the left.
# - Kitchen counter: pale stone left edge runs from (.45, .59) to (.36, 1);
#   its right portion is cropped. A distant black sink and foreground black
#   cooktop interrupt the surface.
# - Glossy pale backsplash occupies much of the right side, under dark wood
#   overhead cabinets and a slim metallic extractor.
# - Major edges: back-wall slats are vertical; counter and cabinet edges
#   converge toward the back at approximately (.46, .58). The door overlaps
#   the slatted wall. Foreground appliances overlap the countertop.
# - The room beyond the image and details behind cabinets are uncertain.
#
# Projection anchors (reference estimates, x right / y down):
# door upper-left (.31,.29); door lower-right (.45,.77);
# counter rear-left (.45,.59); foreground counter left edge (.36,1.0).
# Camera and major dimensions are independent parameters below.
#
# Estimated expanded geometry: approximately 160 boxes and rods total:
# about 45 wall slats, 30 floor grout strips, 30 stone veins, and
# approximately 55 architecture, kitchen, appliance and furniture pieces.

random.seed(13)
scene = Scene("Kitchen interior")

# Major dimensions and camera parameters.
back_y = 3.3
wall_height = 3.05
counter_left = 0.42
counter_right = 2.65
counter_z = 0.91
camera_position = (0.85, -4.25, 1.67)
camera_target = (0.85, 3.3, 1.54)
camera_lens = 32

white = (0.83, 0.82, 0.79)
floor_color = (0.49, 0.47, 0.43)
wood_dark = (0.105, 0.038, 0.014)
wood_mid = (0.29, 0.105, 0.035)
wood_light = (0.40, 0.17, 0.055)
black = (0.012, 0.014, 0.015)
metal = (0.35, 0.35, 0.32)
stone = (0.76, 0.74, 0.68)

room = Asset("Architecture")
room.include("floor", box((12, 13, 0.10), center=(-1, 0, -0.05), color=floor_color))
room.include("back_wall", box((10, 0.12, wall_height), center=(-1.4, back_y+0.08, wall_height/2), color=(0.65, 0.63, 0.59)))
room.include("right_wall", box((0.12, 9.5, wall_height), center=(counter_right+0.08, -1.4, wall_height/2), color=(0.75, 0.74, 0.71)))
room.include("ceiling", box((10, 9, 0.08), center=(-1.3, -0.5, wall_height+0.04), color=(0.75, 0.74, 0.71)))

# Thin grout lines across the tiled floor.
for i in range(12):
    y = -4.8 + i * 0.72
    room.include("floor_joint_y_%02d" % i,
                 box((8, 0.009, 0.003), center=(-1.5, y, 0.003), color=(0.38, 0.37, 0.35)))
for i in range(13):
    x = -5.5 + i * 0.72
    room.include("floor_joint_x_%02d" % i,
                 box((0.009, 9, 0.003), center=(x, -0.8, 0.004), color=(0.39, 0.38, 0.35)))
scene.include("architecture", room)

# Back wall: dark backing with individual narrow vertical wood battens.
slats = Asset("Slatted wood feature wall")
slats.include("dark_backing", box((5.7, 0.05, 2.70),
                                   center=(-2.43, back_y-0.005, 1.35),
                                   color=(0.065, 0.025, 0.012)))
for i in range(46):
    x = -5.20 + i * 0.12
    slats.include("wood_slat_%02d" % i,
                  box((0.075, 0.048, 2.70), center=(x, back_y-0.047, 1.35),
                      color=(wood_mid if i % 4 else wood_light)))
scene.include("slatted_wall", slats)

door = Asset("White door")
door_x = -0.58
door_width = 0.94
door.include("frame", box((door_width+0.13, 0.065, 2.13),
                          center=(door_x, back_y-0.091, 1.065), color=(0.78, 0.78, 0.76)))
door.include("door_leaf", box((door_width, 0.04, 2.01),
                              center=(door_x, back_y-0.13, 1.04), color=(0.90, 0.90, 0.88)))
door.include("handle_plate", box((0.055, 0.012, 0.13),
                                  center=(door_x-0.29, back_y-0.158, 0.99), color=(0.55, 0.55, 0.53)))
door.include("handle", rod(0.012, start=(door_x-0.30, back_y-0.18, 1.01),
                           end=(door_x-0.17, back_y-0.18, 1.01), color=(0.55, 0.55, 0.53)))
scene.include("door", door)

switches = Asset("Wall switches")
switches.include("light_switch", box((0.13, 0.014, 0.09),
                                      center=(-1.28, back_y-0.084, 1.04), color=(0.91, 0.91, 0.88)))
switches.include("low_outlet", box((0.10, 0.014, 0.10),
                                    center=(-1.25, back_y-0.084, 0.24), color=(0.90, 0.90, 0.87)))
scene.include("switches", switches)

low_unit = Asset("Low cabinet at left")
low_unit.include("outer_carcass", box((1.65, 0.46, 0.59),
                                      center=(-4.05, back_y-0.32, 0.30), color=(0.035, 0.034, 0.031)))
low_unit.include("white_front", box((1.43, 0.02, 0.34),
                                     center=(-4.05, back_y-0.56, 0.22), color=(0.86, 0.86, 0.83)))
low_unit.include("wood_trim", box((1.45, 0.025, 0.045),
                                   center=(-4.05, back_y-0.575, 0.43), color=wood_mid))
scene.include("low_cabinet", low_unit)

kitchen = Asset("Kitchen counter and backsplash")
kitchen.include("base_cabinets", box((counter_right-counter_left, 8.1, 0.84),
                                      center=((counter_left+counter_right)/2, -0.75, 0.42),
                                      color=(0.25, 0.12, 0.055)))
kitchen.include("countertop", box((counter_right-counter_left+0.06, 8.15, 0.075),
                                   center=((counter_left+counter_right)/2, -0.75, counter_z),
                                   color=stone))
kitchen.include("back_end_panel", box((counter_right-counter_left, 0.08, 1.12),
                                       center=((counter_left+counter_right)/2, back_y-0.09, 1.48),
                                       color=(0.25, 0.10, 0.035)))
kitchen.include("backsplash", box((0.035, 8.0, 1.20),
                                   center=(counter_right-0.03, -0.75, 1.54),
                                   color=(0.82, 0.82, 0.79)))
scene.include("kitchen", kitchen)

# Sparse short veins in the stone, kept on the horizontal surface.
veins = Asset("Countertop stone veins")
for i in range(30):
    x = random.uniform(counter_left+0.05, counter_right-0.08)
    y = random.uniform(-4.4, 3.0)
    length = random.uniform(0.07, 0.30)
    dx = random.uniform(-0.07, 0.07)
    veins.include("vein_%02d" % i,
                  rod(0.003, start=(x, y, counter_z+0.039),
                      end=(x+dx, y+length, counter_z+0.039),
                      color=(0.39, 0.36, 0.31)))
scene.include("stone_veins", veins)

sink = Asset("Inset black sink")
sink.include("dark_rim", box((1.08, 0.86, 0.014),
                              center=(1.22, 1.82, counter_z+0.046), color=(0.10, 0.09, 0.075)))
sink.include("basin", box((0.94, 0.72, 0.016),
                           center=(1.22, 1.82, counter_z+0.055), color=(0.018, 0.019, 0.018)))
sink.include("inner_edge", box((0.84, 0.018, 0.006),
                                center=(1.22, 2.14, counter_z+0.065), color=(0.31, 0.28, 0.23)))
scene.include("sink", sink)

hob = Asset("Black glass cooktop")
hob.include("glass", box((1.32, 1.65, 0.018),
                          center=(1.24, -1.80, counter_z+0.050), color=(0.008, 0.012, 0.014)))
# Burner rings made as flat curves after SceneAct realization.
scene.include("cooktop", hob)

overhead = Asset("Upper wood cabinets and extractor")
overhead.include("cabinet_mass", box((1.75, 7.8, 0.91),
                                     center=(1.78, -0.73, 2.67), color=(0.16, 0.065, 0.025)))
overhead.include("lower_fascia", box((1.80, 7.8, 0.08),
                                      center=(1.77, -0.73, 2.19), color=(0.11, 0.045, 0.018)))
overhead.include("front_vertical_end", box((0.055, 0.10, 0.90),
                                            center=(0.88, 3.08, 2.67), color=(0.09, 0.034, 0.012)))
# Metallic extractor panel beneath the overhanging upper cabinetry.
overhead.include("extractor", box((1.40, 3.4, 0.065),
                                   center=(1.82, -1.75, 2.14), color=(0.48, 0.47, 0.43)))
overhead.include("extractor_dark_inset", box((0.86, 2.8, 0.012),
                                              center=(1.73, -1.65, 2.103), color=(0.25, 0.24, 0.22)))
overhead.include("under_cabinet_light", box((0.035, 7.3, 0.025),
                                            center=(1.00, -0.65, 2.12), color=(1.0, 0.90, 0.66)))
scene.include("upper_cabinets", overhead)

realize(scene)

# Add thin burner outlines as editable curve objects, on top of the glass.
for j, (cx, cy, radius) in enumerate([(0.98, -1.34, 0.27),
                                       (1.48, -1.34, 0.23),
                                       (0.98, -2.15, 0.27),
                                       (1.48, -2.15, 0.23)]):
    curve = bpy.data.curves.new("Burner ring %d" % j, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.003
    curve.bevel_resolution = 1
    spline = curve.splines.new("POLY")
    spline.points.add(47)
    for i, point in enumerate(spline.points):
        a = 2 * math.pi * i / 48
        point.co = (cx + radius*math.cos(a), cy + radius*math.sin(a),
                    counter_z+0.061, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new("Cooktop burner %d" % j, curve)
    bpy.context.collection.objects.link(obj)
    mat = bpy.data.materials.get("Burner ring material")
    if mat is None:
        mat = bpy.data.materials.new("Burner ring material")
        mat.diffuse_color = (0.09, 0.095, 0.09, 1)
    obj.data.materials.append(mat)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.75, 0.74, 0.71, 1)
background.inputs["Strength"].default_value = 0.55

sc.render.resolution_x = 512
sc.render.resolution_y = 342
sc.render.resolution_percentage = 100
set_view(camera_position, camera_target, lens=camera_lens)
area_emitter((-3.5, -1.5, 3.0), power=500, size=4.0, target=(0, 2, 0.9))
area_emitter((1.4, -1.0, 2.05), power=180, size=3.5, target=(1.2, 0.0, 0.9),
             color=(1.0, 0.82, 0.62))

# A compact numerical check of visible geometry landmarks.
landmarks = [
    ("door upper left", (door_x-door_width/2, back_y-0.16, 2.045), (0.31, 0.29)),
    ("door lower right", (door_x+door_width/2, back_y-0.16, 0.035), (0.45, 0.77)),
    ("counter rear left", (counter_left, back_y-0.13, counter_z+0.038), (0.45, 0.59)),
    ("counter near left", (counter_left, -3.8, counter_z+0.038), (0.36, 1.00)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
                                    y=sc.render.resolution_y,
                                    scale_x=sc.render.pixel_aspect_x,
                                    scale_y=sc.render.pixel_aspect_y)
for name, p, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    uv = None if clip.w <= 1e-8 else (0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
    print("LANDMARK", name, "reference", ref, "projected",
          None if uv is None else tuple(round(v, 3) for v in uv))
