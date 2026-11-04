from sceneact import *
import bpy
import math
import random

# Reference comparison:
# 1. Upper-left: head and pillow are too tall and angular. Lower the head
#    crest by .09 and replace the rigid pillow with a softly bulging mesh.
# 2. Center/lower-right: the mattress floats above a thin tubular frame.
#    Raise and deepen the apron, extend the cushion downward, and shorten
#    the visible feet slightly while keeping the camera and seat footprint.
# 3. Broad upholstery region: fabric is too white and its pattern too faint.
#    Use warmer cream, stronger faded rose bands, and visible floral stitches.
#
# Estimated reference bounds: chaise (.035,.24)-(.83,.93), pillow
# (.075,.26)-(.32,.54), cropped cane chair (0,.80)-(.20,1).
# Wall/floor junction lies near y=.50; the near arm occludes the pillow
# and mattress. Camera framing and the improved wall orientation are retained.

CHAISE_LENGTH = 3.05
CHAISE_WIDTH = 1.10
SEAT_HEIGHT = .77
CAMERA_POSITION = (2.05, -6.0, 4.10)
CAMERA_TARGET = (.17, .12, 1.10)
CAMERA_LENS = 60
WALL_DISTANCE = 2.55
WALL_ANGLE = 23

random.seed(8)
scene = Scene("French chaise longue")
wall = (.63, .60, .52)
trim = (.73, .69, .59)
green = (.19, .235, .18)
gold = (.47, .39, .25)
pale_gold = (.67, .58, .40)
fabric = (.61, .535, .425)

room = Asset("Paneled room")
room.include("floor", box((12,12,.12), center=(0,0,-.08),
                          color=(.105,.051,.030)))
architecture = Asset("Wall and moldings")
architecture.include("wall", box((10,.16,4.8),
    center=(0,WALL_DISTANCE+.08,2.36), color=wall))
for i,(z,t,d) in enumerate([
    (.10,.14,.13),(.21,.042,.075),(.31,.035,.065),
    (1.64,.070,.08),(1.74,.032,.06),
    (2.11,.050,.06),(2.43,.045,.065),(2.56,.03,.05)
]):
    architecture.include(f"rail_{i}", box((9.7,d,t),
        center=(0,WALL_DISTANCE-.045,z),color=trim))
for p,(left,right) in enumerate([
    (-3.4,-1.75),(-1.69,2.10),(2.17,3.8)
]):
    for layer in range(3):
        inset=layer*.024
        lo,hi=.38+inset,1.53-inset
        a,b=left+inset,right-inset
        color=trim if layer!=1 else (.51,.48,.40)
        for j,x in enumerate((a,b)):
            architecture.include(f"panel_{p}_{layer}_v_{j}",
                box((.018,.032,hi-lo),
                    center=(x,WALL_DISTANCE-.022-layer*.009,(hi+lo)/2),
                    color=color))
        for j,z in enumerate((lo,hi)):
            architecture.include(f"panel_{p}_{layer}_h_{j}",
                box((b-a,.032,.018),
                    center=((a+b)/2,WALL_DISTANCE-.022-layer*.009,z),
                    color=color))
for j,x in enumerate((-1.72,.64)):
    architecture.include(f"joint_{j}",box((.007,.006,4.2),
        center=(x,WALL_DISTANCE-.005,2.12),color=(.33,.31,.25)))
architecture.include("pilaster",box((.30,.34,3.5),
    center=(2.30,WALL_DISTANCE-.12,1.73),color=trim))
architecture.include("return",box((.9,.7,3.6),
    center=(2.90,WALL_DISTANCE+.22,1.78),color=wall))
for j,x in enumerate((2.22,2.38)):
    architecture.include(f"pilaster_bead_{j}",box((.018,.025,3.2),
        center=(x,WALL_DISTANCE-.30,1.75),color=trim))
architecture.turn("z",WALL_ANGLE,pivot=(0,WALL_DISTANCE,0))
room.include("architecture",architecture)
scene.include("room",room)

floor=Asset("Dark parquet")
wood_colors=[
    (.135,.065,.040),(.165,.080,.047),(.115,.052,.032),
    (.185,.095,.056),(.145,.070,.042),(.155,.076,.047)
]
tile=.64
for row in range(-9,10):
    for col in range(-9,10):
        for k in range(5):
            if (row+col)%2==0:
                u=col*tile+tile/2
                v=row*tile+(k+.5)*tile/5
                angle=45
            else:
                u=col*tile+(k+.5)*tile/5
                v=row*tile+tile/2
                angle=135
            x=(u-v)/math.sqrt(2)
            y=(u+v)/math.sqrt(2)
            if abs(x)>5.4 or abs(y)>5.4:
                continue
            plank=box((tile-.002,tile/5-.002,.018),
                center=(x,y,-.008),color=random.choice(wood_colors))
            plank.turn("z",angle)
            floor.include(f"board_{row}_{col}_{k}",plank)
scene.include("parquet",floor)

chaise=Asset("Chaise longue")
front_rail=[
    (-1.30,-.565,.70),(-1.03,-.57,.69),(-.70,-.575,.68),
    (-.25,-.578,.675),(.22,-.575,.67),(.69,-.57,.66),
    (1.15,-.55,.66),(1.43,-.43,.67)
]
apron=sweep_tube(points=front_rail,radius=.087,color=green)
apron.resize((1,.48,1),pivot=(0,-.575,.67))
chaise.include("front_apron",apron)
for j,dz in enumerate((-.068,.063)):
    chaise.include(f"apron_bead_{j}",sweep_tube(
        points=[(x,y-.038,z+dz) for x,y,z in front_rail],
        radius=.010,color=pale_gold))
chaise.include("rear_rail",sweep_tube(
    points=[(-1.4,.48,.71),(-.7,.53,.70),
            (.5,.53,.69),(1.42,.41,.69)],
    radius=.050,color=green))
chaise.include("end_rail",sweep_tube(
    points=[(1.43,-.45,.70),(1.52,-.20,.71),
            (1.54,.15,.72),(1.43,.45,.73)],
    radius=.035,color=green))

for i,(x,y) in enumerate([
    (-1.14,-.49),(1.28,-.44),(-1.16,.43),(1.29,.41)
]):
    sign=1 if x>0 else -1
    points=[
        (x,y,.70),(x+sign*.045,y-.015,.52),
        (x-sign*.035,y-.025,.32),(x-sign*.015,y-.045,.17),
        (x+sign*.045,y-.075,.13)
    ]
    chaise.include(f"leg_{i}",sweep_tube(
        points=points,radius=.035,color=green))
    chaise.include(f"leg_bead_{i}",sweep_tube(
        points=[(a,b-.031,c) for a,b,c in points],
        radius=.007,color=pale_gold))
    chaise.include(f"foot_{i}",fillet_box((.10,.08,.05),radius=.022,
        center=(points[-1][0],points[-1][1],.107),color=gold))

def lower_head(point):
    x,y,z=point
    return (x,y,z-.09*max(0,min(1,(z-1.2)/.65)))

head_outline=list(map(lower_head,[
    (-1.45,-.53,.69),(-1.54,-.55,1.18),(-1.59,-.50,1.63),
    (-1.54,-.40,1.85),(-1.48,-.17,1.91),(-1.43,.10,1.87),
    (-1.38,.36,1.71),(-1.33,.51,1.62),(-1.25,.54,1.48),
    (-1.18,.54,.80)
]))
chaise.include("head_frame",sweep_tube(
    points=head_outline,radius=.040,color=green))
chaise.include("head_bead",sweep_tube(
    points=[(x+.023,y-.007,z) for x,y,z in head_outline],
    radius=.010,color=pale_gold))
arm_top=[
    (-1.57,-.53,1.54),(-1.41,-.59,1.40),(-1.13,-.60,1.30),
    (-.91,-.59,1.26),(-.77,-.58,1.17),(-.68,-.575,.94),
    (-.53,-.57,.73)
]
arm_bottom=[
    (-1.45,-.54,.76),(-1.23,-.58,.70),(-.91,-.58,.68),
    (-.60,-.57,.68),(-.53,-.57,.73)
]
for j,path in enumerate((arm_top,arm_bottom)):
    chaise.include(f"near_arm_{j}",sweep_tube(
        points=path,radius=.040 if j==0 else .035,color=green))
    chaise.include(f"arm_bead_{j}",sweep_tube(
        points=[(x,y-.034,z+.004) for x,y,z in path],
        radius=.010,color=pale_gold))
far_arm=[
    (-1.40,.49,1.66),(-1.18,.55,1.49),(-.88,.56,1.41),
    (-.65,.55,1.40),(-.61,.55,1.18),(-.48,.54,.91)
]
chaise.include("far_arm",sweep_tube(
    points=far_arm,radius=.035,color=green))
chaise.include("far_arm_bead",sweep_tube(
    points=[(x,y-.02,z+.025) for x,y,z in far_arm],
    radius=.009,color=pale_gold))
chaise.include("far_arm_upholstery",fillet_box(
    (.65,.075,.38),radius=.035,center=(-.98,.52,1.18),color=fabric))

for group,(cx,cy,cz,scale) in enumerate([
    (.22,-.637,.63,.15),(-1.49,-.38,1.78,.10)
]):
    for sign in (-1,1):
        points=[]
        for k in range(30):
            angle=k/29*2*math.pi
            radius=scale*(1-.78*k/29)
            points.append((
                cx+sign*(.025+radius*math.cos(angle)),
                cy-.006*math.sin(angle),
                cz+.55*radius*math.sin(angle)))
        chaise.include(f"scroll_{group}_{sign}",
            sweep_tube(points=points,radius=.009,color=pale_gold))
scene.include("chaise",chaise)

# The pillow remains a separate meaningful asset, realized before tailoring.
pillow=Asset("Loose cream pillow")
pillow.include("body",fillet_box((.27,.87,.69),radius=.12,
    center=(-1.12,-.10,1.32),color=(.70,.59,.41)))
scene.include("pillow",pillow)

label=Asset("Seat label")
card=box((.19,.095,.008),center=(.72,.13,.954),
         color=(.025,.15,.115))
card.turn("z",80)
label.include("card",card)
for i in range(4):
    line=box((.050,.0025,.001),
        center=(.72,.105+i*.016,.959),color=(.62,.69,.53))
    line.turn("z",-10)
    label.include(f"print_{i}",line)
scene.include("label",label)

curtain=Asset("Curtains")
curtain.include("window",box((.10,1.3,3.5),
    center=(-2.13,.18,1.8),color=(.91,.90,.83)))
for i in range(13):
    y=-.65+i*.085
    x=-2.08+.035*math.sin(i*1.8)
    curtain.include(f"fold_{i}",rod(radius=.060,
        start=(x,y,.10),end=(x-.08,y,3.5),
        color=(.76+.035*(i%3),.73+.035*(i%3),.63+.04*(i%3))))
for i in range(5):
    curtain.include(f"edge_{i}",rod(radius=.025,
        start=(-1.98+i*.024,-.69,.03),
        end=(-2.13+i*.026,-.69,3.5),
        color=(.43+i*.035,.33+i*.035,.21+i*.03)))
scene.include("curtains",curtain)

chair=Asset("Foreground cane chair")
CHAIR_X=-1.08
CHAIR_Y=-1.61
chair.include("frame",fillet_box((.84,.78,.10),radius=.045,
    center=(CHAIR_X,CHAIR_Y,.48),color=green))
chair.include("cane_base",box((.72,.66,.018),
    center=(CHAIR_X,CHAIR_Y,.542),color=(.32,.20,.115)))
for i in range(30):
    x=CHAIR_X-.34+i*.024
    chair.include(f"cane_x_{i}",rod(radius=.0035,
        start=(x,CHAIR_Y-.30,.556),end=(x,CHAIR_Y+.30,.556),
        color=(.49,.35,.20)))
for i in range(27):
    y=CHAIR_Y-.31+i*.024
    chair.include(f"cane_y_{i}",rod(radius=.0035,
        start=(CHAIR_X-.34,y,.558),end=(CHAIR_X+.34,y,.558),
        color=(.51,.37,.22)))
for i,y in enumerate((CHAIR_Y-.34,CHAIR_Y+.34)):
    chair.include(f"bead_{i}",rod(radius=.012,
        start=(CHAIR_X-.40,y,.545),end=(CHAIR_X+.40,y,.545),
        color=pale_gold))
scene.include("foreground_chair",chair)

realize(scene)

def textile(name,base,patterned=False):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*base,1)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    shader=nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value=(*base,1)
    shader.inputs["Roughness"].default_value=.9
    coordinates=nodes.new("ShaderNodeTexCoord")
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=180
    noise.inputs["Detail"].default_value=2
    links.new(coordinates.outputs["Generated"],noise.inputs["Vector"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.17
    bump.inputs["Distance"].default_value=.009
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],shader.inputs["Normal"])
    if patterned:
        separate=nodes.new("ShaderNodeSeparateXYZ")
        links.new(coordinates.outputs["Generated"],separate.inputs[0])
        multiply=nodes.new("ShaderNodeMath")
        multiply.operation="MULTIPLY"
        multiply.inputs[1].default_value=15
        links.new(separate.outputs["Y"],multiply.inputs[0])
        fraction=nodes.new("ShaderNodeMath")
        fraction.operation="FRACT"
        links.new(multiply.outputs[0],fraction.inputs[0])
        ramp=nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation="CONSTANT"
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
        colors=[
            (0,base),(.08,(.43,.255,.235)),(.145,base),
            (.21,(.49,.40,.30)),(.235,base),
            (.70,(.49,.40,.30)),(.725,base)]
        for index,(position,color) in enumerate(colors):
            element=(ramp.color_ramp.elements[0] if index==0
                else ramp.color_ramp.elements.new(position))
            element.position=position
            element.color=(*color,1)
        links.new(fraction.outputs[0],ramp.inputs[0])
        links.new(ramp.outputs["Color"],shader.inputs["Base Color"])
    return mat

cloth=textile("Rose striped cream linen",fabric,True)
plain=textile("Warm pillow linen",(.70,.59,.41))
for ob in list(bpy.data.objects):
    if ob.type!="MESH":
        continue
    ancestor=ob
    ancestry=[]
    while ancestor is not None:
        ancestry.append(ancestor.name.lower())
        ancestor=ancestor.parent
    if any("pillow" in name for name in ancestry):
        ob.hide_render=True
    elif any("far_arm_upholstery" in name for name in ancestry):
        ob.data.materials.clear()
        ob.data.materials.append(cloth)

group=bpy.data.objects.new("Tailored upholstery",None)
bpy.context.collection.objects.link(group)

def mesh_object(name,vertices,faces,material,parent=group):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    ob.parent=parent
    for polygon in mesh.polygons:
        polygon.use_smooth=True
    return ob

def signed_power(value,power):
    return math.copysign(abs(value)**power,value)

vertices=[]
faces=[]
segments=96
rings=40
for j in range(rings+1):
    latitude=-math.pi/2+math.pi*j/rings
    radial=max(0,math.cos(latitude))**.36
    vertical=signed_power(math.sin(latitude),.65)
    for i in range(segments):
        angle=2*math.pi*i/segments
        x=signed_power(math.cos(angle),.47)
        y=signed_power(math.sin(angle),.63)
        vertices.append((
            .015+(CHAISE_LENGTH/2-.035)*radial*x,
            (CHAISE_WIDTH/2+.002)*radial*y,
            SEAT_HEIGHT+.17*vertical))
for j in range(rings):
    for i in range(segments):
        a=j*segments+i
        b=j*segments+(i+1)%segments
        faces.append((a,b,b+segments,a+segments))
mesh_object("Continuous upholstered mattress",vertices,faces,cloth)

head_vertices=list(map(lower_head,[
    (-1.41,-.49,.79),(-1.48,-.50,1.20),(-1.51,-.46,1.61),
    (-1.47,-.37,1.79),(-1.41,-.16,1.85),(-1.36,.10,1.81),
    (-1.31,.34,1.66),(-1.26,.46,1.56),(-1.19,.48,.80),
    (-1.29,-.01,1.31)]))
head=mesh_object("Head padded panel",head_vertices,
    [(i,(i+1)%9,9) for i in range(9)],cloth)
head.modifiers.new("Padding","SOLIDIFY").thickness=.055
side_vertices=[
    (-1.51,-.548,1.47),(-1.37,-.56,1.36),(-1.11,-.565,1.26),
    (-.92,-.56,1.22),(-.81,-.56,1.13),(-.73,-.56,.92),
    (-.57,-.55,.72),(-.64,-.55,.71),(-.93,-.55,.71),
    (-1.22,-.55,.74),(-1.42,-.54,.81),(-1.23,-.58,1.00)]
side=mesh_object("Near padded side",side_vertices,
    [(i,(i+1)%11,11) for i in range(11)],cloth)
side.modifiers.new("Padding","SOLIDIFY").thickness=.045

# A rounded square pillow, broad face angled toward the camera.
pv=[]
pf=[]
pn=64
pm=32
for j in range(pm+1):
    lat=-math.pi/2+math.pi*j/pm
    r=max(0,math.cos(lat))**.45
    for i in range(pn):
        a=2*math.pi*i/pn
        u=.40*r*signed_power(math.cos(a),.40)
        v=.35*r*signed_power(math.sin(a),.40)
        depth=.145*signed_power(math.sin(lat),.75)
        # Broad face normal points toward positive X and negative Y.
        x=-1.10+.69*u+.72*depth-.15*v
        y=-.09+.72*u-.69*depth
        z=1.32+v+.014*math.sin(9*u+4*v)*(1-r)
        pv.append((x,y,z))
for j in range(pm):
    for i in range(pn):
        a=j*pn+i
        b=j*pn+(i+1)%pn
        pf.append((a,b,b+pn,a+pn))
mesh_object("Soft loose pillow",pv,pf,plain)

stitch=bpy.data.materials.new("Muted pink woven flowers")
stitch.diffuse_color=(.40,.205,.19,1)
stitch.use_nodes=True
stitch.node_tree.nodes["Principled BSDF"].inputs[
    "Base Color"].default_value=(.40,.205,.19,1)
stitch.node_tree.nodes["Principled BSDF"].inputs[
    "Roughness"].default_value=.95
fv=[]
ff=[]
for row in range(9):
    yy=-.43+row*.105
    for col in range(21):
        xx=-1.24+col*.125+(row%2)*.045
        q=(abs(xx-.015)/1.49)**(2/.47)+(abs(yy)/.552)**(2/.63)
        if q>=.93:
            continue
        zz=SEAT_HEIGHT+.17*(1-q)**(.65/2)+.003
        for k in range(4):
            angle=k*math.pi/2
            cx=xx+.010*math.cos(angle)
            cy=yy+.010*math.sin(angle)
            index=len(fv)
            fv.extend([
                (cx-.007,cy,zz),(cx,cy-.004,zz),
                (cx+.007,cy,zz),(cx,cy+.004,zz)])
            ff.append((index,index+1,index+2,index+3))
mesh_object("Woven floral marks",fv,ff,stitch)

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-3,-1,3.3),power=360,size=3,
    target=(0,0,.65),color=(1,.94,.85))
area_emitter((1,-3,3.8),power=65,size=4,
    target=(0,0,1),color=(.87,.92,1))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("World")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.73,.76,.79,1)
background.inputs["Strength"].default_value=.18
sc.view_settings.view_transform="AgX"
