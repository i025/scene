from sceneact import *
import bpy
from mathutils import Vector

# Reference versus second render, approximate normalized image coordinates:
# Background windows: reference x=0-.25, y=.34-.65; render x=0-.36, y=.32-.75.
# Main machine: reference x=.61-.79, y=.30-.67; render x=.54-.75, y=.36-.69.
# Green tank: reference x=.36-.45, y=.53-.77; render x=.29-.36, y=.65-.88.
# Foreground conveyor: reference x=0-.67, y=.72-1; render x=0-.55, y=.79-1.
# Roof beams: reference mostly near-horizontal and converge to the right; rendered
# beams show a stronger diagonal. Both views crop the conveyor at the image edge.
# Rails cross the machinery in both, but the render has a large solid white
# transfer bed where the reference has open silver frames and blue rollers.
#
# Ranked corrections:
# 1. CAMERA_X reduces the oblique viewing angle, making long platform edges
#    more horizontal and shifting the foreground tank right relative to machinery.
#    Camera aim is lowered slightly to move the machine and tank upward.
# 2. TANK_Y moves the tank back toward the platform, lifting its visible contour;
#    MAIN_X moves the main machine locally right without shifting the windows.
# 3. Transfer-bed depth is reduced and separate open frames added, allowing the
#    foreground rollers and gaps to remain visible.
# The roof, wall, machinery, yellow rails, duct paths and stair flights remain
# separate editable assets. Exact hidden machinery and pipe connections are uncertain.
#
# Inventory and image anchors:
# Roof and steel structure (0,0)-(1,.36); strip windows (0,.33)-(.25,.66).
# Elevated machines and railings (.06,.30)-(.98,.78), with duct elbows above.
# Tank (.36,.53)-(.45,.77), overlapping the platform; conveyors (0,.72)-(.67,1).
# Estimated primitive count: hall 61, platforms 15, machines 18, rails 58,
# stairs 69, ducts 19, tank 8, conveyors 110, rear equipment 5; about 363 meshes.

scene = Scene("Workshop")
CAMERA_POS = (4.0, -15.0, 4.5)
CAMERA_TARGET = (0.0, 3.0, 3.05)
CAMERA_LENS = 35
HALL_W, HALL_D, HALL_H = 15.0, 30.0, 7.0
DECK_Z = 2.05
MAIN_X = 3.35
TANK_X, TANK_Y = -0.75, 0.0

C = {
    "floor": (.09, .29, .21), "wall": (.15, .17, .17),
    "steel": (.065, .078, .078), "roof": (.21, .22, .21),
    "window": (.75, .85, .88), "windowframe": (.17, .19, .19),
    "silver": (.56, .59, .58), "bright": (.73, .75, .73),
    "darkmetal": (.22, .25, .24), "yellow": (.95, .62, .015),
    "green": (.015, .28, .20), "blue": (.045, .19, .46),
    "black": (.035, .045, .044), "white": (.80, .82, .79),
}

def bx(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def rd(parent, name, a, b, radius, color):
    if sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-10:
        parent.include(name, rod(radius=radius, start=a, end=b, color=color))

hall = Asset("Hall_structure")
bx(hall, "green_epoxy_floor", (HALL_W, HALL_D, .12), (0, 3, -.06), C["floor"])
bx(hall, "left_wall", (.16, HALL_D, HALL_H), (-7.5, 3, 3.5), C["wall"])
bx(hall, "back_wall", (HALL_W, .15, HALL_H), (0, 18, 3.5), C["wall"])
bx(hall, "roof_sheet", (HALL_W, HALL_D, .16), (0, 3, 7), C["roof"])
for i, y in enumerate([-11, -7, -3, 1, 5, 9, 13, 17]):
    bx(hall, "left_column_%d" % i, (.26, .25, 7), (-7.28, y, 3.5), C["steel"])
    bx(hall, "roof_crossbeam_%d" % i, (14.9, .23, .28), (0, y, 6.78), C["steel"])
    if y >= 5:
        bx(hall, "right_column_%d" % i, (.24, .25, 7), (7.28, y, 3.5), C["steel"])
for i, x in enumerate([-5, -2.5, 0, 2.5, 5]):
    bx(hall, "roof_purlin_%d" % i, (.14, HALL_D, .14), (x, 3, 6.78), C["steel"])
for i, y in enumerate([-10, -7.7, -5.4, -3.1, -.8, 1.5, 3.8, 6.1, 8.4, 10.7, 13]):
    bx(hall, "window_%d" % i, (.05, .74, 2.8), (-7.39, y, 3.5), C["window"])
    bx(hall, "window_vertical_frame_%d" % i, (.07, .035, 2.8), (-7.34, y, 3.5), C["windowframe"])
    bx(hall, "window_crossbar_%d" % i, (.07, .74, .035), (-7.33, y, 3.25), C["windowframe"])
scene.include("architecture", hall)

platform = Asset("Raised_equipment_platform")
bx(platform, "deck", (11.0, 4.5, .18), (.1, 3.4, DECK_Z), C["darkmetal"])
bx(platform, "front_fascia", (11.0, .14, .25), (.1, 1.12, 1.98), C["silver"])
for ix, x in enumerate([-5.2, -3.0, -.8, 1.5, 3.6, 5.3]):
    for iy, y in enumerate([1.35, 5.35]):
        bx(platform, "support_%d_%d" % (ix, iy), (.14, .14, 1.98),
           (x, y, .99), C["darkmetal"])
scene.include("equipment_platforms", platform)

machines = Asset("Stainless_processing_machines")
bx(machines, "main_lower_body", (3.3, 2.0, 1.05), (MAIN_X, 3.2, 2.68), C["silver"])
bx(machines, "main_upper_body", (3.0, 1.9, 1.12), (MAIN_X, 3.25, 3.72), C["silver"])
bx(machines, "main_hood", (3.0, 1.95, .28), (MAIN_X, 3.25, 4.40), C["bright"])
bx(machines, "main_front_opening", (2.65, .06, .38), (MAIN_X, 2.22, 3.61), C["black"])
for i, z in enumerate([3.47, 3.57, 3.67, 3.77]):
    bx(machines, "mouth_slat_%d" % i, (2.57, .075, .035), (MAIN_X, 2.17, z), C["silver"])
bx(machines, "main_front_panel", (3.1, .08, .40), (MAIN_X, 2.13, 2.85), C["bright"])
bx(machines, "left_base", (2.3, 1.8, 1.1), (-3.3, 4.0, 2.67), C["silver"])
bx(machines, "left_head", (1.9, 1.6, .72), (-3.3, 4.0, 3.54), C["bright"])
bx(machines, "left_front_opening", (1.9, .06, .28), (-3.3, 3.08, 2.96), C["darkmetal"])
bx(machines, "center_unit", (2.0, 1.65, 1.25), (-.45, 4.35, 2.78), C["silver"])
bx(machines, "center_top", (1.9, 1.5, .14), (-.45, 4.35, 3.48), C["bright"])
bx(machines, "control_cabinet", (.75, .72, 2.2), (5.1, 4.9, 3.2), C["white"])
bx(machines, "control_screen", (.32, .045, .3), (5.1, 4.52, 3.55), C["darkmetal"])
scene.include("processing_machines", machines)

rails = Asset("Yellow_platform_guardrails")
for seg, (x0, x1) in enumerate([(-5.3, -4.4), (-2.9, .3), (1.7, 4.1), (5.1, 5.6)]):
    for j, z in enumerate([2.45, 2.92, 3.38]):
        rd(rails, "front_rail_%d_%d" % (seg, j), (x0, 1.04, z), (x1, 1.04, z), .034, C["yellow"])
    n = max(1, round((x1 - x0) / .7))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        rd(rails, "front_post_%d_%d" % (seg, i), (x, 1.04, 2.14), (x, 1.04, 3.42), .035, C["yellow"])
for side, x in [("left", -5.3), ("right", 5.6)]:
    for j, z in enumerate([2.45, 2.92, 3.38]):
        rd(rails, side + "_rail_%d" % j, (x, 1.04, z), (x, 5.55, z), .032, C["yellow"])
    for i, y in enumerate([1.04, 1.9, 2.8, 3.7, 4.6, 5.55]):
        rd(rails, side + "_post_%d" % i, (x, y, 2.13), (x, y, 3.42), .035, C["yellow"])
for j, z in enumerate([2.45, 2.92, 3.38]):
    rd(rails, "back_rail_%d" % j, (-5.3, 5.55, z), (5.6, 5.55, z), .03, C["yellow"])
for i, x in enumerate([-5.3, -4.3, -3.3, -2.3, -1.3, -.3, .7, 1.7, 2.7, 3.7, 4.7, 5.6]):
    rd(rails, "back_post_%d" % i, (x, 5.55, 2.13), (x, 5.55, 3.42), .032, C["yellow"])
scene.include("platform_guardrails", rails)

stairs = Asset("Yellow_access_stairs")
def flight(name, xcenter, bottom_y=-2.1, top_y=1.05):
    width = 1.15
    for i in range(9):
        t = (i + .5) / 9
        bx(stairs, name + "_tread_%02d" % i, (width, .32, .065),
           (xcenter, bottom_y + (top_y - bottom_y) * t, .10 + 1.98 * t), C["silver"])
    for side in [-1, 1]:
        x = xcenter + side * width * .55
        rd(stairs, name + "_stringer_%d" % side, (x, bottom_y, .08), (x, top_y, 2.1), .055, C["yellow"])
        rd(stairs, name + "_handrail_%d" % side, (x, bottom_y, 1.05), (x, top_y, 3.12), .035, C["yellow"])
        rd(stairs, name + "_midrail_%d" % side, (x, bottom_y, .58), (x, top_y, 2.65), .025, C["yellow"])
        for j in range(4):
            t = j / 3
            y = bottom_y + (top_y - bottom_y) * t
            z = .10 + 2 * t
            rd(stairs, name + "_post_%d_%d" % (side, j), (x, y, z), (x, y, z + 1), .03, C["yellow"])
flight("left_stair", -3.65)
flight("middle_stair", 1.0)
flight("right_stair", 4.6, -2.8, 1.05)
scene.include("access_stairs", stairs)

ducts = Asset("Insulated_ductwork")
def duct(name, points, radius):
    for i in range(len(points) - 1):
        rd(ducts, name + "_segment_%d" % i, points[i], points[i + 1], radius, C["bright"])
    for i, p in enumerate(points[1:-1]):
        ducts.include(name + "_elbow_%d" % i, ball(radius=radius, center=p, color=C["bright"]))
duct("main_exhaust", [(MAIN_X, 3.6, 4.55), (MAIN_X, 3.6, 5.25),
                      (MAIN_X - .20, 3.6, 5.60), (MAIN_X - 1.1, 3.6, 5.60)], .21)
duct("left_exhaust", [(-3.3, 4.2, 3.9), (-3.3, 4.2, 4.65),
                      (-2.9, 4.2, 4.94), (-1.7, 4.2, 4.94), (-1.1, 4.2, 4.05)], .18)
duct("process_pipe", [(-4.7, 5.2, 3.8), (-1.3, 5.2, 3.8),
                      (.3, 5.2, 4.05), (4.0, 5.2, 4.05)], .12)
for i, x in enumerate([-3, 0, 3]):
    rd(ducts, "hanger_%d" % i, (x, 5.2, 4.1), (x, 5.2, 6.74), .025, C["darkmetal"])
scene.include("ductwork", ducts)

tank = Asset("Green_vertical_tank")
rd(tank, "cylindrical_shell", (TANK_X, TANK_Y, .40), (TANK_X, TANK_Y, 1.75), .50, C["green"])
tank.include("domed_head", ball(radius=.50, center=(TANK_X, TANK_Y, 1.75), color=C["green"]))
rd(tank, "top_neck", (TANK_X, TANK_Y, 2.15), (TANK_X, TANK_Y, 2.31), .10, C["green"])
rd(tank, "side_flange", (TANK_X + .43, TANK_Y, 1.15), (TANK_X + .65, TANK_Y, 1.15), .10, C["silver"])
for i, (dx, dy) in enumerate([(-.3, -.22), (.3, -.22), (-.3, .22), (.3, .22)]):
    bx(tank, "leg_%d" % i, (.08, .08, .4), (TANK_X + dx, TANK_Y + dy, .2), C["darkmetal"])
scene.include("green_tank", tank)

conveyor = Asset("Foreground_roller_conveyors")
for line, (xc, width, y0, y1) in enumerate([
        (-4.2, 2.15, -11.0, -3.0),
        (-1.7, 2.15, -10.0, -3.2),
        (.8, 2.0, -9.0, -3.3),
        (3.0, 1.8, -7.3, -3.3)]):
    for side in [-1, 1]:
        x = xc + side * width / 2
        bx(conveyor, "line%d_rail_%d" % (line, side), (.11, y1 - y0, .18),
           (x, (y0 + y1) / 2, .95), C["bright"])
        for j, y in enumerate([y0 + .4, (y0 + y1) / 2, y1 - .4]):
            bx(conveyor, "line%d_leg_%d_%d" % (line, side, j), (.09, .09, .9),
               (x, y, .45), C["silver"])
    count = int((y1 - y0) / .42)
    for i in range(count):
        y = y0 + .21 + i * .42
        rd(conveyor, "line%d_roller_%02d" % (line, i),
           (xc - width / 2 + .06, y, 1.02), (xc + width / 2 - .06, y, 1.02), .055, C["blue"])
    bx(conveyor, "line%d_motor" % line, (.35, .42, .32),
       (xc + width / 2 + .22, y1 - .8, .65), C["darkmetal"])
for j, y in enumerate([-3.6, -2.9]):
    bx(conveyor, "transfer_frame_%d" % j, (8.4, .10, .15), (-.8, y, 1.03), C["bright"])
for i, x in enumerate([-4.6, -3.2, -1.8, -.4, 1.0, 2.4, 3.1]):
    bx(conveyor, "transfer_leg_%d" % i, (.10, .1, .95), (x, -3.18, .49), C["silver"])
    bx(conveyor, "transfer_crosspiece_%d" % i, (.09, .8, .10), (x, -3.25, 1.03), C["silver"])
scene.include("conveyor_lines", conveyor)

rear = Asset("Rear_equipment")
bx(rear, "cabinet", (1.2, 1.0, 1.8), (6.0, 8.4, .9), C["white"])
bx(rear, "machine", (2.0, 1.3, 1.1), (3.3, 9.3, .55), C["silver"])
for i, x in enumerate([2.6, 3.3, 4]):
    rd(rear, "pipe_%d" % i, (x, 9.3, 1.1), (x, 9.3, 2.2), .08, C["silver"])
scene.include("rear_equipment", rear)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .77, .80, 1)
background.inputs["Strength"].default_value = .5

# Copy shared finishes before editing so other material users are unaffected.
def tune(label, rgb, metallic, roughness):
    selected = []
    for obj in sc.objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes:
                continue
            shader = mat.node_tree.nodes.get("Principled BSDF")
            if shader:
                col = shader.inputs["Base Color"].default_value
                if sum(abs(col[i] - rgb[i]) for i in range(3)) < .025:
                    selected.append((obj, slot, mat))
    copies = {}
    for obj, slot, mat in selected:
        key = mat.name
        if key not in copies:
            newmat = mat.copy()
            newmat.name = label + "_surface"
            shader = newmat.node_tree.nodes.get("Principled BSDF")
            shader.inputs["Metallic"].default_value = metallic
            shader.inputs["Roughness"].default_value = roughness
            copies[key] = newmat
        slot.material = copies[key]
    for mat in copies.values():
        shader = mat.node_tree.nodes.get("Principled BSDF")
        print("MATERIAL", label, "meshes", len(selected), "assigned", mat.name,
              "users", mat.users, "metallic", shader.inputs["Metallic"].default_value,
              "roughness", shader.inputs["Roughness"].default_value)

tune("green_epoxy_floor", C["floor"], 0.0, .18)
tune("stainless_machine_and_framework", C["silver"], .72, .31)
tune("bright_duct_and_frame", C["bright"], .78, .24)
tune("painted_tank", C["green"], .12, .33)
tune("yellow_guardrails", C["yellow"], .10, .38)

area_emitter((-6, -4, 5.4), power=1700, size=7, target=(0, 2, 2), color=(.82, .91, 1))
area_emitter((-4, 5, 5.8), power=1400, size=6, target=(0, 3, 1.5), color=(.87, .94, 1))
area_emitter((2, 2, 6.5), power=1300, size=7, target=(0, 2, 1.5), color=(1, .98, .94))
area_emitter((5, -5, 5.8), power=700, size=6, target=(0, 2, 2), color=(1, 1, 1))

# Original aspect for projection checks; final output is controlled by the runner.
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100

landmarks = [
    ("window top", (-7.34, -3.1, 4.9), (.16, .34)),
    ("main machine top", (MAIN_X - 1.5, 2.275, 4.54), (.62, .30)),
    ("tank top", (TANK_X, TANK_Y, 2.25), (.40, .54)),
    ("conveyor frame", (-2.8, -3.6, 1.10), (.20, .76)),
]
def project(p):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    if clip.w <= 1e-8:
        return None
    return (.5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))

def table(label):
    print("LANDMARK", label, "reference_uv", "projected_uv")
    for name, p, ref in landmarks:
        uv = project(p)
        print(name, ref, tuple(round(v, 3) for v in uv) if uv else None)

# Compare the previous camera and proposed camera on the same actual points.
# Also print a small aim trial and restore it. These checks are projections, not
# measurements of visible bounds or occlusion.
set_view((8.0, -13.0, 4.7), (0.0, 3.0, 3.25), lens=35)
table("previous_camera")
set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS)
table("chosen_camera")
cam = sc.camera
old_rot = cam.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2] - .2))
cam.rotation_euler = (trial_target - Vector(CAMERA_POS)).to_track_quat("-Z", "Y").to_euler()
table("trial_aim_down")
cam.rotation_euler = old_rot
bpy.context.view_layer.update()

try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
