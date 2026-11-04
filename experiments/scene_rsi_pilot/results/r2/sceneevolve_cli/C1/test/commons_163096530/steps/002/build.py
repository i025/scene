from sceneact import *
import bpy, math, random

# The left bunks need larger silhouettes and must sit farther right.
# The foreground right bunk must retreat to the extreme right border.
# Floorboards and ironwork need substantially darker, richer materials.
random.seed(9)
scene = Scene('Historic dormitory')
WOOD=(.25,.125,.043)
BEAM=(.105,.070,.029)
METAL=(.045,.060,.061)
WALL=(.69,.70,.45)
WHITE=(.87,.88,.82)

def add(parent,key,size,center,color):
    parent.include(key,box(size=size,center=center,color=color))

room=Asset('Room architecture')
add(room,'back plaster',(7,.16,3.5),(0,4.85,1.75),WALL)
add(room,'left plaster',(.16,10,3.5),(-3.5,0,1.75),(.72,.70,.53))
add(room,'ceiling',(7,10,.14),(0,0,3.55),(.56,.59,.36))
for i in range(25):
    x=-3.5+(i+.5)*.28
    v=random.uniform(-.025,.025)
    add(room,'floorboard%d'%i,(.275,10,.075),(x,0,-.0375),
        (.185+v,.105+v*.65,.043+v*.35))
add(room,'rear skirting',(7,.07,.13),(0,4.72,.065),(.18,.125,.055))
for i,y in enumerate([-4,-1.8,.4,2.55,4.65]):
    add(room,'wall upright%d'%i,(.15,.15,3.5),(-3.37,y,1.75),BEAM)
for i,z in enumerate([1.12,2.44,3.42]):
    add(room,'wall horizontal%d'%i,(.15,9.8,.14),(-3.37,0,z),BEAM)
for i,y in enumerate([-1.5,3.15]):
    add(room,'ceiling beam%d'%i,(7,.20,.23),(0,y,3.38),BEAM)
scene.include('architecture',room)

def bunk(name,x,y,width=1.15,length=2.22):
    a=Asset(name)
    for i,xx in enumerate([x-width/2,x+width/2]):
        for j,yy in enumerate([y-length/2,y+length/2]):
            a.include('post%d%d'%(i,j),rod(.028,start=(xx,yy,.055),
                end=(xx,yy,2.43),color=METAL))
            a.include('cap%d%d'%(i,j),ball(.034,center=(xx,yy,2.43),color=METAL))
            add(a,'foot%d%d'%(i,j),(.10,.10,.025),(xx,yy,.025),(.18,.20,.18))
    for k,z in enumerate([.48,1.71]):
        add(a,'bed base%d'%k,(width,length,.075),(x,y,z),METAL)
        a.include('mattress%d'%k,fillet_box(
            size=(width-.045,length-.045,.145),radius=.055,
            center=(x,y,z+.11),color=WHITE))
        add(a,'sheet%d'%k,(width-.025,length-.065,.040),
            (x,y,z+.195),(.94,.94,.90))
        add(a,'blanket%d'%k,(width-.01,length*.51,.035),
            (x,y-.41,z+.226),(.77,.81,.82))
        a.include('pillow%d'%k,fillet_box(size=(width*.76,.43,.14),
            radius=.06,center=(x,y+length/2-.31,z+.25),color=(.96,.96,.92)))
        for j,xx in enumerate([x-width/2,x+width/2]):
            a.include('side frame%d%d'%(k,j),rod(.022,
                start=(xx,y-length/2,z+.04),
                end=(xx,y+length/2,z+.04),color=METAL))
        for end,yy in enumerate([y-length/2,y+length/2]):
            heights=[z+.30,z+.45,z+.59] if k else [z+.31,z+.48]
            for r,zz in enumerate(heights):
                a.include('end rail%d%d%d'%(k,end,r),rod(.021,
                    start=(x-width/2,yy,zz),end=(x+width/2,yy,zz),color=METAL))
    for j,xx in enumerate([x-width/2,x+width/2]):
        for k,z in enumerate([2.08,2.27]):
            a.include('guard%d%d'%(j,k),rod(.019,
                start=(xx,y-length/2,z),end=(xx,y+length/2,z),color=METAL))
    xx=x+width/2+.025
    for j,yy in enumerate([y-.49,y-.03]):
        a.include('ladder side%d'%j,rod(.025,start=(xx,yy,.09),
            end=(xx,yy,1.88),color=(.15,.18,.18)))
    for k in range(6):
        z=.30+k*.28
        a.include('ladder rung%d'%k,rod(.021,start=(xx,y-.49,z),
            end=(xx,y-.03,z),color=(.21,.24,.24)))
    return a

scene.include('near left bunk',bunk('Near left bunk',-2.20,.10))
scene.include('rear left bunk',bunk('Rear left bunk',-2.20,2.65))

cab=Asset('Wooden wardrobe')
cx=-.45
cy=4.39
add(cab,'dark interior',(.98,.16,1.92),(cx,4.68,1.06),(.065,.032,.010))
for i,x in enumerate([cx-.54,cx+.54]):
    add(cab,'outer side%d'%i,(.095,.58,1.99),(x,cy,1.09),WOOD)
add(cab,'center stile',(.065,.57,1.93),(cx+.025,cy,1.08),(.30,.155,.048))
add(cab,'base',(1.18,.65,.13),(cx,cy,.17),(.28,.135,.037))
add(cab,'crown',(1.23,.68,.10),(cx,cy,2.13),(.34,.19,.065))
add(cab,'crown lip',(1.28,.72,.045),(cx,cy,2.19),(.27,.14,.037))
for i,x in enumerate([cx-.44,cx+.44]):
    for j,y in enumerate([4.15,4.61]):
        add(cab,'foot%d%d'%(i,j),(.13,.13,.17),(x,y,.09),WOOD)
add(cab,'left door',(.47,.065,1.84),(cx-.275,4.065,1.10),(.35,.18,.052))
for i,z in enumerate([.65,1.57]):
    add(cab,'door panel%d'%i,(.355,.025,.70),(cx-.275,4.018,z),(.29,.135,.031))
cab.include('handle',rod(.018,start=(cx-.09,4.005,.98),
    end=(cx-.09,4.005,1.12),color=(.12,.085,.025)))
add(cab,'open shelf',(.46,.55,.055),(cx+.29,cy,.91),(.34,.18,.06))
cab.include('hanging rail',rod(.018,start=(cx+.08,cy,1.97),
    end=(cx+.49,cy,1.97),color=(.12,.11,.07)))
for i in range(4):
    x=cx+.13+i*.085
    cab.include('hanger%d'%i,sweep_tube(points=[
        (x,cy,1.95),(x-.045,cy,1.84),(x+.045,cy,1.84),(x,cy,1.95)],
        radius=.008,color=(.20,.14,.06)))
scene.include('wardrobe',cab)

fire=Asset('Stone fireplace')
fx=1.35
add(fire,'sooty recess',(1.53,.035,1.42),(fx,4.746,.74),(.043,.035,.024))
add(fire,'hearth',(2.02,.92,.07),(fx,4.34,.035),(.23,.22,.17))
for j in range(5):
    for i in range(5):
        x=fx-.64+i*.29+(j%2)*.08
        v=random.random()*.045
        add(fire,'inner masonry%d_%d'%(j,i),(.273,.05,.215),
            (x,4.70,.17+j*.235),(.12+v,.105+v,.070+v*.7))
for side in [-1,1]:
    x=fx+side*.91
    for j in range(3):
        add(fire,'jamb%d_%d'%(side,j),(.26,.33,.42),
            (x,4.58,.23+j*.42),(.40+j*.012,.40+j*.008,.32+j*.006))
# Slightly sloping stone shoulder pieces soften the opening's top corners.
add(fire,'broad stone lintel',(2.10,.35,.30),(fx,4.58,1.46),(.45,.45,.36))
add(fire,'inner top',(1.38,.16,.12),(fx,4.45,1.28),(.34,.34,.27))
for side in [-1,1]:
    add(fire,'inner edge%d'%side,(.085,.15,1.10),
        (fx+side*.76,4.45,.63),(.33,.33,.26))
    shoulder=box((.26,.16,.12),center=(fx+side*.68,4.45,1.23),
        color=(.37,.37,.29))
    shoulder.turn('y',side*24)
    fire.include('shoulder%d'%side,shoulder)
scene.include('fireplace',fire)

rad=Asset('Small fireplace heater')
for i in range(8):
    rad.include('fin%d'%i,rod(.017,
        start=(fx+.38+i*.037,4.20,.10),
        end=(fx+.32+i*.037,4.34,.66),color=(.64,.66,.61)))
for z,y in [(.11,4.20),(.65,4.34)]:
    rad.include('header%.2f'%z,rod(.025,start=(fx+.31,y,z),
        end=(fx+.64,y,z),color=(.63,.65,.60)))
scene.include('heater',rad)
scene.include('coal bucket',rod(.09,length=.25,
    center=(fx+1.05,4.13,.14),color=(.055,.065,.058)))

clock=Asset('Wall clock')
clock.include('rim',rod(.115,start=(-.20,4.735,2.64),
    end=(-.20,4.69,2.64),color=(.42,.48,.40)))
clock.include('face',rod(.096,start=(-.20,4.68,2.64),
    end=(-.20,4.67,2.64),color=(.64,.68,.58)))
clock.include('hand1',rod(.005,start=(-.20,4.655,2.64),
    end=(-.20,4.655,2.70),color=(.23,.28,.23)))
clock.include('hand2',rod(.005,start=(-.20,4.653,2.64),
    end=(-.16,4.653,2.62),color=(.23,.28,.23)))
scene.include('clock',clock)

scene.include('right foreground bunk',bunk('Cropped right bunk',2.40,-1.20))
add(scene,'foreground wooden upright',(.13,.14,3.1),
    (1.70,-1.93,1.55),(.39,.18,.040))

realize(scene)
CAMERA_POSITION=(1.20,-5.95,1.67)
CAMERA_TARGET=(-1.19,2.55,1.49)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=36,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.69,.57,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
area_emitter((-2.8,-2.8,2.8),power=700,size=3.1,
    target=(-.5,2,.9),color=(1,.96,.83))
area_emitter((1,-.5,3.15),power=100,size=3.5,
    target=(0,3,1),color=(.89,.92,1))

for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.76
    col=bs.inputs['Base Color'].default_value
    if col[0]<.25 and abs(col[0]-col[1])<.045 and col[2]>.035:
        bs.inputs['Metallic'].default_value=.55
        bs.inputs['Roughness'].default_value=.36
    if col[0]<.40 and col[1]<.29 and col[0]>col[2]*1.6:
        coord=nodes.new('ShaderNodeTexCoord')
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(7,.30,3)
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=3
        mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(col[0]*.52,col[1]*.48,col[2]*.45,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(col[0]*1.18,col[1]*1.13,col[2]*1.08,1)
        mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0])
        mat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.24
        bump.inputs['Distance'].default_value=.025
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
