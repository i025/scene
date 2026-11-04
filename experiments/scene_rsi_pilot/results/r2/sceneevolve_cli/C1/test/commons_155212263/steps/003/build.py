from sceneact import *
import bpy, math, random
random.seed(13)

# Floorboards should run across the bench, giving diagonals toward the upper right.
# The viewpoint needs stronger recession along the bench and less empty foreground.
# The projecting vise, drawer and pale bucket need to sit farther left beneath the machines.

scene = Scene('Historic metalworking shop')
wood=(.14,.115,.075)
edgewood=(.25,.205,.135)
iron=(.065,.075,.069)
steel=(.23,.25,.23)
rust=(.18,.125,.075)
wall=(.39,.445,.405)

def add(parent,name,shape):
    parent.include(name,shape)

def beam(parent,name,a,b,r=.025,color=iron):
    add(parent,name,rod(r,start=a,end=b,color=color))

def wheel(parent,name,x,y,z,radius,color=iron,spokes=6):
    for j in range(28):
        a=2*math.pi*j/28
        b=2*math.pi*(j+1)/28
        beam(parent,name+'rim'+str(j),
             (x+radius*math.cos(a),y,z+radius*math.sin(a)),
             (x+radius*math.cos(b),y,z+radius*math.sin(b)),.032,color)
    for j in range(spokes):
        a=2*math.pi*j/spokes+.15
        points=[(x,y,z),
                (x+radius*.50*math.cos(a+.32),y,z+radius*.50*math.sin(a+.32)),
                (x+radius*.94*math.cos(a),y,z+radius*.94*math.sin(a))]
        for k in range(2):
            beam(parent,f'{name}spoke{j}_{k}',points[k],points[k+1],.037,color)
    beam(parent,name+'hub',(x,y-.085,z),(x,y+.085,z),.082,color)

floor=Asset('Worn plank floor')
for i in range(60):
    xx=-7+i*.245
    v=random.uniform(-.025,.025)
    c=(.33+v,.265+v,.17+v*.7)
    add(floor,'plank'+str(i),box((.236,15,.075),center=(xx,-1,-.045),color=c))
    yy=random.uniform(-4,1)
    add(floor,'joint'+str(i),box((.235,.012,.003),center=(xx,yy,-.006),color=(.12,.10,.065)))
scene.include('floor',floor)

architecture=Asset('Old plaster and windows')
add(architecture,'lower_wall',box((14,.17,1.65),center=(-.6,1.27,.825),color=wall))
add(architecture,'upper_wall',box((14,.17,1.5),center=(-.6,1.27,4.7),color=wall))
for i,x in enumerate([-5.4,-3.2,-.9,1.4,3.7,6]):
    add(architecture,'pier'+str(i),box((.30,.19,3.25),center=(x,1.26,3.13),color=wall))
for i,x in enumerate([-4.3,-2.05,.25,2.55,4.85]):
    add(architecture,'glass'+str(i),box((1.86,.045,2.65),center=(x,1.34,3.08),color=(.78,.87,.90)))
    add(architecture,'sill'+str(i),box((2.10,.40,.09),center=(x,1.09,1.74),color=(.20,.23,.20)))
    for j,xx in enumerate([x-.94,x,x+.94]):
        add(architecture,f'frame{i}_{j}',box((.047,.10,2.75),center=(xx,1.23,3.08),color=(.23,.28,.26)))
    add(architecture,'crossbar'+str(i),box((1.9,.1,.045),center=(x,1.23,2.63),color=(.29,.34,.31)))
add(architecture,'left_wall',box((.18,3.3,5.5),center=(-5.6,-.3,2.75),color=(.36,.35,.29)))
for i in range(20):
    x=random.uniform(-5.1,4.6)
    z=random.uniform(.25,1.55)
    add(architecture,'patch'+str(i),box((random.uniform(.12,.40),.012,random.uniform(.10,.33)),
        center=(x,1.174,z),color=(.30,.35,.30)))
scene.include('architecture',architecture)

bench=Asset('Continuous oak workbench')
add(bench,'slab',box((9.4,1.06,.19),center=(-.55,.36,1.03),color=edgewood))
add(bench,'apron',box((9.3,.11,.19),center=(-.55,-.15,.85),color=wood))
for i,x in enumerate([-4.9,-3.3,-1.6,.1,1.8,3.7]):
    for j,y in enumerate([-.04,.76]):
        add(bench,f'leg{i}_{j}',box((.18,.19,.94),center=(x,y,.48),color=wood))
    add(bench,'foot'+str(i),box((.24,1.1,.13),center=(x,.34,.15),color=wood))
    add(bench,'stretcher'+str(i),box((1.3,.09,.12),center=(x-.55,.67,.32),color=wood))
for i in range(16):
    x=random.uniform(-5,3.9)
    y=random.uniform(-.05,.76)
    add(bench,'scar'+str(i),box((random.uniform(.08,.35),.018,.004),
        center=(x,y,1.128),color=(.105,.09,.055)))
scene.include('bench',bench)

def lathe(name,x,length,scale=1):
    a=Asset(name)
    for j,y in enumerate([.14,.49]):
        beam(a,'bedrail'+str(j),(x-length/2,y,1.18),(x+length/2,y,1.18),.048,steel)
    for j,xx in enumerate([x-length*.34,x+length*.34]):
        add(a,'foot'+str(j),box((.24,.66,.12),center=(xx,.32,1.16),color=iron))
        add(a,'pedestal'+str(j),box((.20,.29,.35*scale),center=(xx,.32,1.34),color=iron))
    beam(a,'spindle',(x-length*.47,.32,1.52),(x+length*.56,.32,1.52),.055,steel)
    beam(a,'headstock',(x-length*.36,.32,1.52),(x-length*.07,.32,1.52),.155*scale,iron)
    beam(a,'chuck',(x-length*.04,.32,1.52),(x+length*.07,.32,1.52),.11*scale,steel)
    beam(a,'tailstock',(x+length*.26,.32,1.52),(x+length*.44,.32,1.52),.125*scale,iron)
    add(a,'rest',box((.38,.08,.055),center=(x+.10,.09,1.43),color=steel))
    beam(a,'restpost',(x+.1,.09,1.18),(x+.1,.09,1.43),.027)
    beam(a,'crank',(x+length*.56,.32,1.52),(x+length*.56,.32,1.32),.025)
    beam(a,'handle',(x+length*.56,.23,1.32),(x+length*.56,.46,1.32),.036,wood)
    add(a,'bearingcap',box((.20,.25,.065),center=(x-length*.28,.32,1.70),color=iron))
    scene.include(name,a)

lathe('Foreground screw cutting lathe',2.10,1.85)
lathe('Middle small lathe',-2.35,1.35,.8)
lathe('Far small lathe',-4.20,1.2,.7)

drive=Asset('Tall cast iron belt drive')
for i,x in enumerate([.75,1.22]):
    add(drive,'column'+str(i),box((.085,.13,.95),center=(x,.81,1.63),color=iron))
add(drive,'bearing',box((.66,.22,.12),center=(.99,.80,2.03),color=iron))
wheel(drive,'large',1.03,.67,2.13,.53,iron,5)
for j in range(24):
    a=2*math.pi*j/24
    b=2*math.pi*(j+1)/24
    beam(drive,'rear'+str(j),(1.03+.49*math.cos(a),.80,2.13+.49*math.sin(a)),
         (1.03+.49*math.cos(b),.80,2.13+.49*math.sin(b)),.023,rust)
beam(drive,'axle',(1.03,.52,2.13),(1.03,1.02,2.13),.05)
beam(drive,'crank',(1.03,.48,2.13),(1.28,.48,1.92),.03)
beam(drive,'grip',(1.28,.29,1.92),(1.28,.53,1.92),.035,wood)
scene.include('drive',drive)

small=Asset('Blue gray middle wheel')
wheel(small,'wheel',-2.10,.66,1.89,.34,(.15,.25,.28),6)
beam(small,'stand',(-2.10,.70,1.11),(-2.10,.70,1.91),.055)
scene.include('middlewheel',small)

anvil=Asset('Large iron anvil')
add(anvil,'base',box((.70,.46,.11),center=(-.60,.29,1.18),color=rust))
add(anvil,'waist',box((.31,.28,.37),center=(-.60,.29,1.38),color=rust))
for i in range(3):
    add(anvil,'shoulder'+str(i),box((.36+i*.12,.31+i*.035,.075),
        center=(-.60,.29,1.49+i*.075),color=(.23,.17,.10)))
add(anvil,'face',box((.72,.40,.09),center=(-.56,.29,1.71),color=(.32,.27,.18)))
for i in range(6):
    beam(anvil,'horn'+str(i),(-.19+i*.10,.29,1.64),(-.08+i*.10,.29,1.64),
         .145-i*.024,(.26,.20,.125))
scene.include('anvil',anvil)

vise=Asset('Heavy projecting front vise')
add(vise,'fixed',box((.49,.19,.20),center=(.82,-.19,1.10),color=iron))
add(vise,'moving',box((.49,.17,.20),center=(.82,-.65,1.10),color=iron))
for j,y in enumerate([-.20,-.65]):
    add(vise,'face'+str(j),box((.50,.06,.055),center=(.82,y,1.22),color=steel))
beam(vise,'slide',(.82,-.79,.91),(.82,.16,.91),.10)
beam(vise,'screw',(.82,-.97,.94),(.82,-.15,.94),.043,steel)
beam(vise,'crossbar',(.82,-.95,.61),(.82,-.95,1.13),.025,steel)
for j,z in enumerate([.60,1.14]):
    add(vise,'knob'+str(j),ball(.043,center=(.82,-.95,z),color=iron))
beam(vise,'support',(.82,-.27,.12),(.82,-.27,.98),.062)
vise.move((-.55,-.08,0))
scene.include('vise',vise)

tray=Asset('Open tool drawer')
add(tray,'bottom',box((1.04,.64,.06),center=(2.02,-.48,.64),color=wood))
for j,y in enumerate([-.80,-.17]):
    add(tray,'wall'+str(j),box((1.1,.065,.27),center=(2.02,y,.76),color=iron))
for j,x in enumerate([1.48,2.56]):
    add(tray,'end'+str(j),box((.06,.64,.27),center=(x,-.48,.76),color=wood))
beam(tray,'pull',(1.89,-.85,.76),(2.13,-.85,.76),.025,rust)
tray.move((-.45,-.12,-.02))
scene.include('drawer',tray)

tools=Asset('Loose metalworking tools')
for i in range(26):
    x=random.uniform(-4.7,3.7)
    y=random.uniform(-.04,.65)
    beam(tools,'file'+str(i),(x,y,1.15),(x+.27,y+.05,1.17),.018,steel)
    beam(tools,'handle'+str(i),(x-.12,y-.02,1.15),(x,y,1.15),.026,wood)
for i,x in enumerate([1.22,1.46,2.95,-1.42]):
    add(tools,'plate'+str(i),box((.30,.25,.026),center=(x,.02,1.15),color=(.36,.36,.30)))
for i,x in enumerate([-3.75,-2.9,-1.15,.1,2.95]):
    add(tools,'block'+str(i),box((.16,.20,.15),center=(x,.80,1.21),color=rust))
scene.include('tools',tools)

storage=Asset('Under bench storage')
for i,(x,y,r,h) in enumerate([(2.05,-.32,.29,.53),(3.25,.08,.34,.61),(-2.8,.22,.25,.52)]):
    col=(.43,.43,.34) if i==0 else (.20,.23,.16)
    beam(storage,'bin'+str(i),(x,y,.045),(x,y,h),r,col)
    beam(storage,'opening'+str(i),(x,y,h+.002),(x,y,h+.018),r*.85,(.065,.07,.045))
    beam(storage,'scrap'+str(i),(x-.08,y,h-.05),(x+.08,y,h+.15),.055,wood)
    for j in range(2):
        z=.10+j*(h-.13)
        beam(storage,f'band{i}_{j}',(x,y,z),(x,y,z+.025),r*1.015,iron)
for i in range(6):
    x=-.50+i*.11
    beam(storage,'stock'+str(i),(x,-.22,.08),(x-.18,-.10,1.08),.018,rust)
for i,x in enumerate([-4.3,-3.4,-1.5]):
    add(storage,'box'+str(i),box((.57,.54,.45),center=(x,.34,.27),color=(.16,.17,.115)))
scene.include('storage',storage)

walltools=Asset('Wall rods and window objects')
for i,x in enumerate([-4.8,-3.0,-1.1,.05,3.3,4.2]):
    beam(walltools,'hanging'+str(i),(x,1.10,1.34),(x+.12,1.10,2.60),.022,rust)
for i in range(18):
    x=-5+i*.50
    h=random.uniform(.12,.28)
    beam(walltools,'bottle'+str(i),(x,1.03,1.80),(x,1.03,1.80+h),.046,
         random.choice([steel,rust,(.24,.28,.23)]))
    beam(walltools,'neck'+str(i),(x,1.03,1.80+h),(x,1.03,1.87+h),.022,iron)
scene.include('walltools',walltools)

marker=Asset('Aisle direction marker')
add(marker,'disc',rod(.29,start=(-1.70,-2.02,.003),end=(-1.70,-2.02,.008),color=(.22,.30,.32)))
add(marker,'shaft',box((.105,.24,.004),center=(-1.70,-2.01,.012),color=(.70,.73,.68)))
for i in range(4):
    add(marker,'arrow'+str(i),box((.27-i*.065,.045,.004),
        center=(-1.70,-2.12-i*.04,.012),color=(.70,.73,.68)))
scene.include('marker',marker)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    if bs is None:
        continue
    col=tuple(bs.inputs['Base Color'].default_value)
    bs.inputs['Roughness'].default_value=.85
    if max(col[:3])-min(col[:3])<.08 and max(col[:3])<.48:
        bs.inputs['Metallic'].default_value=.60
        bs.inputs['Roughness'].default_value=.64
    tex=nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=24
    tex.inputs['Detail'].default_value=3
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.30
    bump.inputs['Distance'].default_value=.018
    mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if max(col[:3])>.75:
        bs.inputs['Emission Color'].default_value=(.72,.83,.89,1)
        bs.inputs['Emission Strength'].default_value=.65
    else:
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(col[0]*.48,col[1]*.48,col[2]*.48,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(col[0]*1.15,col[1]*1.15,col[2]*1.15,1)
        mat.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
        mat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])

CAMERA_POSITION=(5.3,-4.7,3.5)
CAMERA_TARGET=(-.85,.30,1.12)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=43,sensor=36)
area_emitter((-.5,.5,4.7),power=550,size=4,target=(-.4,-.2,.7),color=(.84,.91,1))
area_emitter((3,-3,3.8),power=130,size=4,target=(0,.3,1),color=(1,.88,.71))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.43,.49,.54,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.22
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
