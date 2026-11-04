from sceneact import *
import bpy, math, random

# Reference anchors: nearest bunk bounds approximately (.02,.28)-(.41,.90).
# Second bunk occupies (.38,.33)-(.53,.78).
# Wardrobe bounds (.54,.34)-(.67,.68).
# Fireplace bounds (.68,.39)-(.90,.70).
# Rear floor junction crosses approximately (.44,.65)-(.91,.71).
# A cropped bunk post and ladder occlude the extreme right edge.
random.seed(9)
scene = Scene('Historic dormitory')
WOOD = (.25,.14,.065)
BEAM = (.13,.095,.052)
METAL = (.115,.145,.145)
WALL = (.69,.69,.47)
STONE = (.43,.43,.34)
WHITE = (.87,.88,.82)

def add(parent, key, size, center, color):
    parent.include(key, box(size=size, center=center, color=color))

# Room shell, with individual wide floorboards.
room = Asset('Room architecture')
add(room, 'back plaster', (7,.16,3.5), (0,4.85,1.75), WALL)
add(room, 'left plaster', (.16,10,3.5), (-3.5,.0,1.75), (.72,.70,.52))
add(room, 'ceiling', (7,10,.14), (0,0,3.55), (.65,.66,.47))
for i in range(25):
    x = -3.5 + (i+.5)*.28
    col = (.29+random.uniform(-.035,.04), .205+random.uniform(-.025,.03), .115+random.uniform(-.018,.025))
    add(room, 'floorboard %02d'%i, (.274,10,.075), (x,0,-.0375), col)
add(room, 'rear skirting', (7,.07,.13), (0,4.72,.065), (.23,.19,.105))
# Exposed timber framing on the left wall.
for i,y in enumerate([-4.0,-1.8,.4,2.55,4.65]):
    add(room, 'wall upright %d'%i, (.15,.15,3.5), (-3.37,y,1.75), BEAM)
for i,z in enumerate([1.12,2.44,3.42]):
    add(room, 'wall horizontal %d'%i, (.15,9.8,.14), (-3.37,0,z), BEAM)
for i,y in enumerate([-1.5,3.15]):
    add(room, 'ceiling beam %d'%i, (7,.20,.23), (0,y,3.38), BEAM)
scene.include('architecture', room)

def bunk(name, x, y, width=1.15, length=2.22):
    a = Asset(name)
    # y is the bed center; front is towards the camera.
    for i,xx in enumerate([x-width/2,x+width/2]):
        for j,yy in enumerate([y-length/2,y+length/2]):
            a.include('post%d%d'%(i,j), rod(.028, start=(xx,yy,.055), end=(xx,yy,2.43), color=METAL))
            a.include('cap%d%d'%(i,j), ball(.034, center=(xx,yy,2.43), color=METAL))
            add(a,'foot%d%d'%(i,j),(.10,.10,.025),(xx,yy,.025),(.25,.27,.25))
    for k,z in enumerate([.48,1.71]):
        add(a, 'bed base%d'%k, (width,length,.085), (x,y,z), METAL)
        add(a, 'mattress%d'%k, (width-.045,length-.045,.145), (x,y,z+.11), WHITE)
        add(a, 'sheet%d'%k, (width-.025,length-.065,.045), (x,y,z+.195), (.93,.93,.87))
        # A pale blanket covers the foot of each mattress.
        add(a,'blanket%d'%k,(width-.01,length*.52,.045),(x,y-.41,z+.226),(.72,.78,.79))
        a.include('pillow%d'%k, fillet_box(size=(width*.76,.43,.14),radius=.06,
                      center=(x,y+length/2-.31,z+.25), color=(.94,.94,.89)))
        for j,xx in enumerate([x-width/2,x+width/2]):
            a.include('side frame%d%d'%(k,j),rod(.022,start=(xx,y-length/2,z+.04),end=(xx,y+length/2,z+.04),color=METAL))
        for end,yy in enumerate([y-length/2,y+length/2]):
            for r,zz in enumerate([z+.30,z+.45,z+.59] if k else [z+.31,z+.48]):
                a.include('end rail%d%d%d'%(k,end,r),rod(.021,start=(x-width/2,yy,zz),end=(x+width/2,yy,zz),color=METAL))
    # Upper safety rails run along both long edges.
    for j,xx in enumerate([x-width/2,x+width/2]):
        for k,z in enumerate([2.08,2.27]):
            a.include('guard%d%d'%(j,k),rod(.019,start=(xx,y-length/2,z),end=(xx,y+length/2,z),color=METAL))
    # Ladder on the exposed long side.
    xx=x+width/2+.025
    for j,yy in enumerate([y-.49,y-.03]):
        a.include('ladder side%d'%j,rod(.025,start=(xx,yy,.09),end=(xx,yy,1.88),color=(.29,.32,.31)))
    for k in range(6):
        z=.30+k*.28
        a.include('ladder rung%d'%k,rod(.021,start=(xx,y-.49,z),end=(xx,y-.03,z),color=(.33,.36,.35)))
    return a

scene.include('near left bunk', bunk('Near left bunk',-2.68,.10))
scene.include('rear left bunk', bunk('Rear left bunk',-2.68,2.65))

# Tall narrow antique wardrobe, one door open and an exposed hanging compartment.
cab = Asset('Wooden wardrobe')
cx=-.45
cy=4.39
add(cab,'dark interior',(.98,.16,1.92),(cx,4.68,1.06),(.105,.065,.027))
for i,x in enumerate([cx-.54,cx+.54]):
    add(cab,'outer side%d'%i,(.095,.58,1.99),(x,cy,1.09),WOOD)
add(cab,'center stile',(.065,.57,1.93),(cx+.025,cy,1.08),(.32,.19,.075))
add(cab,'base',(1.18,.65,.13),(cx,cy,.17),(.31,.18,.065))
add(cab,'crown',(1.23,.68,.10),(cx,cy,2.13),(.36,.23,.10))
add(cab,'crown lip',(1.28,.72,.045),(cx,cy,2.19),(.30,.19,.07))
for i,x in enumerate([cx-.44,cx+.44]):
    for j,y in enumerate([4.15,4.61]):
        add(cab,'foot%d%d'%(i,j),(.13,.13,.17),(x,y,.09),WOOD)
# Closed left door with inset raised panels.
add(cab,'left door',(.47,.065,1.84),(cx-.275,4.065,1.10),(.37,.23,.09))
for i,z in enumerate([.65,1.57]):
    add(cab,'door panel%d'%i,(.355,.025,.70),(cx-.275,4.018,z),(.32,.19,.069))
cab.include('handle',rod(.018,start=(cx-.09,4.005,.98),end=(cx-.09,4.005,1.12),color=(.13,.11,.055)))
add(cab,'open shelf',(.46,.55,.055),(cx+.29,cy,.91),(.37,.23,.10))
cab.include('hanging rail',rod(.018,start=(cx+.08,cy,1.97),end=(cx+.49,cy,1.97),color=(.18,.17,.13)))
for i in range(4):
    x=cx+.13+i*.085
    cab.include('hanger%d'%i,sweep_tube(points=[(x,cy,1.95),(x-.045,cy,1.84),(x+.045,cy,1.84),(x,cy,1.95)],radius=.008,color=(.24,.20,.11)))
scene.include('wardrobe',cab)

# Deep soot-black fireplace with stone lintel and square jambs.
fire = Asset('Stone fireplace')
fx=1.80
add(fire,'sooty recess',(1.53,.035,1.42),(fx,4.746,.74),(.075,.066,.048))
add(fire,'hearth',(2.02,.92,.07),(fx,4.34,.035),(.28,.28,.23))
for j in range(5):
    z=.17+j*.235
    for i in range(5):
        x=fx-.64+i*.29+(j%2)*.08
        col=(.20+random.random()*.08,.18+random.random()*.07,.13+random.random()*.05)
        add(fire,'inner masonry%d_%d'%(j,i),(.273,.05,.215),(x,4.70,z),col)
for side in [-1,1]:
    x=fx+side*.91
    for j in range(3):
        add(fire,'jamb%d_%d'%(side,j),(.26,.33,.42),(x,4.58,.23+j*.42),(.45+j*.012,.45+j*.008,.37+j*.006))
add(fire,'broad stone lintel',(2.10,.35,.30),(fx,4.58,1.46),(.49,.49,.40))
add(fire,'inner top',(1.56,.16,.13),(fx,4.45,1.28),(.39,.39,.32))
for side in [-1,1]:
    add(fire,'inner edge%d'%side,(.085,.15,1.16),(fx+side*.76,4.45,.66),(.38,.38,.31))
scene.include('fireplace',fire)

# Small pale metal radiator leaning in the hearth.
rad = Asset('Small fireplace heater')
for i in range(8):
    rad.include('fin%d'%i, rod(.017,start=(2.18+i*.037,4.20,.10),end=(2.12+i*.037,4.34,.66),color=(.64,.66,.61)))
for z,y in [(.11,4.20),(.65,4.34)]:
    rad.include('header%.2f'%z,rod(.025,start=(2.11,y,z),end=(2.44,y,z),color=(.63,.65,.60)))
scene.include('heater',rad)
scene.include('coal bucket',rod(.105,length=.27,center=(2.85,4.13,.15),color=(.10,.12,.11)))

# Simple round wall clock above the wardrobe.
clock=Asset('Wall clock')
clock.include('rim',rod(.115,start=(-.20,4.735,2.64),end=(-.20,4.69,2.64),color=(.47,.52,.45)))
clock.include('face',rod(.096,start=(-.20,4.68,2.64),end=(-.20,4.67,2.64),color=(.68,.70,.61)))
clock.include('hand1',rod(.005,start=(-.20,4.655,2.64),end=(-.20,4.655,2.70),color=(.28,.32,.28)))
clock.include('hand2',rod(.005,start=(-.20,4.653,2.64),end=(-.16,4.653,2.62),color=(.28,.32,.28)))
scene.include('clock',clock)

# Foreground right bed, largely cropped by the image border.
scene.include('right foreground bunk',bunk('Cropped right bunk',3.10,-1.20))
add(scene,'foreground wooden upright',(.13,.14,3.1),(2.48,-1.93,1.55),(.46,.25,.08))

realize(scene)
CAMERA_POSITION=(2.85,-5.95,1.67)
CAMERA_TARGET=(-.45,2.55,1.49)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=30,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.69,.58,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.38
area_emitter((-2.7,-2.8,2.8),power=1050,size=3.4,target=(-.5,2,.9),color=(1,.94,.79))
area_emitter((1,-.5,3.15),power=170,size=3.5,target=(0,3,1),color=(.89,.92,1))

# Subtle procedural surfaces retain editable geometry.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.77
        color=bs.inputs['Base Color'].default_value
        if color[0] < .38 and color[1] < .29 and color[0] > color[2]*1.6:
            tex=nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=7
            tex.inputs['Detail'].default_value=3
            coord=nodes.new('ShaderNodeTexCoord')
            mapping=nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(5,.22,3)
            mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
            mat.node_tree.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
            bump=nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.22
            bump.inputs['Distance'].default_value=.035
            mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.25
