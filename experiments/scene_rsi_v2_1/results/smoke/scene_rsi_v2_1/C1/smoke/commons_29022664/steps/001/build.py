import bpy
import math
import random
from sceneact import *

random.seed(18)
scene = Scene("Compact kitchen")
ivory = (.79, .80, .74)
stone = (.43, .43, .38)
steel = (.43, .48, .47)
chrome = (.62, .67, .66)
navy = (.012, .043, .058)
grout = (.49, .52, .47)

def add(name, node):
    scene.include(name, node)
    return node

def rounded_plate(size, center, radius, color):
    w, d, h = size
    thick = max(radius * 2.5, h)
    p = fillet_box((w, d, thick), radius=radius, center=center, color=color)
    p.resize((1, 1, h / thick), pivot=center)
    return p

# Pale, narrow wood flooring.
add("floor foundation", box((7, 7, .08), center=(0, 0, -.055), color=(.72,.72,.65)))
for i in range(33):
    x = -3.3 + i*.20
    for j in range(5):
        y = -4.0 + j*1.55 + (i % 3)*.44
        c = random.uniform(.73,.84)
        add("floorboard_%d_%d" % (i,j),
            box((.198,1.547,.018), center=(x,y,-.006),
                color=(c+.035,c+.025,c-.025)))

# Back wall and the tiled splashback.
add("back wall", box((5,.12,3.1), center=(0,.724,1.5), color=(.79,.79,.72)))
add("tile grout backing", box((4.8,.018,1.43), center=(0,.649,1.59), color=grout))
for row in range(8):
    for col in range(25):
        x = -2.5 + col*.151
        z = .905 + row*.151
        tint = random.uniform(.88,1.13)
        add("blue tile_%d_%d"%(row,col),
            box((.146,.016,.146), center=(x,.632,z),
                color=(navy[0]*tint,navy[1]*tint,navy[2]*tint)))
# White wall return at the left.
add("left wall", box((.12,2.6,3.0), center=(-1.38,.01,1.48), color=(.81,.81,.73)))
add("left door jamb", box((.055,.11,2.35), center=(-1.294,-.30,1.175), color=(.68,.67,.56)))
add("left low trim", box((.035,.58,.09), center=(-1.306,.12,.055), color=(.72,.71,.62)))

# Cabinet carcase, recessed toe kick, and separate flat drawer/door fronts.
add("cabinet body", box((2.64,.585,.755), center=(.05,.303,.477), color=(.65,.66,.60)))
add("recessed plinth", box((2.55,.47,.11), center=(.05,.348,.071), color=(.70,.71,.64)))
add("plinth face", box((2.54,.022,.078), center=(.05,.104,.064), color=(.74,.75,.68)))

front_y = -.004
left_x = -.823
for k,(bottom,top) in enumerate(((.675,.851),(.435,.670),(.116,.430))):
    add("left drawer %d"%k,
        box((.824,.035,top-bottom), center=(left_x,front_y,(bottom+top)/2),color=ivory))
add("middle cupboard", box((.803,.035,.735),center=(.001,front_y,.484),color=ivory))
add("sink cupboard", box((.805,.035,.735),center=(.812,front_y,.484),color=ivory))
add("right filler", box((.103,.036,.735),center=(1.272,front_y,.484),color=ivory))

# Brushed metal U-shaped cabinet handles.
def handle(name, x, z, width=.215):
    yfront = -.065
    pts = [(x-width/2,-.024,z+.009),
           (x-width/2,yfront+.009,z-.006),
           (x-width/2+.018,yfront,z-.017),
           (x+width/2-.018,yfront,z-.017),
           (x+width/2,yfront+.009,z-.006),
           (x+width/2,-.024,z+.009)]
    add(name, sweep_tube(points=pts,radius=.010,color=(.56,.58,.51)))
handle("top drawer pull",left_x,.807)
handle("middle drawer pull",left_x,.644)
handle("bottom drawer pull",left_x,.402)
handle("middle door pull",.001,.807)
handle("sink door pull",.812,.807)

# Worktop, cut for the two sink basins.
top = box((2.77,.687,.044),center=(.035,.313,.884),color=stone)
large_cut = rounded_plate((.463,.438,.16),(.724,.324,.877),.058,(1,1,1))
small_cut = rounded_plate((.233,.353,.16),(1.098,.357,.877),.045,(1,1,1))
add("stone worktop", subtract(top,large_cut,small_cut))

# Metal sink rim with integrated right-hand draining board.
rim = rounded_plate((1.087,.542,.014),(1.018,.335,.913),.031,steel)
hole_a = rounded_plate((.463,.426,.12),(.724,.324,.912),.057,steel)
hole_b = rounded_plate((.234,.341,.12),(1.098,.357,.912),.042,steel)
add("sink rim and draining board",subtract(rim,hole_a,hole_b))

def basin(name,cx,cy,w,d,depth,r):
    outer=fillet_box((w,d,depth),radius=r,
                     center=(cx,cy,.908-depth/2),color=steel)
    inner=fillet_box((w-.018,d-.018,depth+.055),radius=r-.007,
                     center=(cx,cy,.908-depth/2+.035),color=steel)
    add(name,subtract(outer,inner))
basin("large steel basin",.724,.324,.489,.452,.187,.060)
basin("small steel basin",1.098,.357,.258,.367,.148,.048)

# Circular drains and dark central holes in the basin floors.
for name,x,y,z,r in (("large",.746,.280,.741,.046),("small",1.106,.318,.781,.032)):
    add(name+" drain flange",rod(radius=r,length=.004,center=(x,y,z),color=chrome))
    add(name+" drain dark inset",rod(radius=r*.73,length=.005,center=(x,y,z+.003),color=(.10,.13,.12)))
    add(name+" drain strainer",rod(radius=r*.56,length=.006,center=(x,y,z+.005),color=steel))
    for n in range(8):
        a=n*math.tau/8
        add(name+" strainer hole "+str(n),
            rod(radius=.0025,length=.0015,center=(x+r*.39*math.cos(a),y+r*.39*math.sin(a),z+.0088),color=(.07,.09,.08)))

# Recessed parallel grooves on the draining surface at the right.
for i in range(10):
    x=1.278+i*.024
    add("drainer channel %d"%i,
        rod(radius=.0034,start=(x,.110,.922),end=(x,.551,.922),color=(.21,.27,.26)))
    add("drainer channel highlight %d"%i,
        rod(radius=.0018,start=(x+.004,.110,.923),end=(x+.004,.551,.923),color=(.65,.70,.67)))

# High arched faucet and its small lever.
add("faucet foot",rod(radius=.034,length=.018,center=(.969,.570,.931),color=chrome))
add("faucet body",rod(radius=.023,start=(.969,.570,.932),end=(.969,.570,1.057),color=chrome))
tap_points=[
    (.969,.570,1.025),(.972,.574,1.120),(.974,.575,1.238),
    (.972,.568,1.304),(.959,.549,1.335),(.935,.517,1.345),
    (.912,.475,1.345),(.895,.432,1.333),(.886,.399,1.310),
    (.882,.376,1.275),(.882,.374,1.239)
]
add("curved chrome faucet",sweep_tube(points=tap_points,radius=.013,color=chrome))
add("faucet nozzle",rod(radius=.017,start=(.882,.374,1.252),end=(.882,.374,1.226),color=steel))
add("tap mixer housing",rod(radius=.024,start=(.980,.568,.972),end=(1.022,.568,.995),color=chrome))
add("tap lever",rod(radius=.008,start=(1.017,.568,.995),end=(1.062,.570,1.065),color=chrome))

# Cropped appliance at the right side of the cabinets.
add("oven side",box((.57,.62,.83),center=(1.646,.29,.443),color=(.68,.70,.65)))
add("oven black glass",box((.49,.026,.57),center=(1.646,-.038,.48),color=(.018,.036,.038)))
add("oven bottom metal strip",box((.51,.04,.075),center=(1.646,-.047,.155),color=(.64,.67,.63)))
add("oven handle",rod(radius=.013,start=(1.433,-.094,.738),end=(1.858,-.094,.738),color=chrome))

realize(scene)

# Surface finishes and restrained procedural texture.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    c=bs.inputs["Base Color"].default_value
    rgb=tuple(c[:3])
    bs.inputs["Roughness"].default_value=.52
    if all(abs(rgb[i]-steel[i])<.012 for i in range(3)) or all(abs(rgb[i]-chrome[i])<.012 for i in range(3)):
        bs.inputs["Metallic"].default_value=.88
        bs.inputs["Roughness"].default_value=.22 if rgb[0]>.5 else .29
    if all(abs(rgb[i]-stone[i])<.012 for i in range(3)):
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        tex=nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=42
        tex.inputs["Detail"].default_value=5
        tex.inputs["Roughness"].default_value=.78
        ramp=nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(.235,.245,.227,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(.54,.53,.47,1)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump=nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.16
        bump.inputs["Distance"].default_value=.0015
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value=.69
    if rgb[2]<.08 and rgb[0]<.03:
        bs.inputs["Roughness"].default_value=.25
    if rgb[0]>.70 and rgb[1]>.70 and rgb[2]<rgb[0]-.025:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        coord=nodes.new("ShaderNodeTexCoord")
        mapping=nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(55,2.3,3)
        links.new(coord.outputs["Generated"],mapping.inputs[0])
        noise=nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=3
        noise.inputs["Detail"].default_value=2
        links.new(mapping.outputs["Vector"],noise.inputs["Vector"])
        bump=nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.12
        bump.inputs["Distance"].default_value=.001
        links.new(noise.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bs.inputs["Normal"])

world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("SceneWorld")
    bpy.context.scene.world=world
world.use_nodes=True
background=world.node_tree.nodes.get("Background")
if background is None:
    background=world.node_tree.nodes.new("ShaderNodeBackground")
output=world.node_tree.nodes.get("World Output")
if output is None:
    output=world.node_tree.nodes.new("ShaderNodeOutputWorld")
world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.72,.77,.80,1)
background.inputs["Strength"].default_value=.38

set_view(position=(-.29,-2.55,2.18),target=(.015,.29,.64),lens=37,sensor=36)
area_emitter(position=(-2.0,-1.7,3.8),power=450,size=3.0,target=(0,.2,.65),color=(1,.965,.88))
area_emitter(position=(1,-1.4,3.2),power=95,size=2.3,target=(.5,.2,.6),color=(.88,.94,1))

sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.25
sc.render.image_settings.file_format='PNG'
