# Observed crown (.32,.10)-(.72,.11) is too small versus reference (.26,.06)-(.75,0); tighter framing and steeper view should enlarge both doors and crop the base.
# Foreground wheel is broad at (.09,.48)-(.39,1), versus narrow (.24,.39)-(.37,1); rotate and translate its complete owner independently of the cabinet.
# Mantel currently overlaps the right door; move its complete fireplace owner backward so the door occludes it, and lower the swift's overextended crossing rods.
from sceneact import *
import bpy, math

scene = Scene('Country kitchen')
W, D, H = 1.74, .55, 2.82
CAMERA = (2.65, -7.3, 3.15)
TARGET = (-.02, -.12, 1.52)
LENS = 64
wood = (.34,.135,.047)
edge = (.27,.095,.029)
panel = (.40,.18,.075)
cream = (.78,.78,.68)
metal = (.32,.34,.32)
green = (.035,.20,.18)

room = Asset('Plastered room')
room.include('back plaster', box((8,.12,5), center=(0,.64,2), color=(.73,.72,.65)))
room.include('left wall', box((.13,6,5), center=(-2.12,-1.5,2), color=(.76,.75,.68)))
room.include('ochre lower wall', box((.05,5,.76), center=(-2.04,-1.5,.38), color=(.48,.40,.23)))
room.include('dado rail', box((.09,5,.055), center=(-2.01,-1.5,.79), color=(.57,.49,.32)))
room.include('floor', box((8,8,.1), center=(0,0,-.05), color=(.32,.28,.21)))
scene.include('room', room)

fire = Asset('Whitewashed fireplace')
fire.include('left pier', box((.32,.52,1.32), center=(1.55,.35,.66), color=(.75,.75,.69)))
fire.include('right pier', box((.55,.55,1.32), center=(2.75,.35,.66), color=(.72,.72,.66)))
fire.include('dark hearth opening', box((1.04,.10,1.2), center=(2.13,.56,.60), color=(.055,.047,.038)))
fire.include('oak mantel', box((2.10,.64,.34), center=(2.15,.22,1.45), color=(.16,.085,.04)))
for j in range(7):
    fire.include('mortar left '+str(j), box((.325,.008,.014), center=(1.55,.083,.12+j*.17), color=(.58,.59,.55)))
for j in range(5):
    fire.include('back brick '+str(j), box((.98,.025,.018), center=(2.14,.49,.16+j*.2), color=(.19,.17,.13)))
fire.move((-.18,.20,0))
scene.include('fireplace', fire)

cab = Asset('Oak dresser')
cab.include('back boards', box((W,.065,2.69), center=(0,.42,1.345), color=wood))
for x in (-W/2,W/2):
    cab.include('upright '+str(x), box((.105,D,1.76), center=(x,.15,1.90), color=wood))
cab.include('base carcass', box((W,.56,.84), center=(0,.12,.45), color=wood))
cab.include('counter', box((W+.16,.73,.075), center=(0,.035,.995), color=panel))
cab.include('counter front lip', box((W+.18,.06,.055), center=(0,-.35,.965), color=edge))
for x in (-.43,.43):
    cab.include('lower door '+str(x), box((.79,.055,.67), center=(x,-.19,.435), color=panel))
    cab.include('lower inset '+str(x), box((.61,.022,.49), center=(x,-.226,.435), color=wood))
    for z in (.15,.72):
        cab.include('base hinge '+str((x,z)), box((.037,.026,.10), center=(x+(.34 if x>0 else -.34),-.245,z), color=(.17,.15,.11)))
cab.include('central stile', box((.075,.09,.76), center=(0,-.24,.43), color=edge))
cab.include('drawer face', box((W-.08,.085,.19), center=(0,-.30,.855), color=panel))
for x in (-.46,.46):
    cab.include('drawer handle '+str(x), rod(.018,start=(x-.055,-.363,.855),end=(x+.055,-.363,.855),color=(.24,.18,.09)))
for z in (1.12,1.67,2.18,2.66):
    cab.include('shelf '+str(z), box((W-.12,.53,.045), center=(0,.13,z), color=wood))
    cab.include('shelf edge '+str(z), box((W-.10,.035,.043), center=(0,-.15,z-.012), color=panel))
cab.include('top frieze', box((W+.03,.59,.16), center=(0,.15,2.74), color=wood))
for z,width,depth in ((2.83,W+.18,.66),(2.865,W+.27,.70),(2.895,W+.31,.74)):
    cab.include('cornice '+str(z), box((width,depth,.04), center=(0,.15,z), color=edge))
scene.include('dresser',cab)

for side in (-1,1):
    door = Asset('Left open door' if side<0 else 'Right open door')
    hinge = side*.91
    outer = hinge+side*.73
    cx = (hinge+outer)/2
    door.include('door slab', box((.73,.057,1.57), center=(cx,-.12,1.91), color=panel))
    door.include('recessed field', box((.55,.025,1.29), center=(cx,-.16,1.88), color=wood))
    for x in (cx-.32,cx+.32):
        door.include('frame stile '+str(x), box((.075,.05,1.57), center=(x,-.18,1.91), color=panel))
    for z in (1.155,2.665):
        door.include('frame rail '+str(z), box((.73,.05,.08), center=(cx,-.18,z), color=panel))
    pts=[]
    for i in range(15):
        a=math.pi*i/14
        pts.append((cx+.275*math.cos(a),-.19,2.37+.22*math.sin(a)))
    door.include('arched panel molding', sweep_tube(points=pts,radius=.013,color=panel))
    for z in (1.23,2.58):
        door.include('hinge '+str(z), box((.065,.07,.045), center=(hinge,-.14,z), color=(.14,.12,.085)))
    door.turn('z',side*24,pivot=(hinge,-.12,0))
    scene.include('door '+str(side),door)

def plate(name,x,y,z,r,decor=True):
    a=Asset(name)
    a.include('rim',rod(r,length=.025,center=(x,y,z),axis='+y',color=cream))
    a.include('well',rod(r*.78,length=.027,center=(x,y-.018,z),axis='+y',color=(.85,.84,.75)))
    a.include('inner well',rod(r*.65,length=.029,center=(x,y-.025,z),axis='+y',color=(.79,.80,.72)))
    if decor:
        for k in range(10):
            t=2*math.pi*k/10
            a.include('leaf '+str(k),rod(r*.055,length=.008,center=(x+r*.86*math.sin(t),y-.036,z+r*.86*math.cos(t)),axis='+y',color=(.25,.36,.25)))
        a.include('center flower',rod(r*.11,length=.01,center=(x,y-.044,z),axis='+y',color=(.41,.45,.28)))
    scene.include(name,a)

for i,(x,r) in enumerate(((-.60,.165),(-.21,.18),(.24,.18),(.63,.17))):
    plate('Lower display plate '+str(i),x,.19,1.34,r)
plate('Upper left patterned plate',-.44,.24,1.91,.205)
plate('Upper right patterned plate',.47,.24,1.92,.21)

def bowl(name,x,y,z,r,col=cream):
    a=Asset(name)
    a.include('foot',rod(r*.48,length=.025,center=(x,y,z+.012),color=col))
    body=ball(r,center=(x,y,z+r*.43),color=col)
    body.resize((1,1,.46))
    a.include('body',body)
    a.include('open mouth',rod(r*.86,length=.006,center=(x,y,z+r*.86),color=(.47,.48,.42)))
    a.include('rim',rod(r,length=.012,center=(x,y,z+r*.88),color=col))
    scene.include(name,a)

bowl('White bowl on upper shelf',.02,-.015,1.695,.17)
bowl('Small lower bowl',-.05,-.10,1.145,.13)
for i,x in enumerate((-.74,.72)):
    bowl('Shelf cup '+str(i),x,-.035,1.145,.085)
    bowl('Shelf saucer '+str(i),x,-.035,1.145,.105)

def pot(name,x,y,z,r,col):
    a=Asset(name)
    body=ball(r,center=(x,y,z+r*.77),color=col)
    body.resize((1,.80,.85))
    a.include('body',body)
    a.include('lid',rod(r*.66,length=.025,center=(x,y,z+r*1.55),color=col))
    a.include('knob',ball(r*.12,center=(x,y,z+r*1.72),color=col))
    a.include('spout',rod(r*.17,start=(x-r*.70,y,z+r*.8),end=(x-r*1.48,y,z+r*1.35),color=col))
    pts=[(x+r*.78,y,z+r*1.40),(x+r*1.35,y,z+r*1.48),(x+r*1.48,y,z+r*.70),(x+r*.79,y,z+r*.43)]
    a.include('handle',sweep_tube(points=pts,radius=r*.095,color=col))
    scene.include(name,a)

pot('Cream teapot',-.64,-.025,1.695,.135,cream)
pot('Green teapot',.59,-.03,1.695,.145,green)
pot('Pewter jug',.69,.12,2.205,.12,metal)
pot('Small pewter pot',-.08,.17,2.205,.10,metal)
for i,x in enumerate((-.72,-.54)):
    a=Asset('Stoneware bottle '+str(i))
    a.include('body',rod(.043,length=.145,center=(x,.19,2.28),color=(.56,.48,.34)))
    a.include('neck',rod(.018,length=.17,center=(x,.19,2.425),color=(.48,.41,.29)))
    scene.include('bottle '+str(i),a)
for i in range(8):
    x=-.39+i*.06
    a=Asset('Glass '+str(i))
    a.include('tumbler',rod(.022,length=.105,center=(x,-.005,2.255),color=(.59,.64,.61)))
    a.include('mouth',rod(.018,length=.003,center=(x,-.005,2.31),color=(.25,.29,.27)))
    scene.include('glass '+str(i),a)

swift=Asset('Yarn winding swift')
swift.include('base',box((1.02,.36,.045),center=(0,-.37,1.067),color=(.48,.23,.075)))
for x in (-.46,.46):
    swift.include('upright '+str(x),box((.055,.075,.43),center=(x,-.26,1.30),color=(.52,.25,.085)))
    swift.include('foot '+str(x),box((.12,.40,.045),center=(x,-.39,1.10),color=panel))
for k,z in enumerate((1.15,1.25,1.36,1.46)):
    swift.include('cross rod '+str(k),rod(.010,start=(-.46,-.27,z),end=(.45,-.55,2.61-z),color=(.50,.52,.49)))
    swift.include('return rod '+str(k),rod(.009,start=(-.46,-.55,z),end=(.45,-.27,2.61-z),color=(.54,.55,.49)))
swift.include('axle',rod(.016,start=(-.53,-.40,1.32),end=(.53,-.40,1.32),color=metal))
scene.include('swift',swift)

wheel=Asset('Foreground spinning wheel')
WC=(-.97,-1.16,.77)
R=.88
angle=math.radians(100)
def wp(u,z,depth=0):
    return (WC[0]+u*math.cos(angle)-depth*math.sin(angle),
            WC[1]+u*math.sin(angle)+depth*math.cos(angle),WC[2]+z)
for depth in (-.035,.035):
    pts=[wp(R*math.cos(i*2*math.pi/48),R*math.sin(i*2*math.pi/48),depth) for i in range(49)]
    wheel.include('rim '+str(depth),sweep_tube(points=pts,radius=.034,color=(.27,.23,.17)))
for k in range(10):
    a=k*2*math.pi/10
    wheel.include('spoke '+str(k),rod(.017,start=wp(0,0),end=wp(R*.96*math.cos(a),R*.96*math.sin(a)),color=(.36,.29,.20)))
wheel.include('hub',rod(.065,start=wp(0,0,-.14),end=wp(0,0,.14),color=(.28,.23,.16)))
wheel.include('support',rod(.045,start=(-1.09,-1.39,.05),end=wp(0,0,.11),color=(.39,.31,.21)))
wheel.include('front spindle post',rod(.035,start=(-1.36,-1.49,.02),end=(-1.36,-1.49,.72),color=(.53,.42,.27)))
wheel.include('spindle finial',ball(.048,center=(-1.36,-1.49,.77),color=(.51,.40,.26)))
wheel.include('spindle',rod(.014,start=(-1.36,-1.49,.68),end=(-1.20,-1.45,1.26),color=(.63,.59,.47)))
wheel.include('treadle',box((.19,.57,.035),center=(-1.03,-1.40,.08),color=(.31,.24,.16)))
wheel.move((.55,0,0))
scene.include('spinning wheel',wheel)

realize(scene)
for mat in bpy.data.materials:
    c=mat.diffuse_color
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.52
        if c[0]>.20 and c[0]>c[1]*1.5 and c[1]>c[2]*1.5:
            nt=mat.node_tree
            tex=nt.nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=4
            tex.inputs['Detail'].default_value=3
            coord=nt.nodes.new('ShaderNodeTexCoord')
            mapping=nt.nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(19,19,1.8)
            nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
            nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
            ramp=nt.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.17
            ramp.color_ramp.elements[0].color=(c[0]*.65,c[1]*.65,c[2]*.65,1)
            ramp.color_ramp.elements[1].position=.85
            ramp.color_ramp.elements[1].color=(c[0]*1.19,c[1]*1.19,c[2]*1.19,1)
            nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
            nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.13
            bump.inputs['Distance'].default_value=.012
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs[0],bs.inputs['Normal'])
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.70,.74,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3.5,-4,4.5),power=650,size=3.6,target=(0,0,1.3),color=(1,.91,.76))
area_emitter((1,-3,3.5),power=110,size=4,target=(0,0,1.5),color=(.83,.89,1))
