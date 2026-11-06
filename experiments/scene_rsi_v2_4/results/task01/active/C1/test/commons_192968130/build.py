from sceneact import *
import bpy, math

# Reference inventory, in normalized image coordinates:
# Vertical oak wall: (0,.12)-(.46,.76), closely spaced dark gaps.
# White door: (.31,.29)-(.45,.77), silver lever, pale narrow surround.
# Black bench with white inset: cropped at left, (0,.65)-(.20,.80).
# Gray tiled floor: lower left; ceiling: upper left.
# Stone counter: far corner (.46,.60), left edge reaching (.36,1).
# Black sink and bronze draining board: (.46,.64)-(.62,.72).
# Black hob: (.40,.77)-(.78,1), cropped at bottom, four fine burner rings.
# Walnut cupboards: (.46,0)-(1,.43); extractor underneath.
# Pale glossy backsplash occupies the right, with a warm light along its top.
# Small switch and socket beside the door remain separate parts.
# Hidden cabinet interiors and the near ends of the kitchen remain uncertain.
#
# Sparse landmarks: batten top y=.12; door top corners (.31,.295),(.45,.295);
# door bottom y=.765; bench top y=.66; counter rear corner (.46,.60);
# sink center (.535,.675); hob far edge around y=.77.
#
# Revision ledger:
# Observed: door and wall were too far right, wall top too low; counter's
# near edge ran rightward instead of leftward, exposing excessive base fronts.
# Camera position relative to the counter and local kitchen/back-wall spacing
# both contribute. Move the camera inside the counter's lateral span and retain
# a nearly straight view toward the back wall. A modest downward pitch places
# the protected door floor contact and top closer to their reference heights.
# Observed: counter/door lateral gap was much too wide. Move the kitchen
# toward the door independently, preserving door size and bench proportions.
# Observed: sink was too small and far away. Bring its complete assembly nearer;
# place the hob's far edge nearer the camera so it occupies the foreground.
# Raise battens while preserving their floor contact and regular dark gaps.
# The exact upper-cabinet terminal depth is uncertain; retain its box assembly
# and add the visible walnut end lining above the far end of the counter.
#
# Estimated expansion: approximately 205 SceneAct primitive meshes,
# including 59 battens, 54 floor-joint strips, and 12 draining-board parts.
# Four Blender curves are surface markings. No expensive Boolean operations.
# All groups have explicit dimensions and world-space placements.

scene = Scene("Compact walnut kitchen")

def A(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def B(a, name, size, center, color):
    n = box(size=size, center=center, color=color)
    a.include(name, n)
    return n

cream = (.78,.77,.71)
white = (.85,.86,.83)
oak = (.30,.135,.047)
walnut = (.085,.032,.012)
black = (.008,.011,.010)
stone = (.64,.61,.52)

room = A("Room architecture")
B(room,"Floor",(8,10,.12),(-1,0,-.065),(.48,.46,.41))
B(room,"Back plaster",(6,.15,3.15),(-1.35,4.23,1.575),cream)
B(room,"Kitchen wall",(.12,9,3.15),(1.13,.15,1.575),cream)
B(room,"Ceiling",(8,10,.12),(-1,.1,3.14),(.82,.82,.77))

slats = A("Oak batten wall")
B(slats,"Dark backing",(4.25,.035,2.95),(-1.8,4.125,1.475),(.043,.028,.017))
for i in range(59):
    B(slats,"Oak vertical %02d"%i,(.044,.058,2.95),
      (-3.87+i*.071,4.077,1.475),oak)

door = A("Back door")
B(door,"Outer surround",(.85,.095,2.15),(-.36,4.005,1.075),white)
B(door,"Shadow reveal",(.744,.035,2.044),(-.36,3.946,1.027),(.40,.40,.37))
B(door,"White leaf",(.713,.043,2.015),(-.36,3.922,1.025),(.80,.82,.80))
B(door,"Left jamb",(.035,.08,2.13),(-.77,3.94,1.065),white)
B(door,"Right jamb",(.035,.08,2.13),(.05,3.94,1.065),white)
B(door,"Header",(.855,.08,.045),(-.36,3.94,2.115),white)
door.include("Handle rose",rod(radius=.025,length=.018,
    center=(-.62,3.887,1.04),axis='+y',color=(.48,.49,.46)))
B(door,"Silver lever",(.13,.027,.018),(-.58,3.867,1.049),(.48,.49,.46))
door.include("Key plate",rod(radius=.013,length=.012,
    center=(-.62,3.887,.945),axis='+y',color=(.48,.49,.46)))
for z in [.25,1.75]:
    B(door,"Hinge %.2f"%z,(.015,.025,.065),(-.012,3.887,z),(.48,.49,.46))

fixtures = A("Switch and socket")
for name,x,z,w,h in [
    ("Light switch",-.99,1.08,.09,.09),
    ("Low power socket",-.96,.29,.075,.09)
]:
    B(fixtures,name,(w,.025,h),(x,4.025,z),white)
    B(fixtures,name+" inset",(w*.55,.012,h*.55),(x,4.005,z),(.70,.71,.68))

bench = A("Black bench with white front")
B(bench,"Carcass",(1.39,.43,.47),(-2.27,3.83,.235),(.014,.019,.018))
B(bench,"White inset",(1.24,.025,.29),(-2.30,3.598,.206),(.81,.84,.82))
B(bench,"Top",(1.42,.47,.045),(-2.27,3.81,.49),(.010,.014,.013))
B(bench,"Bottom trim",(1.35,.025,.035),(-2.27,3.59,.045),(.035,.043,.038))

# Kitchen axis is +Y, ending at y=3.03; lateral pivot x=.66.
base = A("Lower walnut cabinets")
B(base,"Cabinet body",(.69,5.05,.85),(.715,.505,.445),walnut)
B(base,"Recessed plinth",(.58,5.0,.10),(.76,.505,.05),(.045,.029,.015))
for j in range(7):
    B(base,"Lower door %02d"%j,(.027,.707,.73),
      (.359,-1.66+j*.721,.475),walnut)

counter = A("Marble worktop")
B(counter,"Stone slab",(.82,5.1,.045),(.66,.48,.902),stone)

sink = A("Inset sink and drainer")
sx,sy=.625,1.55
B(sink,"Inset dark rectangle",(.64,.67,.012),(sx,sy,.932),(.035,.029,.016))
B(sink,"Deep black bowl",(.40,.43,.013),(.55,sy-.025,.940),(.008,.010,.008))
for name,size,center in [
    ("Left rim",(.016,.65,.012),(.312,sy,.947)),
    ("Right rim",(.016,.65,.012),(.937,sy,.947)),
    ("Far rim",(.64,.016,.012),(sx,sy+.32,.947)),
    ("Near rim",(.64,.016,.012),(sx,sy-.32,.947))
]:
    B(sink,name,size,center,(.24,.17,.066))
B(sink,"Drainboard",(.145,.58,.008),(.845,sy,.949),(.10,.078,.034))
for j in range(7):
    B(sink,"Drainboard rib %02d"%j,(.115,.009,.006),
      (.845,sy-.24+j*.077,.955),(.27,.20,.085))

hob = A("Ceramic cooktop")
B(hob,"Black reflective glass",(.71,1.02,.014),(.595,.10,.935),black)

upper = A("Walnut upper cupboards")
# Deeper wall cupboards show a broad underside from this close viewpoint.
B(upper,"Cupboard carcass",(.84,5.1,1.03),(.68,.48,2.595),walnut)
for j in range(7):
    yy=-1.70+j*.725
    B(upper,"Walnut face %02d"%j,(.028,.712,1.01),
      (.246,yy,2.595),walnut)
    B(upper,"Dark lower lip %02d"%j,(.036,.712,.025),
      (.237,yy,2.09),(.035,.015,.006))
B(upper,"Far end panel",(.87,.045,1.04),(.68,3.05,2.595),(.070,.027,.009))

end_lining = A("Walnut terminal wall lining")
B(end_lining,"Counter-to-cupboard end lining",(.84,.035,1.18),
  (.68,3.065,1.51),(.10,.039,.012))

backsplash = A("Glossy ivory backsplash")
B(backsplash,"Glass wall",(.018,5.12,1.17),(1.056,.49,1.505),(.74,.75,.70))

extractor = A("Integrated extractor")
B(extractor,"Brushed metal underside",(.70,1.0,.028),(.68,.02,2.067),(.45,.46,.42))
B(extractor,"Filter inset",(.48,.60,.009),(.65,.02,2.049),(.25,.26,.23))
for j in range(8):
    B(extractor,"Filter slit %02d"%j,(.44,.012,.003),
      (.65,-.22+j*.065,2.042),(.10,.11,.09))

lightstrip = A("Under cupboard lighting")
B(lightstrip,"Warm luminous strip",(.025,5.03,.014),
  (1.012,.48,2.061),(1.0,.76,.40))

floor_joints = A("Floor tile joints")
for j in range(9):
    yy=-2.1+j*.65
    B(floor_joints,"Cross joint %02d"%j,(5.1,.003,.0015),
      (-1.5,yy,-.0038),(.35,.33,.29))
    for i in range(5):
        xx=-4+i*1.24+(j%2)*.62
        B(floor_joints,"Staggered joint %02d %02d"%(j,i),
          (.003,.65,.0015),(xx,yy+.325,-.0038),(.35,.33,.29))

scene.settle()
realize(scene)

# SceneAct emits generic Blender object names. Materials are identified by their
# actual colors, rather than assuming semantic part names survive realization.
def close(c, ref):
    return sum(abs(c[i]-ref[i]) for i in range(3)) < .015

for m in list(bpy.data.materials):
    m.use_nodes=True
    nt=m.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    c=tuple(bs.inputs["Base Color"].default_value[:3])
    bs.inputs["Roughness"].default_value=.43
    if close(c,black):
        bs.inputs["Roughness"].default_value=.085
        bs.inputs["Metallic"].default_value=.28
    if close(c,(.74,.75,.70)):
        bs.inputs["Roughness"].default_value=.11
    if close(c,(.48,.49,.46)) or close(c,(.45,.46,.42)):
        bs.inputs["Metallic"].default_value=.8
        bs.inputs["Roughness"].default_value=.25
    if close(c,(.24,.17,.066)):
        bs.inputs["Metallic"].default_value=.7
        bs.inputs["Roughness"].default_value=.24
    if close(c,(1.0,.76,.40)):
        bs.inputs["Emission Color"].default_value=(1,.73,.35,1)
        bs.inputs["Emission Strength"].default_value=4

    if close(c,walnut) or close(c,oak):
        coord=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(16,16,.65)
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=3
        tex.inputs["Detail"].default_value=2
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(*[v*.65 for v in c],1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(*[v*1.25 for v in c],1)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs["Vector"])
        nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bs.inputs["Roughness"].default_value=.34

    if close(c,stone):
        coord=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(2,8,2)
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=4
        noise.inputs["Detail"].default_value=3
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.43
        ramp.color_ramp.elements[0].color=(.19,.16,.11,1)
        ramp.color_ramp.elements[1].position=.49
        ramp.color_ramp.elements[1].color=(.72,.68,.57,1)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bs.inputs["Roughness"].default_value=.28

ringmat=bpy.data.materials.new("Muted ceramic burner markings")
ringmat.use_nodes=True
rbs=ringmat.node_tree.nodes.get("Principled BSDF")
rbs.inputs["Base Color"].default_value=(.065,.071,.059,1)
rbs.inputs["Roughness"].default_value=.3

def ring(name,x,y,r):
    cu=bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'
    cu.bevel_depth=.0014
    cu.bevel_resolution=1
    sp=cu.splines.new('POLY')
    sp.points.add(56)
    for j,p in enumerate(sp.points):
        t=2*math.pi*j/56
        p.co=(x+r*math.cos(t),y+r*math.sin(t),.945,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    cu.materials.append(ringmat)

for i,(x,y,r) in enumerate([
    (.42,.35,.155),(.78,.35,.115),
    (.42,-.16,.12),(.78,-.19,.17)
]):
    ring("Burner ring %d"%i,x,y,r)

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
background.inputs["Color"].default_value=(.76,.79,.83,1)
background.inputs["Strength"].default_value=.22

# Explicit camera position, target, and lens. The camera lies to the right of
# the counter's exposed edge, giving the observed leftward foreground slope.
set_view(position=(.54,-2.0,1.66),
         target=(.45,4.05,1.21),lens=32,sensor=36)
area_emitter(position=(-2.8,-.3,2.65),power=410,size=4,
             target=(.0,2.5,1),color=(1,.92,.81))
area_emitter(position=(-1.8,3.0,2.95),power=110,size=2.5,
             target=(-1.5,4,1.2),color=(1,.91,.78))
area_emitter(position=(.97,1.1,2.01),power=48,size=2.0,
             target=(1.05,1.3,1.25),color=(1,.73,.40))
sc.view_settings.view_transform='AgX'
