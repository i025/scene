from sceneact import *
import bpy
from mathutils import Vector

# Visual comparison, normalized coordinates, reference versus first render:
# Roof: reference occupies y=0-.35, with its underside filling the frame;
# render shows the outside roof at y=.10-.32 and empty background around the hall.
# Left windows: reference x=0-.25, y=.33-.65; render x=.06-.31, y=.35-.70.
# Main machine: reference x=.61-.80, y=.30-.70; render x=.42-.72, y=.31-.69.
# Tank: reference x=.36-.45, y=.53-.77; render x=.34-.42, y=.61-.80.
# Conveyor: reference covers x=0-.68, y=.72-1; render x=0-.49, y=.72-1.
# Reference railings extend almost across the image, with several visible gaps and
# stairs; render railings are concentrated in the middle. The near right column
# masks much of the equipment. The photographed roof beams are nearly horizontal,
# while the rendered exterior roof outline slopes markedly.
#
# Largest discrepancies: (1) camera outside and above the hall, exposing the roof
# exterior and outside background; (2) machine/platform cluster too small and the
# near right column obstructs it; (3) tank and conveyor sit low and left, with the
# foreground conveyor too sparse. Lowering and moving the camera inside the hall
# should reveal the underside of the roof, reduce the downward view, and expand the
# machinery in frame. Enlarging the main machine locally moves its right contour
# rightward. Extending the conveyor locally fills the lower foreground. Moving the
# tank slightly toward the center makes its silhouette less obscured.
#
# Inventory: structural shell and window wall; steel frames and roof purlins;
# elevated machinery, decks and supports; yellow guardrails and three stairs;
# insulated ducts and hangers; green tank; blue conveyors, silver frames and motors.
# Machine interiors, distant pipe routes, and concealed floor contacts are uncertain.
# Primitive estimate: hall 55, platforms and machines 42, rails and stairs 125,
# ducts 20, tank 8, conveyors 95, background equipment 8: about 353 meshes.
# Each box, ball and rod emits one primitive; no fillets or boolean operations.

scene = Scene("Workshop")

# Camera and asset parameters are independent.
CAM_POS = (8.0, -13.0, 4.7)
CAM_TARGET = (0.0, 3.0, 3.25)
CAM_LENS = 35
HALL_W, HALL_D, HALL_H = 15.0, 30.0, 7.0
DECK_Z = 2.05
MAIN_X = 2.8
TANK_X, TANK_Y = -1.0, -1.0

C = {
    "floor": (.09, .29, .21),
    "wall": (.15, .17, .17),
    "steel": (.065, .078, .078),
    "roof": (.21, .22, .21),
    "window": (.75, .85, .88),
    "windowframe": (.17, .19, .19),
    "silver": (.56, .59, .58),
    "bright": (.73, .75, .73),
    "darkmetal": (.22, .25, .24),
    "yellow": (.95, .62, .015),
    "green": (.015, .28, .20),
    "blue": (.045, .19, .46),
    "black": (.035, .045, .044),
    "white": (.80, .82, .79),
}

def bx(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def rd(parent, name, a, b, radius, color):
    if sum((a[i]-b[i])**2 for i in range(3)) > 1e-10:
        parent.include(name, rod(radius=radius, start=a, end=b, color=color))

hall = Asset("Hall_structure")
bx(hall, "green_epoxy_floor", (HALL_W, HALL_D, .12), (0, 3, -.06), C["floor"])
bx(hall, "left_wall", (.16, HALL_D, HALL_H), (-7.5, 3, 3.5), C["wall"])
bx(hall, "back_wall", (HALL_W, .15, HALL_H), (0, 18, 3.5), C["wall"])
bx(hall, "roof_sheet", (HALL_W, HALL_D, .16), (0, 3, 7), C["roof"])

# Repeating frames and purlins give the large roof its visible structural rhythm.
for i, y in enumerate([-11, -7, -3, 1, 5, 9, 13, 17]):
    bx(hall, "left_column_%d" % i, (.26, .25, 7), (-7.28, y, 3.5), C["steel"])
    bx(hall, "roof_crossbeam_%d" % i, (14.9, .23, .28), (0, y, 6.78), C["steel"])
    # The nearest camera-side column is behind the camera; the remaining columns
    # frame the far side without masking the main equipment.
    if y >= 5:
        bx(hall, "right_column_%d" % i, (.24, .25, 7), (7.28, y, 3.5), C["steel"])
for i, x in enumerate([-5, -2.5, 0, 2.5, 5]):
    bx(hall, "longitudinal_purlin_%d" % i, (.14, HALL_D, .14), (x, 3, 6.78), C["steel"])
for i, y in enumerate([-10, -7.7, -5.4, -3.1, -.8, 1.5, 3.8, 6.1, 8.4, 10.7, 13]):
    bx(hall, "window_%d" % i, (.05, .74, 2.8), (-7.39, y, 3.50), C["window"])
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
# Right processing unit: the front panels and horizontal mouth remain separate.
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
# Two stair openings remain in the front rail.
for seg, (x0, x1) in enumerate([(-5.3, -4.4), (-2.9, .3), (1.7, 4.1), (5.1, 5.6)]):
    for j, z in enumerate([2.45, 2.92, 3.38]):
        rd(rails, "front_rail_%d_%d" % (seg, j), (x0, 1.04, z), (x1, 1.04, z), .034, C["yellow"])
    n = max(1, round((x1-x0)/.7))
    for i in range(n+1):
        x = x0 + (x1-x0)*i/n
        rd(rails, "front_post_%d_%d" % (seg, i), (x, 1.04, 2.14), (x, 1.04, 3.42), .035, C["yellow"])
for side, x in [("left", -5.3), ("right", 5.6)]:
    for j, z in enumerate([2.45, 2.92, 3.38]):
        rd(rails, side+"_rail_%d" % j, (x, 1.04, z), (x, 5.55, z), .032, C["yellow"])
    for i, y in enumerate([1.04, 1.9, 2.8, 3.7, 4.6, 5.55]):
        rd(rails, side+"_post_%d" % i, (x, y, 2.13), (x, y, 3.42), .035, C["yellow"])
for j, z in enumerate([2.45, 2.92, 3.38]):
    rd(rails, "back_rail_%d" % j, (-5.3, 5.55, z), (5.6, 5.55, z), .03, C["yellow"])
for i, x in enumerate([-5.3, -4.3, -3.3, -2.3, -1.3, -.3, .7, 1.7, 2.7, 3.7, 4.7, 5.6]):
    rd(rails, "back_post_%d" % i, (x, 5.55, 2.13), (x, 5.55, 3.42), .032, C["yellow"])
scene.include("platform_guardrails", rails)

stairs = Asset("Yellow_access_stairs")
def flight(name, xcenter, bottom_y=-2.1, top_y=1.05):
    width = 1.15
    for i in range(9):
        t = (i+.5)/9
        bx(stairs, name+"_tread_%02d" % i, (width, .32, .065),
           (xcenter, bottom_y+(top_y-bottom_y)*t, .10+1.98*t), C["silver"])
    for side in [-1, 1]:
        x = xcenter + side*width*.55
        rd(stairs, name+"_stringer_%d" % side, (x, bottom_y, .08), (x, top_y, 2.1), .055, C["yellow"])
        rd(stairs, name+"_handrail_%d" % side, (x, bottom_y, 1.05), (x, top_y, 3.12), .035, C["yellow"])
        rd(stairs, name+"_midrail_%d" % side, (x, bottom_y, .58), (x, top_y, 2.65), .025, C["yellow"])
        for j in range(4):
            t = j/3
            y = bottom_y+(top_y-bottom_y)*t
            z = .10+2*t
            rd(stairs, name+"_post_%d_%d" % (side, j), (x, y, z), (x, y, z+1), .03, C["yellow"])
flight("left_stair", -3.65)
flight("middle_stair", 1.0)
flight("right_stair", 4.6, -2.8, 1.05)
scene.include("access_stairs", stairs)

ducts = Asset("Insulated_ductwork")
def duct(name, points, radius):
    for i in range(len(points)-1):
        rd(ducts, name+"_segment_%d" % i, points[i], points[i+1], radius, C["bright"])
    for i, p in enumerate(points[1:-1]):
        ducts.include(name+"_elbow_%d" % i, ball(radius=radius, center=p, color=C["bright"]))
duct("main_exhaust", [(MAIN_X, 3.6, 4.55), (MAIN_X, 3.6, 5.25),
                      (MAIN_X-.20, 3.6, 5.60), (MAIN_X-1.1, 3.6, 5.60)], .21)
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
rd(tank, "side_flange", (TANK_X+.43, TANK_Y, 1.15), (TANK_X+.65, TANK_Y, 1.15), .10, C["silver"])
for i, (dx, dy) in enumerate([(-.3, -.22), (.3, -.22), (-.3, .22), (.3, .22)]):
    bx(tank, "leg_%d" % i, (.08, .08, .4), (TANK_X+dx, TANK_Y+dy, .2), C["darkmetal"])
scene.include("green_tank", tank)

conveyor = Asset("Foreground_roller_conveyors")
for line, (xc, width, y0, y1) in enumerate([
        (-4.2, 2.15, -11.0, -3.0),
        (-1.7, 2.15, -10.0, -3.2),
        (.8, 2.0, -9.0, -3.3),
        (3.0, 1.8, -7.3, -3.3)]):
    for side in [-1, 1]:
        x = xc+side*width/2
        bx(conveyor, "line%d_rail_%d" % (line, side), (.11, y1-y0, .18),
           (x, (y0+y1)/2, .95), C["bright"])
        for j, y in enumerate([y0+.4, (y0+y1)/2, y1-.4]):
            bx(conveyor, "line%d_leg_%d_%d" % (line, side, j), (.09, .09, .9),
               (x, y, .45), C["silver"])
    count = int((y1-y0)/.42)
    for i in range(count):
        y = y0+.21+i*.42
        rd(conveyor, "line%d_roller_%02d" % (line, i),
           (xc-width/2+.06, y, 1.02), (xc+width/2-.06, y, 1.02), .055, C["blue"])
    bx(conveyor, "line%d_motor" % line, (.35, .42, .32),
       (xc+width/2+.22, y1-.8, .65), C["darkmetal"])
bx(conveyor, "transverse_transfer_bed", (8.4, 1.0, .14), (-.8, -3.18, 1.03), C["white"])
for i, x in enumerate([-4.6, -3.2, -1.8, -.4, 1.0, 2.4, 3.1]):
    bx(conveyor, "transfer_leg_%d" % i, (.10, .1, .95), (x, -3.18, .49), C["silver"])
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
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .77, .80, 1)
background.inputs["Strength"].default_value = .5

# SceneAct finish colors are shared. Copy materials for the selected finish subset
# before changing the shader; print the assigned material and final values.
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
                if sum(abs(col[i]-rgb[i]) for i in range(3)) < .025:
                    selected.append((obj, slot, mat))
    copies = {}
    for obj, slot, mat in selected:
        if mat.name not in copies:
            newmat = mat.copy()
            newmat.name = label+"_surface"
            shader = newmat.node_tree.nodes.get("Principled BSDF")
            shader.inputs["Metallic"].default_value = metallic
            shader.inputs["Roughness"].default_value = roughness
            copies[mat.name] = newmat
        slot.material = copies[mat.name]
    for mat in copies.values():
        shader = mat.node_tree.nodes.get("Principled BSDF")
        print("MATERIAL", label, "meshes", len(selected), "assigned", mat.name,
              "users", mat.users, "metallic", shader.inputs["Metallic"].default_value,
              "roughness", shader.inputs["Roughness"].default_value)

tune("green_epoxy_floor", C["floor"], 0.0, .18)
tune("stainless_machine_and_framework", C["silver"], .72, .31)
tune("bright_insulated_duct_and_frame", C["bright"], .78, .24)
tune("painted_tank", C["green"], .12, .33)
tune("yellow_guardrails", C["yellow"], .10, .38)

area_emitter((-6, -4, 5.4), power=1700, size=7, target=(0, 2, 2), color=(.82, .91, 1))
area_emitter((-4, 5, 5.8), power=1400, size=6, target=(0, 3, 1.5), color=(.87, .94, 1))
area_emitter((2, 2, 6.5), power=1300, size=7, target=(0, 2, 1.5), color=(1, .98, .94))
area_emitter((5, -5, 5.8), power=700, size=6, target=(0, 2, 2), color=(1, 1, 1))

# The supplied reference uses 512:267. The runner controls actual output.
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)

landmarks = [
    ("window top", (-7.34, -3.1, 4.9), (.16, .34)),
    ("main machine top", (MAIN_X-1.5, 2.275, 4.54), (.62, .30)),
    ("tank top", (TANK_X, TANK_Y, 2.25), (.40, .54)),
    ("conveyor corner", (-5.275, -9.0, 1.04), (.08, .94)),
]

def project(p):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                                 scale_x=sc.render.pixel_aspect_x,
                                 scale_y=sc.render.pixel_aspect_y)
    clip = proj @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    if clip.w <= 1e-8:
        return None
    return (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))

def table(label):
    print("LANDMARK", label, "reference_uv", "projected_uv")
    for name, p, ref in landmarks:
        uv = project(p)
        print(name, ref, tuple(round(v, 3) for v in uv) if uv else None)

# Compare a small upward aim trial with the chosen camera, then restore the chosen
# target. The printed numerical check distinguishes point projections from contours.
table("chosen")
cam = sc.camera
old_rot = cam.rotation_euler.copy()
trial_target = Vector((CAM_TARGET[0], CAM_TARGET[1], CAM_TARGET[2]+.2))
cam.rotation_euler = (trial_target-Vector(CAM_POS)).to_track_quat("-Z", "Y").to_euler()
table("trial_target_up_0.2")
cam.rotation_euler = old_rot
bpy.context.view_layer.update()

try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
