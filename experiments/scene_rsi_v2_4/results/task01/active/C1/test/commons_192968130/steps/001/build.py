from sceneact import *
import bpy, math

# Reference inventory (normalized image bounds):
# Room: pale ceiling (0,0)-(0.47,.12), warm gray tiled floor (0,.76)-(.42,1).
# Back wall: closely spaced oak vertical battens (0,.12)-(.46,.76).
# White door and surround (.31,.29)-(.45,.77); small metal handle at (.34,.53).
# Low black bench with white front (0,.65)-(.20,.80), cropped at left.
# Right kitchen: marble worktop (.39,.59)-(1,1), black inset sink
# (.46,.63)-(.62,.72), foreground black ceramic hob (.40,.77)-(.78,1).
# Dark walnut upper cupboards (.46,0)-(1,.43), pale extractor underneath;
# glossy ivory backsplash (.57,.28)-(1,1), with warm under-cabinet light.
# Counter and cupboards are cropped near the camera; hidden cabinet details uncertain.
# Landmarks: door upper corners (.313,.295),(.448,.295); door lower right
# (.445,.763); countertop far left (.455,.599), sink corners approximately
# (.48,.646),(.583,.642),(.615,.704),(.461,.712).
# Long kitchen edges converge near (.50,.47), with uncertainty from crop and reflections.
# Batten top edge nearly horizontal; door uprights nearly vertical.
# Planned geometry: about 155 box/rod meshes, plus 5 simple sink solids.
# Group pivots: room origin; kitchen x=.95, y=1; back wall y=4.15.

scene = Scene("Warm compact kitchen")
def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def B(a, name, size, center, color):
    n = box(size=size, center=center, color=color)
    a.include(name, n)
    return n

ivory = (.82,.81,.75)
white = (.87,.87,.84)
wood = (.25,.105,.036)
darkwood = (.105,.040,.015)
black = (.008,.009,.009)
room = asset("Room shell")
B(room,"Floor foundation",(8,10,.12),(-1,0,-.07),(.49,.46,.39))
B(room,"Back plaster",(6,.15,3.1),(-1.35,4.23,1.55),(.66,.61,.52))
B(room,"Right plaster",(.12,9,3.1),(1.65,.15,1.55),ivory)
B(room,"Ceiling",(8,10,.12),(-1,.1,3.08),(.85,.84,.79))

slats = asset("Oak batten feature wall")
B(slats,"Dark backing",(4.25,.035,2.69),(-1.8,4.125,1.345),(.063,.043,.028))
for i in range(59):
    x = -3.87 + i*.071
    B(slats,"Vertical oak batten %02d"%i,(.044,.058,2.69),
      (x,4.077,1.345),(.34,.16,.064))

door = asset("White back door")
# Door opening masks battens and backing at the right side.
B(door,"Outer frame",(.85,.095,2.15),(-.36,4.005,1.075),(.88,.87,.82))
B(door,"Door shadow reveal",(.744,.035,2.044),(-.36,3.946,1.027),(.45,.44,.40))
B(door,"Door leaf",(.713,.043,2.015),(-.36,3.922,1.025),(.80,.81,.78))
B(door,"Left jamb",(.035,.08,2.13),(-.77,3.94,1.065),white)
B(door,"Right jamb",(.035,.08,2.13),(.05,3.94,1.065),white)
B(door,"Top jamb",(.855,.08,.045),(-.36,3.94,2.115),white)
door.include("Handle rose",rod(radius=.025,length=.018,center=(-.62,3.887,1.04),axis='+y',color=(.48,.49,.46)))
B(door,"Lever",(.13,.027,.018),(-.58,3.867,1.049),(.52,.53,.50))
door.include("Key escutcheon",rod(radius=.013,length=.012,center=(-.62,3.887,.945),axis='+y',color=(.37,.38,.35)))
for z in [.25,1.75]:
    B(door,"Hinge %.2f"%z,(.015,.025,.065),(-.012,3.887,z),(.49,.48,.43))
fixtures = asset("Wall switches")
for name,x,z,w,h in [("Switch",-.99,1.08,.09,.09),("Low socket",-.96,.29,.075,.09)]:
    B(fixtures,name,(w,.025,h),(x,4.025,z),(.86,.86,.81))
    B(fixtures,name+" insert",(w*.55,.012,h*.55),(x,4.005,z),(.72,.73,.69))

bench = asset("Low black bench")
B(bench,"Black carcass",(1.39,.43,.47),(-2.27,3.83,.235),(.018,.022,.021))
B(bench,"White inset front",(1.24,.025,.29),(-2.30,3.598,.206),(.80,.82,.80))
B(bench,"Top slab",(1.42,.47,.045),(-2.27,3.81,.49),(.012,.016,.015))
B(bench,"Bottom trim",(1.35,.025,.035),(-2.27,3.59,.045),(.055,.061,.056))

kitchen = asset("Kitchen lower cabinets")
# Counter axis runs from the near crop to the far end at y=3.52.
B(kitchen,"Base cabinet body",(.69,5.6,.85),(1.235,.72,.445),(.25,.15,.078))
B(kitchen,"Recessed plinth",(.58,5.5,.10),(1.28,.72,.05),(.075,.055,.035))
for j in range(7):
    yy=-1.67+j*.8
    B(kitchen,"Walnut lower door %02d"%j,(.027,.785,.73),(.879,yy,.475),wood)

counter = asset("Stone countertop")
B(counter,"Counter slab",(.82,5.7,.045),(1.18,.72,.902),(.71,.68,.57))
# Sink is an inset dark bowl with a narrow metal rim, opening retained visibly.
sink = asset("Inset sink and draining board")
sx,sy=.995,2.57
B(sink,"Dark sink inset",(.64,.67,.012),(sx,sy,.932),(.045,.035,.020))
B(sink,"Bowl interior bottom",(.40,.40,.013),(.92,sy-.03,.939),(.014,.015,.012))
for name,size,loc in [
    ("Left bronze rim",(.016,.65,.012),(.682,sy,.947)),
    ("Right bronze rim",(.016,.65,.012),(1.307,sy,.947)),
    ("Far bronze rim",(.64,.016,.012),(sx,sy+.32,.947)),
    ("Near bronze rim",(.64,.016,.012),(sx,sy-.32,.947))]:
    B(sink,name,size,loc,(.27,.20,.09))
B(sink,"Drain board",(.145,.58,.008),(1.215,sy,.949),(.12,.10,.057))
for j in range(7):
    B(sink,"Drain groove %02d"%j,(.115,.009,.006),(1.215,sy-.24+j*.077,.955),(.33,.26,.13))

hob = asset("Black glass cooktop")
B(hob,"Glass plate",(.71,1.02,.014),(1.115,.66,.935),(.008,.012,.012))
# Thin rings remain separate semantic parts, with subdued gray ceramic markings.
for i,(xx,yy,rr) in enumerate([(.94,.91,.155),(1.30,.91,.115),(.94,.40,.12),(1.30,.37,.17)]):
    pts=[(xx+rr*math.cos(t*2*math.pi/40), yy+rr*math.sin(t*2*math.pi/40),.945) for t in range(41)]
    # Blender curve is used only for a surface marking; primary geometry is SceneAct.
    # Added after realization below.
    pass

upper = asset("Walnut wall cupboards")
B(upper,"Cabinet body",(.49,5.75,1.0),(1.375,.73,2.55),darkwood)
for j in range(8):
    yy=-1.78+j*.73
    B(upper,"Tall walnut face %02d"%j,(.028,.718,.98),(1.117,yy,2.55),(.19,.077,.027))
    B(upper,"Lower edge %02d"%j,(.032,.718,.025),(1.105,yy,2.065),(.065,.029,.011))
B(upper,"Far end panel",(.51,.045,1.01),(1.365,3.59,2.55),(.15,.060,.023))
backsplash = asset("Glossy pale backsplash")
B(backsplash,"Glass wall panel",(.018,5.8,1.14),(1.576,.70,1.49),(.78,.78,.72))
extractor = asset("Integrated extractor")
B(extractor,"Stainless underside",(.44,1.00,.028),(1.345,.47,2.037),(.50,.51,.46))
B(extractor,"Filter inset",(.29,.60,.009),(1.325,.47,2.019),(.29,.30,.27))
for j in range(8):
    B(extractor,"Filter slit %02d"%j,(.255,.012,.003),(1.325,.23+j*.065,2.012),(.13,.14,.12))
B(upper,"Under cupboard light strip",(.024,5.6,.013),(1.53,.72,2.015),(.98,.85,.54))

scene.settle()
realize(scene)

# Restrained procedural wood, limestone floor, and marble replace unresolved fine detail.
def mat_principled(obj):
    m=obj.active_material
    if m is None:
        m=bpy.data.materials.new(obj.name+" material")
        obj.data.materials.append(m)
    m.use_nodes=True
    return m,m.node_tree.nodes.get("Principled BSDF")

for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    m,bs=mat_principled(obj)
    name=obj.name.lower()
    bs.inputs['Roughness'].default_value=.44
    if "glass plate" in name:
        bs.inputs['Roughness'].default_value=.10
        bs.inputs['Metallic'].default_value=.25
    if "glass wall" in name:
        bs.inputs['Roughness'].default_value=.13
    if "rim" in name or "stainless" in name or "lever" in name:
        bs.inputs['Metallic'].default_value=.78
        bs.inputs['Roughness'].default_value=.24
    if "walnut" in name or "oak batten" in name:
        nt=m.node_tree
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=4
        tex.inputs["Detail"].default_value=2
        coord=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(12,12,.6)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        base=bs.inputs['Base Color'].default_value[:]
        ramp.color_ramp.elements[0].position=.2
        ramp.color_ramp.elements[0].color=(base[0]*.55,base[1]*.55,base[2]*.55,1)
        ramp.color_ramp.elements[1].position=.8
        ramp.color_ramp.elements[1].color=(base[0]*1.35,base[1]*1.35,base[2]*1.35,1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
    if "counter slab" in name:
        nt=m.node_tree
        coord=nt.nodes.new("ShaderNodeTexCoord")
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs['Scale'].default_value=5.5
        noise.inputs['Detail'].default_value=3
        nt.links.new(coord.outputs['Generated'],noise.inputs['Vector'])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.42
        ramp.color_ramp.elements[0].color=(.28,.25,.19,1)
        ramp.color_ramp.elements[1].position=.51
        ramp.color_ramp.elements[1].color=(.75,.72,.64,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])

# Floor joints: simple flush curves make long rectangular warm gray tiles.
line_mat=bpy.data.materials.new("Fine grout")
line_mat.diffuse_color=(.32,.30,.26,1)
def line(name,pts,radius,material):
    cu=bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'
    cu.bevel_depth=radius
    cu.bevel_resolution=1
    sp=cu.splines.new('POLY')
    sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):
        p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob
for j in range(12):
    y=-3+j*.65
    line("Tile cross joint",[(-4,y,.001),(1.6,y,.001)],.002,line_mat)
    for i in range(5):
        x=-4+i*1.24+(j%2)*.62
        line("Staggered tile joint",[(x,y,.001),(x,y+.65,.001)],.002,line_mat)

ringmat=bpy.data.materials.new("Subtle hob ring gray")
ringmat.diffuse_color=(.10,.105,.09,1)
for i,(xx,yy,rr) in enumerate([(.94,.91,.155),(1.30,.91,.115),(.94,.40,.12),(1.30,.37,.17)]):
    pts=[(xx+rr*math.cos(t*2*math.pi/56),yy+rr*math.sin(t*2*math.pi/56),.945) for t in range(57)]
    line("Ceramic burner %d"%i,pts,.0015,ringmat)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.76,.79,.83,1)
background.inputs['Strength'].default_value=.32

# Camera: near-level view down the counter, full-height door in the middle distance.
set_view(position=(-.12,-1.85,1.66),target=(-.18,4.05,1.61),lens=28,sensor=36)
area_emitter(position=(-2.8,-.3,2.65),power=530,size=4.0,target=(.1,2.5,1.0),color=(1,.92,.80))
area_emitter(position=(-1.8,3.0,2.9),power=140,size=2.5,target=(-1.5,4,1.2),color=(1,.91,.76))
area_emitter(position=(1.43,1.3,1.99),power=65,size=2.5,target=(1.53,1.4,1.25),color=(1,.73,.39))
sc.view_settings.view_transform='AgX'
