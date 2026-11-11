from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and approximate normalized image anchors:
# - Ceiling: (0.00, 0.00)-(1.00, 0.31), pale narrow parallel boards.
# - Rear window wall: (0.03, 0.30)-(0.66, 0.58), dark mullions over bright panes.
# - Right window wall: (0.65, 0.23)-(1.00, 0.56), bright panes, dark frames.
# - Large foreground left pendant: (0.02, 0.03)-(0.23, 0.41), dark stem and dome.
# - More pendants recede across (0.37, 0.28)-(1.00, 0.44).
# - Left booth row: (0.00, 0.50)-(0.33, 0.92), dark rectangular backs.
# - Foreground tabletop: (0.00, 0.85)-(0.46, 1.00), pale surface, cropped.
# - Center dining tables and chairs: (0.35, 0.51)-(0.85, 1.00), chair backs
#   overlap tabletop edges; chairs have slim legs and reflective pedestal bases.
# - Large leafy plant: (0.76, 0.40)-(1.00, 1.00), partially hides right furniture.
# - Small rear plant: (0.34, 0.47)-(0.53, 0.66).
# - Dark plank floor: (0.22, 0.58)-(1.00, 1.00), lines converge toward rear.
# Dominant edges: rear window top nearly horizontal, ceiling boards converge toward
# right; floor lines converge toward the rear; pendant cords are nearly vertical.
# Occluded window exterior and furniture behind plants are uncertain.
#
# Primitive estimate: architecture ~70, furniture ~115, lamps ~35, plants ~110,
# totaling roughly 330 SceneAct primitives. No Boolean operations or fillets.

random.seed(9)
scene = Scene("Restaurant")
C = {
    "white": (0.77, 0.78, 0.76),
    "ceiling": (0.80, 0.81, 0.79),
    "frame": (0.18, 0.19, 0.18),
    "glass": (0.91, 0.93, 0.90),
    "outside": (0.78, 0.81, 0.77),
    "floor": (0.22, 0.23, 0.22),
    "seam": (0.35, 0.36, 0.34),
    "table": (0.67, 0.68, 0.66),
    "chair": (0.32, 0.33, 0.32),
    "booth": (0.25, 0.26, 0.25),
    "metal": (0.52, 0.54, 0.52),
    "dark": (0.065, 0.075, 0.07),
    "leaf": (0.12, 0.15, 0.12),
}
W, BACK, CEIL = 10.0, 7.0, 3.55
CAM_POS = (-0.55, -9.8, 2.75)
CAM_TARGET = (0.15, 3.2, 1.62)
CAM_LENS = 27

# Architecture consists of separately editable planes, mullions and ceiling seams.
room = Asset("Architecture")
room.include("floor", box((W, 19, .12), center=(0, 0, -.07), color=C["floor"]))
room.include("ceiling", box((W, 19, .12), center=(0, 0, CEIL+.06), color=C["ceiling"]))
room.include("rear_sill", box((W, .13, .44), center=(0, BACK, .22), color=C["white"]))
room.include("rear_header", box((W, .14, .25), center=(0, BACK, 3.43), color=C["white"]))
room.include("rear_glazing", box((W, .035, 2.73), center=(0, BACK+.04, 1.84), color=C["glass"]))
for i, x in enumerate([-5, -3.45, -1.85, -.20, 1.45, 3.10, 5]):
    room.include("rear_mullion_%d" % i, box((.065, .12, 2.8), center=(x, BACK-.04, 1.86), color=C["frame"]))
room.include("rear_sill_rail", box((W, .13, .09), center=(0, BACK-.05, .60), color=C["frame"]))
room.include("rear_top_rail", box((W, .13, .08), center=(0, BACK-.05, 3.22), color=C["frame"]))
# Right wall recedes from foreground to the rear.
room.include("right_sill", box((.14, 18, .60), center=(5, 0, .30), color=C["white"]))
room.include("right_glazing", box((.035, 18, 2.55), center=(5.04, 0, 1.91), color=C["glass"]))
room.include("right_header", box((.14, 18, .32), center=(5, 0, 3.39), color=C["white"]))
for i, y in enumerate([-7, -4.2, -1.4, 1.4, 4.2, 7]):
    room.include("right_mullion_%d" % i, box((.13, .065, 2.65), center=(4.97, y, 1.93), color=C["frame"]))
room.include("right_sill_rail", box((.14, 18, .085), center=(4.96, 0, .65), color=C["frame"]))
# The left side is mostly outside the frame; a low wall supports booth seating.
room.include("left_low_wall", box((.12, 18, .63), center=(-5, 0, .315), color=C["white"]))
for i in range(28):
    y = -9.0 + i * .6
    room.include("ceiling_joint_%02d" % i,
                 box((W, .014, .008), center=(0, y, CEIL-.008), color=(.55,.56,.54)))
for i in range(20):
    x = -4.85 + i*.51
    room.include("floor_board_joint_%02d" % i,
                 box((.012, 18, .005), center=(x, 0, .002), color=C["seam"]))
scene.include("architecture", room)

# A washed-out hint of distant trees is visible through the rear glazing.
exterior = Asset("Exterior_silhouettes")
for i in range(11):
    x = -4.6 + i*.91
    z = .95 + random.random()*.30
    crown = ball(.48, center=(x, BACK+.6, z+.48), color=(.74,.77,.73))
    crown.resize((1.1,.20,.9))
    exterior.include("tree_%02d" % i, crown)
scene.include("exterior", exterior)

# Dark upholstered booths in a row along the left side.
booths = Asset("Left_booths")
for i, y in enumerate([-5.2, -2.9, -.6, 1.7, 4.0]):
    b = Asset("Booth_%d" % i)
    b.include("back", box((2.45,.15,1.03), center=(-3.65,y, .67), color=C["booth"]))
    b.include("back_top_edge", box((2.46,.17,.035), center=(-3.65,y,1.19), color=(.39,.40,.39)))
    b.include("seat", box((2.4,.82,.16), center=(-3.65,y+.43,.43), color=C["booth"]))
    b.include("base", box((2.25,.68,.35), center=(-3.65,y+.43,.20), color=(.19,.20,.19)))
    booths.include("booth_%d" % i, b)
scene.include("booths", booths)

# Square restaurant tables with thin light tops and single pedestal supports.
def make_table(name, x, y, sx=1.48, sy=1.05):
    a = Asset(name)
    a.include("top", box((sx,sy,.075), center=(x,y,.77), color=C["table"]))
    a.include("edge", box((sx,sy,.025), center=(x,y,.72), color=(.29,.30,.29)))
    a.include("pedestal", rod(.055, start=(x,y,.09), end=(x,y,.72), color=C["metal"]))
    base = ball(.29, center=(x,y,.07), color=C["metal"])
    base.resize((1,1,.16))
    a.include("base", base)
    return a

tables = Asset("Dining_tables")
table_positions = [
    (-3.38,-6.55,2.65,1.40),
    (-3.55,-3.95,2.00,.92),
    (-3.55,-1.55,1.95,.92),
    (-3.55,.85,1.95,.92),
    (-.85,-1.25,1.55,1.12),
    (1.45,-.25,1.55,1.10),
    (-.75,1.65,1.48,1.02),
    (1.55,2.25,1.42,1.00),
    (-.80,4.12,1.35,.88),
    (1.50,4.65,1.35,.88),
]
for i,(x,y,sx,sy) in enumerate(table_positions):
    tables.include("table_%02d" % i, make_table("Table_%02d" % i,x,y,sx,sy))
scene.include("tables", tables)

# Chair back, seat and supports remain distinct editable parts.
def make_chair(name, x, y, angle=0):
    a = Asset(name)
    a.include("back", box((.83,.105,.89), center=(x,y,.94), color=C["chair"]))
    a.include("back_top_trim", box((.84,.12,.035), center=(x,y,1.39), color=C["metal"]))
    a.include("seat", box((.79,.68,.10), center=(x,y+.30,.49), color=C["chair"]))
    for j, dx in enumerate([-.34,.34]):
        a.include("back_support_%d" % j,
                  rod(.025, start=(x+dx,y,.12), end=(x+dx,y,.92), color=C["metal"]))
        a.include("front_leg_%d" % j,
                  rod(.023, start=(x+dx,y+.58,.06), end=(x+dx,y+.58,.50), color=C["metal"]))
    if angle:
        a.turn(axis="+z", degrees=angle, pivot=(x,y,0))
    return a

chairs = Asset("Dining_chairs")
chair_specs = [
    (-1.9,-2.55,-7), (-.45,-2.75,5),
    (.52,-1.55,-3), (2.35,-1.53,2),
    (-1.90,.35,0), (-.15,.20,4),
    (.45,.78,-4), (2.35,.85,3),
    (-1.75,2.95,0), (-.15,2.88,0),
    (.48,3.35,0), (2.42,3.35,0),
    (-1.65,5.10,0), (.05,5.0,0),
    (.65,5.45,0), (2.35,5.45,0),
    (3.35,-3.0,-8),
]
for i,(x,y,ang) in enumerate(chair_specs):
    chairs.include("chair_%02d" % i, make_chair("Chair_%02d" % i,x,y,ang))
scene.include("chairs", chairs)

# Pendant shades are flattened ellipsoids and short cylindrical collars.
lamps = Asset("Pendant_lights")
lamp_specs = [
    (-3.35,-5.6,2.50,.72),
    (-3.50,-1.8,2.59,.52),
    (-3.30,2.20,2.65,.37),
    (-2.40,5.20,2.66,.25),
    (-.95,3.70,2.62,.31),
    (.90,2.40,2.61,.37),
    (2.65,1.10,2.60,.41),
    (4.05,2.85,2.67,.32),
    (4.50,-1.40,2.65,.37),
]
for i,(x,y,z,r) in enumerate(lamp_specs):
    a = Asset("Pendant_%02d" % i)
    a.include("cord", rod(.012, start=(x,y,z+.23), end=(x,y,CEIL), color=C["dark"]))
    a.include("collar", rod(r*.25, start=(x,y,z+.02), end=(x,y,z+.30), color=C["dark"]))
    dome = ball(r, center=(x,y,z), color=C["dark"])
    dome.resize((1,1,.42))
    a.include("shade", dome)
    rim = ball(r*1.02, center=(x,y,z-.12), color=(.15,.16,.15))
    rim.resize((1,1,.055))
    a.include("rim", rim)
    lamps.include("pendant_%02d" % i, a)
scene.include("pendants", lamps)

# Plants use branching stalks and narrow, individually editable leaf silhouettes.
def plant(name, x, y, height, spread, count):
    a = Asset(name)
    a.include("pot", box((.48,.48,.58), center=(x,y,.29), color=(.23,.24,.22)))
    for i in range(count):
        ang = 2*math.pi*i/count + random.uniform(-.18,.18)
        length = random.uniform(.55,1.0)*spread
        topz = random.uniform(.60,1.0)*height
        ex, ey = x+math.cos(ang)*length, y+math.sin(ang)*length
        a.include("stem_%02d" % i, rod(.015, start=(x,y,.42),
                                      end=(ex,ey,topz), color=C["leaf"]))
        # Elongated blades run diagonally from the branch midpoint.
        for j in range(2):
            t = .55 + j*.29
            lx = x + (ex-x)*t
            ly = y + (ey-y)*t
            lz = .42 + (topz-.42)*t
            blade = ball(.20, center=(lx,ly,lz), color=C["leaf"])
            blade.resize((1.7,.25,.10))
            blade.turn(axis="+z", degrees=math.degrees(ang)+(-32 if j==0 else 32))
            a.include("leaf_%02d_%d" % (i,j), blade)
    return a

scene.include("large_right_plant", plant("Large_right_plant", 4.05,-1.45,2.58,1.65,20))
scene.include("rear_planter", plant("Rear_planter", -2.00,4.35,1.42,.90,12))

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 379
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

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
background.inputs["Color"].default_value = (0.83,0.85,0.83,1)
background.inputs["Strength"].default_value = .8

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0,3,3.25), power=650, size=7, target=(0,0,0), color=(1,1,1))
area_emitter((-3,-5,3.1), power=400, size=5, target=(-1,1,0), color=(1,1,1))
area_emitter((4,3,2.6), power=500, size=5, target=(0,0,1), color=(1,1,1))

# Reference estimates and computed projections use geometry points, not object origins.
landmarks = [
    ("rear_left_window_top", (-3.45, BACK-.04, 3.22), (.10,.31)),
    ("rear_center_window_top", (1.45, BACK-.04, 3.22), (.47,.32)),
    ("right_rear_window_corner", (4.97, BACK, 3.22), (.65,.29)),
    ("middle_table_corner", (-1.625,-1.81,.8075), (.38,.65)),
    ("foreground_table_corner", (-2.055,-7.25,.8075), (.45,.99)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("LANDMARK                       reference       projected")
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point,1.0))
    if clip.w > 1e-8:
        uv = (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print("%-29s (%5.2f,%5.2f)  (%5.2f,%5.2f)" %
              (name,ref[0],ref[1],uv[0],uv[1]))
    else:
        print("%-29s behind camera" % name)

sc.view_settings.view_transform = "AgX"
