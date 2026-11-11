from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and visual anchors, normalized to the 512 x 379 image:
# Ceiling: (0,0)-(1,.31), narrow pale boards; its rear edge is almost horizontal.
# Rear windows: (.03,.30)-(.65,.58), with dark vertical mullions and bright panes.
# Right windows: (.65,.23)-(1,.57), their upper edge rises toward the right.
# Large left pendant: (.02,.03)-(.23,.41), cord, tall collar and broad dark dome.
# Smaller pendants: approximately (.37,.28)-(1,.44), overlapping the windows.
# Left booth backs: (0,.52)-(.33,.90); pale foreground table: (0,.85)-(.46,1).
# Center tables and dark chair backs: (.35,.52)-(.85,1), chairs overlap table edges.
# Right plant: (.77,.40)-(1,1), dark leafy fronds overlap windows and chairs.
# Small rear plant: (.34,.46)-(.53,.66). Dark floorboards converge toward the rear.
# Exterior and furniture hidden by the foliage are uncertain.
#
# Review of the preceding full render against the reference:
# 1. The rear window top appeared around y=.38 versus approximately .31 in the
#    reference; the floor occupied too much of the view. Lowering camera target Z
#    should move stationary window and furniture contours upward.
# 2. The large pendant was cut off at the left edge, while the reference shade is
#    fully visible near x=.02-.23. Moving this lamp right and farther from the
#    camera should reveal it and reduce its apparent size.
# 3. Foreground furniture was too pale, and the foreground right chair and plant
#    did not make the dark overlapping masses in the photograph. Darker finishes,
#    a closer right chair, and more substantial leaves address those local regions.
# 4. The reference rear-window corner is near (.65,.29), versus the rendered
#    corner near (.70,.38). A modest rightward camera target moves it left; the
#    lower target also moves it up. Rear left extent is locally widened.
# 5. The reference foreground table reaches about x=.46 at the bottom; the
#    previous tabletop was cropped much farther left. Its width and position are
#    adjusted locally. Ceiling seams and the arrangement of receding tables remain.
# Computed point projections below are separate from observed silhouette bounds.
#
# Approximate expanded primitive count: architecture 80, booths 20, tables 40,
# chairs 119, pendants 36, plants 155, exterior 9: about 459 meshes. No booleans.

random.seed(9)
scene = Scene("Restaurant")
C = {
    "white": (.78,.79,.77), "ceiling": (.82,.83,.81),
    "frame": (.14,.15,.14), "glass": (.94,.95,.92),
    "floor": (.16,.17,.16), "seam": (.26,.27,.25),
    "table": (.68,.69,.67), "chair": (.19,.20,.19),
    "booth": (.15,.16,.15), "metal": (.50,.52,.50),
    "dark": (.035,.042,.038), "leaf": (.055,.075,.055),
}
W, BACK, CEIL = 10.0, 7.0, 3.55
CAM_POS = (-.55,-9.8,2.75)
OLD_TARGET = (.15,3.2,1.62)
CAM_TARGET = (.65,3.2,.92)
CAM_LENS = 27

room = Asset("Architecture")
room.include("floor", box((W,19,.12), center=(0,0,-.07), color=C["floor"]))
room.include("ceiling", box((W,19,.12), center=(0,0,CEIL+.06), color=C["ceiling"]))
room.include("rear_sill", box((W,.13,.44), center=(0,BACK,.22), color=C["white"]))
room.include("rear_header", box((W,.14,.25), center=(0,BACK,3.43), color=C["white"]))
room.include("rear_glazing", box((W,.035,2.73), center=(0,BACK+.04,1.84), color=C["glass"]))
for i,x in enumerate([-5,-3.45,-1.85,-.20,1.45,3.10,5]):
    room.include("rear_mullion_%d"%i, box((.065,.12,2.8), center=(x,BACK-.04,1.86), color=C["frame"]))
room.include("rear_sill_rail", box((W,.13,.09), center=(0,BACK-.05,.60), color=C["frame"]))
room.include("rear_top_rail", box((W,.13,.08), center=(0,BACK-.05,3.22), color=C["frame"]))
room.include("right_sill", box((.14,18,.60), center=(5,0,.30), color=C["white"]))
room.include("right_glazing", box((.035,18,2.55), center=(5.04,0,1.91), color=C["glass"]))
room.include("right_header", box((.14,18,.32), center=(5,0,3.39), color=C["white"]))
for i,y in enumerate([-7,-4.2,-1.4,1.4,4.2,7]):
    room.include("right_mullion_%d"%i, box((.13,.065,2.65), center=(4.97,y,1.93), color=C["frame"]))
room.include("right_sill_rail", box((.14,18,.085), center=(4.96,0,.65), color=C["frame"]))
room.include("left_low_wall", box((.12,18,.63), center=(-5,0,.315), color=C["white"]))
for i in range(28):
    room.include("ceiling_joint_%02d"%i, box((W,.014,.008),
                 center=(0,-9+i*.6,CEIL-.008), color=(.58,.59,.57)))
for i in range(20):
    room.include("floor_joint_%02d"%i, box((.012,18,.005),
                 center=(-4.85+i*.51,0,.002), color=C["seam"]))
scene.include("architecture",room)

exterior = Asset("Exterior_silhouettes")
for i in range(9):
    crown = ball(.48, center=(-4.6+i*1.12,BACK+.6,1.5+random.random()*.2),
                 color=(.81,.83,.80))
    crown.resize((1.1,.20,.9))
    exterior.include("distant_tree_%02d"%i,crown)
scene.include("exterior",exterior)

booths = Asset("Left_booths")
for i,y in enumerate([-5.2,-2.9,-.6,1.7,4.0]):
    b = Asset("Booth_%d"%i)
    b.include("back",box((2.45,.15,1.03),center=(-3.65,y,.67),color=C["booth"]))
    b.include("top_edge",box((2.46,.17,.035),center=(-3.65,y,1.19),color=(.31,.32,.31)))
    b.include("seat",box((2.4,.82,.16),center=(-3.65,y+.43,.43),color=C["booth"]))
    b.include("base",box((2.25,.68,.35),center=(-3.65,y+.43,.20),color=(.12,.13,.12)))
    booths.include("booth_%d"%i,b)
scene.include("booths",booths)

def make_table(name,x,y,sx,sy):
    a=Asset(name)
    a.include("top",box((sx,sy,.075),center=(x,y,.77),color=C["table"]))
    a.include("edge",box((sx,sy,.025),center=(x,y,.72),color=(.25,.26,.25)))
    a.include("pedestal",rod(.055,start=(x,y,.09),end=(x,y,.72),color=C["metal"]))
    base=ball(.29,center=(x,y,.07),color=C["metal"])
    base.resize((1,1,.16))
    a.include("base",base)
    return a

tables=Asset("Dining_tables")
table_positions=[
    (-3.20,-6.55,3.45,1.50),(-3.55,-3.95,2.0,.92),
    (-3.55,-1.55,1.95,.92),(-3.55,.85,1.95,.92),
    (-.85,-1.25,1.55,1.12),(1.45,-.25,1.55,1.10),
    (-.75,1.65,1.48,1.02),(1.55,2.25,1.42,1.00),
    (-.80,4.12,1.35,.88),(1.50,4.65,1.35,.88)]
for i,(x,y,sx,sy) in enumerate(table_positions):
    tables.include("table_%02d"%i,make_table("Table_%02d"%i,x,y,sx,sy))
scene.include("tables",tables)

def make_chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("back",box((.83,.105,.89),center=(x,y,.94),color=C["chair"]))
    a.include("back_top_trim",box((.84,.12,.028),center=(x,y,1.39),color=(.40,.41,.40)))
    a.include("seat",box((.79,.68,.10),center=(x,y+.30,.49),color=C["chair"]))
    for j,dx in enumerate([-.34,.34]):
        a.include("back_support_%d"%j,rod(.025,start=(x+dx,y,.12),end=(x+dx,y,.92),color=C["metal"]))
        a.include("front_leg_%d"%j,rod(.023,start=(x+dx,y+.58,.06),end=(x+dx,y+.58,.50),color=C["metal"]))
    if angle:
        a.turn(axis="+z",degrees=angle,pivot=(x,y,0))
    return a

chairs=Asset("Dining_chairs")
chair_specs=[
    (-1.9,-2.55,-7),(-.45,-2.75,5),(.52,-1.55,-3),(2.35,-1.53,2),
    (-1.90,.35,0),(-.15,.20,4),(.45,.78,-4),(2.35,.85,3),
    (-1.75,2.95,0),(-.15,2.88,0),(.48,3.35,0),(2.42,3.35,0),
    (-1.65,5.10,0),(.05,5.0,0),(.65,5.45,0),(2.35,5.45,0),
    (3.0,-4.0,-8)]
for i,(x,y,ang) in enumerate(chair_specs):
    chairs.include("chair_%02d"%i,make_chair("Chair_%02d"%i,x,y,ang))
scene.include("chairs",chairs)

lamps=Asset("Pendant_lights")
lamp_specs=[
    (-2.70,-4.55,2.50,.72),(-3.50,-1.8,2.59,.52),
    (-3.30,2.20,2.65,.37),(-2.40,5.20,2.66,.25),
    (-.95,3.70,2.62,.31),(.90,2.40,2.61,.37),
    (2.65,1.10,2.60,.41),(4.05,2.85,2.67,.32),
    (4.50,-1.40,2.65,.37)]
for i,(x,y,z,r) in enumerate(lamp_specs):
    a=Asset("Pendant_%02d"%i)
    a.include("cord",rod(.012,start=(x,y,z+.23),end=(x,y,CEIL),color=C["dark"]))
    a.include("collar",rod(r*.25,start=(x,y,z+.02),end=(x,y,z+.30),color=C["dark"]))
    dome=ball(r,center=(x,y,z),color=C["dark"])
    dome.resize((1,1,.42))
    a.include("shade",dome)
    rim=ball(r*1.02,center=(x,y,z-.12),color=(.10,.11,.10))
    rim.resize((1,1,.055))
    a.include("rim",rim)
    lamps.include("pendant_%02d"%i,a)
scene.include("pendants",lamps)

def plant(name,x,y,height,spread,count):
    a=Asset(name)
    a.include("pot",box((.48,.48,.58),center=(x,y,.29),color=(.18,.19,.17)))
    for i in range(count):
        ang=2*math.pi*i/count+random.uniform(-.18,.18)
        length=random.uniform(.55,1.0)*spread
        topz=random.uniform(.62,1.0)*height
        ex=x+math.cos(ang)*length
        ey=y+math.sin(ang)*length
        a.include("stem_%02d"%i,rod(.016,start=(x,y,.42),end=(ex,ey,topz),color=C["leaf"]))
        for j in range(3):
            t=.40+j*.23
            lx=x+(ex-x)*t
            ly=y+(ey-y)*t
            lz=.42+(topz-.42)*t
            blade=ball(.22,center=(lx,ly,lz),color=C["leaf"])
            blade.resize((1.8,.32,.12))
            blade.turn(axis="+z",degrees=math.degrees(ang)+(-34 if j%2==0 else 34))
            a.include("leaf_%02d_%d"%(i,j),blade)
    return a

scene.include("large_right_plant",plant("Large_right_plant",4.05,-2.2,2.65,1.70,25))
scene.include("rear_planter",plant("Rear_planter",-2.00,4.35,1.42,.90,13))

realize(scene)
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.render.pixel_aspect_x=1
sc.render.pixel_aspect_y=1

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
background.inputs["Color"].default_value=(.83,.85,.83,1)
background.inputs["Strength"].default_value=.8

landmarks=[
    ("rear_left_window_top",(-3.45,BACK-.04,3.22),(.10,.31)),
    ("rear_center_window_top",(1.45,BACK-.04,3.22),(.47,.32)),
    ("right_rear_window_corner",(4.97,BACK,3.22),(.65,.29)),
    ("middle_table_corner",(-1.625,-1.81,.8075),(.38,.65)),
    ("foreground_table_corner",(-1.475,-7.30,.8075),(.45,.99)),
]
def projections():
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    result=[]
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1))
        result.append(None if clip.w<=1e-8 else
                      (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return result

# Compare the previous camera and a small trial target adjustment numerically.
set_view(CAM_POS,OLD_TARGET,lens=CAM_LENS,sensor=36)
before=projections()
set_view(CAM_POS,(.25,3.2,1.48),lens=CAM_LENS,sensor=36)
trial=projections()
print("LANDMARK                     reference      old camera     small trial")
for (name,p,ref),old,new in zip(landmarks,before,trial):
    print(name,ref,old,new)

# Restore the original aim if the trial does not move the rear corner left/up.
if before[2] is not None and trial[2] is not None and trial[2][0]<before[2][0] and trial[2][1]<before[2][1]:
    set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
else:
    set_view(CAM_POS,OLD_TARGET,lens=CAM_LENS,sensor=36)
final_uv=projections()
print("LANDMARK                     reference      final projected")
for (name,p,ref),uv in zip(landmarks,final_uv):
    print(name,ref,uv)

area_emitter((0,3,3.25),power=650,size=7,target=(0,0,0),color=(1,1,1))
area_emitter((-3,-5,3.1),power=400,size=5,target=(-1,1,0),color=(1,1,1))
area_emitter((4,3,2.6),power=500,size=5,target=(0,0,1),color=(1,1,1))
sc.view_settings.view_transform="AgX"
