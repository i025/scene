# Reference inventory and comparison with the second complete render.
# Coordinates are approximate normalized image coordinates, x right, y down.
# Background wall: reference (0,0)-(.82,.73); render (0,0)-(.80,.74).
# Curtain: reference (.81,0)-(1,.43); render (.80,0)-(1,.57).
# Sofa: reference (.02,.28)-(.97,.95); render (.07,.28)-(.91,.80).
# Sofa top is nearly horizontal in both. The reference has deeper arms and a
# taller visible front, with rounded cushions and an angled left pillow.
# Table: reference rear-left (.32,.61), front-left around (.33,.74), with
# legs cropped at the bottom; render rear-left (.27,.62), front-left (.27,.73),
# and visible leg bottoms around .98. Its right side is cropped in both.
# Plant: reference (.56,.33)-(.72,.65); render (.51,.28)-(.70,.65).
# Cups: reference centers about (.51,.60), (.77,.60); render (.42,.59), (.79,.59).
# The tabletop overlaps the sofa front; the plant and two cups overlap the sofa.
# The reference table edges slope slightly upward to the right, while the
# rendered table edges are nearly horizontal. Sofa rear, curtain folds, and
# rear table legs are partly hidden and uncertain.
#
# Ranked corrections:
# 1. Increase sofa vertical size about its base by 24%, predicting a higher
#    top and a lower, deeper visible front. Shift the sofa down slightly in
#    world space to retain its top near the reference anchor.
# 2. Move the table and its contents slightly right and closer to the camera;
#    the left contour moves right and its front legs extend below the frame.
#    Rotate the table group slightly around Z to give its long edges a slope.
# 3. Move the left setting toward the plant; shorten the tallest flower stems
#    so their top moves down. Retain the right cup and plant's relative position.
# 4. The render looks brighter and flatter than the reference, but brightness
#    depends on both lighting and surface color. Darken the sofa's lower front
#    and use a stronger directional key while retaining the pale wall.
# Camera remains unchanged, preserving the matching sofa width and background.
# Computed projections below are geometry points, not rendered silhouette bounds.
#
# Estimated expanded primitives: architecture 9; sofa 11 fillet boxes * 26 =
# 286; table 5; two settings 30 including tube expansions; bouquet 106.
# Approximately 436 total primitive meshes.

import math
import bpy
from mathutils import Vector
from sceneact import *

scene = Scene("Living room")
SOFA_W = 3.75
SOFA_Y = .65
SOFA_Z_SCALE = 1.24
SOFA_Z_OFFSET = -.08
TABLE_X = .84
TABLE_Y = -1.22
TABLE_W = 3.05
TABLE_D = 1.02
TABLE_Z = .69
TABLE_ANGLE = 3.0
CAM_POS = (.05, -7.6, 1.95)
CAM_TARGET = (.05, .12, 1.03)
CAM_LENS = 60

wall = (.76,.75,.72)
floor = (.25,.24,.23)
ochre = (.53,.235,.055)
ochre_light = (.68,.34,.085)
ochre_shadow = (.39,.15,.032)
wood = (.028,.022,.019)
ceramic = (.89,.90,.86)
leaf = (.16,.26,.09)
leaf_light = (.29,.37,.13)
stem = (.18,.25,.09)
flower = (.42,.46,.60)
flower_light = (.62,.65,.75)

architecture = Asset("Architecture")
architecture.include("back_wall", box((10,.12,5), center=(0,1.38,2.48), color=wall))
architecture.include("floor", box((10,10,.10), center=(0,0,-.05), color=floor))
architecture.include("window_shadow", box((1.05,.05,3.8),
    center=(2.28,1.29,2.35), color=(.055,.055,.055)))
for i,(x,width,shade) in enumerate([
    (1.72,.16,.09),(1.86,.15,.16),(2.00,.14,.08),
    (2.14,.16,.23),(2.28,.16,.13),(2.43,.17,.055)]):
    architecture.include("curtain_fold_%02d" % i, box(
        (width,.10,3.55), center=(x,1.18+.025*(i%2),2.26),
        color=(shade,shade*.98,shade*.96)))
scene.include("architecture", architecture)

sofa = Asset("Mustard sofa")
sofa.include("lower_body", fillet_box((SOFA_W-.30,.95,.63),.09,
    center=(0,SOFA_Y,.38),color=ochre_shadow))
sofa.include("front_panel", fillet_box((SOFA_W-.34,.15,.43),.055,
    center=(0,SOFA_Y-.49,.31),color=ochre))
sofa.include("back_frame", fillet_box((SOFA_W-.32,.32,1.10),.09,
    center=(0,SOFA_Y+.34,1.12),color=ochre))
for i,x in enumerate((-.84,.84)):
    sofa.include("back_cushion_%d" % i, fillet_box((1.64,.28,.67),.08,
        center=(x,SOFA_Y+.13,1.22),color=ochre_light))
for i,x in enumerate((-1.10,0,1.10)):
    sofa.include("seat_cushion_%d" % i,fillet_box((1.07,.78,.28),.09,
        center=(x,SOFA_Y-.12,.79),color=ochre_light if i==1 else ochre))
for side,x in (("left",-1.77),("right",1.77)):
    sofa.include(side+"_arm",fillet_box((.39,1.04,1.05),.075,
        center=(x,SOFA_Y-.03,.62),color=ochre))
pillow=fillet_box((.63,.18,.57),.075,center=(-1.20,SOFA_Y-.16,1.22),
                  color=(.82,.48,.18))
pillow.turn(axis="+y",degrees=-14)
sofa.include("loose_pillow",pillow)
sofa.resize((1,1,SOFA_Z_SCALE),pivot=(0,0,0))
sofa.move((0,0,SOFA_Z_OFFSET))
scene.include("sofa",sofa)

# Table group and settings are rotated together about the table center.
group = Asset("Coffee table and tabletop objects")
table = Asset("Coffee table")
table.include("top",box((TABLE_W,TABLE_D,.11),
    center=(TABLE_X,TABLE_Y,TABLE_Z),color=wood))
for i,x in enumerate((TABLE_X-1.38,TABLE_X+1.38)):
    for j,y in enumerate((TABLE_Y-.40,TABLE_Y+.40)):
        table.include("leg_%d_%d" % (i,j),box((.14,.14,.66),
            center=(x,y,.34),color=wood))
group.include("table",table)

def place_setting(name,x,y):
    a=Asset(name)
    nap=box((.67,.42,.018),center=(x,y,.755),color=(.62,.68,.64))
    nap.turn(axis="+z",degrees=-6)
    a.include("lower_napkin",nap)
    nap2=box((.59,.34,.015),center=(x+.01,y,.768),color=(.83,.85,.80))
    nap2.turn(axis="+z",degrees=4)
    a.include("upper_napkin",nap2)
    saucer=ball(.25,center=(x,y,.79),color=ceramic)
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
    group.include(name,a)

place_setting("Left place setting",.12,-1.14)
place_setting("Right place setting",1.34,-1.13)

plant=Asset("Flower pot and bouquet")
px,py=.60,-.98
for i in range(5):
    z0=.75+i*.057
    plant.include("pot_section_%d" % i,rod(.14+i*.012,
        start=(px,py,z0),end=(px,py,z0+.061),color=(.075,.085,.068)))
plant.include("pot_lip",rod(.205,start=(px,py,1.025),
    end=(px,py,1.065),color=(.09,.10,.08)))
plant.include("soil",rod(.177,start=(px,py,1.065),
    end=(px,py,1.069),color=(.10,.085,.055)))
heads=[(-.29,-.01,1.43),(-.20,.02,1.52),(-.08,.02,1.37),
       (.01,.02,1.58),(.13,.02,1.48),(.27,0,1.49),
       (.32,.04,1.42),(.08,-.03,1.32),(-.15,-.06,1.30)]
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
group.include("flower_arrangement",plant)
group.turn(axis="+z",degrees=TABLE_ANGLE,pivot=(TABLE_X,TABLE_Y,0))
scene.include("table_group",group)

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
background.inputs["Strength"].default_value=.32
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)

# Rotate explicit tabletop landmarks by the same world-space table rotation.
def table_point(x,y,z):
    a=math.radians(TABLE_ANGLE)
    dx,dy=x-TABLE_X,y-TABLE_Y
    return (TABLE_X+dx*math.cos(a)-dy*math.sin(a),
            TABLE_Y+dx*math.sin(a)+dy*math.cos(a),z)

landmarks=[
    ("sofa upper left",(.17,.28),(-1.68,.99,1.555*SOFA_Z_SCALE+SOFA_Z_OFFSET)),
    ("right arm top",(.81,.41),(1.57,.10,1.145*SOFA_Z_SCALE+SOFA_Z_OFFSET)),
    ("table rear left",(.32,.61),table_point(TABLE_X-TABLE_W/2,TABLE_Y+TABLE_D/2,.745)),
    ("pot rim",(.61,.53),table_point(px,py,1.065)),
    ("table front right",(1.0,.72),table_point(TABLE_X+TABLE_W/2,TABLE_Y-TABLE_D/2,.745)),
    ("curtain left",(.81,.10),(1.72,1.18,2.50)),
]
bpy.context.view_layer.update()
cam=sc.camera
dg=bpy.context.evaluated_depsgraph_get()
projection=cam.calc_matrix_camera(dg,x=512,y=342,
    scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
print("Landmark | reference estimate | projected geometry point")
for name,ref,p in landmarks:
    clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv=None if clip.w<=1e-8 else (
        .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
    print(name,ref,None if uv is None else tuple(round(v,3) for v in uv))

area_emitter((-3.4,-4.0,5.4),power=850,size=4.5,
    target=(0,.2,.8),color=(1.0,.92,.82))
area_emitter((3.7,-.1,4.6),power=300,size=3.0,
    target=(0,.5,1.0),color=(.86,.91,1.0))
