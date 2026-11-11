# Reference inventory and approximate image anchors (normalized x, y; y downward):
# - Dark steel roof and beams: across (0.00, 0.00)-(1.00, 0.40).
# - Left wall with tall narrow daylight windows: (0.00, 0.31)-(0.24, 0.66).
# - Large stainless processing machine and platform: (0.56, 0.29)-(0.81, 0.76).
# - Smaller machines and silver ductwork behind: (0.22, 0.30)-(0.63, 0.65).
# - Yellow platform railings and stairs: (0.07, 0.42)-(0.96, 0.96).
# - Green vertical tank in front of platform: (0.36, 0.53)-(0.45, 0.78).
# - Blue and silver foreground conveyor: (0.00, 0.75)-(0.67, 1.00), cropped.
# - Green reflective floor: mainly (0.64, 0.69)-(1.00, 1.00).
# Dominant edges: roof beams run nearly horizontally, with slight perspective;
# window and structural columns are vertical; stair rails rise diagonally.
# The tank overlaps the platform, and the conveyor overlaps the tank's base.
# Back machinery and duct connections are partly occluded and remain approximate.
#
# Expanded primitive estimate: architecture ~35, windows ~30, equipment ~55,
# platforms, railings and stairs ~115, ducts ~25, tank ~12, conveyor ~65:
# approximately 337 meshes. No fillets or Boolean operations.
#
# The photo is 512 x 267; the fixed rendering runner controls final output.
# Camera, equipment positions and dimensions are kept independent below.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Workshop")

# Dimensions and placement in meters.
HALL_W, HALL_D, HALL_H = 15.0, 21.0, 6.7
PLATFORM_Z = 2.05
MAIN_X, MAIN_Y = 2.2, 2.25
TANK_X, TANK_Y = -1.4, -2.15
CAM_POS = (10.4, -19.2, 8.1)
CAM_TARGET = (0.0, 1.1, 2.8)
CAM_LENS = 39.0

steel_dark = (0.105, 0.125, 0.13)
wall = (0.31, 0.34, 0.33)
roof = (0.22, 0.24, 0.23)
floor_green = (0.12, 0.34, 0.25)
silver = (0.64, 0.68, 0.68)
silver_light = (0.78, 0.81, 0.79)
silver_dark = (0.34, 0.39, 0.39)
black = (0.10, 0.12, 0.12)
yellow = (0.95, 0.65, 0.025)
tank_green = (0.015, 0.38, 0.25)
blue = (0.07, 0.31, 0.65)
window = (0.70, 0.81, 0.86)

def add(parent, name, node):
    parent.include(name, node)

def B(parent, name, size, center, color):
    add(parent, name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    add(parent, name, rod(radius=radius, start=a, end=b, color=color))

def rail(parent, name, a, b, z0, h=0.95, posts=4):
    ax, ay = a
    bx, by = b
    R(parent, name + "_top", (ax, ay, z0+h), (bx, by, z0+h), .027, yellow)
    R(parent, name + "_middle", (ax, ay, z0+h*.52), (bx, by, z0+h*.52), .021, yellow)
    for j in range(posts):
        t = j / max(1, posts-1)
        x, y = ax+(bx-ax)*t, ay+(by-ay)*t
        R(parent, name + "_post_%d" % j, (x,y,z0), (x,y,z0+h), .025, yellow)

# Architecture.
building = Asset("steel_frame_hall")
B(building, "epoxy_floor", (HALL_W,HALL_D,.14), (0,1,-.07), floor_green)
B(building, "left_wall", (.16,HALL_D,HALL_H), (-HALL_W/2,1,HALL_H/2), wall)
B(building, "far_wall", (HALL_W,.16,HALL_H), (0,11.4,HALL_H/2), wall)
B(building, "roof_panels", (HALL_W,HALL_D,.13), (0,1,HALL_H), roof)
# Exposed roof members and columns.
for i, y in enumerate((-8,-4,0,4,8,11)):
    B(building, "left_column_%d"%i, (.22,.24,HALL_H), (-7.32,y,HALL_H/2), steel_dark)
    B(building, "right_column_%d"%i, (.22,.24,HALL_H), (7.32,y,HALL_H/2), steel_dark)
    B(building, "cross_roof_beam_%d"%i, (HALL_W,.20,.24), (0,y,6.46), steel_dark)
for i, x in enumerate((-5,-2,1,4,7)):
    B(building, "roof_purlin_%d"%i, (.10,HALL_D,.12), (x,1,6.53), steel_dark)
# A row of strip windows, their mullions and bright daylight panes.
for i, y in enumerate((-6.7,-4.9,-3.1,-1.3,.5,2.3,4.1,5.9,7.7,9.5)):
    B(building, "window_%d"%i, (.035,.65,2.55), (-7.39,y,3.07), window)
    B(building, "window_mullion_%d"%i, (.06,.045,2.58), (-7.34,y,3.07), steel_dark)
    B(building, "window_sill_%d"%i, (.10,.70,.055), (-7.32,y,1.79), steel_dark)
scene.include("hall", building)

# Main raised platform, with open legs and visible supporting beams.
platform = Asset("machine_platform")
B(platform, "deck", (8.6,3.7,.16), (0.15,2.1,PLATFORM_Z), silver_dark)
for i, x in enumerate((-3.95,-1.95,.05,2.05,4.15)):
    for j, y in enumerate((.36,3.84)):
        B(platform, "support_%d_%d"%(i,j), (.13,.13,PLATFORM_Z), (x,y,PLATFORM_Z/2), silver_dark)
B(platform, "front_beam", (8.6,.15,.24), (.15,.28,1.87), silver)
B(platform, "rear_beam", (8.6,.15,.24), (.15,3.92,1.87), silver_dark)
rail(platform, "front_left", (-4.1,.22), (-.65,.22), PLATFORM_Z+.08, posts=5)
rail(platform, "front_right", (.25,.22), (4.4,.22), PLATFORM_Z+.08, posts=6)
rail(platform, "left_side", (-4.1,.22), (-4.1,3.9), PLATFORM_Z+.08, posts=4)
rail(platform, "right_side", (4.4,.22), (4.4,3.9), PLATFORM_Z+.08, posts=4)
rail(platform, "rear", (-4.1,3.9), (4.4,3.9), PLATFORM_Z+.08, posts=8)
scene.include("platform", platform)

# Main stainless production unit: lower chassis, wide rectangular housing,
# dark opening with lip, and a smaller upper head.
machines = Asset("processing_machines")
B(machines, "main_base", (3.55,2.05,.50), (MAIN_X,MAIN_Y,2.38), silver_dark)
B(machines, "main_body", (3.55,1.92,1.15), (MAIN_X,MAIN_Y,3.17), silver)
B(machines, "main_front_inset", (2.85,.045,.48), (MAIN_X,1.255,3.26), black)
B(machines, "main_opening_inner", (2.58,.035,.27), (MAIN_X,1.225,3.27), silver_dark)
B(machines, "main_upper_panel", (3.18,1.65,.62), (MAIN_X,MAIN_Y,4.03), silver_light)
B(machines, "main_upper_cap", (2.72,1.40,.18), (MAIN_X,MAIN_Y,4.43), silver)
B(machines, "machine_lower_ledge", (3.75,.22,.12), (MAIN_X,1.15,2.79), silver_light)
for i, x in enumerate((.75,1.35,1.95,2.55,3.15,3.7)):
    B(machines, "front_panel_divider_%d"%i, (.035,.04,.48), (x,1.19,3.26), silver)
# Round indicator on head.
R(machines, "head_indicator_rim", (2.20,1.405,4.06), (2.20,1.35,4.06), .105, silver_dark)
R(machines, "head_indicator", (2.20,1.345,4.06), (2.20,1.32,4.06), .060, tank_green)
# Smaller units behind and to the left.
for i, (x,y,w) in enumerate(((-3.05,2.35,1.45),(-1.25,2.7,1.65),(.25,3.05,1.15))):
    B(machines, "aux_chassis_%d"%i, (w,1.38,.95), (x,y,2.70), silver)
    B(machines, "aux_top_%d"%i, (w*.88,1.20,.44), (x,y,3.38), silver_light)
    B(machines, "aux_front_%d"%i, (w*.75,.035,.27), (x,y-.70,2.82), silver_dark)
    B(machines, "aux_base_%d"%i, (w+0.10,1.50,.12), (x,y,2.20), silver_dark)
scene.include("machines", machines)

# Silver insulated ducts with simple short bends and vertical hangers.
ducts = Asset("insulated_ductwork")
def pipepath(name, points, radius):
    for i in range(len(points)-1):
        R(ducts, "%s_%d"%(name,i), points[i], points[i+1], radius, silver_light)
    for i, p in enumerate(points[1:-1]):
        add(ducts, "%s_elbow_%d"%(name,i), ball(radius=radius, center=p, color=silver_light))
pipepath("main_riser", [(2.25,2.8,4.40),(2.25,2.8,5.05),(2.42,2.8,5.25),
                         (3.1,2.8,5.25),(3.28,2.8,5.05),(3.28,2.8,4.50)], .18)
pipepath("left_riser", [(-3.1,2.6,3.58),(-3.1,2.6,4.22),(-2.92,2.6,4.40),
                         (-1.95,2.6,4.40),(-1.72,2.6,4.17),(-1.72,2.6,3.64)], .15)
pipepath("horizontal_process", [(-1.7,3.05,3.95),(.0,3.05,3.95),(1.0,3.05,3.80)], .12)
for i, x in enumerate((-2.6,2.7)):
    R(ducts, "hanger_%d"%i, (x,2.8,5.23), (x,2.8,6.40), .025, silver_dark)
scene.include("ducts", ducts)

# Two flights of yellow-railed stairs in front of the operating platform.
def staircase(name, x0, x1, y_top, y_bottom, z_top, n):
    stair = Asset(name)
    width = x1-x0
    for i in range(n):
        t = (i+0.5)/n
        y = y_bottom + (y_top-y_bottom)*t
        z = z_top*t
        B(stair, "tread_%d"%i, (width,abs(y_top-y_bottom)/n*.78,.065),
          ((x0+x1)/2,y,z), silver_light)
    for k, x in enumerate((x0,x1)):
        R(stair, "stringer_%d"%k, (x,y_bottom,.05), (x,y_top,z_top), .06, silver_dark)
        R(stair, "handrail_%d"%k, (x,y_bottom,.95), (x,y_top,z_top+.95), .028, yellow)
        R(stair, "midrail_%d"%k, (x,y_bottom,.51), (x,y_top,z_top+.51), .022, yellow)
        for j in range(5):
            t = j/4
            y = y_bottom+(y_top-y_bottom)*t
            z = .05+(z_top-.05)*t
            R(stair, "upright_%d_%d"%(k,j), (x,y,z), (x,y,z+.95), .025, yellow)
    scene.include(name, stair)

staircase("right_access_stair", 4.20,5.25, .35,-3.5, PLATFORM_Z, 10)
staircase("left_access_stair", -3.95,-3.0, .35,-2.65, PLATFORM_Z, 9)

# Green pressure vessel, domed top and bottom, feet and flanged connections.
tank = Asset("green_vertical_tank")
R(tank, "shell", (TANK_X,TANK_Y,.42), (TANK_X,TANK_Y,1.92), .47, tank_green)
add(tank, "top_head", ball(radius=.47, center=(TANK_X,TANK_Y,1.90), color=tank_green))
add(tank, "bottom_head", ball(radius=.47, center=(TANK_X,TANK_Y,.45), color=tank_green))
for i, (dx,dy) in enumerate(((-.30,-.23),(.30,-.23),(-.30,.23),(.30,.23))):
    B(tank, "foot_%d"%i, (.09,.09,.45), (TANK_X+dx,TANK_Y+dy,.225), silver_dark)
R(tank, "top_neck", (TANK_X,TANK_Y,2.27), (TANK_X,TANK_Y,2.48), .09, silver)
R(tank, "top_flange", (TANK_X,TANK_Y,2.42), (TANK_X,TANK_Y,2.47), .15, silver_dark)
R(tank, "side_connection", (TANK_X+.38,TANK_Y,1.62), (TANK_X+.67,TANK_Y,1.62), .07, silver)
scene.include("tank", tank)

# Foreground conveyor: several rails and a restrained set of visible rollers.
conveyor = Asset("foreground_conveyor")
# Runs across the foreground, cropped at the left edge.
for j, y in enumerate((-6.9,-5.7,-4.5)):
    B(conveyor, "blue_belt_%d"%j, (8.9,.83,.10), (-2.2,y,.93), blue)
    for side in (-1,1):
        yy = y+side*.49
        B(conveyor, "side_rail_%d_%d"%(j,side), (9.0,.08,.17), (-2.2,yy,1.02), silver_light)
        for i, x in enumerate((-5.8,-2.9,0,2.0)):
            B(conveyor, "leg_%d_%d_%d"%(j,side,i), (.09,.09,.92), (x,yy,.46), silver)
    for i in range(10):
        x = -6.2+i*.87
        R(conveyor, "roller_%d_%d"%(j,i), (x,y-.40,1.00), (x,y+.40,1.00), .025, silver_light)
B(conveyor, "transfer_frame", (1.65,4.15,.14), (2.8,-5.65,.92), silver)
B(conveyor, "motor", (.48,.35,.32), (3.55,-5.4,.62), silver_dark)
scene.include("conveyor", conveyor)

# Service piping and rear electrical cabinet.
services = Asset("service_equipment")
B(services, "electrical_cabinet", (.75,.65,2.35), (6.3,4.0,1.175), silver_light)
B(services, "cabinet_door", (.60,.035,2.05), (6.3,3.66,1.20), silver)
for i, x in enumerate((-5.4,-4.95,-4.5)):
    R(services, "floor_process_pipe_%d"%i, (x,-1.2,.22), (x,4.8,.22), .055, silver)
scene.include("services", services)

realize(scene)

# Configure render-relevant materials after SceneAct realization.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    col = bsdf.inputs["Base Color"].default_value
    r,g,b = col[0],col[1],col[2]
    if g > r*1.3 and g > b*1.05:
        bsdf.inputs["Roughness"].default_value = .25
        bsdf.inputs["Metallic"].default_value = .22
    elif abs(r-g)<.10 and abs(g-b)<.10 and r>.30:
        bsdf.inputs["Metallic"].default_value = .72
        bsdf.inputs["Roughness"].default_value = .27
    else:
        bsdf.inputs["Roughness"].default_value = .46

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
background.inputs["Color"].default_value = (0.70,0.78,0.82,1)
background.inputs["Strength"].default_value = .50

# The runner owns output resolution. Set the photograph's aspect for the
# landmark projection, without rendering or writing files.
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
area_emitter((-6,-2,5.7), power=1800, size=7, target=(0,1,1.8))
area_emitter((2,0,6.2), power=1300, size=7, target=(0,1,0))
area_emitter((5,7,6.3), power=1000, size=6, target=(1,2,2))
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass

# Compare actual visible geometry landmarks against separately recorded estimates.
# The associations are approximate because the single photograph leaves depth
# and exact corners uncertain.
landmarks = [
    ("main head upper front", (MAIN_X, MAIN_Y-.825, 4.34), (.68,.31)),
    ("main platform front right", (4.4,.22,PLATFORM_Z), (.79,.61)),
    ("tank top", (TANK_X,TANK_Y,2.37), (.40,.53)),
    ("left window top", (-7.39,-3.1,4.34), (.10,.34)),
    ("foreground rail corner", (2.0,-6.21,1.10), (.53,.83)),
]
def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
             y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
             scale_y=sc.render.pixel_aspect_y)
    out = []
    for label,p,ref in landmarks:
        q = proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if q.w <= 1e-8 else (.5*(q.x/q.w+1), .5*(1-q.y/q.w))
        out.append((label,ref,uv))
    return out

# If the primary machine is outside the frame, make one small aiming correction.
initial = projections()
primary = initial[0][2]
if primary is not None and (primary[0] < .05 or primary[0] > .95 or primary[1] < .05 or primary[1] > .90):
    original_rotation = sc.camera.rotation_euler.copy()
    direction = Vector((MAIN_X, MAIN_Y, 3.25)) - sc.camera.location
    sc.camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
    trial = projections()
    # Retain the correction only when both the tank and foreground rail remain
    # at least partly inside the photograph.
    if any(row[2] is None or not (-.10 < row[2][0] < 1.10 and -.10 < row[2][1] < 1.10)
           for row in (trial[2],trial[4])):
        sc.camera.rotation_euler = original_rotation

print("Landmark projections: label | reference estimate | actual")
for label,ref,uv in projections():
    print(label, ref, None if uv is None else tuple(round(v,3) for v in uv))
