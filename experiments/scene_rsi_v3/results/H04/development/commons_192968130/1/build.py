from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and comparison with the second render, normalized coordinates:
# - Slatted back wall: reference top near y=.11, render near y=.15; both
#   continue to the floor around y=.76. The door overlaps this wall.
# - Door: reference approximately (.31,.29)-(.45,.77), render approximately
#   (.30,.28)-(.43,.77). Widen its right edge, keeping the left edge and floor.
# - Low cabinet: reference approximately (0,.65)-(.20,.80), render approximately
#   (0,.67)-(.21,.80); retain its crop and black/white silhouette.
# - Counter: reference left edge from (.46,.59) to (.36,1); render roughly
#   (.45,.61) to (.34,1). Its general slope and overlap with the floor agree.
# - Foreground hob: reference begins around (.40,.77) and its right edge reaches
#   approximately .79 at the bottom; render starts around (.38,.76) and reaches
#   about .88. Narrow it and shift its left edge slightly right.
# - Sink: reference roughly (.46,.64)-(.62,.70); render roughly (.47,.62)-
#   (.60,.65). Extend it toward the camera to increase its visible depth.
# - Upper cabinets: reference is a large dark mass above the backsplash, with
#   its back end around x=.46 and a narrow metallic underside. Render has a
#   much larger pale underside and the dark mass begins around x=.33 at the top.
#   Move the cabinet's left face right and darken its underside; retain a slim
#   extractor and the light strip. The edge slopes converge toward the rear.
# - Pale backsplash fills the right side. Reference is glossy and softly lit;
#   render appears flat and white, with a large triangular light region. Darker
#   overhead surfaces and a restrained glossy finish address this visible area.
# - Ceiling, tiled floor, switches, stone and black sink remain separate assets.
#   The unseen room and sink interior depth are uncertain.
#
# Ranked corrections: (1) upper cabinet silhouette and light/dark distribution,
# (2) hob size, (3) sink depth, (4) small door width and wall-height changes.
# Cabinet left-face x moves right, narrowing its projected foreground underside;
# its lowered dark fascia fills more of the upper image. Hob width decreases
# and its center shifts right; sink near edge moves downward in the image.
# Camera position, target, and lens stay unchanged: background and counter anchors
# do not show a common displacement. A small aim trial is projected and restored.
# Computed landmark positions printed below are distinct from visible contours.
# Estimated expanded primitives: 46 slats, 25 floor joints, 30 stone veins,
# about 35 other boxes/rods, and four curve rings: approximately 136 meshes
# plus four curves. No fillets, booleans, or cloned assemblies.

random.seed(13)
scene = Scene("Kitchen interior")

# Independent camera and scene parameters.
back_y = 3.3
wall_height = 3.72
counter_left = 0.50
counter_right = 1.78
counter_z = 0.91
camera_position = (0.85, -4.25, 1.67)
camera_target = (0.85, 3.3, 1.54)
camera_lens = 32

wood_mid = (0.29, 0.105, 0.035)
wood_light = (0.40, 0.17, 0.055)
stone = (0.76, 0.74, 0.68)

room = Asset("Architecture")
room.include("floor", box((12, 13, 0.10), center=(-1, 0, -0.05),
                          color=(0.49, 0.47, 0.43)))
room.include("back_wall", box((10, 0.12, wall_height),
                              center=(-1.4, back_y+0.08, wall_height/2),
                              color=(0.65, 0.63, 0.59)))
room.include("right_wall", box((0.12, 9.5, wall_height),
                               center=(counter_right+0.08, -1.4, wall_height/2),
                               color=(0.75, 0.74, 0.71)))
room.include("ceiling", box((10, 9, 0.08),
                            center=(-1.3, -0.5, wall_height+0.04),
                            color=(0.75, 0.74, 0.71)))
for i in range(12):
    room.include("floor_joint_y_%02d" % i,
                 box((8, 0.009, 0.003),
                     center=(-1.5, -4.8+i*0.72, 0.003),
                     color=(0.38, 0.37, 0.35)))
for i in range(13):
    room.include("floor_joint_x_%02d" % i,
                 box((0.009, 9, 0.003),
                     center=(-5.5+i*0.72, -0.8, 0.004),
                     color=(0.39, 0.38, 0.35)))
scene.include("architecture", room)

slats = Asset("Slatted wood feature wall")
slat_height = 3.65
slats.include("dark_backing", box((5.7, 0.05, slat_height),
                                  center=(-2.43, back_y-0.005, slat_height/2),
                                  color=(0.065, 0.025, 0.012)))
for i in range(46):
    slats.include("wood_slat_%02d" % i,
                  box((0.075, 0.048, slat_height),
                      center=(-5.20+i*0.12, back_y-0.047, slat_height/2),
                      color=wood_mid if i % 4 else wood_light))
scene.include("slatted_wall", slats)

door = Asset("White door")
door_x = -0.17
door_width = 1.12
door_height = 2.65
door.include("frame", box((door_width+0.13, 0.065, door_height+0.08),
                          center=(door_x, back_y-0.091, (door_height+0.08)/2),
                          color=(0.78, 0.78, 0.76)))
door.include("door_leaf", box((door_width, 0.04, door_height),
                              center=(door_x, back_y-0.13, door_height/2+0.025),
                              color=(0.90, 0.90, 0.88)))
door.include("handle_plate", box((0.055, 0.012, 0.13),
                                 center=(door_x-0.38, back_y-0.158, 1.20),
                                 color=(0.55, 0.55, 0.53)))
door.include("handle", rod(0.012, start=(door_x-0.39, back_y-0.18, 1.22),
                           end=(door_x-0.26, back_y-0.18, 1.22),
                           color=(0.55, 0.55, 0.53)))
scene.include("door", door)

switches = Asset("Wall switches")
switches.include("light_switch", box((0.13, 0.014, 0.09),
                                      center=(-1.03, back_y-0.084, 1.20),
                                      color=(0.91, 0.91, 0.88)))
switches.include("low_outlet", box((0.10, 0.014, 0.10),
                                    center=(-1.00, back_y-0.084, 0.26),
                                    color=(0.90, 0.90, 0.87)))
scene.include("switches", switches)

low_unit = Asset("Low cabinet at left")
low_unit.include("outer_carcass", box((1.65, 0.46, 0.59),
                                      center=(-2.38, back_y-0.32, 0.30),
                                      color=(0.035, 0.034, 0.031)))
low_unit.include("white_front", box((1.43, 0.02, 0.34),
                                     center=(-2.38, back_y-0.56, 0.22),
                                     color=(0.86, 0.86, 0.83)))
low_unit.include("wood_trim", box((1.45, 0.025, 0.045),
                                   center=(-2.38, back_y-0.575, 0.43),
                                   color=wood_mid))
scene.include("low_cabinet", low_unit)

counter_mid = (counter_left+counter_right)/2
counter_width = counter_right-counter_left
kitchen = Asset("Kitchen counter and backsplash")
kitchen.include("base_cabinets", box((counter_width, 8.1, 0.84),
                                     center=(counter_mid, -0.75, 0.42),
                                     color=(0.25, 0.12, 0.055)))
kitchen.include("countertop", box((counter_width+0.06, 8.15, 0.075),
                                  center=(counter_mid, -0.75, counter_z),
                                  color=stone))
kitchen.include("back_end_panel", box((counter_width, 0.08, 1.12),
                                      center=(counter_mid, back_y-0.09, 1.48),
                                      color=(0.25, 0.10, 0.035)))
kitchen.include("backsplash", box((0.035, 8.0, 1.20),
                                  center=(counter_right-0.03, -0.75, 1.54),
                                  color=(0.76, 0.75, 0.72)))
scene.include("kitchen", kitchen)

veins = Asset("Countertop stone veins")
for i in range(30):
    x = random.uniform(counter_left+0.05, counter_right-0.08)
    y = random.uniform(-4.4, 3.0)
    length = random.uniform(0.07, 0.30)
    dx = random.uniform(-0.07, 0.07)
    veins.include("vein_%02d" % i,
                  rod(0.0025, start=(x, y, counter_z+0.039),
                      end=(x+dx, y+length, counter_z+0.039),
                      color=(0.39, 0.36, 0.31)))
scene.include("stone_veins", veins)

sink = Asset("Inset black sink")
sink.include("dark_rim", box((0.88, 1.28, 0.014),
                             center=(1.09, 1.62, counter_z+0.046),
                             color=(0.10, 0.09, 0.075)))
sink.include("basin", box((0.76, 1.14, 0.016),
                          center=(1.09, 1.62, counter_z+0.055),
                          color=(0.018, 0.019, 0.018)))
sink.include("inner_edge", box((0.70, 0.018, 0.006),
                               center=(1.09, 2.15, counter_z+0.065),
                               color=(0.31, 0.28, 0.23)))
scene.include("sink", sink)

hob = Asset("Black glass cooktop")
hob.include("glass", box((0.76, 1.65, 0.018),
                         center=(1.10, -1.80, counter_z+0.050),
                         color=(0.008, 0.012, 0.014)))
scene.include("cooktop", hob)

overhead = Asset("Upper wood cabinets and extractor")
cab_left = 0.79
cab_right = 1.81
cab_center = (cab_left+cab_right)/2
cab_width = cab_right-cab_left
overhead.include("cabinet_mass", box((cab_width, 7.8, 1.15),
                                    center=(cab_center, -0.73, 2.75),
                                    color=(0.115, 0.042, 0.014)))
overhead.include("lower_fascia", box((cab_width, 7.8, 0.12),
                                     center=(cab_center, -0.73, 2.14),
                                     color=(0.075, 0.026, 0.008)))
overhead.include("front_vertical_end", box((0.055, 0.10, 1.15),
                                           center=(cab_left+0.025, 3.08, 2.75),
                                           color=(0.09, 0.034, 0.012)))
overhead.include("extractor", box((0.58, 3.4, 0.035),
                                  center=(1.48, -1.75, 2.065),
                                  color=(0.35, 0.34, 0.31)))
overhead.include("extractor_dark_inset", box((0.42, 2.8, 0.010),
                                             center=(1.46, -1.65, 2.042),
                                             color=(0.16, 0.15, 0.13)))
overhead.include("under_cabinet_light", box((0.025, 7.3, 0.018),
                                           center=(0.86, -0.65, 2.065),
                                           color=(1.0, 0.90, 0.66)))
scene.include("upper_cabinets", overhead)

realize(scene)

# Editable outlines on the glass surface.
ring_mat = bpy.data.materials.new("Burner ring material")
ring_mat.diffuse_color = (0.09, 0.095, 0.09, 1)
for j, (cx, cy, radius) in enumerate([(0.94, -1.34, 0.17),
                                      (1.25, -1.34, 0.16),
                                      (0.94, -2.15, 0.17),
                                      (1.25, -2.15, 0.16)]):
    curve = bpy.data.curves.new("Burner ring %d" % j, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0025
    curve.bevel_resolution = 1
    spline = curve.splines.new("POLY")
    spline.points.add(47)
    for i, point in enumerate(spline.points):
        a = 2*math.pi*i/48
        point.co = (cx+radius*math.cos(a), cy+radius*math.sin(a),
                    counter_z+0.061, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new("Cooktop burner %d" % j, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(ring_mat)

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
area_emitter((-3.5, -1.5, 3.4), power=500, size=4.0, target=(0, 2, 0.9))
area_emitter((1.1, -1.0, 2.05), power=150, size=3.5,
             target=(1.2, 0.0, 0.9), color=(1.0, 0.82, 0.62))

# Reference points correspond to actual geometry; the foreground point is a
# particular point on the counter edge, not necessarily the bottom image crop.
landmarks = [
    ("door upper left", (door_x-door_width/2, back_y-0.16, door_height+0.025),
     (0.31, 0.29)),
    ("door lower right", (door_x+door_width/2, back_y-0.16, 0.035),
     (0.45, 0.77)),
    ("counter rear left", (counter_left, back_y-0.13, counter_z+0.038),
     (0.45, 0.59)),
    ("counter foreground edge", (counter_left, -1.1, counter_z+0.038),
     None),
]
cam = sc.camera

def project_table(label):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    for name, p, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
        uv = None if clip.w <= 1e-8 else (
            0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
        print(label, name, "reference", ref, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

project_table("CURRENT")
# Trial aim only: upward aim should move fixed scene points down in the image.
# Restore it because the supported corrections are local geometry changes.
original_rotation = cam.rotation_euler.copy()
trial_target = Vector((camera_target[0], camera_target[1], camera_target[2]+0.08))
cam.rotation_euler = (trial_target-Vector(camera_position)).to_track_quat('-Z', 'Y').to_euler()
project_table("UPWARD_TRIAL")
cam.rotation_euler = original_rotation
bpy.context.view_layer.update()
