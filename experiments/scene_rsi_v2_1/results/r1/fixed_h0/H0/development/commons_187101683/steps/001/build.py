import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(18)
scene = Scene("Warm living room")

gold = (.64, .335, .105)
seatgold = (.72, .405, .145)
backgold = (.77, .455, .185)
pillowgold = (.86, .58, .28)
wood = (.065, .041, .026)
white = (.91, .93, .90)
green = (.16, .29, .10)

scene.include("wall", box((12, .16, 7), center=(0, 1.49, 3.1), color=(.84,.83,.79)))
scene.include("carpet", box((12, 12, .10), center=(0,0,-.065), color=(.32,.31,.29)))

sofa = Asset("Mustard velvet sofa")
sofa.include("lower upholstered plinth", fillet_box((3.52,1.17,.40), radius=.065, center=(0,.46,.29), color=gold))
sofa.include("front upholstered rail", fillet_box((3.12,.18,.28), radius=.045, center=(0,-.115,.49), color=seatgold))
sofa.include("back frame", fillet_box((3.35,.28,1.35), radius=.065, center=(0,.94,.98), color=gold))
for i,x in enumerate((-.79,.79)):
    sofa.include("back cushion "+str(i), fillet_box((1.59,.28,.86), radius=.075, center=(x,.735,1.255), color=backgold))
    sofa.include("seat cushion "+str(i), fillet_box((1.55,.92,.24), radius=.085, center=(x,.235,.735), color=seatgold))
for i,x in enumerate((-1.70,1.70)):
    sofa.include("rounded arm "+str(i), fillet_box((.36,1.20,1.15), radius=.10, center=(x,.39,.76), color=gold))
scene.include("sofa", sofa)

pillow = fillet_box((.59,.21,.61), radius=.065, center=(-1.19,.48,1.23), color=pillowgold)
pillow.turn(axis="y", degrees=-12)
pillow.turn(axis="x", degrees=10)
scene.include("left loose pillow", pillow)
pillow2=fillet_box((.49,.19,.49),radius=.07,center=(1.22,.60,1.21),color=backgold)
pillow2.turn(axis="y",degrees=13)
scene.include("right loose pillow",pillow2)

table=Asset("Dark rectangular coffee table")
table.include("solid wooden top",box((2.65,.99,.105),center=(.60,-1.23,.735),color=wood))
for x in (-.63,1.83):
    for y in (-1.64,-.82):
        table.include("leg %.2f %.2f"%(x,y),box((.095,.095,.68),center=(x,y,.34),color=(.032,.025,.020)))
table.include("front apron",box((2.48,.065,.115),center=(.60,-1.635,.64),color=wood))
scene.include("coffee table",table)

# Two folded pale linen napkins beneath the cups.
for i,(x,y,a) in enumerate(((-.08,-1.29,-9),(1.02,-1.35,-12))):
    nap=box((.66,.37,.012),center=(x,y,.796),color=(.60,.69,.63))
    nap.turn(axis="z",degrees=a)
    scene.include("linen napkin "+str(i),nap)
    fold=box((.58,.16,.009),center=(x+.015,y-.06,.806),color=(.78,.80,.73))
    fold.turn(axis="z",degrees=a+6)
    scene.include("folded napkin edge "+str(i),fold)

# Porcelain is assembled from closely spaced rings, preserving a tapered silhouette.
def cup_and_saucer(name,x,y,handle_side):
    a=Asset(name)
    a.include("saucer bottom",rod(.195,length=.018,center=(x,y,.819),color=white))
    a.include("saucer lip",subtract(
        rod(.207,length=.012,center=(x,y,.831),color=white),
        rod(.166,length=.03,center=(x,y,.84),color=white)))
    bottom=.837
    height=.215
    for j in range(28):
        z=bottom+(j+.5)*height/28
        r=.078+.036*(j+.5)/28
        outer=rod(r,length=height/28+.001,center=(x,y,z),color=white)
        if j>1:
            inner=rod(r-.008,length=height/28+.012,center=(x,y,z),color=white)
            outer=subtract(outer,inner)
        a.include("porcelain section %02d"%j,outer)
    a.include("dark tea",rod(.096,length=.004,center=(x,y,bottom+.178),color=(.16,.10,.045)))
    pts=[]
    for j in range(25):
        t=math.pi*j/24
        pts.append((x+handle_side*(.101+.086*math.sin(t)),y,bottom+.112+.071*math.cos(t)))
    a.include("loop handle",sweep_tube(points=pts,radius=.012,color=white))
    scene.include(name,a)

cup_and_saucer("Left teacup",-.08,-1.22,-1)
cup_and_saucer("Right teacup",1.02,-1.28,1)

# Small charcoal flowerpot, subtly flared at the top.
potx,poty=.52,-.98
potbottom=.79
pot=Asset("Charcoal ceramic flowerpot")
for j in range(24):
    h=.265/24
    z=potbottom+(j+.5)*h
    r=.105+.041*(j+.5)/24
    pot.include("pot band %02d"%j,rod(r,length=h+.001,center=(potx,poty,z),color=(.055,.064,.056)))
pot.include("dark soil",rod(.131,length=.009,center=(potx,poty,1.057),color=(.055,.038,.023)))
pot.include("upper rim",subtract(
    rod(.148,length=.018,center=(potx,poty,1.053),color=(.065,.073,.062)),
    rod(.133,length=.032,center=(potx,poty,1.056),color=(.065,.073,.062))))
scene.include("flower pot",pot)

flowers=Asset("Airy blue and white flowers")
heads=[
    (-.23,.015,1.36,.061),(-.12,.05,1.48,.065),
    (.015,.02,1.59,.064),(.11,.02,1.45,.073),
    (.25,.015,1.48,.070),(.21,-.06,1.34,.067),
    (-.06,-.10,1.38,.057),(.04,-.045,1.47,.059)
]
for i,(dx,dy,z,r) in enumerate(heads):
    end=(potx+dx,poty+dy,z)
    start=(potx+random.uniform(-.04,.04),poty+random.uniform(-.04,.04),1.045)
    flowers.include("flower stem "+str(i),sweep_tube(points=[start,((start[0]+end[0])*.5,(start[1]+end[1])*.5,z-.17),end],radius=.004,color=(.24,.34,.13)))
    for j in range(29):
        zz=random.uniform(-1,1)
        ang=random.uniform(0,math.tau)
        rr=math.sqrt(1-zz*zz)
        p=(end[0]+r*rr*math.cos(ang),end[1]+r*rr*math.sin(ang),end[2]+r*zz*.8)
        color=random.choice([(.60,.68,.76),(.73,.78,.81),(.84,.85,.81),(.54,.63,.74)])
        flowers.include("tiny floret %d %d"%(i,j),ball(random.uniform(.012,.019),center=p,color=color))
for j in range(42):
    angle=random.uniform(0,math.tau)
    rr=random.uniform(.07,.26)
    z=random.uniform(1.09,1.30)
    end=(potx+math.cos(angle)*rr,poty+math.sin(angle)*rr*.63,z)
    flowers.include("leaf twig "+str(j),rod(.0026,start=(potx,poty,1.065),end=end,color=green))
    leaf=ball(1,center=end,color=random.choice([(.18,.32,.12),(.26,.39,.16),(.30,.42,.19)]))
    leaf.resize((.045,.014,.016))
    leaf.turn(axis="y",degrees=random.uniform(-35,35))
    leaf.turn(axis="z",degrees=math.degrees(angle))
    flowers.include("pointed leaf "+str(j),leaf)
scene.include("floral arrangement",flowers)

realize(scene)

# Add fine surface variation to upholstery, wood and carpet.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    col=bs.inputs["Base Color"].default_value
    bs.inputs["Roughness"].default_value=.72
    if col[0]>.5 and col[1]<.65 and col[2]<.4:
        tex=mat.node_tree.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=150
        tex.inputs["Detail"].default_value=2
        bump=mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.17
        bump.inputs["Distance"].default_value=.012
        mat.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        if "Sheen Weight" in bs.inputs:
            bs.inputs["Sheen Weight"].default_value=.22
    if col[0]>.85 and col[1]>.85:
        bs.inputs["Roughness"].default_value=.24
    if .025<col[0]<.09 and col[1]<.065:
        tex=mat.node_tree.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=6
        tex.inputs["Detail"].default_value=3
        mapping=mat.node_tree.nodes.new("ShaderNodeVectorMath")
        mapping.operation="MULTIPLY"
        mapping.inputs[1].default_value=(1,32,14)
        coord=mat.node_tree.nodes.new("ShaderNodeTexCoord")
        mat.node_tree.links.new(coord.outputs["Generated"],mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs[0],tex.inputs["Vector"])
        bump=mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.18
        bump.inputs["Distance"].default_value=.008
        mat.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

def fabric_material(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=.88
    return m

# Long folded curtain at the bright right-hand window.
curtainmat=fabric_material("Warm gray heavy curtain",(.28,.29,.28))
verts=[]
faces=[]
nu,nv=64,65
for j in range(nv):
    t=j/(nv-1)
    z=.02+3.9*t
    # The inner edge is drawn toward the window near the sofa's arm.
    inward=.20*math.exp(-((z-1.65)/.56)**2)
    left=1.45+inward
    width=.78-inward
    for i in range(nu):
        u=i/(nu-1)
        x=left+width*u
        y=1.10+.075*math.sin(u*math.pi*11)+.018*math.sin(u*math.pi*23)
        y-=.16*math.exp(-((z-1.9)/.65)**2)*(1-u)
        verts.append((x,y,z))
for j in range(nv-1):
    for i in range(nu-1):
        a=j*nu+i
        faces.append((a,a+1,a+1+nu,a+nu))
mesh=bpy.data.meshes.new("Curtain fabric folds")
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new("Gathered gray curtain",mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(curtainmat)
for p in mesh.polygons:
    p.use_smooth=True
sub=obj.modifiers.new("Soft fabric","SUBSURF")
sub.levels=1
solid=obj.modifiers.new("Fabric thickness","SOLIDIFY")
solid.thickness=.008

# A light sheer strip catches daylight along the outside edge.
sheermat=fabric_material("Ivory window sheer",(.85,.86,.82))
verts=[]
faces=[]
for j in range(24):
    z=3.9*j/23
    for i in range(16):
        u=i/15
        verts.append((2.13+.38*u,1.17+.035*math.sin(u*math.pi*7),z))
for j in range(23):
    for i in range(15):
        a=j*16+i
        faces.append((a,a+1,a+17,a+16))
mesh=bpy.data.meshes.new("Sheer pleats")
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new("Bright window sheer",mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(sheermat)
for p in mesh.polygons:
    p.use_smooth=True

set_view(position=(-.48,-6.75,2.65),target=(.10,-.02,1.00),lens=49,sensor=36)
area_emitter(position=(3.5,-.15,4.2),power=650,size=3.0,target=(0,.1,.8),color=(1.0,.96,.88))
area_emitter(position=(-2.3,-3.5,3.5),power=150,size=4,target=(0,0,1),color=(.88,.93,1.0))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.74,.78,.82,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.28

sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.35
cam=sc.camera
cam.data.dof.use_dof=True
cam.data.dof.focus_distance=(Vector((.45,-.8,1.05))-cam.location).length
cam.data.dof.aperture_fstop=7.1
