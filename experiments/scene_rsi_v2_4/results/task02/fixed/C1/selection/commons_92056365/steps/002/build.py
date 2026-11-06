from sceneact import *
import bpy, math, random

# REFERENCE INVENTORY:
# White boarded ceiling: image x=0..1, y=0..~.31.
# Rear windows: x=0..~.66, y=~.31..~.54; right windows continue to right edge.
# Dark bell pendants with cylindrical necks, cables and pale open undersides.
# Largest pendant: x~.02..~.23, y~.12..~.36.
# Upholstered pedestal chairs and square tables overlap throughout lower half.
# Foreground broad chair back: x=0..~.33, y~.72..~.90.
# Foreground table crosses the bottom edge; right chair occupies ~.72..~.88.
# Palm: x~.78..1, y~.41..1; rear planted divider around y=.51.. .59.
# Exterior foliage/buildings are faint; obscured furniture geometry is uncertain.
# Shared observed anchors: rear window head y~.31, sill y~.53;
# rear/right corner x~.65; ceiling side edge rises toward upper right;
# large left lamp is fully inside frame, foreground furniture is heavily cropped.
# Inferred: room depth, chair spacing, exterior distances and hidden supports.
#
# REVIEW:
# Previous execution succeeded and produced the supplied image. Named emitted
# parts remained present; this does not verify photographic completeness.
# Visual agreement was limited: rear glazing was too small and low, the left
# lamp was cropped, foreground furniture lacked the broad reference coverage,
# and chairs/exterior had insufficient tonal separation.
# Camera focal length, pitch and room proportions are competing explanations
# for the shared anchor errors; attribution is unresolved. Selected correction:
# modestly narrower field of view and lower aim, retaining camera position.
# Local lamp and foreground placement are then adjusted to observed cropping.
# Finish corrections darken upholstery/floor and brighten exterior backings.
# These are unverified revisions, not measured improvements.
#
# Editable parameter families: CAMERA, ROOM, furniture dimensions, palette.
# Expanded estimate: about 950 primitive meshes including Boolean operands:
# architecture/lines ~145, exterior ~23, chairs ~370, tables ~75,
# lamps ~80, divider plants ~60, palm ~200. No fillet expansion.

random.seed(13)
scene = Scene(name="Window cafe")

CAMERA = {
    "position": (-.95, -5.0, 1.74),
    "target": (.90, 5.0, 1.30),
    "lens": 32.0
}
ROOM = {"width": 8.8, "depth": 12.6, "height": 3.45}
TABLE_W, TABLE_D, TABLE_H = 1.12, .83, .77
P = {
    "floor": (.115, .12, .11),
    "ceiling": (.88, .89, .86),
    "frame": (.23, .25, .23),
    "chair": (.17, .19, .17),
    "chair_edge": (.13, .15, .13),
    "table": (.48, .50, .46),
    "metal": (.58, .60, .56),
    "lamp": (.025, .035, .025),
    "leaf": (.035, .065, .035),
    "pot": (.12, .15, .12)
}
W, D, H = ROOM["width"], ROOM["depth"], ROOM["height"]

room = Asset(name="architecture")
scene.include("room", room)
room.include("floor", box((W,D,.12),(0,2.7,-.07),P["floor"]))
room.include("ceiling", box((W,D,.09),(0,2.7,H+.045),P["ceiling"]))

for i in range(49):
    y = -3.5+i*.26
    room.include("ceiling_joint_%02d"%i,
                 box((W,.008,.005),(0,y,H-.004),(.64,.66,.62)))
for i,x in enumerate([-3.5,-1.7,.1,1.9,3.7]):
    room.include("ceiling_seam_%d"%i,
                 box((.008,D,.005),(x,2.7,H-.005),(.75,.76,.72)))
for i in range(25):
    room.include("floor_long_%d"%i,
                 box((.006,D,.003),(-4.4+i*.37,2.7,.001),(.30,.32,.28)))
for i in range(35):
    room.include("floor_cross_%d"%i,
                 box((W,.006,.003),(0,-3.6+i*.37,.002),(.27,.29,.25)))

room.include("rear_exterior",
             box((9,.08,3.6),(0,9.03,1.9),(.88,.91,.86)))
room.include("right_exterior",
             box((.08,13,3.6),(4.51,2.7,1.9),(.91,.93,.89)))
# Continuing left glazing avoids an unsupported blank opaque region.
room.include("left_exterior",
             box((.08,13,3.6),(-4.51,2.7,1.9),(.90,.92,.87)))
room.include("back_apron",
             box((W,.16,.72),(0,8.9,.36),(.65,.67,.62)))
room.include("right_apron",
             box((.16,D,.72),(4.4,2.7,.36),(.65,.67,.62)))
room.include("left_apron",
             box((.16,D,.72),(-4.4,2.7,.36),(.65,.67,.62)))

for z in [.76,3.12,3.40]:
    room.include("back_rail_"+str(z),
                 box((W,.13,.065),(0,8.83,z),P["frame"]))
    for side in [-1,1]:
        room.include("side_rail_%s_%s"%(side,z),
                     box((.13,D,.065),(side*4.32,2.7,z),P["frame"]))
for j,x in enumerate([-4.35,-2.65,-.95,.75,2.45,4.28]):
    room.include("back_mullion_%d"%j,
                 box((.055,.13,2.65),(x,8.81,2.07),P["frame"]))
for side in [-1,1]:
    for j,y in enumerate([-3.5,-1.5,.5,2.5,4.5,6.5,8.85]):
        room.include("side_mullion_%d_%d"%(side,j),
                     box((.13,.055,2.65),(side*4.29,y,2.07),P["frame"]))

outside = Asset(name="exterior_shapes")
scene.include("exterior", outside)
for i in range(22):
    x = random.uniform(-4.3,4.3)
    z = random.uniform(.9,1.8)
    shape = ball(random.uniform(.18,.39),(x,8.96,z),(.64,.69,.61))
    shape.resize((1,.22,1.1))
    outside.include("distant_foliage_%d"%i,shape)
outside.include("building_band",
                box((8.7,.03,.10),(0,8.95,1.03),(.70,.73,.67)))

def chair(name, px, py, angle=0, width_scale=1):
    a = Asset(name=name)
    a.include("foot",rod(.245,length=.045,center=(0,0,.035),color=P["metal"]))
    a.include("pedestal",rod(.075,length=.36,center=(0,0,.24),color=P["metal"]))
    a.include("seat_base",box((.73,.69,.12),(0,0,.46),P["chair_edge"]))
    a.include("seat_cushion",box((.65,.60,.085),(0,.015,.555),P["chair"]))
    a.include("back",box((.75,.115,.62),(0,-.31,.82),P["chair"]))
    a.include("back_top_edge",
              box((.76,.12,.018),(0,-.31,1.135),(.30,.32,.28)))
    for side in [-1,1]:
        a.include("arm_"+str(side),
                  box((.065,.62,.32),(side*.36,.005,.73),P["chair"]))
        a.include("arm_cap_"+str(side),
                  box((.075,.64,.018),(side*.36,.005,.90),(.29,.31,.27)))
    a.resize((width_scale,1,1),pivot=(0,0,0))
    a.turn("z",angle,pivot=(0,0,0))
    a.move((px,py,0))
    return a

def table(name, x, y, width=TABLE_W, depth=TABLE_D):
    a = Asset(name=name)
    a.include("top_edge",
              box((width,depth,.045),(0,0,TABLE_H-.015),(.10,.12,.10)))
    a.include("top",
              box((width-.018,depth-.018,.022),(0,0,TABLE_H+.015),P["table"]))
    a.include("column",
              rod(.065,length=.69,center=(0,0,.37),color=P["metal"]))
    a.include("base",
              rod(.265,length=.035,center=(0,0,.035),color=P["metal"]))
    a.include("ashtray",
              rod(.075,length=.018,center=(.18,.08,TABLE_H+.038),
                  color=(.73,.75,.69)))
    a.move((x,y,0))
    return a

for row,y in enumerate([-.35,1.75,3.8,5.8,7.55]):
    for col,x in enumerate([-2.65,.25,2.85]):
        if row==0 and col==2:
            continue
        name = "dining_%d_%d"%(row,col)
        dining = Asset(name=name)
        dining.include("table",table("table",x,y))
        dining.include("left_chair",chair("left_chair",x-.90,y,-90))
        dining.include("right_chair",chair("right_chair",x+.90,y,90))
        if row>=2:
            dining.include("far_chair",chair("far_chair",x,y+.77,180))
        scene.include(name,dining)

front = Asset(name="foreground_dining")
front.include("table",table("foreground_table",-1.35,-2.85,1.65,1.1))
front.include("rear_facing_chair",
              chair("large_cropped_back",-1.80,-1.95,0,1.4))
scene.include("foreground",front)
scene.include("right_foreground_chair",
              chair("right_foreground_chair",1.20,-1.0,8,1.1))

def pendant(name,x,y,r=.30,bottom=2.40,long_neck=False):
    a = Asset(name=name)
    dome = ball(r,(x,y,bottom),P["lamp"])
    dome.resize((1,1,.88),pivot=(x,y,bottom))
    inner = ball(r-.025,(x,y,bottom-.012),(.77,.79,.72))
    inner.resize((1,1,.88),pivot=(x,y,bottom-.012))
    cutter = box((r*3,r*3,r*2),(x,y,bottom-r),P["lamp"])
    a.include("shade",subtract(dome,inner,cutter))
    if long_neck:
        neck_height = .40
        neck_center = bottom+.61
    else:
        neck_height = r*.72
        neck_center = bottom+r*.91
    a.include("neck",
              rod(r*.35,length=neck_height,center=(x,y,neck_center),color=P["lamp"]))
    a.include("neck_band",
              rod(r*.355,length=.027,
                  center=(x,y,neck_center+.055),color=(.36,.39,.33)))
    top = neck_center+neck_height*.5
    a.include("cable",
              rod(.006,start=(x,y,top),end=(x,y,H-.035),color=(.12,.14,.12)))
    a.include("ceiling_canopy",
              rod(.065,length=.018,center=(x,y,H-.015),color=P["lamp"]))
    a.include("bulb",ball(.045,(x,y,bottom+.07),(.95,.95,.87)))
    scene.include(name,a)

pendant("large_left_pendant",-1.80,-.75,.49,2.10,True)
pendant("large_right_pendant",2.55,2.10,.39,2.23)
pendant("middle_pendant",.15,3.10,.30,2.31)
pendant("rear_left_pendant",-2.55,4.55,.25,2.26)
pendant("rear_middle_pendant",-.55,6.3,.245,2.28)
pendant("rear_right_pendant",2.65,6.5,.23,2.3)
pendant("side_pendant",3.67,4.25,.23,2.30)
pendant("far_side_pendant",3.75,8.0,.22,2.30)
pendant("left_mid_pendant",-3.65,2.25,.27,2.26)

planters = Asset(name="rear_planters")
scene.include("rear_planters",planters)
for i,x in enumerate([-1.8,-.7,.4,1.5]):
    planters.include("box_%d"%i,
                     box((.90,.38,.40),(x,6.85,.75),(.27,.31,.24)))
    for j in range(7):
        xx=x+random.uniform(-.4,.4)
        yy=6.85+random.uniform(-.12,.12)
        h=random.uniform(.25,.55)
        planters.include("stem_%d_%d"%(i,j),
                         rod(.009,start=(xx,yy,.94),
                             end=(xx+.09,yy,.94+h),color=P["leaf"]))
        leaf=ball(.105,(xx+.08,yy,.99+h),(.16,.22,.13))
        leaf.resize((1,.45,.5))
        planters.include("leaf_%d_%d"%(i,j),leaf)

palm = Asset(name="right_palm")
scene.include("right_palm",palm)
px,py=2.15,.30
palm.include("pot",rod(.31,length=.46,center=(px,py,.24),color=P["pot"]))
palm.include("pot_rim",
             rod(.335,length=.065,center=(px,py,.48),color=(.20,.23,.17)))

for k in range(13):
    angle=math.radians(-160+k*29)
    base=(px+random.uniform(-.13,.13),
          py+random.uniform(-.1,.1),.44)
    height=random.uniform(1.18,1.98)
    reach=random.uniform(.65,1.13)
    mid=(px+math.cos(angle)*reach*.40,
         py+math.sin(angle)*reach*.40,height+.10)
    end=(px+math.cos(angle)*reach,
         py+math.sin(angle)*reach,height-.08)
    palm.include("frond_stem_%d"%k,
                 sweep_tube([base,mid,end],.012,P["leaf"]))
    for j in range(1,6):
        t=j/6
        cx=mid[0]+(end[0]-mid[0])*t
        cy=mid[1]+(end[1]-mid[1])*t
        cz=mid[2]+(end[2]-mid[2])*t
        length=.38*(1-t*.60)
        for side in [-1,1]:
            direction=angle+side*1.03
            ex=cx+math.cos(direction)*length
            ey=cy+math.sin(direction)*length
            ez=cz+.14*(1-t)
            palm.include("leaflet_stem_%d_%d_%d"%(k,j,side),
                         rod(.008,start=(cx,cy,cz),end=(ex,ey,ez),color=P["leaf"]))
            blade=ball(1,((cx+ex)*.5,(cy+ey)*.5,(cz+ez)*.5),P["leaf"])
            blade.resize((length*.51,.024,.009),pivot=blade.centroid)
            blade.turn("y",-15,pivot=blade.centroid)
            blade.turn("z",math.degrees(direction),pivot=blade.centroid)
            palm.include("leaflet_blade_%d_%d_%d"%(k,j,side),blade)

realize(scene)

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
background.inputs["Color"].default_value=(.86,.88,.84,1)
background.inputs["Strength"].default_value=.55

# Exterior backing is a bright overcast surface, preserving darker outside foliage.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c=bsdf.inputs["Base Color"].default_value
    if c[0]>.85 and c[1]>.90 and c[2]>.85:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value=(.93,.95,.91,1)
            bsdf.inputs["Emission Strength"].default_value=.65

area_emitter((0,8.3,2.6),power=1500,size=7,target=(0,1,.4),color=(1,1,.97))
area_emitter((4.0,2.8,2.7),power=1250,size=6,target=(-1,2,.8),color=(1,1,.97))
area_emitter((-2,-3,3.1),power=260,size=5,target=(0,3,1),color=(1,1,1))
area_emitter((0,2,2.5),power=180,size=6,target=(0,3,3.45),color=(1,1,1))

set_view(position=CAMERA["position"],target=CAMERA["target"],
         lens=CAMERA["lens"],sensor=36)
sc.camera.data.clip_start=.08
sc.camera.data.clip_end=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.45
sc.view_settings.gamma=1.0

# All dimensions are positive; cables terminate below ceiling, with explicit
# assembly pivots. Active camera and world are initialized after realization.
# The external runner performs the sole render and save.
