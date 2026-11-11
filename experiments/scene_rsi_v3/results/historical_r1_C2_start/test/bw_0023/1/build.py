# Reference inventory, estimated within the phone-screen interior:
# - Warm neo-Gothic hall fills the view, with ribbed pointed vaults in the
#   upper half and clustered piers and arcades receding toward a bright end.
# - A chandelier hangs left of center, partly overlapping the small sphere.
# - A staircase and dark-red ornamental railing occupy the lower foreground,
#   crossing diagonally toward the lower right. Their lower ends are occluded.
# - A matte magenta sphere is near the middle; a much larger iridescent sphere
#   occupies the right foreground and is clipped by the screen boundary.
# - The far end, side openings, and lower level are partially occluded.
#
# The second feedback image shows a recognizable hall, but its frontal stair,
# centered tunnel and fully visible circular bubble differ from the reference.
# This revision makes the stair and railing cross the foreground diagonally,
# moves the bubble toward the right edge, and adds deeper architectural shadows
# and brighter light at the far end. Exact hidden architecture remains uncertain.
#
# Expanded primitive estimate: hall shell 5, vault ribs 166, arcade ribs 72,
# columns 112, distant opening 7, stair and railing 65, chandelier 35,
# spheres 2: approximately 464 meshes. No Boolean operations.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Neo-Gothic heritage gallery")
stone = (0.68, 0.62, 0.53)
light_stone = (0.80, 0.75, 0.67)
dark_stone = (0.36, 0.32, 0.27)
red = (0.24, 0.025, 0.018)
gold = (0.60, 0.37, 0.10)
marble = (0.78, 0.75, 0.69)

def line(asset, name, a, b, radius, color):
    if (Vector(a) - Vector(b)).length > 0.00001:
        asset.include(name, rod(radius, start=a, end=b, color=color))

def path(asset, name, points, radius, color):
    for i in range(len(points)-1):
        line(asset, "%s_%02d" % (name, i), points[i], points[i+1], radius, color)

# Hall axis is Y; the viewer is on the upper gallery looking along it.
vaults = Asset("vaults")
vaults.include("floor", box((9.8, 32, .20), center=(0,10,-.12), color=stone))
vaults.include("left wall", box((.3,32,8.8), center=(-4.9,10,4.3), color=stone))
vaults.include("right wall", box((.3,32,8.8), center=(4.9,10,4.3), color=stone))
vaults.include("ceiling", box((10,32,.22), center=(0,10,8.70), color=light_stone))
bays = [-2.0, 1.8, 5.6, 9.4, 13.2, 17.0, 20.8]
profile = [(-4.55,4.25),(-4.25,5.45),(-3.55,6.52),(-2.55,7.38),
           (-1.35,8.0),(0,8.46),(1.35,8.0),(2.55,7.38),
           (3.55,6.52),(4.25,5.45),(4.55,4.25)]
for j,y in enumerate(bays):
    path(vaults, "cross rib %d" % j, [(x,y,z) for x,z in profile],
         .11, dark_stone)
    if j < len(bays)-1:
        y2 = bays[j+1]
        for side in (-1,1):
            mid = (0,(y+y2)/2,8.43)
            path(vaults, "groin a %d %d" % (j,side),
                 [(side*4.48,y,4.30),(side*3.8,y+.35,5.75),
                  (side*2.6,y+.85,6.95),mid], .075, dark_stone)
            path(vaults, "groin b %d %d" % (j,side),
                 [mid,(side*2.6,y2-.85,6.95),
                  (side*3.8,y2-.35,5.75),(side*4.48,y2,4.30)],
                 .075, dark_stone)
for side in (-1,1):
    x = side*4.5
    for j in range(len(bays)-1):
        ya,yb = bays[j],bays[j+1]
        mid = (ya+yb)/2
        path(vaults, "side arcade %d %d" % (side,j),
             [(x,ya,3.7),(x,ya+.35,4.7),(x,ya+1.05,5.45),
              (x,mid,6.15),(x,yb-1.05,5.45),(x,yb-.35,4.7),
              (x,yb,3.7)], .09, dark_stone)
scene.include("vaults", vaults)

columns = Asset("columns")
for side in (-1,1):
    for j,y in enumerate(bays):
        x = side*4.4
        columns.include("base %d %d" % (side,j),
                        box((.76,.76,.22), center=(x,y,.12), color=dark_stone))
        columns.include("plinth %d %d" % (side,j),
                        box((.59,.59,.35), center=(x,y,.38), color=stone))
        for k,(dx,dy,r) in enumerate([(0,0,.22),(-.24,0,.105),
                                      (.24,0,.105),(0,-.22,.105)]):
            line(columns, "shaft %d %d %d" % (side,j,k),
                 (x+dx,y+dy,.53),(x+dx,y+dy,4.05),r,light_stone)
        columns.include("capital %d %d" % (side,j),
                        box((.74,.72,.24), center=(x,y,4.10), color=stone))
        columns.include("abacus %d %d" % (side,j),
                        box((.85,.80,.12), center=(x,y,4.28), color=dark_stone))
scene.include("columns", columns)

far = Asset("far daylight")
far.include("end wall", box((9.5,.24,8.5), center=(0,23.2,4.25),
                             color=(.78,.73,.64)))
far.include("bright opening", box((2.35,.035,4.7), center=(0,23.04,2.45),
                                   color=(1,.96,.84)))
for x in (-1.24,1.24):
    line(far, "portal jamb %s" % x, (x,22.98,.10),(x,22.98,4.5),.12,stone)
path(far, "portal arch",
     [(-1.24,22.98,4.5),(-.85,22.98,5.05),(0,22.98,5.72),
      (.85,22.98,5.05),(1.24,22.98,4.5)], .11, stone)
scene.include("far daylight", far)

# Staircase crosses the foreground diagonally. These local coordinates make
# each tread a separate editable slab, with an open wrought-metal railing.
stairs = Asset("staircase & railing")
angle = math.radians(-38)
def stair_point(x,y,z):
    return (x*math.cos(angle)-y*math.sin(angle)-.9,
            x*math.sin(angle)+y*math.cos(angle)-1.2,z)

for i in range(10):
    y = -2.1+i*.38
    z = .12+i*.135
    step = box((3.4,.40,.14), center=stair_point(0,y,z), color=marble)
    step.turn('+z', -38)
    stairs.include("marble step %02d" % i, step)
    nosing = box((3.42,.045,.045),
                 center=stair_point(0,y-.19,z+.065), color=light_stone)
    nosing.turn('+z', -38)
    stairs.include("step nosing %02d" % i, nosing)
landing = box((3.9,1.4,.20), center=stair_point(0,2.18,1.40), color=marble)
landing.turn('+z', -38)
stairs.include("landing", landing)

xr = -1.78
y0,y1 = -2.26,1.45
z0,z1 = .20,1.55
def sp(y,z):
    return stair_point(xr,y,z)
line(stairs, "lower rail", sp(y0,z0+.28),sp(y1,z1+.28),.06,red)
line(stairs, "upper handrail", sp(y0,z0+1.25),sp(y1,z1+1.25),.085,red)
line(stairs, "gold handrail trim", sp(y0,z0+1.32),sp(y1,z1+1.32),.026,gold)
for i in range(11):
    t=i/10
    y=y0+(y1-y0)*t
    z=z0+(z1-z0)*t
    line(stairs, "baluster %02d" % i, sp(y,z+.28),sp(y,z+1.25),.035,red)
    if i<10:
        yn=y0+(y1-y0)*(i+1)/10
        zn=z0+(z1-z0)*(i+1)/10
        line(stairs, "gold diagonal %02d" % i, sp(y,z+.38),
             sp(yn,zn+1.06),.023,gold)
        line(stairs, "red diagonal %02d" % i, sp(y,z+1.05),
             sp(yn,zn+.38),.021,red)
for i,(y,z) in enumerate([(y0,z0),(y1,z1)]):
    line(stairs, "newel %d" % i,sp(y,z),sp(y,z+1.42),.09,red)
    stairs.include("finial %d" % i,ball(.11,center=sp(y,z+1.45),color=gold))
scene.include("staircase & railing", stairs)

chandelier = Asset("chandelier")
cx,cy,cz = -1.30,7.2,4.15
line(chandelier,"suspension",(cx,cy,cz+.3),(cx,cy,8.3),.025,gold)
line(chandelier,"stem",(cx,cy,cz-.45),(cx,cy,cz+.35),.07,gold)
chandelier.include("central drop",ball(.16,center=(cx,cy,cz-.45),color=gold))
for i in range(8):
    a=2*math.pi*i/8
    dx,dy=math.cos(a),math.sin(a)
    p0=(cx,cy,cz-.18)
    p1=(cx+.42*dx,cy+.42*dy,cz-.35)
    p2=(cx+.78*dx,cy+.78*dy,cz-.10)
    path(chandelier,"arm %d" % i,[p0,p1,p2],.035,gold)
    line(chandelier,"candle %d" % i,p2,(p2[0],p2[1],p2[2]+.24),
         .055,light_stone)
    chandelier.include("bulb %d" % i,
                        ball(.075,center=(p2[0],p2[1],p2[2]+.29),
                             color=(1,.88,.63)))
scene.include("chandelier", chandelier)

spheres = Asset("spheres")
spheres.include("large iridescent bubble",
                ball(2.15,center=(4.25,1.65,3.35),color=(.65,.45,.8)))
spheres.include("small magenta sphere",
                ball(.58,center=(-.25,6.4,3.85),color=(.72,.005,.36)))
scene.include("spheres", spheres)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
wn=sc.world.node_tree.nodes
background=wn.get("Background") or wn.new("ShaderNodeBackground")
output=wn.get("World Output") or wn.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.68,.70,.73,1)
background.inputs["Strength"].default_value=.32

def lineage(obj):
    names=[]
    while obj:
        names.append(obj.name.lower())
        obj=obj.parent
    return " ".join(names)

def material(name,color,roughness=.5,metallic=0):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=roughness
    p.inputs["Metallic"].default_value=metallic
    return mat

limestone=material("Warm aged sandstone",(.68,.61,.51),.8)
n=limestone.node_tree.nodes
l=limestone.node_tree.links
p=n.get("Principled BSDF")
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=6
noise.inputs["Detail"].default_value=3
ramp=n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color=(.38,.33,.27,1)
ramp.color_ramp.elements[1].color=(.81,.75,.65,1)
bump=n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.12
bump.inputs["Distance"].default_value=.035
l.new(noise.outputs["Fac"],ramp.inputs["Fac"])
l.new(ramp.outputs["Color"],p.inputs["Base Color"])
l.new(noise.outputs["Fac"],bump.inputs["Height"])
l.new(bump.outputs["Normal"],p.inputs["Normal"])

bubble=material("Iridescent soap film",(.65,.35,.68),.10,.10)
n=bubble.node_tree.nodes
l=bubble.node_tree.links
p=n.get("Principled BSDF")
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value=.38
elif "Transmission" in p.inputs:
    p.inputs["Transmission"].default_value=.38
p.inputs["IOR"].default_value=1.33
if "Thin Film Thickness" in p.inputs:
    p.inputs["Thin Film Thickness"].default_value=420
    p.inputs["Thin Film IOR"].default_value=1.33
layer=n.new("ShaderNodeLayerWeight")
ramp=n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors=[(0,(.05,.55,.9,1)),(.14,(.95,.06,.55,1)),
        (.28,(1,.66,.03,1)),(.42,(.08,.8,.65,1)),
        (.56,(.42,.10,.9,1)),(.70,(1,.3,.15,1)),
        (.85,(.12,.75,.95,1)),(1,(.9,.65,.9,1))]
for pos,col in colors:
    e=ramp.color_ramp.elements[0] if pos==0 else ramp.color_ramp.elements.new(pos)
    e.position=pos
    e.color=col
l.new(layer.outputs["Facing"],ramp.inputs["Fac"])
l.new(ramp.outputs["Color"],p.inputs["Base Color"])

magenta=material("Matte deep magenta",(.55,.002,.26),.72)
bulb=material("Warm glowing bulbs",(1,.82,.55),.35)
p=bulb.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value=(1,.70,.35,1)
    p.inputs["Emission Strength"].default_value=4
elif "Emission" in p.inputs:
    p.inputs["Emission"].default_value=(1,.70,.35,1)
opening=material("Daylight in distant portal",(1,.94,.78),.8)
p=opening.node_tree.nodes.get("Principled BSDF")
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value=(1,.92,.76,1)
    p.inputs["Emission Strength"].default_value=2

for obj in bpy.data.objects:
    if obj.type!="MESH":
        continue
    name=lineage(obj)
    mat=None
    if "large iridescent bubble" in name:
        mat=bubble
        for poly in obj.data.polygons:
            poly.use_smooth=True
    elif "small magenta sphere" in name:
        mat=magenta
        for poly in obj.data.polygons:
            poly.use_smooth=True
    elif "bulb " in name:
        mat=bulb
    elif "bright opening" in name:
        mat=opening
    elif ("vaults" in name or "columns" in name) and not any(
            s in name for s in ("rib","groin","arcade","abacus")):
        mat=limestone
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

set_view((.25,-8.7,4.55),(.05,8.3,4.05),lens=31,sensor=36)
area_emitter((-1.3,7.0,4.4),power=1100,size=2.2,
             target=(0,5,1),color=(1,.73,.48))
area_emitter((0,22.5,5),power=3200,size=4.0,
             target=(0,5,3),color=(1,.92,.78))
area_emitter((-3,-4,6.8),power=500,size=5,
             target=(0,6,3),color=(1,.83,.68))

for label in ("vaults","columns","staircase & railing","chandelier","spheres"):
    coll=bpy.data.collections.get(label)
    if coll is None:
        coll=bpy.data.collections.new(label)
        sc.collection.children.link(coll)
    for obj in list(bpy.data.objects):
        if label in lineage(obj) and obj.name not in coll.objects:
            coll.objects.link(obj)
            for old in list(obj.users_collection):
                if old!=coll:
                    old.objects.unlink(obj)

sc.render.engine="CYCLES"
sc.cycles.use_denoising=True
sc.render.resolution_x=3840
sc.render.resolution_y=2160
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
try:
    sc.view_settings.view_transform="Filmic"
except Exception:
    pass
