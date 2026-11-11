from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory, normalized image coordinates, and observed render comparison:
# 1. Rear glazing and ceiling: reference window top near y=.31, right corner
#    near (.65,.29); render top near y=.33 and corner near (.67,.33). The
#    reference panes are nearly white, while the rendered panes are medium gray.
#    The ceiling's horizontal lines and the right edge rising to the right are
#    present in both. Bright emissive glazing should restore the large light area.
# 2. Foreground left pendant: reference dome occupies approximately
#    (.02,.23)-(.22,.35), with a tall collar above; rendered shade occupies
#    (0,.35)-(.22,.47), is cropped, and has a flat oval profile. Move its center
#    right and upward and make a deeper, flat-bottomed dome. This is a local
#    adjustment and does not move the other pendant or window contours.
# 3. Foreground left booth and table: reference booth back occupies approximately
#    (0,.72)-(.32,.86), and the table reaches x=.46 at the bottom. Rendered
#    backs appear pale and the foreground table reaches only about x=.27.
#    Darken the booth and widen/advance its foreground table locally.
# 4. Reference chair backs form dark blocks from approximately (.43,.57) through
#    (.88,.96); render has much paler backs mostly in (.25,.52)-(.93,.74).
#    Move selected near chairs toward the camera, preserve gaps between backs,
#    and use darker upholstery. Illumination also affects observed brightness.
# 5. Reference right foliage forms a dark, leafy mass at (.78,.40)-(1,1);
#    rendered foliage is sparse, thin, and mostly around (.72,.38)-(1,.65).
#    Longer, wider leaf blades and a nearer plant extend its silhouette down
#    and right, with gaps between fronds. Rear planter remains partly occluded.
# The floor boards converge into the room in both views. The reference foreground
# has less empty floor and more overlapping furniture. Distant exterior detail,
# hidden chair backs and plant pots are uncertain.
# Camera remains as in the last successful render: the background framing is
# substantially closer than the local foreground silhouettes. Reference positions
# below are visual estimates, while computed projections are geometry points.
# Approximate expanded primitives: architecture 72, booths 20, tables 40,
# chairs 119, pendants 36, plants 180, exterior 9: about 476 meshes.
# No booleans, fillets, file access, rendering, or saving.

random.seed(9)
scene = Scene("Restaurant")
C = {
    "white": (.78,.79,.77), "ceiling": (.82,.83,.81),
    "frame": (.10,.11,.10), "glass": (.96,.97,.95),
    "floor": (.10,.105,.10), "seam": (.23,.24,.22),
    "table": (.61,.62,.60), "chair": (.085,.09,.085),
    "booth": (.07,.075,.07), "metal": (.43,.45,.43),
    "dark": (.025,.03,.027), "leaf": (.025,.045,.025)
}
W, BACK, CEIL = 10.0, 7.0, 3.55
CAM_POS = (-.55,-9.8,2.75)
CAM_TARGET = (.65,3.2,.92)
CAM_LENS = 27

room = Asset("Architecture")
room.include("floor", box((W,19,.12), center=(0,0,-.07), color=C["floor"]))
room.include("ceiling", box((W,19,.12), center=(0,0,CEIL+.06), color=C["ceiling"]))
room.include("rear_sill", box((W,.13,.44), center=(0,BACK,.22), color=C["white"]))
room.include("rear_header", box((W,.14,.25), center=(0,BACK,3.43), color=C["white"]))
room.include("rear_glazing", box((W,.035,2.73), center=(0,BACK+.04,1.84), color=C["glass"]))
for i,x in enumerate([-5,-3.45,-1.85,-.20,1.45,3.10,5]):
    room.include("rear_mullion_%d"%i, box((.065,.12,2.8),
                 center=(x,BACK-.04,1.86), color=C["frame"]))
room.include("rear_sill_rail", box((W,.13,.09), center=(0,BACK-.05,.60), color=C["frame"]))
room.include("rear_top_rail", box((W,.13,.08), center=(0,BACK-.05,3.22), color=C["frame"]))
room.include("right_sill", box((.14,18,.60), center=(5,0,.30), color=C["white"]))
room.include("right_glazing", box((.035,18,2.55), center=(5.04,0,1.91), color=C["glass"]))
room.include("right_header", box((.14,18,.32), center=(5,0,3.39), color=C["white"]))
for i,y in enumerate([-7,-4.2,-1.4,1.4,4.2,7]):
    room.include("right_mullion_%d"%i, box((.13,.065,2.65),
                 center=(4.97,y,1.93), color=C["frame"]))
room.include("right_sill_rail", box((.14,18,.085), center=(4.96,0,.65), color=C["frame"]))
room.include("left_low_wall", box((.12,18,.63), center=(-5,0,.315), color=C["white"]))
for i in range(28):
    room.include("ceiling_joint_%02d"%i, box((W,.014,.008),
                 center=(0,-9+i*.6,CEIL-.008), color=(.55,.56,.54)))
for i in range(20):
    room.include("floor_joint_%02d"%i, box((.012,18,.005),
                 center=(-4.85+i*.51,0,.002), color=C["seam"]))
scene.include("architecture",room)

booths = Asset("Left_booths")
for i,y in enumerate([-5.2,-2.9,-.6,1.7,4.0]):
    b = Asset("Booth_%d"%i)
    b.include("back",box((2.45,.15,1.03),center=(-3.65,y,.67),color=C["booth"]))
    b.include("top_edge",box((2.46,.17,.035),center=(-3.65,y,1.19),color=(.24,.25,.24)))
    b.include("seat",box((2.4,.82,.16),center=(-3.65,y+.43,.43),color=C["booth"]))
    b.include("base",box((2.25,.68,.35),center=(-3.65,y+.43,.20),color=(.07,.075,.07)))
    booths.include("booth_%d"%i,b)
scene.include("booths",booths)

def make_table(name,x,y,sx,sy):
    a=Asset(name)
    a.include("top",box((sx,sy,.075),center=(x,y,.77),color=C["table"]))
    a.include("edge",box((sx,sy,.025),center=(x,y,.72),color=(.18,.19,.18)))
    a.include("pedestal",rod(.055,start=(x,y,.09),end=(x,y,.72),color=C["metal"]))
    base=ball(.29,center=(x,y,.07),color=C["metal"])
    base.resize((1,1,.16))
    a.include("base",base)
    return a

tables=Asset("Dining_tables")
table_positions=[
    (-2.75,-7.15,4.5,1.65),(-3.55,-3.95,2.0,.92),
    (-3.55,-1.55,1.95,.92),(-3.55,.85,1.95,.92),
    (-.85,-1.25,1.55,1.12),(1.45,-.25,1.55,1.10),
    (-.75,1.65,1.48,1.02),(1.55,2.25,1.42,1.00),
    (-.80,4.12,1.35,.88),(1.50,4.65,1.35,.88)]
for i,(x,y,sx,sy) in enumerate(table_positions):
    tables.include("table_%02d"%i,make_table("Table_%02d"%i,x,y,sx,sy))
scene.include("tables",tables)

def make_chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("back",box((.86,.105,.89),center=(x,y,.94),color=C["chair"]))
    a.include("back_top_trim",box((.87,.12,.028),center=(x,y,1.39),color=(.32,.33,.32)))
    a.include("seat",box((.79,.68,.10),center=(x,y+.30,.49),color=C["chair"]))
    for j,dx in enumerate([-.34,.34]):
        a.include("back_support_%d"%j,rod(.025,start=(x+dx,y,.12),
                  end=(x+dx,y,.92),color=C["metal"]))
        a.include("front_leg_%d"%j,rod(.023,start=(x+dx,y+.58,.06),
                  end=(x+dx,y+.58,.50),color=C["metal"]))
    if angle:
        a.turn(axis="+z",degrees=angle,pivot=(x,y,0))
    return a

chairs=Asset("Dining_chairs")
chair_specs=[
    (-1.25,-4.0,-7),(.35,-4.3,5),(1.45,-3.35,-3),(2.65,-3.8,2),
    (-1.90,.35,0),(-.15,.20,4),(.45,.78,-4),(2.35,.85,3),
    (-1.75,2.95,0),(-.15,2.88,0),(.48,3.35,0),(2.42,3.35,0),
    (-1.65,5.10,0),(.05,5.0,0),(.65,5.45,0),(2.35,5.45,0),
    (3.0,-5.3,-8)]
for i,(x,y,ang) in enumerate(chair_specs):
    chairs.include("chair_%02d"%i,make_chair("Chair_%02d"%i,x,y,ang))
scene.include("chairs",chairs)

# A dome consists of upper and lower ellipsoid portions. A dark rim hides the
# lower portion's curved edge and gives the visible nearly flat shade opening.
lamps=Asset("Pendant_lights")
lamp_specs=[
    (-2.10,-4.10,2.88,.69),(-3.50,-1.8,2.59,.52),
    (-3.30,2.20,2.65,.37),(-2.40,5.20,2.66,.25),
    (-.95,3.70,2.62,.31),(.90,2.40,2.61,.37),
    (2.65,1.10,2.60,.41),(4.05,2.85,2.67,.32),
    (4.50,-1.40,2.65,.37)]
for i,(x,y,z,r) in enumerate(lamp_specs):
    a=Asset("Pendant_%02d"%i)
    a.include("cord",rod(.012,start=(x,y,z+.25),end=(x,y,CEIL),color=C["dark"]))
    a.include("collar",rod(r*.25,start=(x,y,z+.06),
              end=(x,y,z+.40),color=C["dark"]))
    dome=ball(r,center=(x,y,z),color=C["dark"])
    dome.resize((1,1,.58))
    a.include("shade",dome)
    rim=ball(r*.97,center=(x,y,z-.17),color=(.035,.04,.035))
    rim.resize((1,1,.06))
    a.include("rim",rim)
    lamps.include("pendant_%02d"%i,a)
scene.include("pendants",lamps)

def plant(name,x,y,height,spread,count):
    a=Asset(name)
    a.include("pot",box((.48,.48,.58),center=(x,y,.29),color=(.10,.11,.10)))
    for i in range(count):
        ang=2*math.pi*i/count+random.uniform(-.15,.15)
        length=random.uniform(.55,1.0)*spread
        topz=random.uniform(.60,1.0)*height
        ex=x+math.cos(ang)*length
        ey=y+math.sin(ang)*length
        a.include("stem_%02d"%i,rod(.015,start=(x,y,.42),
                  end=(ex,ey,topz),color=C["leaf"]))
        for j in range(4):
            t=.32+j*.18
            lx=x+(ex-x)*t
            ly=y+(ey-y)*t
            lz=.42+(topz-.42)*t
            blade=ball(.24,center=(lx,ly,lz),color=C["leaf"])
            blade.resize((2.0,.34,.10))
            blade.turn(axis="+z",degrees=math.degrees(ang)+(-35 if j%2==0 else 35))
            a.include("leaf_%02d_%d"%(i,j),blade)
    return a

scene.include("large_right_plant",plant("Large_right_plant",4.0,-4.0,2.75,1.8,26))
scene.include("rear_planter",plant("Rear_planter",-2.00,4.35,1.42,.90,10))

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
background.inputs["Strength"].default_value=.55

# Give only the glazing a bright surface. It remains real geometry behind the
# window frames; the washed-out exterior is uncertain in the source photograph.
window_mat=bpy.data.materials.new("Bright_window_glazing")
window_mat.use_nodes=True
nodes=window_mat.node_tree.nodes
nodes.clear()
em=nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value=(.91,.93,.90,1)
em.inputs["Strength"].default_value=1.25
out=nodes.new("ShaderNodeOutputMaterial")
window_mat.node_tree.links.new(em.outputs["Emission"],out.inputs["Surface"])
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        mat=slot.material
        if mat and all(abs(mat.diffuse_color[i]-C["glass"][i])<.015 for i in range(3)):
            slot.material=window_mat

set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
bpy.context.view_layer.update()
cam=sc.camera
dg=bpy.context.evaluated_depsgraph_get()
projection=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
                                 scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
landmarks=[
    ("rear_window_top",(-3.45,BACK-.04,3.22),(.10,.31)),
    ("right_rear_corner",(4.97,BACK,3.22),(.65,.29)),
    ("middle_table_corner",(-1.625,-1.81,.8075),(.38,.65)),
    ("foreground_table_corner",(-.50,-7.975,.8075),(.46,.99)),
    ("large_pendant_center",(-2.10,-4.10,2.88),(.12,.28))
]
print("LANDMARK reference estimated; projected geometry point")
for name,p,ref in landmarks:
    clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1))
    uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
    print(name,ref,uv)

area_emitter((0,3,3.25),power=650,size=7,target=(0,0,0),color=(1,1,1))
area_emitter((-3,-5,3.1),power=400,size=5,target=(-1,1,0),color=(1,1,1))
area_emitter((4,3,2.6),power=500,size=5,target=(0,0,1),color=(1,1,1))
sc.view_settings.view_transform="AgX"
