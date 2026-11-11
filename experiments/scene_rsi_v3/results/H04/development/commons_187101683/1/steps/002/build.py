# Reference inventory, normalized image bounds, and observed first-render comparison:
# Wall: reference (0,0)-(.82,.74), render mostly (0,0)-(.72,.64).
# Curtain: reference (.81,0)-(1,.43), render (.72,0)-(.85,.56).
# Sofa: reference (.02,.28)-(.97,.95), render (.20,.33)-(.80,.70).
# Table: reference (.32,.59)-(1,1), render (.29,.58)-(.84,.85).
# Pot and flowers: reference (.56,.33)-(.72,.65), render (.49,.36)-(.61,.62).
# Left cup: reference (.46,.55)-(.55,.65), render (.38,.54)-(.44,.63).
# Right cup: reference (.72,.55)-(.81,.65), render (.64,.54)-(.71,.63).
# The table overlaps the sofa; cups and plant overlap the tabletop and sofa.
# Reference sofa top is nearly horizontal; table front edge slopes down slightly
# to the right. The render's table is nearly horizontal and exposes too much floor.
# Sofa rear, back table legs, and the window behind the curtain remain uncertain.
#
# Largest visible discrepancies:
# 1. Sofa and table occupy too little of the frame. Increase lens 43 -> 60,
#    moving their outside contours away from the frame center.
# 2. Table is too centered and its legs end inside the frame. Move the table
#    and its settings right, and lower camera height; the tabletop and legs should
#    occupy more of the lower-right foreground.
# 3. Curtain appears too far left and too pale. Move it right and darken its folds.
# 4. Sofa is too pale and rigid. Deepen the ochre and retain its individual cushions.
# Camera trial projections are printed for the original and revised pose; these
# are point projections, not measurements of rendered silhouettes.
#
# Expanded primitive estimate: architecture 9; sofa 10 fillet boxes * 26 = 260;
# table 5; place settings about 28 including tubes; bouquet about 100. Total ~402.

import math
import bpy
from mathutils import Vector
from sceneact import *

scene = Scene("Living room")

# Geometry and camera parameters are independent.
SOFA_W = 3.75
SOFA_Y = .65
TABLE_W = 3.05
TABLE_Y = -1.00
TABLE_X = .72
TABLE_Z = .69
OLD_CAMERA = ((.05, -7.6, 2.65), (0, .12, 1.00), 43)
CAM_POS = (.05, -7.6, 1.95)
CAM_TARGET = (.05, .12, 1.03)
CAM_LENS = 60

wall = (.76, .75, .72)
floor = (.25, .24, .23)
ochre = (.58, .275, .075)
ochre_light = (.70, .365, .105)
ochre_shadow = (.46, .19, .045)
wood = (.028, .022, .019)
ceramic = (.88, .89, .85)
leaf = (.16, .26, .09)
leaf_light = (.29, .37, .13)
stem = (.18, .25, .09)
flower = (.42, .46, .60)
flower_light = (.62, .65, .75)

architecture = Asset("Architecture")
architecture.include("back_wall", box((10, .12, 5), center=(0, 1.38, 2.48), color=wall))
architecture.include("floor", box((10, 10, .10), center=(0, 0, -.05), color=floor))
architecture.include("window_shadow", box((1.05, .05, 3.8),
    center=(2.28, 1.29, 2.35), color=(.055, .055, .055)))
for i, (x, width, shade) in enumerate([
    (1.72,.16,.09), (1.86,.15,.16), (2.00,.14,.08),
    (2.14,.16,.23), (2.28,.16,.13), (2.43,.17,.055)]):
    architecture.include("curtain_fold_%02d" % i, box(
        (width, .10, 3.55), center=(x, 1.18+.025*(i%2), 2.26),
        color=(shade, shade*.98, shade*.96)))
scene.include("architecture", architecture)

sofa = Asset("Mustard sofa")
sofa.include("lower_body", fillet_box((SOFA_W-.30,.95,.63), .09,
    center=(0,SOFA_Y,.38), color=ochre_shadow))
sofa.include("front_panel", fillet_box((SOFA_W-.34,.15,.43), .055,
    center=(0,SOFA_Y-.49,.31), color=ochre))
sofa.include("back_frame", fillet_box((SOFA_W-.32,.32,1.10), .09,
    center=(0,SOFA_Y+.34,1.12), color=ochre))
for i,x in enumerate((-.84,.84)):
    sofa.include("back_cushion_%d" % i, fillet_box((1.64,.28,.67), .08,
        center=(x,SOFA_Y+.13,1.22), color=ochre_light))
for i,x in enumerate((-1.10,0,1.10)):
    sofa.include("seat_cushion_%d" % i, fillet_box((1.07,.78,.28), .09,
        center=(x,SOFA_Y-.12,.79), color=ochre_light if i==1 else ochre))
for side,x in (("left",-1.77),("right",1.77)):
    sofa.include(side+"_arm", fillet_box((.39,1.04,1.05), .075,
        center=(x,SOFA_Y-.03,.62), color=ochre))
pillow = fillet_box((.63,.18,.57), .075,
    center=(-1.20,SOFA_Y-.16,1.22), color=(.82,.48,.18))
pillow.turn(axis="+y", degrees=-14)
sofa.include("loose_pillow", pillow)
scene.include("sofa", sofa)

table = Asset("Coffee table")
table.include("top", box((TABLE_W,1.02,.11),
    center=(TABLE_X,TABLE_Y,TABLE_Z), color=wood))
for i,x in enumerate((TABLE_X-1.38,TABLE_X+1.38)):
    for j,y in enumerate((TABLE_Y-.40,TABLE_Y+.40)):
        table.include("leg_%d_%d" % (i,j), box((.14,.14,.66),
            center=(x,y,.34), color=wood))
scene.include("coffee_table", table)

def place_setting(name,x,y):
    a = Asset(name)
    nap = box((.67,.42,.018), center=(x,y,.755), color=(.62,.68,.64))
    nap.turn(axis="+z", degrees=-6)
    a.include("lower_napkin",nap)
    nap2 = box((.59,.34,.015), center=(x+.01,y,.768), color=(.83,.85,.80))
    nap2.turn(axis="+z", degrees=4)
    a.include("upper_napkin",nap2)
    saucer = ball(.25,center=(x,y,.79),color=ceramic)
    saucer.resize((1,.72,.075))
    a.include("saucer",saucer)
    a.include("cup_body",rod(.145,start=(x,y,.80),end=(x,y,1.035),color=ceramic))
    a.include("cup_rim",rod(.151,start=(x,y,1.025),end=(x,y,1.046),
        color=(.95,.95,.91)))
    a.include("inside",rod(.119,start=(x,y,1.046),end=(x,y,1.049),
        color=(.57,.53,.46)))
    a.include("handle",sweep_tube(points=[
        (x-.12,y,1.00),(x-.21,y,1.015),(x-.23,y,.96),
        (x-.20,y,.89),(x-.13,y,.88)],radius=.018,color=ceramic))
    scene.include(name,a)

place_setting("Left place setting", -.25, -.92)
place_setting("Right place setting", 1.22, -.91)

plant = Asset("Flower pot and bouquet")
px,py = .48,-.76
for i in range(5):
    z0=.75+i*.057
    plant.include("pot_section_%d" % i,rod(.14+i*.012,
        start=(px,py,z0),end=(px,py,z0+.061),color=(.075,.085,.068)))
plant.include("pot_lip",rod(.205,start=(px,py,1.025),
    end=(px,py,1.065),color=(.09,.10,.08)))
plant.include("soil",rod(.177,start=(px,py,1.065),
    end=(px,py,1.069),color=(.10,.085,.055)))
heads=[(-.29,-.01,1.46),(-.20,.02,1.56),(-.08,.02,1.39),
       (.01,.02,1.68),(.13,.02,1.52),(.27,0,1.53),
       (.32,.04,1.44),(.08,-.03,1.34),(-.15,-.06,1.32)]
for i,(dx,dy,z) in enumerate(heads):
    end=(px+dx,py+dy,z)
    plant.include("stem_%02d" % i,rod(.009,
        start=(px+dx*.15,py+dy,1.065),end=end,color=stem))
    for j in range(3):
        t=.32+.17*j
        side=-1 if (i+j)%2 else 1
        blade=ball(.073,center=(px+dx*t+side*.065,
            py+dy*t+(.025 if j%2 else -.025),1.065+(z-1.065)*t),
            color=leaf_light if j==1 else leaf)
        blade.resize((1.15,.30,.28))
        blade.turn(axis="+y",degrees=side*25)
        plant.include("leaf_%02d_%d" % (i,j),blade)
    for j in range(7):
        ang=2*math.pi*j/7
        r=.045 if j else 0
        fl=ball(.033 if j else .042,
            center=(end[0]+r*math.cos(ang),end[1]+r*.42*math.sin(ang),
                    end[2]+r*.65*math.sin(ang)),
            color=flower_light if (i+j)%3==0 else flower)
        plant.include("blossom_%02d_%d" % (i,j),fl)
scene.include("flower_arrangement",plant)

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
background.inputs["Color"].default_value=(.72,.72,.70,1)
background.inputs["Strength"].default_value=.38
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100

# Explicit world landmarks and separately estimated reference positions.
landmarks=[
    ("sofa upper left",(.17,.28),(-1.68,.99,1.555)),
    ("right arm top",(.81,.41),(1.57,.10,1.145)),
    ("table rear left",(.32,.61),(TABLE_X-TABLE_W/2,TABLE_Y+.51,.745)),
    ("pot rim",(.61,.53),(px,py,1.065)),
    ("table front right",(1.0,.72),(TABLE_X+TABLE_W/2,TABLE_Y-.51,.745)),
    ("curtain left",(.81,.10),(1.72,1.18,2.50)),
]
def report(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(dg,x=512,y=342,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    print(label,"| reference | projected")
    for name,ref,p in landmarks:
        clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,ref,None if uv is None else tuple(round(v,3) for v in uv))

# Check the old pose, then a small lens trial, then the final camera.
set_view(*OLD_CAMERA[:2],lens=OLD_CAMERA[2],sensor=36)
report("original")
sc.camera.data.lens=46
report("trial lens 46")
sc.camera.data.lens=OLD_CAMERA[2]
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
report("revised")

area_emitter((-3.4,-4.0,5.4),power=850,size=4.5,
    target=(0,.2,.8),color=(1.0,.92,.82))
area_emitter((3.7,-.1,4.6),power=450,size=3.0,
    target=(0,.5,1.0),color=(.86,.91,1.0))
