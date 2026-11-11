# Reference versus previous render, approximate normalized image coordinates:
# The reference classroom is the inset at x=.58-.91, y=.44-.96. Within that
# inset, the rear windows span roughly x=.08-.73, y=.04-.33; the foreground
# cabinet spans x=.39-.80, y=.55-.91, overlapping a red rug near the bottom.
# In the previous render, the window wall occupies about x=.44-.82, y=.20-.49,
# the foreground cabinet about x=.36-.51, y=.52-.70, and a blank exterior
# side wall occupies x=.58-.84, y=.25-.89. Gray exterior surrounds the room.
# Largest discrepancies: (1) the camera looks at the room from outside and
# the side wall hides much of the layout; (2) the room and foreground cabinet
# are too small in frame; (3) window and shelf edges converge too strongly.
# The reference has visible gaps between low shelves, tables behind the main
# cabinet, and warm flooring; the foreground cabinet hides part of the rug.
#
# Corrections: move the camera into the front corner and aim toward the rear
# wall, omit the near side wall that blocks the view, and use a moderate wide
# lens. This should move the window row toward the top and spread its ends
# toward the image edges, while enlarging the foreground cabinet toward the
# lower center. Move the foreground cabinet locally toward the camera so it
# remains the dominant furniture silhouette. Numerical projections below
# compare the previous camera, a small trial, and the selected camera; these
# computed points are distinct from the observed image contours.
#
# Inventory: cream rear and right walls, light plank floor, six large rear
# windows with pale frames, low open wooden shelving on the walls and in the
# middle, a large foreground open cabinet with trays and objects, two child
# tables and stools, a rust-red round rug, and loose Montessori materials.
# The precise far-right layout and individual shelf contents are uncertain.
# Estimated expansion: about 190 primitive boxes and rods, no Boolean solids,
# fillets, clones or sweep tubes. All major items have named asset children.

import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

scene = Scene("Montessori classroom")

ROOM_W, ROOM_D, ROOM_H = 8.0, 6.2, 3.0
CAMERA_POSITION = (3.75, -4.65, 2.75)
CAMERA_TARGET = (-0.05, 1.05, 1.05)
CAMERA_LENS = 23.5

cream = (0.82, 0.80, 0.71)
floor_color = (0.68, 0.51, 0.34)
wood = (0.57, 0.38, 0.22)
wood_light = (0.73, 0.54, 0.34)
wood_dark = (0.34, 0.22, 0.13)
frame = (0.89, 0.88, 0.80)
glass = (0.62, 0.76, 0.73)
rug_color = (0.52, 0.13, 0.09)
white = (0.88, 0.85, 0.75)
green = (0.30, 0.43, 0.22)
blue = (0.25, 0.40, 0.45)
yellow = (0.78, 0.57, 0.25)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
add_box(architecture, "wood floor", (ROOM_W, ROOM_D, 0.10),
        (0, 0, -0.05), floor_color)
add_box(architecture, "rear cream wall", (ROOM_W, 0.12, ROOM_H),
        (0, ROOM_D / 2, ROOM_H / 2), cream)
# The right wall is beyond the camera, but remains available where visible.
add_box(architecture, "right cream wall", (0.12, ROOM_D, ROOM_H),
        (ROOM_W / 2, 0, ROOM_H / 2), cream)
add_box(architecture, "rear skirting", (ROOM_W, 0.06, 0.13),
        (0, ROOM_D / 2 - 0.09, 0.065), frame)
add_box(architecture, "right skirting", (0.06, ROOM_D, 0.13),
        (ROOM_W / 2 - 0.09, 0, 0.065), frame)
for i in range(15):
    x = -3.75 + i * 0.50
    add_box(architecture, "floor plank joint %02d" % i,
            (0.008, ROOM_D, 0.002), (x, 0, 0.002), (0.53, 0.39, 0.25))
scene.include("architecture", architecture)

windows = Asset("Back wall windows")
window_y = ROOM_D / 2 - 0.075
for i in range(6):
    x = -3.22 + i * 1.27
    add_box(windows, "daylight glazing %d" % i, (1.13, 0.025, 1.42),
            (x, window_y, 2.03), glass)
    for side in (-1, 1):
        add_box(windows, "upright %d %d" % (i, side), (0.055, 0.07, 1.54),
                (x + side * 0.59, window_y - 0.04, 2.03), frame)
    for z in (1.28, 2.78):
        add_box(windows, "horizontal frame %d %.2f" % (i, z),
                (1.23, 0.07, 0.055), (x, window_y - 0.04, z), frame)
    add_box(windows, "center mullion %d" % i, (0.035, 0.07, 1.44),
            (x, window_y - 0.045, 2.03), frame)
add_box(windows, "continuous sill", (7.8, 0.20, 0.08),
        (0, window_y - 0.09, 1.26), frame)
scene.include("windows", windows)

def shelf(name, x, y, width, depth, height, divisions=2):
    a = Asset(name)
    t = 0.045
    add_box(a, "top", (width, depth, t), (x, y, height - t/2), wood_light)
    add_box(a, "bottom", (width, depth, t), (x, y, 0.08), wood)
    add_box(a, "middle shelf", (width, depth, t), (x, y, height*0.51), wood_light)
    for side in (-1, 1):
        add_box(a, "side %d" % side, (t, depth, height-0.10),
                (x + side*(width-t)/2, y, height/2 + 0.02), wood)
    for j in range(1, divisions):
        px = x - width/2 + width*j/divisions
        add_box(a, "partition %d" % j, (t, depth, height-0.16),
                (px, y, height/2), wood)
    add_box(a, "back panel", (width-2*t, 0.025, height-0.12),
            (x, y+depth/2-t/2, height/2), wood_dark)
    scene.include(name, a)

shelf("foreground open cabinet", 0.25, -1.55, 2.35, 0.62, 0.88, 3)
shelf("middle left cabinet", -2.15, 0.40, 1.75, 0.52, 0.84)
shelf("middle right cabinet", 1.35, 0.95, 1.65, 0.52, 0.84)
shelf("rear left cabinet", -2.72, 2.58, 1.8, 0.52, 0.80)
shelf("rear center cabinet", -0.42, 2.58, 1.65, 0.52, 0.80)
shelf("rear right cabinet", 2.05, 2.58, 1.8, 0.52, 0.80)
shelf("right storage", 3.18, 1.55, 1.15, 0.45, 0.78)

materials = Asset("Learning materials")
def tray(name, x, y, z, w=0.36, d=0.23):
    add_box(materials, name+" base", (w, d, 0.025), (x, y, z), wood_dark)
    for s in (-1, 1):
        add_box(materials, name+" long rim %d" % s, (w, 0.022, 0.045),
                (x, y+s*d/2, z+0.028), wood_light)
        add_box(materials, name+" end rim %d" % s, (0.022, d, 0.045),
                (x+s*w/2, y, z+0.028), wood_light)

for i, (x,y,z) in enumerate([
    (-2.70,.40,.86), (-2.00,.40,.86), (.80,.95,.86), (1.50,.95,.86),
    (-3.15,2.58,.82), (-2.50,2.58,.82), (-.55,2.58,.82),
    (1.75,2.58,.82), (2.40,2.58,.82),
    (-.45,-1.55,.90), (.25,-1.55,.90), (.95,-1.55,.90)
]):
    tray("tray %02d" % i, x,y,z)

for i, (x,y,z,c) in enumerate([
    (-2.70,.40,.93,yellow), (-2.00,.40,.93,blue),
    (.80,.95,.93,green), (1.50,.95,.93,yellow),
    (-.45,-1.55,.97,blue), (.25,-1.55,.97,yellow),
    (.95,-1.55,.97,green), (-2.50,2.58,.89,yellow)
]):
    add_box(materials, "geometric block %d" % i, (.12,.10,.09), (x,y,z), c)
for i, (x,z) in enumerate([
    (-.47,.20), (.23,.20), (.95,.20),
    (-.47,.56), (.23,.56), (.95,.56)
]):
    add_box(materials, "cabinet box %d" % i, (.31,.24,.13),
            (x,-1.68,z), wood_light if i%2 else white)
scene.include("materials", materials)

def table(name, x, y, width, depth):
    a = Asset(name)
    add_box(a, "top", (width,depth,.065), (x,y,.59), wood_light)
    for sx in (-1,1):
        for sy in (-1,1):
            add_box(a, "leg %d %d" % (sx,sy), (.06,.06,.55),
                    (x+sx*(width/2-.09),y+sy*(depth/2-.09),.28),wood)
    scene.include(name,a)

def stool(name,x,y):
    a=Asset(name)
    add_box(a,"seat",(.33,.31,.045),(x,y,.34),wood_light)
    for sx in (-1,1):
        for sy in (-1,1):
            add_box(a,"leg %d %d" % (sx,sy),(.035,.035,.31),
                    (x+sx*.125,y+sy*.11,.16),wood)
    scene.include(name,a)

table("central activity table",-.55,.30,1.25,.70)
table("right activity table",2.55,-.10,1.05,.65)
for i,(x,y) in enumerate([(-1.02,-.30),(.0,-.30),(-.75,.90),
                           (2.30,-.70),(2.90,-.70)]):
    stool("child stool %d" % i,x,y)

rug=Asset("Round red rug")
rug.include("rug disk",rod(radius=1.05,length=.018,
                            center=(.25,-1.55,.012),axis="+z",color=rug_color))
scene.include("rug",rug)

realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(0.78,0.84,0.89,1)
background.inputs["Strength"].default_value=.65

sc.render.engine="CYCLES"
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.render.resolution_x=1920
sc.render.resolution_y=1080
sc.render.resolution_percentage=100
sc.render.pixel_aspect_x=1
sc.render.pixel_aspect_y=1

area_emitter((0,3.7,3.5),power=1800,size=5,
             target=(0,-.3,.5),color=(1,.91,.79))
area_emitter((-3,-3,4.8),power=700,size=7,
             target=(0,0,.5),color=(1,.96,.89))

landmarks=[
    ("left window upper",(-3.81,window_y,2.78),(.08,.05)),
    ("right window upper",(3.72,window_y,2.78),(.89,.05)),
    ("foreground cabinet top left",(-.925,-1.86,.88),(.35,.58)),
    ("foreground cabinet top right",(1.425,-1.86,.88),(.77,.69)),
    ("rear cabinet left",(-3.62,2.32,.80),(.08,.44)),
]

def project(point):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(
        dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    clip=projection @ cam.matrix_world.inverted() @ Vector((*point,1.0))
    if clip.w<=1e-8:
        return None
    return (round(.5*(clip.x/clip.w+1),3),
            round(.5*(1-clip.y/clip.w),3))

def projection_table(label):
    print(label)
    for name,point,ref in landmarks:
        print(name,"reference",ref,"computed",project(point))

# Trial upward aim: verify that stationary features move down, then restore.
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
projection_table("Selected camera")
set_view(CAMERA_POSITION,(CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]+.15),
         lens=CAMERA_LENS,sensor=36)
projection_table("Trial aim 0.15 m higher")
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
bpy.context.view_layer.update()
