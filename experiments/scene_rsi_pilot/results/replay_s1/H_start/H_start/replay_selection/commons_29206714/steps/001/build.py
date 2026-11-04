from sceneact import *
import bpy, math, random
random.seed(12)

# Cabinet bounds approximately (0.15,0.02)-(0.89,1.00); open doors dominate its sides.
# Shelf fronts cross near image y=.28, .45 and .62.
# Dark wooden counter crosses image y=.72; lower cupboard continues below frame.
# Large foreground wheel occludes the cabinet at image x=.23-.37.
# Pale plaster fills the left background; white chimney and dark hearth occupy the right.
# Camera looks slightly downward, with cabinet top edges rising gently toward the right.

scene = Scene('Historic kitchen')
wood = (.36,.145,.052)
edge = (.27,.095,.028)
panel = (.43,.20,.085)
cream = (.78,.77,.65)
green = (.20,.30,.18)
metal = (.32,.34,.32)

def add(parent, name, obj):
    parent.include(name, obj)
    return obj

room = Asset('Plaster walls and hearth')
add(room,'back',box((7,.16,4.8),center=(0,.69,2),color=(.72,.72,.66)))
add(room,'floor',box((7,6,.12),center=(0,-1,-.08),color=(.30,.26,.19)))
add(room,'left_wainscot',box((2.8,.08,.57),center=(-2,.57,.28),color=(.49,.45,.30)))
add(room,'chair_rail',box((2.9,.11,.045),center=(-2,.51,.58),color=(.56,.51,.36)))
add(room,'chimney',box((1.2,.32,3.3),center=(1.73,.36,1.65),color=(.80,.80,.74)))
add(room,'hearth_dark',box((1.0,.16,1.1),center=(1.86,.10,.47),color=(.065,.06,.046)))
add(room,'mantel_beam',box((1.45,.35,.34),center=(1.80,-.01,1.08),color=(.16,.095,.053)))
for i in range(5):
    add(room,f'brick_h_{i}',box((.75,.025,.016),center=(1.92,-.002,.13+i*.16),color=(.33,.31,.25)))
for i in range(4):
    add(room,f'brick_v_{i}',box((.017,.025,.15),center=(1.72+(i%2)*.22,-.01,.21+i*.16),color=(.30,.29,.23)))
scene.include('Room',room)

cab = Asset('Pine dresser')
W=1.60
# Lower cupboard, substantial front frame and two recessed doors.
add(cab,'base_body',box((W,.62,.82),center=(0,.10,.43),color=wood))
for x in (-.80,.80):
    add(cab,f'base_stile_{x}',box((.10,.70,.89),center=(x,.03,.45),color=panel))
add(cab,'lower_front_rail',box((1.6,.08,.09),center=(0,-.25,.13),color=edge))
for j,x in enumerate((-.39,.39)):
    add(cab,f'lower_door_{j}',box((.70,.065,.68),center=(x,-.257,.44),color=panel))
    add(cab,f'lower_inset_{j}',box((.53,.022,.51),center=(x,-.300,.44),color=wood))
    for xx in (x-.30,x+.30):
        add(cab,f'lower_frame_{j}_{xx}',box((.045,.03,.64),center=(xx,-.306,.44),color=panel))
    add(cab,f'lower_knob_{j}',ball(.022,center=(x+(.22 if j==0 else -.22),-.34,.54),color=edge))
for i,x in enumerate((-.42,.42)):
    add(cab,f'drawer_{i}',box((.74,.09,.19),center=(x,-.28,.91),color=panel))
    add(cab,f'drawer_inset_{i}',box((.64,.018,.115),center=(x,-.335,.91),color=wood))
    add(cab,f'drawer_handle_{i}',rod(.018,start=(x-.07,-.37,.915),end=(x+.07,-.37,.915),color=edge))
add(cab,'counter',box((1.81,.80,.085),center=(0,-.005,1.055),color=panel))
add(cab,'counter_lip',box((1.85,.82,.035),center=(0,-.01,1.10),color=wood))
# Upper case and deep dark backing.
add(cab,'upper_back',box((1.64,.075,1.43),center=(0,.355,1.83),color=(.29,.125,.05)))
for i in range(8):
    add(cab,f'back_board_{i}',box((.006,.012,1.40),center=(-.72+i*.205,.306,1.83),color=(.22,.083,.028)))
for x in (-.82,.82):
    add(cab,f'upper_side_{x}',box((.105,.62,1.48),center=(x,.08,1.83),color=wood))
    add(cab,f'front_pillar_{x}',box((.075,.075,1.50),center=(x,-.26,1.84),color=panel))
for i,z in enumerate((1.16,1.64,2.13,2.57)):
    add(cab,f'shelf_{i}',box((1.65,.60,.055),center=(0,.035,z),color=wood))
    add(cab,f'shelf_edge_{i}',box((1.67,.055,.055),center=(0,-.28,z),color=edge))
for i,(w,d,z,h) in enumerate(((1.87,.75,2.59,.085),(1.96,.80,2.655,.045),(2.03,.84,2.69,.035))):
    add(cab,f'cornice_{i}',box((w,d,h),center=(0,.075,z),color=wood if i!=1 else edge))
# Open doors, constructed in their closed positions and rotated about hinges.
for j,side in enumerate((-1,1)):
    door=Asset(f'Open door {j}')
    cx=side*.405
    add(door,'board',box((.78,.062,1.49),center=(cx,-.30,1.84),color=panel))
    add(door,'recess',box((.60,.018,1.15),center=(cx,-.339,1.78),color=wood))
    cap=rod(.30,length=.018,center=(cx,-.339,2.31),axis='+y',color=wood)
    cap.resize((1,1,.72))
    add(door,'arched_crown',cap)
    for k,xx in enumerate((cx-.35,cx+.35)):
        add(door,f'border_{k}',box((.055,.028,1.46),center=(xx,-.351,1.84),color=panel))
    for k,z in enumerate((1.135,2.55)):
        add(door,f'cross_border_{k}',box((.76,.025,.055),center=(cx,-.35,z),color=panel))
    for k,z in enumerate((1.35,2.29)):
        add(door,f'hinge_{k}',box((.085,.025,.035),center=(side*.765,-.357,z),color=(.16,.14,.10)))
    door.turn('z',side*135,pivot=(side*.81,-.27,1.84))
    cab.include(f'door_{j}',door)
scene.include('Dresser',cab)

dishes=Asset('Shelf china and pewter')
def plate(name,x,y,z,r,dec=True):
    p=Asset(name)
    add(p,'rim',rod(r,length=.025,center=(x,y,z),axis='+y',color=(.78,.79,.70)))
    add(p,'well',rod(r*.81,length=.029,center=(x,y-.018,z),axis='+y',color=(.88,.87,.77)))
    if dec:
        # Small rim motifs and a central floral sprig.
        for k in range(12):
            a=2*math.pi*k/12
            mark=ball(r*.038,center=(x+math.cos(a)*r*.87,y-.037,z+math.sin(a)*r*.87),color=green)
            mark.resize((1,.25,1.6))
            add(p,f'rim_leaf_{k}',mark)
        for k in range(5):
            a=k*2.4
            add(p,f'sprig_{k}',rod(.005,start=(x,y-.041,z-r*.15),end=(x+math.sin(a)*r*.23,y-.041,z+r*(.08+k*.06)),color=green))
    dishes.include(name,p)

plate('Upper left floral plate',-.40,.20,1.865,.218)
plate('Upper right floral plate',.48,.22,1.87,.225)
for i,x in enumerate((-.62,-.22,.22,.63)):
    plate(f'Lower plate {i}',x,.18,1.405,.195)

def bowl(name,x,y,z,r=.12,col=cream):
    ob=ball(r,center=(x,y,z),color=col)
    ob.resize((1,1,.43))
    add(dishes,name,ob)
    add(dishes,name+'_rim',rod(r,length=.015,center=(x,y,z+.025),color=(.91,.90,.81)))
    add(dishes,name+'_inner',rod(r*.83,length=.016,center=(x,y,z+.034),color=col))
def pot(name,x,y,z,r,col):
    body=ball(r,center=(x,y,z),color=col)
    body.resize((1,.80,1.0))
    add(dishes,name,body)
    add(dishes,name+'_lid',rod(r*.65,length=.025,center=(x,y,z+r*.83),color=col))
    add(dishes,name+'_knob',ball(r*.16,center=(x,y,z+r*1.02),color=col))
    add(dishes,name+'_spout',rod(r*.19,start=(x-r*.65,y,z+.01),end=(x-r*1.48,y,z+r*.62),color=col))
    pts=[(x+r*.78+math.sin(a)*r*.65,y,z+math.cos(a)*r*.70) for a in (0,.65,1.3,1.95,2.6,3.14)]
    add(dishes,name+'_handle',sweep_tube(pts,radius=r*.105,color=col))
pot('Cream teapot',-.57,-.04,1.76,.135,(.83,.80,.66))
pot('Teal teapot',.55,-.035,1.78,.145,(.025,.19,.18))
bowl('Middle bowl',.035,-.015,1.70,.145)
for i in range(3):
    add(dishes,f'middle_saucers_{i}',rod(.17,length=.013,center=(.04,-.035,1.666+i*.015),color=cream))
for i,x in enumerate((-.67,.63,.75)):
    bowl(f'Lower cup {i}',x,-.12,1.23,.074)
    add(dishes,f'Lower cup handle {i}',rod(.027,length=.018,center=(x+.075,-.12,1.25),axis='+y',color=cream))
# Upper shelf glasses, bottles and metal pitchers.
for i in range(6):
    x=-.49+i*.086
    add(dishes,f'glass_{i}',rod(.031,length=.115,center=(x,.02,2.22),color=(.48,.51,.47),opacity=.48))
    add(dishes,f'glass_rim_{i}',rod(.034,length=.009,center=(x,.02,2.281),color=(.70,.72,.65),opacity=.65))
for i,x in enumerate((-.72,-.57)):
    add(dishes,f'bottle_{i}',rod(.048,length=.19,center=(x,.16,2.25),color=(.49,.43,.28)))
    add(dishes,f'bottle_neck_{i}',rod(.021,length=.16,center=(x,.16,2.40),color=(.53,.49,.36)))
pot('Pewter pitcher',.60,.08,2.31,.13,(.30,.31,.28))
pot('Small pewter jug',.02,.09,2.24,.095,(.36,.38,.35))
scene.include('China',dishes)

swift=Asset('Wood and metal yarn apparatus on counter')
add(swift,'base',box((.91,.31,.045),center=(-.04,-.38,1.15),color=(.51,.25,.08)))
for i,x in enumerate((-.48,.37)):
    add(swift,f'end_{i}',box((.055,.25,.39),center=(x,-.35,1.36),color=panel))
    add(swift,f'foot_{i}',box((.19,.36,.035),center=(x,-.36,1.18),color=wood))
for i,z in enumerate((1.24,1.34,1.44,1.53)):
    add(swift,f'metal_cross_{i}',rod(.009,start=(-.49,-.46 if i%2 else -.24,z),end=(.37,-.24 if i%2 else -.46,z+.025),color=(.48,.49,.43)))
add(swift,'diagonal_wood_1',rod(.018,start=(-.52,-.45,1.20),end=(.30,-.45,1.54),color=panel))
add(swift,'diagonal_wood_2',rod(.018,start=(-.51,-.45,1.51),end=(.31,-.45,1.21),color=panel))
scene.include('Yarn swift',swift)

wheel=Asset('Foreground spinning wheel')
C=(-1.02,-1.02,.79)
R=.68
u=(.46,.888,0)
def wp(a,r=R):
    return (C[0]+u[0]*math.cos(a)*r,C[1]+u[1]*math.cos(a)*r,C[2]+math.sin(a)*r)
for i in range(32):
    a=i*2*math.pi/32
    b=(i+1)*2*math.pi/32
    add(wheel,f'rim_{i}',rod(.052,start=wp(a),end=wp(b),color=(.29,.23,.16)))
for i in range(10):
    a=i*2*math.pi/10
    add(wheel,f'spoke_{i}',rod(.019,start=wp(a,.08),end=wp(a,.63),color=(.38,.29,.17)))
add(wheel,'hub',rod(.072,start=(-1.12,-.97,.79),end=(-.91,-1.08,.79),color=wood))
for i,x in enumerate((-1.20,-.78)):
    add(wheel,f'leg_{i}',rod(.033,start=(x,-1.20,-.05),end=(x,-1.14,.68),color=(.55,.43,.27)))
    add(wheel,f'finial_{i}',ball(.051,center=(x,-1.14,.71),color=(.63,.52,.34)))
add(wheel,'crossbar',rod(.035,start=(-1.29,-1.15,.33),end=(-.68,-1.15,.33),color=wood))
add(wheel,'spindle',rod(.018,start=(-.93,-1.22,.43),end=(-1.07,-1.19,1.08),color=(.73,.70,.59)))
scene.include('Spinning wheel',wheel)

realize(scene)

# Subtle vertical grain preserves the editable wooden components.
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if c[0] > c[1]*1.45 and c[1] > c[2]*1.35:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        if bs is None:
            continue
        bs.inputs['Roughness'].default_value=.48
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=4
        tex.inputs['Detail'].default_value=2
        coord=nt.nodes.new('ShaderNodeTexCoord')
        vec=nt.nodes.new('ShaderNodeVectorMath')
        vec.operation='MULTIPLY'
        vec.inputs[1].default_value=(21,21,1.5)
        nt.links.new(coord.outputs['Generated'],vec.inputs[0])
        nt.links.new(vec.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(c[0]*.62,c[1]*.56,c[2]*.50,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(min(c[0]*1.2,1),c[1]*1.16,c[2]*1.12,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.12
        bump.inputs['Distance'].default_value=.012
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])

CAMERA_POSITION=(2.65,-6.8,2.76)
CAMERA_TARGET=(-.02,-.02,1.47)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=52)
area_emitter((-3.5,-4.0,4.0),power=650,size=3.5,target=(0,0,1.4))
area_emitter((1,-2,3.4),power=110,size=3,target=(0,0,1.5))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.67,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.25
sc.render.resolution_x=512
sc.render.resolution_y=339
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
