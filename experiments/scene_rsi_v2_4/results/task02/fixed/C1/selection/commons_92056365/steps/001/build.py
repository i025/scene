from sceneact import *
import bpy, math, random

# Reference inventory (normalized image estimates):
# Ceiling .00-.99 x .00-.32: white narrow boards, hanging black pendants.
# Rear glazing .02-.73 x .31-.54; right glazing .72-1 x .25-.62.
# Tables and upholstered pedestal armchairs fill .00-.90 x .51-1.
# Large left pendant .02-.23 x .11-.40; large right pendant .72-.82 x .29-.40.
# Foreground chair back .00-.33 x .72-.91; tabletop cropped along bottom.
# Right palm .78-1 x .40-1, overlapping chairs, tables and windows.
# Observed anchors: rear window transom near y=.32; rear sill near y=.53;
# ceiling/right-wall junction rises toward upper right; chair feet grow strongly
# toward bottom; front tabletop and left chair are cropped. Exterior is uncertain.
# Asset map: room/{floor,ceiling,glazing}; pendant_*/{shade,neck,cable};
# dining_*/{table,chairs}; palms/{pot,trunk,fronds}; rear_planters.
# Geometry estimate: approximately 650 primitives, including 150 palm parts,
# 240 chair parts, 70 window/ceiling parts, and 50 lamp solids/cutters.
# Camera, furniture dimensions, component proportions and finishes are separate.

random.seed(13)
scene = Scene(name="Window cafe")
P = {
    "floor":(.24,.25,.23), "ceiling":(.87,.88,.84),
    "frame":(.27,.29,.27), "chair":(.32,.35,.31),
    "chair_edge":(.24,.27,.23), "table":(.46,.48,.43),
    "metal":(.58,.60,.56), "lamp":(.045,.065,.045),
    "leaf":(.055,.10,.055), "pot":(.20,.23,.19)
}
ROOM_W, ROOM_D, HEIGHT = 8.8, 12.6, 3.45
TABLE_W, TABLE_D, TABLE_H = 1.12, .83, .77
CHAIR_W, CHAIR_D = .72, .70

room=Asset(name="architecture")
scene.include("room",room)
room.include("floor",box((ROOM_W,ROOM_D,.12),(0,2.7,-.07),P["floor"]))
room.include("ceiling",box((ROOM_W,ROOM_D,.09),(0,2.7,HEIGHT+.045),P["ceiling"]))

# Narrow ceiling planks and faint longitudinal joints.
for i in range(49):
    y=-3.5+i*.26
    room.include("ceiling_joint_%02d"%i,
                 box((ROOM_W,.009,.006),(0,y,HEIGHT-.004),(.61,.63,.59)))
for x in [-3.5,-1.7,.1,1.9,3.7]:
    room.include("ceiling_seam_"+str(x),
                 box((.012,ROOM_D,.008),(x,2.7,HEIGHT-.006),(.72,.73,.69)))

# Flooring consists of dark rectangular tiles with pale narrow joints.
for i in range(25):
    x=-4.4+i*.37
    room.include("floor_long_%02d"%i,box((.009,12.6,.003),(x,2.7,.001),(.40,.42,.37)))
for i in range(35):
    y=-3.6+i*.37
    room.include("floor_cross_%02d"%i,box((8.8,.008,.003),(0,y,.002),(.36,.38,.33)))

# Bright exterior backing and low opaque window aprons.
room.include("rear_exterior",box((9.0,.08,3.6),(0,9.03,1.9),(.88,.91,.86)))
room.include("right_exterior",box((.08,13,3.6),(4.51,2.7,1.9),(.91,.93,.89)))
room.include("back_apron",box((8.8,.16,.72),(0,8.9,.36),(.69,.71,.66)))
room.include("right_apron",box((.16,12.6,.72),(4.4,2.7,.36),(.68,.70,.65)))
for z in [.76,3.12,3.40]:
    room.include("back_rail_"+str(z),box((8.8,.13,.065),(0,8.83,z),P["frame"]))
    room.include("side_rail_"+str(z),box((.13,12.6,.065),(4.32,2.7,z),P["frame"]))
for j,x in enumerate([-4.35,-2.65,-.95,.75,2.45,4.28]):
    room.include("back_mullion_"+str(j),box((.055,.13,2.65),(x,8.81,2.07),P["frame"]))
for j,y in enumerate([-3.5,-1.5,.5,2.5,4.5,6.5,8.85]):
    room.include("right_mullion_"+str(j),box((.13,.055,2.65),(4.29,y,2.07),P["frame"]))
room.include("left_window_post",box((.09,.16,2.7),(-4.34,8.8,2.05),P["frame"]))

# Soft, low contrast outside foliage and building bands.
outside=Asset(name="exterior_shapes")
scene.include("exterior",outside)
for i in range(22):
    x=random.uniform(-4.3,4.3)
    z=random.uniform(.9,1.8)
    shape=ball(random.uniform(.18,.39),(x,8.96,z),(.74,.79,.71))
    shape.resize((1,.22,1.1))
    outside.include("distant_foliage_"+str(i),shape)
outside.include("building_band",box((8.7,.03,.10),(0,8.95,1.03),(.78,.81,.76)))

def chair(name, px,py,angle=0):
    # Reusable local chair: front +Y, explicit floor pivot.
    a=Asset(name=name)
    a.include("foot",rod(.245,length=.045,center=(0,0,.035),color=P["metal"]))
    a.include("pedestal",rod(.075,length=.36,center=(0,0,.24),color=P["metal"]))
    a.include("seat_base",box((.73,.69,.12),(0,0,.46),P["chair_edge"]))
    a.include("seat_cushion",box((.65,.60,.085),(0,.015,.555),P["chair"]))
    a.include("back",box((.75,.115,.62),(0,-.31,.82),P["chair"]))
    a.include("back_top_edge",box((.76,.12,.025),(0,-.31,1.135),(.42,.44,.39)))
    for side in [-1,1]:
        a.include("arm_"+str(side),box((.085,.62,.32),(side*.36,.005,.73),P["chair"]))
        a.include("arm_cap_"+str(side),box((.09,.64,.025),(side*.36,.005,.90),(.41,.43,.38)))
    a.turn("z",angle,pivot=(0,0,0))
    a.move((px,py,0))
    return a

def table(name,x,y):
    a=Asset(name=name)
    a.include("top_edge",box((TABLE_W,TABLE_D,.045),(0,0,TABLE_H-.015),(.12,.15,.12)))
    a.include("top",box((TABLE_W-.018,TABLE_D-.018,.022),(0,0,TABLE_H+.015),P["table"]))
    a.include("column",rod(.065,length=.69,center=(0,0,.37),color=P["metal"]))
    a.include("base",rod(.265,length=.035,center=(0,0,.035),color=P["metal"]))
    # Small pale ashtray visible on several tables.
    a.include("ashtray",rod(.075,length=.018,center=(.18,.08,TABLE_H+.038),color=(.71,.73,.67)))
    a.move((x,y,0))
    return a

# Receding paired dining rows; modest irregularity reflects the photograph.
for row,y in enumerate([-.35,1.75,3.8,5.8,7.55]):
    for col,x in enumerate([-2.65,.25,2.85]):
        if row==0 and col==2:
            continue
        dining=Asset(name="dining_%d_%d"%(row,col))
        dining.include("table",table("table",x,y))
        dining.include("left_chair",chair("left_chair",x-.90,y, -90))
        dining.include("right_chair",chair("right_chair",x+.90,y,90))
        if row>=2:
            dining.include("far_chair",chair("far_chair",x,y+.77,180))
        scene.include(dining.name,dining)

# Foreground furniture creates the characteristic bottom and left cropping.
front=Asset(name="foreground_dining")
front.include("table",table("foreground_table",-2.45,-2.45))
front.include("rear_facing_chair",chair("large_cropped_back",-2.65,-1.65,180))
scene.include("foreground",front)
scene.include("right_foreground_chair",chair("right_foreground_chair",2.25,-.7,15))

def pendant(name,x,y,r=.30,bottom=2.40):
    a=Asset(name=name)
    # Hollow upper hemisphere gives a broad bell mouth and visible bright interior.
    dome=ball(r,(x,y,bottom),P["lamp"])
    dome.resize((1,1,.88),pivot=(x,y,bottom))
    inner=ball(r-.025,(x,y,bottom-.012),(.73,.75,.68))
    inner.resize((1,1,.88),pivot=(x,y,bottom-.012))
    lower=box((r*3,r*3,r*2),(x,y,bottom-r),P["lamp"])
    a.include("shade",subtract(dome,inner,lower))
    a.include("neck",rod(r*.35,length=r*.72,
                         center=(x,y,bottom+r*.91),color=P["lamp"]))
    a.include("neck_band",rod(r*.355,length=.032,
                              center=(x,y,bottom+r*1.08),color=(.40,.43,.36)))
    top=bottom+r*1.28
    a.include("cable",rod(.008,start=(x,y,top),end=(x,y,HEIGHT-.035),color=(.16,.18,.15)))
    a.include("ceiling_canopy",rod(.073,length=.02,center=(x,y,HEIGHT-.015),color=P["lamp"]))
    a.include("bulb",ball(.045,(x,y,bottom+.07),(.94,.94,.83)))
    scene.include(name,a)

pendant("large_left_pendant",-2.95,-1.6,.49,2.42)
pendant("large_right_pendant",2.35,2.10,.35,2.35)
pendant("middle_pendant",.15,3.10,.30,2.31)
pendant("rear_left_pendant",-2.55,4.55,.25,2.26)
pendant("rear_middle_pendant",-.55,6.3,.245,2.28)
pendant("rear_right_pendant",2.65,6.5,.23,2.3)
pendant("side_pendant",3.67,4.25,.23,2.30)
pendant("far_side_pendant",3.75,8.0,.22,2.30)
pendant("left_mid_pendant",-3.65,2.25,.27,2.26)

# A low row of planted dividers at the back.
planters=Asset(name="rear_planters")
scene.include("rear_planters",planters)
for i,x in enumerate([-1.8,-.7,.4,1.5]):
    planters.include("box_"+str(i),box((.90,.38,.40),(x,6.85,.75),(.35,.39,.32)))
    for j in range(7):
        xx=x+random.uniform(-.4,.4)
        yy=6.85+random.uniform(-.12,.12)
        h=random.uniform(.25,.55)
        planters.include("stem_%d_%d"%(i,j),
                         rod(.009,start=(xx,yy,.94),end=(xx+.09,yy, .94+h),color=P["leaf"]))
        leaf=ball(.105,(xx+.08,yy,.99+h),(.25,.31,.22))
        leaf.resize((1,.45,.5))
        planters.include("leaf_%d_%d"%(i,j),leaf)

# Right foreground palm, composed of individually editable stems and leaflets.
palm=Asset(name="right_palm")
scene.include("right_palm",palm)
px,py=3.43,-.20
palm.include("pot",rod(.31,length=.46,center=(px,py,.24),color=P["pot"]))
palm.include("pot_rim",rod(.335,length=.065,center=(px,py,.48),color=(.29,.32,.26)))
for k in range(10):
    angle=math.radians(-160+k*34)
    base=(px+random.uniform(-.13,.13),py+random.uniform(-.1,.1),.44)
    height=random.uniform(1.15,1.95)
    reach=random.uniform(.65,1.13)
    mid=(px+math.cos(angle)*reach*.40,py+math.sin(angle)*reach*.40,height+.10)
    end=(px+math.cos(angle)*reach,py+math.sin(angle)*reach,height-.08)
    palm.include("frond_stem_"+str(k),sweep_tube([base,mid,end],.014,P["leaf"]))
    for j in range(1,7):
        t=j/7
        cx=mid[0]+(end[0]-mid[0])*t
        cy=mid[1]+(end[1]-mid[1])*t
        cz=mid[2]+(end[2]-mid[2])*t
        length=.30*(1-t*.60)
        for side in [-1,1]:
            ex=cx+math.cos(angle+side*1.03)*length
            ey=cy+math.sin(angle+side*1.03)*length
            ez=cz+.13*(1-t)
            palm.include("leaflet_%d_%d_%d"%(k,j,side),
                         rod(.012,start=(cx,cy,cz),end=(ex,ey,ez),color=P["leaf"]))

realize(scene)

# Bright overcast windows with restrained interior contrast.
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:
    background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:
    output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.82,.85,.79,1)
background.inputs["Strength"].default_value=.65

area_emitter((0,8.3,2.6),power=1500,size=7,target=(0,1,.4),color=(1,1,.96))
area_emitter((4.0,2.8,2.7),power=1250,size=6,target=(-1,2,.8),color=(1,1,.96))
area_emitter((-2,-3,3.1),power=220,size=5,target=(0,3,1),color=(1,1,1))

# Joint framing estimate: wide view with substantial ceiling, rear sill at mid-height,
# foreground furniture cropped, and right window wall receding toward rear center.
set_view(position=(-.95,-5.0,1.74),target=(.25,5.0,1.67),
         lens=25.5,sensor=36)
sc.camera.data.clip_start=.08
sc.camera.data.clip_end=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.45
sc.view_settings.gamma=1.0
# No rendering or saving: the external runner handles both.
