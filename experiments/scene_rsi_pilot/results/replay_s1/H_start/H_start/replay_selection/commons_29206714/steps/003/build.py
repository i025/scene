from sceneact import *
import bpy, math

# The cabinet is too wide; narrow its furniture and contents while preserving height.
# The wheel needs a wider rim silhouette and a small shift to the right.
# Darken the amber timber and replace circular door inserts with arched panels.

scene = Scene('Historic kitchen')
wood=(.23,.075,.020)
edge=(.16,.043,.010)
panel=(.30,.108,.030)
cream=(.78,.77,.65)
green=(.20,.30,.18)

def add(parent,name,obj):
    parent.include(name,obj)
    return obj

room=Asset('Plaster walls and hearth')
add(room,'back',box((8,.16,4.8),center=(0,.69,2),color=(.72,.72,.66)))
add(room,'floor',box((8,6,.12),center=(0,-1,-.08),color=(.30,.26,.19)))
add(room,'wainscot',box((3.4,.08,.57),center=(-2,.57,.28),color=(.49,.45,.30)))
add(room,'chair_rail',box((3.4,.11,.045),center=(-2,.51,.58),color=(.56,.51,.36)))
add(room,'chimney',box((1.2,.32,3.3),center=(1.73,.36,1.65),color=(.80,.80,.74)))
add(room,'hearth',box((1,.16,1.1),center=(1.86,.10,.47),color=(.045,.039,.029)))
add(room,'mantel',box((1.65,.35,.34),center=(1.80,-.01,1.08),color=(.12,.065,.032)))
for i in range(6):
    add(room,f'mortar_horizontal_{i}',box((.85,.025,.014),center=(1.92,-.002,.06+i*.16),color=(.28,.26,.20)))
for i in range(5):
    add(room,f'mortar_vertical_{i}',box((.014,.025,.15),center=(1.72+(i%2)*.22,-.01,.14+i*.16),color=(.27,.25,.20)))
scene.include('Room',room)

cab=Asset('Pine dresser')
add(cab,'base_body',box((1.60,.62,.82),center=(0,.10,.43),color=wood))
for x in (-.80,.80):
    add(cab,f'base_stile_{x}',box((.10,.70,.89),center=(x,.03,.45),color=panel))
add(cab,'lower_rail',box((1.6,.08,.09),center=(0,-.25,.13),color=edge))
for j,x in enumerate((-.39,.39)):
    add(cab,f'lower_door_{j}',box((.70,.065,.68),center=(x,-.257,.44),color=panel))
    add(cab,f'lower_inset_{j}',box((.53,.022,.51),center=(x,-.300,.44),color=wood))
    for k,xx in enumerate((x-.30,x+.30)):
        add(cab,f'lower_frame_{j}_{k}',box((.045,.03,.64),center=(xx,-.306,.44),color=panel))
    add(cab,f'knob_{j}',ball(.022,center=(x+(.22 if j==0 else -.22),-.34,.54),color=edge))
for i,x in enumerate((-.42,.42)):
    add(cab,f'drawer_{i}',box((.74,.09,.19),center=(x,-.28,.91),color=panel))
    add(cab,f'drawer_inset_{i}',box((.64,.018,.115),center=(x,-.335,.91),color=wood))
    add(cab,f'drawer_handle_{i}',rod(.018,start=(x-.07,-.37,.915),end=(x+.07,-.37,.915),color=edge))
add(cab,'counter',box((1.81,.80,.085),center=(0,-.005,1.055),color=panel))
add(cab,'counter_lip',box((1.85,.82,.035),center=(0,-.01,1.10),color=wood))
add(cab,'upper_back',box((1.64,.075,1.43),center=(0,.355,1.83),color=(.19,.058,.017)))
for i in range(8):
    add(cab,f'back_seam_{i}',box((.006,.012,1.40),center=(-.72+i*.205,.306,1.83),color=(.13,.036,.009)))
for x in (-.82,.82):
    add(cab,f'upper_side_{x}',box((.105,.62,1.48),center=(x,.08,1.83),color=wood))
    add(cab,f'front_pillar_{x}',box((.075,.075,1.50),center=(x,-.26,1.84),color=panel))
for i,z in enumerate((1.16,1.64,2.13,2.57)):
    add(cab,f'shelf_{i}',box((1.65,.60,.055),center=(0,.035,z),color=wood))
    add(cab,f'shelf_edge_{i}',box((1.67,.055,.055),center=(0,-.28,z),color=edge))
for i,(w,d,z,h) in enumerate(((1.87,.75,2.59,.085),(1.96,.80,2.655,.045),(2.03,.84,2.69,.035))):
    add(cab,f'cornice_{i}',box((w,d,h),center=(0,.075,z),color=wood if i!=1 else edge))

for j,side in enumerate((-1,1)):
    door=Asset(f'Open door {j}')
    cx=side*.405
    add(door,'board',box((.78,.062,1.49),center=(cx,-.30,1.84),color=panel))
    for face,yy in enumerate((-.343,-.257)):
        add(door,f'panel_rectangle_{face}',box((.60,.014,1.02),center=(cx,yy,1.75),color=wood))
        cap=rod(.30,length=.014,center=(cx,yy,2.26),axis='+y',color=wood)
        cap.resize((1,1,.78))
        cap=overlap(cap,box((.62,.05,.25),center=(cx,yy,2.385),color=wood))
        add(door,f'panel_arch_{face}',cap)
        for k,xx in enumerate((cx-.35,cx+.35)):
            add(door,f'border_{face}_{k}',box((.055,.028,1.46),center=(xx,yy,1.84),color=panel))
        for k,z in enumerate((1.135,2.55)):
            add(door,f'cross_border_{face}_{k}',box((.76,.025,.055),center=(cx,yy,z),color=panel))
    for k,z in enumerate((1.35,2.29)):
        add(door,f'hinge_{k}',box((.085,.025,.035),center=(side*.765,-.25,z),color=(.105,.085,.055)))
    door.turn('z',side*135,pivot=(side*.81,-.27,1.84))
    cab.include(f'door_{j}',door)
cab.resize((.87,1,1),pivot=(0,0,0))
scene.include('Dresser',cab)

dishes=Asset('Shelf china and pewter')
def plate(name,x,y,z,r):
    p=Asset(name)
    add(p,'rim',rod(r,length=.025,center=(x,y,z),axis='+y',color=(.70,.72,.64)))
    add(p,'well',rod(r*.81,length=.029,center=(x,y-.018,z),axis='+y',color=(.83,.83,.74)))
    for k in range(12):
        a=2*math.pi*k/12
        mark=ball(r*.038,center=(x+math.cos(a)*r*.87,y-.037,z+math.sin(a)*r*.87),color=green)
        mark.resize((1,.25,1.6))
        add(p,f'leaf_{k}',mark)
    for k in range(5):
        a=k*2.4
        add(p,f'sprig_{k}',rod(.005,start=(x,y-.041,z-r*.15),end=(x+math.sin(a)*r*.23,y-.041,z+r*(.08+k*.06)),color=green))
    dishes.include(name,p)

plate('Upper left plate',-.40,.20,1.865,.218)
plate('Upper right plate',.48,.22,1.87,.225)
for i,x in enumerate((-.62,-.22,.22,.63)):
    plate(f'Lower plate {i}',x,.18,1.405,.195)

def bowl(name,x,y,z,r=.12,col=cream):
    ob=ball(r,center=(x,y,z),color=col)
    ob.resize((1,1,.43))
    add(dishes,name,ob)
    add(dishes,name+'_rim',rod(r,length=.015,center=(x,y,z+.025),color=(.88,.87,.77)))
    add(dishes,name+'_inner',rod(r*.83,length=.016,center=(x,y,z+.034),color=col))

def pot(name,x,y,z,r,col):
    ob=ball(r,center=(x,y,z),color=col)
    ob.resize((1,.80,1))
    add(dishes,name,ob)
    add(dishes,name+'_lid',rod(r*.65,length=.025,center=(x,y,z+r*.83),color=col))
    add(dishes,name+'_knob',ball(r*.16,center=(x,y,z+r*1.02),color=col))
    add(dishes,name+'_spout',rod(r*.19,start=(x-r*.65,y,z+.01),end=(x-r*1.48,y,z+r*.62),color=col))
    pts=[(x+r*.78+math.sin(a)*r*.65,y,z+math.cos(a)*r*.70) for a in (0,.65,1.3,1.95,2.6,3.14)]
    add(dishes,name+'_handle',sweep_tube(pts,radius=r*.105,color=col))

pot('Cream teapot',-.57,-.04,1.76,.135,(.80,.77,.65))
pot('Teal teapot',.55,-.035,1.78,.145,(.012,.095,.088))
bowl('Middle bowl',.035,-.015,1.70,.145)
for i in range(3):
    add(dishes,f'saucer_{i}',rod(.17,length=.013,center=(.04,-.035,1.666+i*.015),color=cream))
for i,x in enumerate((-.67,.63,.75)):
    bowl(f'Lower cup {i}',x,-.12,1.23,.074)
    add(dishes,f'cup_handle_{i}',rod(.027,length=.018,center=(x+.075,-.12,1.25),axis='+y',color=cream))
for i in range(6):
    x=-.49+i*.086
    add(dishes,f'glass_{i}',rod(.031,length=.115,center=(x,.02,2.22),color=(.38,.42,.39),opacity=.48))
    add(dishes,f'glass_rim_{i}',rod(.034,length=.009,center=(x,.02,2.281),color=(.64,.68,.63),opacity=.65))
for i,x in enumerate((-.72,-.57)):
    add(dishes,f'bottle_{i}',rod(.048,length=.19,center=(x,.16,2.25),color=(.42,.35,.22)))
    add(dishes,f'bottle_neck_{i}',rod(.021,length=.16,center=(x,.16,2.40),color=(.46,.42,.30)))
pot('Pewter pitcher',.60,.08,2.31,.13,(.16,.18,.17))
pot('Small pewter jug',.02,.09,2.24,.095,(.22,.24,.23))
dishes.resize((.87,1,1),pivot=(0,0,0))
scene.include('China',dishes)

swift=Asset('Yarn apparatus')
add(swift,'base',box((.91,.31,.045),center=(-.04,-.38,1.15),color=(.36,.14,.035)))
for i,x in enumerate((-.48,.37)):
    add(swift,f'end_{i}',box((.055,.25,.39),center=(x,-.35,1.36),color=panel))
    add(swift,f'foot_{i}',box((.19,.36,.035),center=(x,-.36,1.18),color=wood))
for i,z in enumerate((1.24,1.34,1.44,1.53)):
    add(swift,f'metal_cross_{i}',rod(.009,start=(-.49,-.46 if i%2 else -.24,z),end=(.37,-.24 if i%2 else -.46,z+.025),color=(.40,.43,.42)))
add(swift,'diagonal_1',rod(.015,start=(-.52,-.45,1.20),end=(.30,-.45,1.54),color=panel))
add(swift,'diagonal_2',rod(.015,start=(-.51,-.45,1.51),end=(.31,-.45,1.21),color=panel))
swift.resize((.87,1,1),pivot=(0,0,0))
scene.include('Yarn swift',swift)

wheel=Asset('Foreground spinning wheel')
C=(-.90,-1.02,.96)
R=.85
u=(-.055,.99849,0)
def wp(a,r=R):
    return (C[0]+u[0]*math.cos(a)*r,C[1]+u[1]*math.cos(a)*r,C[2]+math.sin(a)*r)
for i in range(40):
    add(wheel,f'rim_{i}',rod(.047,start=wp(i*2*math.pi/40),end=wp((i+1)*2*math.pi/40),color=(.15,.12,.085)))
for i in range(10):
    a=i*2*math.pi/10
    add(wheel,f'spoke_{i}',rod(.018,start=wp(a,.08),end=wp(a,R-.04),color=(.23,.17,.11)))
add(wheel,'hub',rod(.074,start=(-1.03,-1.02,.96),end=(-.77,-1.02,.96),color=(.20,.12,.06)))
for i,x in enumerate((-1.08,-.70)):
    add(wheel,f'leg_{i}',rod(.032,start=(x,-1.20,-.15),end=(x,-1.14,.81),color=(.43,.32,.19)))
    add(wheel,f'finial_{i}',ball(.049,center=(x,-1.14,.85),color=(.51,.39,.24)))
add(wheel,'crossbar',rod(.035,start=(-1.17,-1.15,.43),end=(-.60,-1.15,.43),color=wood))
add(wheel,'spindle',rod(.016,start=(-.81,-1.22,.53),end=(-.95,-1.19,1.35),color=(.73,.70,.59)))
scene.include('Spinning wheel',wheel)

realize(scene)
for mat in list(bpy.data.materials):
    c=mat.diffuse_color
    if c[0]>c[1]*1.45 and c[1]>c[2]*1.35:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        if bs is None:
            continue
        bs.inputs['Roughness'].default_value=.44
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=4
        tex.inputs['Detail'].default_value=2
        coord=nt.nodes.new('ShaderNodeTexCoord')
        vec=nt.nodes.new('ShaderNodeVectorMath')
        vec.operation='MULTIPLY'
        vec.inputs[1].default_value=(18,18,1.4)
        nt.links.new(coord.outputs['Generated'],vec.inputs[0])
        nt.links.new(vec.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(c[0]*.63,c[1]*.57,c[2]*.51,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(c[0]*1.18,c[1]*1.14,c[2]*1.10,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.10
        bump.inputs['Distance'].default_value=.009
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])

CAMERA_POSITION=(-1.60,-7.10,2.69)
CAMERA_TARGET=(0,-.02,1.51)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=67)
area_emitter((-3.5,-4,4),power=520,size=3,target=(0,0,1.4))
area_emitter((1,-2,3.4),power=65,size=3,target=(0,0,1.5))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.67,.72,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.20
sc.render.resolution_x=512
sc.render.resolution_y=339
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
