from sceneact import *
import bpy, math, random

scene = Scene('Kitchen corner')
cream=(.77,.72,.59)
cabinet=(.83,.79,.67)
trim=(.88,.84,.72)
steel=(.47,.48,.43)

def add(name,node):
    scene.include(name,node)
    return node

add('back wall',box((3,.10,3.3),center=(0,.63,1.65),color=cream))
add('counter',box((2.5,1.22,.075),center=(0,-.015,.825),color=(.32,.30,.24)))
add('backsplash',box((2.5,.045,.16),center=(0,.545,.92),color=(.33,.31,.25)))
add('cabinet case',box((1.12,.48,1.48),center=(.43,.31,2.265),color=cabinet))
for i,(x,w) in enumerate(((.215,.65),(.795,.45))):
    add('door panel '+str(i),box((w,.034,1.40),center=(x,.043,2.27),color=(.79,.75,.63)))
    for k,xx in enumerate((x-w/2+.028,x+w/2-.028)):
        add('door stile %s %s'%(i,k),box((.055,.035,1.40),center=(xx,.012,2.27),color=trim))
    for k,zz in enumerate((1.595,2.945)):
        add('door rail %s %s'%(i,k),box((w,.035,.055),center=(x,.012,zz),color=trim))
    add('inner recessed panel '+str(i),box((w-.16,.012,1.20),center=(x,.019,2.27),color=(.815,.773,.65)))
add('cabinet bottom lip',box((1.14,.5,.045),center=(.43,.30,1.515),color=trim))
add('right door knob stem',rod(.009,start=(.67,-.005,1.76),end=(.67,-.045,1.76),color=steel))
add('right door knob',ball(.017,center=(.67,-.053,1.76),color=(.40,.36,.25)))

add('window recess',box((.97,.06,2.30),center=(-.675,.565,1.80),color=(.60,.74,.75)))
add('window daylight',box((.86,.015,2.17),center=(-.675,.524,1.80),color=(.73,.87,.91)))
for x in (-1.15,-.20):
    add('window vertical frame '+str(x),box((.055,.11,2.38),center=(x,.49,1.80),color=(.91,.90,.80)))
for z in (.64,1.57,2.96):
    add('window cross frame '+str(z),box((.98,.10,.05),center=(-.675,.48,z),color=(.89,.88,.78)))
add('window middle vertical',box((.033,.055,2.28),center=(-.70,.475,1.80),color=(.86,.87,.80)))
for j in range(39):
    slat=box((.96,.065,.016),center=(-.675,.402,.72+j*.058),color=(.86,.86,.77))
    slat.turn('x',-13)
    add('blind slat '+str(j),slat)
for x in (-1.02,-.39):
    add('blind cord '+str(x),rod(.003,start=(x,.355,.70),end=(x,.355,2.99),color=(.77,.76,.66)))
    add('blind ladder '+str(x),box((.012,.006,2.26),center=(x,.353,1.83),color=(.80,.79,.70)))
add('blind pull cord',rod(.002,start=(-.34,.30,2.77),end=(-.34,.30,1.85),color=(.72,.70,.58)))
add('blind pull',rod(.009,length=.046,center=(-.34,.30,1.83),color=(.86,.82,.65)))

add('paper holder upper mount',ball(.034,center=(.39,-.045,2.45),color=(.38,.36,.28)))
add('paper holder spindle',rod(.015,start=(.39,-.10,1.84),end=(.39,-.10,2.47),color=steel))
add('paper towel roll',rod(.142,length=.59,center=(.39,-.142,2.145),color=(.93,.90,.79)))
add('paper towel loose edge',box((.026,.014,.575),center=(.52,-.21,2.14),color=(.92,.89,.78)))
for x in (.30,.48):
    add('holder lower bracket '+str(x),ball(.025,center=(x,-.08,1.835),color=(.28,.27,.22)))

add('towel ring wall plate',rod(.046,start=(-.145,.19,1.85),end=(-.181,.19,1.85),color=(.49,.46,.35)))
add('towel ring mounting neck',rod(.013,start=(-.18,.19,1.85),end=(-.265,.065,1.85),color=steel))
ringpts=[(-.275+.100*math.cos(2*math.pi*i/100),.045,1.69+.155*math.sin(2*math.pi*i/100)) for i in range(101)]
add('polished towel ring',sweep_tube(points=ringpts,radius=.006,color=(.58,.59,.53)))

# Thin sink components use bevels smaller than half their thickness.
add('sink outer steel rim',fillet_box((.65,.53,.025),radius=.011,center=(-.70,-.39,.868),color=(.34,.35,.31)))
add('sink black basin',fillet_box((.56,.44,.035),radius=.015,center=(-.70,-.40,.879),color=(.025,.034,.025)))
add('sink interior',fillet_box((.47,.35,.02),radius=.009,center=(-.70,-.41,.883),color=(.045,.053,.040)))
add('faucet foot',rod(.043,length=.026,center=(-.66,-.035,.888),color=steel))
faucetpoints=[(-.66,-.035,.90),(-.66,-.035,1.04),(-.66,-.035,1.16),(-.66,-.055,1.19),(-.66,-.11,1.18),(-.66,-.15,1.14)]
add('faucet neck',sweep_tube(points=faucetpoints,radius=.012,color=(.58,.59,.52)))
add('left faucet handle',rod(.014,start=(-.77,-.035,.89),end=(-.82,-.065,.94),color=steel))
add('right faucet handle',rod(.013,start=(-.55,-.035,.89),end=(-.50,-.065,.93),color=steel))
add('small drain cup',rod(.052,length=.029,center=(-.40,-.13,.885),color=(.23,.24,.19)))
add('small drain center',rod(.038,length=.032,center=(-.40,-.13,.888),color=(.09,.10,.075)))

add('blender base',fillet_box((.18,.19,.19),radius=.045,center=(.025,.19,.975),color=(.035,.041,.035)))
add('blender collar',rod(.067,length=.032,center=(.025,.19,1.085),color=(.07,.075,.065)))
add('blender control',ball(.013,center=(.025,.089,.99),color=(.35,.38,.32)))
add('green canister',rod(.061,length=.235,center=(-.20,.18,.99),color=(.31,.35,.16)))
add('canister lid',rod(.064,length=.012,center=(-.20,.18,1.113),color=(.53,.52,.35)))
add('canister silver stripe',box((.022,.008,.18),center=(-.20,.117,.985),color=(.65,.66,.52)))
add('small spice tube',rod(.022,length=.19,center=(-.14,-.012,.965),color=(.62,.60,.42)))
add('spice tube lid',rod(.023,length=.024,center=(-.14,-.012,1.069),color=(.77,.77,.66)))

pitcher=ball(1,center=(.66,.13,1.055),color=(.035,.075,.14))
pitcher.resize((.177,.133,.225))
add('blue water filter pitcher',pitcher)
add('pitcher bottom',fillet_box((.25,.21,.035),radius=.015,center=(.66,.13,.865),color=(.055,.09,.12)))
lid=ball(1,center=(.66,.13,1.256),color=(.38,.39,.35))
lid.resize((.18,.138,.037))
lid.turn('y',-12)
add('pitcher sloped lid',lid)
add('pitcher pouring spout',box((.07,.08,.038),center=(.51,.11,1.272),color=(.36,.37,.32)))
handlepoints=[(.79,.13,1.24),(.87,.13,1.21),(.91,.13,1.13),(.92,.13,1.03),(.88,.13,.94),(.80,.13,.91)]
add('pitcher clear handle',sweep_tube(points=handlepoints,radius=.021,color=(.42,.45,.43)))

bottle=Asset('Filtered water bottle')
bottle.include('body',fillet_box((.267,.205,.272),radius=.058,center=(.30,-.205,.994),color=(.67,.69,.62)))
shoulder=ball(1,center=(.30,-.205,1.117),color=(.69,.71,.64))
shoulder.resize((.130,.101,.139))
bottle.include('shoulders',shoulder)
bottle.include('neck',rod(.041,length=.063,center=(.30,-.205,1.237),color=(.75,.76,.67)))
bottle.include('cap',rod(.043,length=.027,center=(.30,-.205,1.271),color=(.82,.82,.72)))
add('gallon jug',bottle)
add('jug molded handle',sweep_tube(points=[(.39,-.255,1.20),(.42,-.27,1.17),(.43,-.28,1.10),(.40,-.29,1.06)],radius=.015,color=(.72,.74,.66)))

realize(scene)

def material(name,color,roughness=.5,metallic=0,transmission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    if 'Transmission Weight' in p.inputs:
        p.inputs['Transmission Weight'].default_value=transmission
    return m

granite=material('warm mottled fine granite',(.32,.30,.25),.78)
nt=granite.node_tree
p=nt.nodes.get('Principled BSDF')
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=190
noise.inputs['Detail'].default_value=3.3
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.24
ramp.color_ramp.elements[0].color=(.065,.064,.047,1)
ramp.color_ramp.elements[1].position=.77
ramp.color_ramp.elements[1].color=(.64,.59,.45,1)
e=ramp.color_ramp.elements.new(.48)
e.color=(.27,.265,.21,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.23
bump.inputs['Distance'].default_value=.008
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])

metal=material('aged brushed nickel',(.49,.49,.42),.26,.78)
paper=material('soft ivory paper',(.91,.875,.76),.88)
clothmat=material('cream terrycloth',(.84,.81,.71),.98)
for mat,scale,strength in ((paper,150,.10),(clothmat,230,.30)):
    nodes=mat.node_tree.nodes
    n=nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value=scale
    n.inputs['Detail'].default_value=2
    b=nodes.new('ShaderNodeBump')
    b.inputs['Strength'].default_value=strength
    b.inputs['Distance'].default_value=.004
    mat.node_tree.links.new(n.outputs['Fac'],b.inputs['Height'])
    mat.node_tree.links.new(b.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])

for ob in bpy.data.objects:
    if ob.type!='MESH':
        continue
    name=ob.name.lower()
    if 'counter' in name or 'backsplash' in name:
        ob.data.materials.clear()
        ob.data.materials.append(granite)
    if any(k in name for k in ('faucet','polished towel','mounting neck','wall plate','holder upper')):
        ob.data.materials.clear()
        ob.data.materials.append(metal)
    if 'paper towel roll' in name or 'paper towel loose' in name:
        ob.data.materials.clear()
        ob.data.materials.append(paper)
    if any(k in name for k in ('pitcher','bottle','shoulders','neck','cap')):
        for poly in ob.data.polygons:
            poly.use_smooth=True

# Soft hanging fabric, with folds and an uneven lower edge.
verts=[]
faces=[]
nu,nv=36,52
for j in range(nv+1):
    v=j/nv
    for i in range(nu+1):
        u=i/nu
        width=.215*(.74+.26*v)
        x=-.278+(u-.5)*width+.014*math.sin(v*4.4)
        z=1.567-.565*v+.018*math.cos(u*8+1)*v**7
        y=-.035-.050*math.sin(math.pi*v/2)+.019*math.sin(u*math.pi*7+.8*v)*(.4+.6*v)
        z+=.026*math.sin(math.pi*u)*(1-v)**8
        verts.append((x,y,z))
for j in range(nv):
    for i in range(nu):
        a=j*(nu+1)+i
        faces.append((a,a+1,a+nu+2,a+nu+1))
mesh=bpy.data.meshes.new('terry towel drape mesh')
mesh.from_pydata(verts,[],faces)
mesh.update()
towel=bpy.data.objects.new('long ivory hand towel',mesh)
bpy.context.collection.objects.link(towel)
towel.data.materials.append(clothmat)
towel.modifiers.new('cloth thickness','SOLIDIFY').thickness=.004
towel.modifiers.new('soft folds','SUBSURF').levels=1
for p in mesh.polygons:
    p.use_smooth=True

verts=[]
faces=[]
for j in range(25):
    v=j/24
    for i in range(19):
        u=i/18
        verts.append((-.235+(u-.5)*.18+.053*v,
                      .007+.022*math.sin(u*14)+.02*v,
                      1.56-.33*v+.018*math.cos(u*7)*v))
for j in range(24):
    for i in range(18):
        a=j*19+i
        faces.append((a,a+1,a+20,a+19))
me=bpy.data.meshes.new('towel back fold mesh')
me.from_pydata(verts,[],faces)
me.update()
ob=bpy.data.objects.new('folded towel back',me)
bpy.context.collection.objects.link(ob)
ob.data.materials.append(clothmat)
ob.modifiers.new('thickness','SOLIDIFY').thickness=.003
for p in me.polygons:
    p.use_smooth=True

glass=material('clear blender plastic',(.64,.69,.63),.16,0,.72)
def ring_mesh(name,levels,center,mat,lean=0):
    vs=[]
    fs=[]
    count=64
    for z,r in levels:
        for k in range(count):
            t=2*math.pi*k/count
            vs.append((center[0]+r*math.cos(t)+lean*(z-levels[0][0]),
                       center[1]+r*math.sin(t),z))
    for j in range(len(levels)-1):
        for k in range(count):
            a=j*count+k
            b=j*count+(k+1)%count
            fs.append((a,b,b+count,a+count))
    me=bpy.data.meshes.new(name)
    me.from_pydata(vs,[],fs)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for f in me.polygons:
        f.use_smooth=True
    return ob

ring_mesh('clear tall blender cup',[(1.085,.045),(1.12,.049),(1.35,.043),(1.355,.039),(1.12,.043)],(.025,.19),glass,-.23)
rim=material('cup rim highlight',(.59,.62,.55),.2,.35)
ring_mesh('blender cup rim',[(1.347,.044),(1.358,.044),(1.358,.039),(1.347,.039)],(.025-.23*.262,.19),rim)
for off in (-.025,.025):
    cu=bpy.data.curves.new('cup vertical seam','CURVE')
    cu.dimensions='3D'
    cu.bevel_depth=.0017
    spl=cu.splines.new('POLY')
    spl.points.add(1)
    spl.points[0].co=(.025+off,.145,1.10,1)
    spl.points[1].co=(.025+off-.052,.15,1.34,1)
    ob=bpy.data.objects.new('cup molded ridge',cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(rim)

ink=material('faded gray marker',(.28,.30,.27),.9)
text=bpy.data.curves.new('FILTER handwriting','FONT')
text.body='FILTER'
text.align_x='CENTER'
text.size=.034
text.space_character=1.13
text.extrude=.0001
label=bpy.data.objects.new('FILTER label',text)
bpy.context.collection.objects.link(label)
label.location=(.30,-.312,.952)
label.rotation_euler=(math.pi/2,0,0)
label.data.materials.append(ink)

random.seed(12)
for i in range(20):
    z=1.88+random.random()*.52
    a=-math.pi/2+random.uniform(-.65,.65)
    x=.39+.1425*math.cos(a)
    y=-.142+.1425*math.sin(a)
    cu=bpy.data.curves.new('paper embossed curl','CURVE')
    cu.dimensions='3D'
    cu.bevel_depth=.00065
    sp=cu.splines.new('POLY')
    sp.points.add(9)
    for k in range(10):
        t=k/9*math.pi*1.5
        sp.points[k].co=(x+.009*math.cos(t),y-.0007,z+.005*math.sin(t),1)
    ob=bpy.data.objects.new('subtle paper emboss',cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(paper)

set_view(position=(-1.43,-2.92,2.10),target=(-.13,.12,1.66),lens=65)
area_emitter(position=(-1.35,-.05,2.35),power=230,size=1.8,target=(.3,.1,1.35),color=(.82,.90,1))
area_emitter(position=(-.2,-2.0,2.75),power=105,size=2.6,target=(.25,.15,1.4),color=(1,.86,.66))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.53,.44,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.34
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.cycles.use_denoising=True
bpy.context.scene.render.resolution_x=384
bpy.context.scene.render.resolution_y=512
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
