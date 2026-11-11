# Reference inventory (normalized image bounds, approximate):
# - Cleanroom: full image; pale walls, ceiling grid and recessed lights. Floor is
#   mostly hidden by people and equipment.
# - Foreground operator: x .17-.69, y 0-1; white coat, hairnet and profile,
#   right arm extended toward the HMI. Lower body is partly occluded.
# - Background worker: x 0-.22, y .14-1; white coat, hairnet, hands at waist.
# - Packaging machine: x .41-1, y .30-1; stainless structure, dark mechanisms,
#   clear guarded enclosure and a pale conveyor running toward the foreground.
# - HMI: x .62-.80, y .06-.45; tilted light screen in a thick frame, supported
#   from the machine by an articulated arm.
# - Product details and much of the machinery behind the guards are uncertain.
#
# Estimated expanded geometry: about 150 primitives, including repeated ceiling
# panels, framing, rollers, actuators, trays, and the two simplified people.
# Each ball, rod, and box is counted as one primitive.

from sceneact import *
import bpy
import math

scene = Scene("Cleanroom packaging line")

# Restrained palette, shared across related components.
wall = (0.75, 0.87, 0.84)
ceiling = (0.77, 0.88, 0.85)
seam = (0.57, 0.72, 0.69)
white = (0.91, 0.96, 0.94)
coat = (0.91, 0.96, 0.94)
coat_shadow = (0.72, 0.84, 0.82)
skin = (0.78, 0.58, 0.47)
hairnet = (0.67, 0.81, 0.79)
steel = (0.47, 0.59, 0.58)
steel_light = (0.72, 0.81, 0.79)
dark = (0.10, 0.18, 0.18)
black = (0.055, 0.09, 0.09)
belt_color = (0.82, 0.91, 0.87)
screen_color = (0.78, 0.91, 0.91)
glass = (0.65, 0.86, 0.84)

def add_box(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def add_ball(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)

def add_rod(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

# Architecture. The rear wall and ceiling are intentionally plain.
room = Asset("cleanroom")
add_box(room, "floor", (9, 13, .10), (0, 2, -.07), (0.67, .79, .76))
add_box(room, "back_wall", (9, .12, 3.55), (0, 7.7, 1.75), wall)
add_box(room, "right_wall", (.12, 13, 3.55), (4.45, 1.3, 1.75), (0.73, .85, .82))
add_box(room, "ceiling", (9, 13, .10), (0, 1.3, 3.52), ceiling)
for i, x in enumerate((-3.6, -1.8, 0, 1.8, 3.6)):
    add_box(room, "ceiling_long_seam_%d" % i, (.025, 12, .015),
            (x, 1.3, 3.455), seam)
for i, y in enumerate((-3, -1, 1, 3, 5, 7)):
    add_box(room, "ceiling_cross_seam_%d" % i, (9, .025, .015),
            (0, y, 3.45), seam)
for ix, x in enumerate((-2.7, -.9, .9, 2.7)):
    for iy, y in enumerate((-1.7, .3, 2.3, 4.3, 6.3)):
        add_box(room, "recessed_panel_%d_%d" % (ix, iy), (1.12, .67, .018),
                (x, y, 3.435), (0.96, 1.0, .98))
for i, x in enumerate((-3, -1, 1, 3)):
    add_box(room, "floor_seam_x_%d" % i, (.012, 12, .006), (x, 1, -.012), seam)
for i, y in enumerate((0, 3, 6)):
    add_box(room, "floor_seam_y_%d" % i, (9, .012, .006), (0, y, -.011), seam)
scene.include("architecture", room)

# Machine runs along Y; its front conveyor end is nearest the camera.
machine = Asset("packaging_machine")
add_box(machine, "lower_cabinet", (1.70, 3.1, .74), (1.05, 1.65, .43), steel)
add_box(machine, "cabinet_front", (1.67, .035, .62), (1.05, .085, .43), steel_light)
add_box(machine, "cabinet_side_panel", (.035, 2.95, .58), (1.91, 1.65, .44), (0.60, .72, .70))
add_box(machine, "main_deck", (1.93, 3.55, .11), (1.05, 1.54, .89), steel_light)
for x in (.17, 1.93):
    for y in (.03, 3.1):
        add_box(machine, "support_%s_%s" % (x,y), (.10,.10,.84), (x,y,.43), dark)
# Conveyor: an extended light belt with darker side rails and visible end roller.
add_box(machine, "conveyor_belt", (.91, 4.05, .09), (1.10, .72, .98), belt_color)
for x in (.60, 1.60):
    add_box(machine, "belt_side_rail_%s" % x, (.09, 4.15, .14), (x, .72, 1.02), steel_light)
    add_box(machine, "belt_edge_dark_%s" % x, (.035, 4.10, .045), (x, .72, 1.11), dark)
add_rod(machine, "front_end_roller", (.65,-1.34,.99), (1.55,-1.34,.99), .075, steel)
for i, y in enumerate((.55, 1.20, 1.85, 2.50)):
    add_box(machine, "product_tray_%d" % i, (.58, .32, .035),
            (1.10, y, 1.045), (0.86, .91, .81))
    add_box(machine, "product_in_tray_%d" % i, (.43,.22,.045),
            (1.10, y, 1.085), (0.75,.83,.67))

# Mechanical uprights and crossbars; machinery is visible behind the guard.
for x in (.25, 1.84):
    for y in (.65, 2.65):
        add_box(machine, "frame_post_%s_%s" % (x,y), (.09,.09,1.18),
                (x,y,1.51), steel)
for z in (1.24, 1.97):
    for x in (.25, 1.84):
        add_box(machine, "long_profile_%s_%s" % (x,z), (.075,2.1,.075),
                (x,1.65,z), steel_light)
    for y in (.65, 2.65):
        add_box(machine, "cross_profile_%s_%s" % (y,z), (1.65,.075,.075),
                (1.045,y,z), steel_light)
add_box(machine, "upper_mechanism_housing", (1.10,.65,.23), (1.05,2.05,1.78), dark)
add_box(machine, "upper_steel_cover", (1.25,.71,.10), (1.05,2.05,1.94), steel)
for i, x in enumerate((.58, .91, 1.24, 1.57)):
    add_rod(machine, "pneumatic_cylinder_%d" % i, (x,2.02,1.45), (x,2.02,1.76), .052, steel_light)
    add_rod(machine, "piston_rod_%d" % i, (x,2.02,1.30), (x,2.02,1.45), .021, dark)
    add_box(machine, "actuator_foot_%d" % i, (.19,.18,.06), (x,2.02,1.29), steel)
for i, y in enumerate((1.27, 1.55, 1.83, 2.11, 2.39)):
    add_rod(machine, "transverse_roller_%d" % i, (.54,y,1.13), (1.57,y,1.13), .035, steel)
add_rod(machine, "linkage_left", (.39,2.34,1.38), (.64,2.10,1.73), .027, dark)
add_rod(machine, "linkage_right", (1.70,2.34,1.38), (1.45,2.10,1.73), .027, dark)
add_box(machine, "nameplate", (.31,.015,.11), (.43,.594,1.49), white)
add_box(machine, "nameplate_mark", (.20,.008,.013), (.43,.582,1.50), dark)

# Clear guard panels and their slim frames. Their transparency preserves the
# layered view of the working mechanisms.
guard = Asset("transparent_safety_guard")
for x in (.13, 1.97):
    add_box(guard, "side_panel_%s" % x, (.018,2.8,.84),
            (x,1.43,1.36), glass, .16)
    for y in (.03, 1.43, 2.83):
        add_box(guard, "side_vertical_%s_%s" % (x,y), (.045,.045,.89),
                (x,y,1.36), steel_light)
    for z in (.92,1.80):
        add_box(guard, "side_horizontal_%s_%s" % (x,z), (.045,2.84,.045),
                (x,1.43,z), steel_light)
add_box(guard, "front_panel", (1.84,.018,.84), (1.05,.03,1.36), glass, .13)
for z in (.92,1.80):
    add_box(guard, "front_crossbar_%s" % z, (1.88,.045,.045),
            (1.05,.03,z), steel_light)
scene.include("machine_guard", guard)
scene.include("machine", machine)

# HMI and articulated support, placed high over the working area.
hmi = Asset("articulated_hmi")
add_rod(hmi, "mount_post", (1.77,2.45,1.85), (1.77,2.45,2.42), .075, steel)
add_ball(hmi, "lower_joint", (1.77,2.45,2.42), (.11,.11,.11), dark)
add_rod(hmi, "arm_lower", (1.77,2.45,2.42), (2.05,2.06,2.62), .075, steel)
add_ball(hmi, "elbow_joint", (2.05,2.06,2.62), (.105,.105,.105), dark)
add_rod(hmi, "arm_upper", (2.05,2.06,2.62), (1.82,1.70,2.75), .07, steel_light)
# Screen is tilted back and turned slightly toward the operator.
panel = Asset("touchscreen_panel")
add_box(panel, "outer_bezel", (1.00,.13,.83), (1.56,1.65,2.74), steel_light)
add_box(panel, "dark_inner_border", (.88,.025,.71), (1.56,1.565,2.74), (0.28,.38,.40))
add_box(panel, "illuminated_display", (.78,.015,.61), (1.56,1.545,2.74), screen_color)
add_box(panel, "display_sidebar", (.07,.008,.57), (1.24,1.533,2.74), (.64,.76,.83))
panel.turn(axis="y", degrees=-12, pivot=(1.56,1.65,2.74))
panel.turn(axis="z", degrees=-12, pivot=(1.56,1.65,2.74))
hmi.include("panel", panel)
scene.include("hmi", hmi)

# People are deliberately simplified scale figures with separate coat, limbs,
# hairnet and head. The foreground hand meets the lower left part of the HMI.
people = Asset("staff")
operator = Asset("foreground_operator")
add_box(operator, "coat_body", (.67,.39,1.12), (-.72,.30,1.17), coat)
add_box(operator, "coat_skirt", (.78,.43,.48), (-.72,.30,.43), coat)
add_box(operator, "left_leg", (.22,.23,.56), (-.92,.31,.28), coat_shadow)
add_box(operator, "right_leg", (.22,.23,.56), (-.53,.31,.28), coat_shadow)
add_box(operator, "left_shoe", (.27,.36,.10), (-.92,.22,.06), dark)
add_box(operator, "right_shoe", (.27,.36,.10), (-.53,.22,.06), dark)
add_ball(operator, "head", (-.68,.29,2.06), (.19,.17,.25), skin)
add_ball(operator, "hairnet", (-.73,.33,2.22), (.23,.19,.17), hairnet)
add_ball(operator, "nose", (-.49,.19,2.06), (.06,.06,.055), skin)
add_box(operator, "collar", (.40,.34,.13), (-.72,.28,1.77), white)
# Upper arm slopes across the body, forearm reaches the touchscreen.
add_rod(operator, "raised_upper_sleeve", (-.43,.22,1.70), (.22,.46,1.80), .16, coat)
add_rod(operator, "raised_fore_sleeve", (.22,.46,1.80), (.88,1.00,2.25), .125, coat)
add_ball(operator, "operating_hand", (.92,1.04,2.28), (.105,.08,.075), skin)
add_rod(operator, "other_sleeve", (-.99,.27,1.67), (-1.05,.19,1.04), .14, coat)
add_ball(operator, "other_hand", (-1.05,.17,1.00), (.09,.08,.10), skin)
people.include("operator", operator)

worker = Asset("background_worker")
add_box(worker, "coat_body", (.58,.35,1.02), (-2.25,3.2,1.10), coat)
add_box(worker, "coat_lower", (.66,.38,.48), (-2.25,3.2,.42), white)
for x in (-2.42,-2.09):
    add_box(worker, "leg_%s" % x, (.17,.19,.52), (x,3.2,.26), dark)
    add_box(worker, "shoe_%s" % x, (.22,.30,.08), (x,3.13,.05), black)
add_ball(worker, "head", (-2.25,3.2,1.88), (.16,.15,.21), skin)
add_ball(worker, "hairnet", (-2.25,3.23,2.02), (.20,.17,.14), hairnet)
add_box(worker, "glasses", (.27,.025,.035), (-2.25,3.045,1.91), dark)
add_rod(worker, "left_sleeve", (-2.50,3.2,1.52), (-2.37,3.02,1.05), .115, coat)
add_rod(worker, "right_sleeve", (-2.0,3.2,1.52), (-2.14,3.02,1.05), .115, coat)
add_ball(worker, "hands", (-2.25,3.0,1.06), (.15,.08,.075), skin)
people.include("background_worker", worker)
scene.include("staff", people)

realize(scene)

# Create a cool cleanroom world after realization.
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
background.inputs["Color"].default_value = (.72,.88,.85,1)
background.inputs["Strength"].default_value = .7

set_view((0,-8.8,2.42), (0,1.20,1.65), lens=37)
area_emitter((0,-2,3.35), power=750, size=5, target=(0,1,1), color=(.86,1,.97))
area_emitter((-2,3,3.35), power=550, size=4, target=(0,1,1), color=(.88,1,.98))
area_emitter((3,2,3.25), power=500, size=3, target=(1,1,1.2), color=(.82,.98,.96))

# Use the fixed runner's renderer and output policy. Materials created by
# SceneAct remain editable; adjust their broad surface response where possible.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    p = mat.node_tree.nodes.get("Principled BSDF")
    if p:
        c = p.inputs["Base Color"].default_value
        if .40 < c[0] < .75 and .48 < c[1] < .83 and abs(c[0]-c[1]) < .18:
            p.inputs["Metallic"].default_value = .35
            p.inputs["Roughness"].default_value = .32
        else:
            p.inputs["Roughness"].default_value = .56

sc.camera.data.dof.use_dof = True
sc.camera.data.dof.focus_distance = 9.0
sc.camera.data.dof.aperture_fstop = 8.0
