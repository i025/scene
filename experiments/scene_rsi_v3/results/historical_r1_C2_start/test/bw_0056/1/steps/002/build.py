# Reference inventory, approximate normalized image bounds:
# Cleanroom: full frame; pale teal walls and ceiling, recessed rectangular lights;
# floor mostly hidden. Exact rear wall and room depth are uncertain.
# Foreground operator: x=.17-.68, y=0-1; hairnet, profile, white coat and
# raised sleeve, with the hand touching the HMI. Lower body is partly occluded.
# Background worker: x=0-.22, y=.14-1; hairnet, coat, glasses and hands.
# Packaging machine: x=.41-1, y=.34-1; dark upper mechanisms, metal frame,
# clear enclosure, and pale conveyor projecting toward the lower right.
# HMI: x=.62-.80, y=.06-.45; portrait-like tilted screen, metal bezel, arm.
# Right-side equipment and obscured machine internals are only partly visible.
#
# Review of previous rendering: the entire scene appeared too small and distant,
# with too much floor, an intrusive left wall, and a small square HMI. Move the
# viewpoint closer, make the operator and equipment fill the image, elongate
# the HMI, and strengthen the dark machine mechanisms and material contrast.
# Approximate expanded count: architecture 35; equipment and guard 75;
# HMI 11; people 35; right-side fittings 15: about 171 primitives total.
# Each box, ball and rod is one mesh; no fillets or Boolean operations.

from sceneact import *
import bpy
import math

scene = Scene("Cleanroom packaging line")

wall = (0.66, 0.79, 0.76)
ceiling = (0.72, 0.84, 0.81)
seam = (0.49, 0.65, 0.62)
white = (0.86, 0.92, 0.90)
coat = (0.86, 0.93, 0.91)
coat_shadow = (0.70, 0.82, 0.80)
skin = (0.70, 0.46, 0.35)
skin_light = (0.82, 0.59, 0.46)
hairnet = (0.57, 0.73, 0.71)
steel = (0.42, 0.52, 0.51)
steel_light = (0.64, 0.73, 0.71)
dark = (0.065, 0.10, 0.10)
black = (0.025, 0.045, 0.045)
belt = (0.82, 0.91, 0.88)
glass = (0.62, 0.82, 0.80)

def B(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def E(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

room = Asset("cleanroom_architecture")
B(room, "floor", (11, 15, .10), (0, 2, -.07), (0.60, .73, .70))
B(room, "rear_wall", (11, .10, 3.45), (0, 7.8, 1.70), wall)
B(room, "right_wall", (.10, 15, 3.45), (4.9, 1.5, 1.70), (0.68, .80, .77))
B(room, "ceiling", (11, 15, .10), (0, 1.5, 3.42), ceiling)
for i, x in enumerate((-4, -2, 0, 2, 4)):
    B(room, "ceiling_long_joint_%d" % i, (.025, 14, .014),
      (x, 1.5, 3.36), seam)
for i, y in enumerate((-3, -1, 1, 3, 5, 7)):
    B(room, "ceiling_cross_joint_%d" % i, (10, .025, .014),
      (0, y, 3.36), seam)
for i, x in enumerate((-3, -1, 1, 3)):
    for j, y in enumerate((-2, 0, 2, 4, 6)):
        B(room, "ceiling_light_%d_%d" % (i, j), (1.0, .72, .018),
          (x, y, 3.345), (0.96, 1.0, .98))
for i, x in enumerate((-3, -1, 1, 3)):
    B(room, "floor_joint_x_%d" % i, (.012, 14, .006),
      (x, 1.5, -.013), seam)
for i, y in enumerate((0, 3, 6)):
    B(room, "floor_joint_y_%d" % i, (10, .012, .006),
      (0, y, -.012), seam)
scene.include("architecture", room)

# Machine extends away from the camera along Y.
machine = Asset("packaging_machine")
B(machine, "lower_stainless_body", (1.64, 2.85, .72),
  (1.08, 1.25, .43), steel)
B(machine, "front_body_panel", (1.60, .035, .60),
  (1.08, -.19, .43), steel_light)
B(machine, "side_body_panel", (.035, 2.78, .59),
  (1.91, 1.25, .44), (0.53, .64, .62))
B(machine, "work_deck", (1.90, 3.13, .11),
  (1.08, 1.19, .88), steel_light)
for x in (.20, 1.96):
    for y in (-.25, 2.65):
        B(machine, "base_support_%s_%s" % (x, y), (.10, .10, .82),
          (x, y, .43), dark)

conveyor = Asset("conveyor")
B(conveyor, "belt", (.88, 3.95, .09), (1.10, .27, .98), belt)
for x in (.61, 1.59):
    B(conveyor, "side_rail_%s" % x, (.09, 4.0, .14),
      (x, .27, 1.02), steel_light)
    B(conveyor, "dark_rail_edge_%s" % x, (.035, 3.95, .04),
      (x, .27, 1.10), dark)
R(conveyor, "front_end_roller", (.65, -1.70, .99),
  (1.55, -1.70, .99), .075, steel)
for i, y in enumerate((.35, .90, 1.45, 2.00)):
    B(conveyor, "tray_%d" % i, (.58, .31, .025),
      (1.10, y, 1.045), (0.78, .85, .76))
    B(conveyor, "product_%d" % i, (.44, .21, .035),
      (1.10, y, 1.075), (0.69, .78, .60))
machine.include("conveyor", conveyor)

mechanism = Asset("mechanical_internals")
for x in (.28, 1.84):
    for y in (.35, 2.40):
        B(mechanism, "upright_%s_%s" % (x, y), (.085, .085, 1.20),
          (x, y, 1.50), steel)
for z in (1.23, 1.95):
    for x in (.28, 1.84):
        B(mechanism, "long_profile_%s_%s" % (x, z), (.075, 2.12, .075),
          (x, 1.38, z), steel_light)
    for y in (.35, 2.40):
        B(mechanism, "cross_profile_%s_%s" % (y, z), (1.62, .075, .075),
          (1.06, y, z), steel)
B(mechanism, "dark_upper_housing", (1.10, .68, .25),
  (1.05, 1.83, 1.79), dark)
B(mechanism, "upper_cover", (1.22, .72, .09),
  (1.05, 1.83, 1.96), steel)
B(mechanism, "black_vertical_drive", (.29, .34, .52),
  (1.53, 1.80, 2.12), black)
for i, x in enumerate((.56, .88, 1.20, 1.52)):
    R(mechanism, "pneumatic_cylinder_%d" % i,
      (x, 1.81, 1.44), (x, 1.81, 1.75), .052, steel_light)
    R(mechanism, "piston_%d" % i,
      (x, 1.81, 1.28), (x, 1.81, 1.44), .020, dark)
    B(mechanism, "actuator_foot_%d" % i, (.18, .17, .055),
      (x, 1.81, 1.26), steel)
for i, y in enumerate((.70, .98, 1.26, 1.54, 1.82, 2.10)):
    R(mechanism, "guide_roller_%d" % i,
      (.56, y, 1.13), (1.55, y, 1.13), .033, steel)
R(mechanism, "left_linkage", (.38, 2.12, 1.35), (.65, 1.85, 1.72), .026, dark)
R(mechanism, "right_linkage", (1.72, 2.12, 1.35), (1.45, 1.85, 1.72), .026, dark)
B(mechanism, "nameplate", (.30, .018, .10), (.45, .295, 1.48), white)
B(mechanism, "nameplate_mark", (.19, .008, .012), (.45, .282, 1.49), dark)
machine.include("mechanism", mechanism)
scene.include("packaging_machine", machine)

guard = Asset("transparent_guard")
for x in (.13, 1.98):
    B(guard, "side_glazing_%s" % x, (.012, 2.75, .84),
      (x, 1.02, 1.36), glass, .12)
    for y in (-.35, 1.02, 2.39):
        B(guard, "side_frame_post_%s_%s" % (x, y), (.04, .04, .88),
          (x, y, 1.36), steel_light)
    for z in (.92, 1.80):
        B(guard, "side_frame_rail_%s_%s" % (x, z), (.04, 2.78, .04),
          (x, 1.02, z), steel_light)
B(guard, "front_glazing", (1.85, .012, .84),
  (1.055, -.35, 1.36), glass, .10)
for z in (.92, 1.80):
    B(guard, "front_frame_%s" % z, (1.88, .04, .04),
      (1.055, -.35, z), steel_light)
scene.include("machine_guard", guard)

# Vertical, slightly tilted HMI. The display faces toward the camera/operator.
hmi = Asset("articulated_hmi")
R(hmi, "mount_post", (1.82, 1.95, 1.85), (1.82, 1.95, 2.35), .075, steel)
E(hmi, "lower_joint", (1.82, 1.95, 2.35), (.105, .105, .105), dark)
R(hmi, "lower_arm", (1.82, 1.95, 2.35), (2.04, 1.40, 2.56), .065, steel)
E(hmi, "elbow", (2.04, 1.40, 2.56), (.10, .10, .10), dark)
R(hmi, "upper_arm", (2.04, 1.40, 2.56), (1.64, .94, 2.58), .065, steel_light)
panel = Asset("touchscreen_panel")
B(panel, "outer_bezel", (.73, .12, 1.08), (1.40, .82, 2.55), steel_light)
B(panel, "dark_inner_border", (.64, .018, .98), (1.40, .750, 2.55), (0.30, .38, .39))
B(panel, "screen", (.55, .012, .87), (1.40, .735, 2.55), (0.75, .88, .91))
B(panel, "screen_side_strip", (.045, .008, .82), (1.16, .727, 2.55), (.55, .68, .78))
panel.turn(axis="y", degrees=16, pivot=(1.40, .82, 2.55))
panel.turn(axis="z", degrees=-8, pivot=(1.40, .82, 2.55))
hmi.include("panel", panel)
scene.include("hmi", hmi)

# Visible small fittings toward the right edge.
fittings = Asset("right_hand_rail_fittings")
for i, x in enumerate((2.10, 2.43, 2.75)):
    B(fittings, "post_%d" % i, (.07, .07, .72), (x, -.15, .63), steel_light)
    B(fittings, "post_cap_%d" % i, (.11, .11, .06), (x, -.15, 1.02), black)
    B(fittings, "bracket_%d" % i, (.16, .14, .10), (x, -.15, .70), steel)
R(fittings, "horizontal_rail", (1.90, -.15, .83), (2.95, -.15, .83), .035, steel_light)
scene.include("right_side_fittings", fittings)

staff = Asset("staff")
operator = Asset("foreground_operator")
# Rounded coat volume and shoulders retain the broad silhouette of the photo.
E(operator, "coat_torso", (-.82, -.66, 1.23), (.37, .25, .66), coat)
B(operator, "coat_lower", (.70, .43, .64), (-.83, -.66, .48), coat)
E(operator, "shoulder", (-.82, -.66, 1.68), (.34, .23, .18), white)
B(operator, "collar", (.34, .32, .12), (-.78, -.68, 1.77), white)
B(operator, "left_leg", (.23, .25, .47), (-1.02, -.65, .25), coat_shadow)
B(operator, "right_leg", (.23, .25, .47), (-.61, -.65, .25), coat_shadow)
E(operator, "head", (-.75, -.65, 2.00), (.18, .15, .23), skin_light)
E(operator, "hairnet", (-.81, -.62, 2.15), (.22, .18, .16), hairnet)
E(operator, "nose", (-.57, -.72, 2.01), (.055, .045, .045), skin_light)
R(operator, "raised_upper_sleeve", (-.57, -.70, 1.67),
  (-.10, -.50, 1.72), .16, coat)
R(operator, "raised_fore_sleeve", (-.10, -.50, 1.72),
  (.58, .12, 2.14), .13, coat)
E(operator, "hand", (.63, .16, 2.18), (.09, .07, .07), skin_light)
R(operator, "touching_finger", (.65, .16, 2.19), (.75, .23, 2.25), .025, skin_light)
R(operator, "other_sleeve", (-1.08, -.65, 1.63),
  (-1.12, -.62, 1.10), .13, coat)
staff.include("foreground_operator", operator)

worker = Asset("background_worker")
E(worker, "coat_torso", (-2.05, 2.55, 1.20), (.31, .20, .58), coat)
B(worker, "coat_lower", (.59, .36, .52), (-2.05, 2.55, .53), white)
for x in (-2.22, -1.88):
    B(worker, "leg_%s" % x, (.16, .20, .43), (x, 2.55, .22), black)
E(worker, "face", (-2.05, 2.53, 1.88), (.15, .14, .20), skin_light)
E(worker, "hairnet", (-2.05, 2.55, 2.02), (.19, .16, .13), hairnet)
B(worker, "glasses", (.25, .025, .035), (-2.05, 2.385, 1.91), dark)
R(worker, "left_sleeve", (-2.30, 2.55, 1.53),
  (-2.16, 2.38, 1.09), .11, coat)
R(worker, "right_sleeve", (-1.80, 2.55, 1.53),
  (-1.94, 2.38, 1.09), .11, coat)
E(worker, "hands", (-2.05, 2.36, 1.09), (.13, .07, .07), skin)
staff.include("background_worker", worker)
scene.include("staff", staff)

realize(scene)

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
background.inputs["Color"].default_value = (.68, .82, .79, 1)
background.inputs["Strength"].default_value = .35

set_view((0, -4.15, 1.95), (0, .70, 1.65), lens=35)
area_emitter((-1, -2, 3.30), power=360, size=4,
             target=(0, .5, 1.2), color=(.88, 1, .97))
area_emitter((1, 2, 3.28), power=320, size=4,
             target=(.5, 1, 1.1), color=(.86, 1, .97))
area_emitter((3, 0, 3.20), power=200, size=3,
             target=(1, 1, 1.2), color=(.82, .97, .95))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    p = mat.node_tree.nodes.get("Principled BSDF")
    if p is None:
        continue
    c = p.inputs["Base Color"].default_value
    if .35 < c[0] < .67 and .43 < c[1] < .76 and abs(c[0] - c[1]) < .18:
        p.inputs["Metallic"].default_value = .45
        p.inputs["Roughness"].default_value = .30
    else:
        p.inputs["Roughness"].default_value = .55

sc.camera.data.dof.use_dof = True
sc.camera.data.dof.focus_distance = 3.5
sc.camera.data.dof.aperture_fstop = 8.0
