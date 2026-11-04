from sceneact import *
import bpy, math, random
random.seed(13)

# Bench runs from upper left (0.05,.30) toward lower right (.98,.69).
# Large drive wheel occupies (.60,.13)-(.75,.38).
# Anvil sits near (.39,.33)-(.55,.47).
# Front vise projects into the aisle around (.49,.58)-(.73,.79).
# Pale window wall fills the upper right; wood floor fills lower left.
# Foreground bench and bins obscure the wall-floor boundary.

scene = Scene('Historic metalworking shop')
wood = (.25,.205,.135)
edgewood = (.35,.29,.19)
iron = (.13,.145,.135)
steel = (.32,.34,.32)
rust = (.24,.18,.12)
wall = (.58,.62,.56)
cream = (.73,.73,.63)

def add(parent, name, shape):
    parent.include(name, shape)

def beam(parent, name, a, b, r=.025, color=iron):
    add(parent, name, rod(r, start=a, end=b, color=color))

def wheel(parent, name, x, y, z, radius, color=iron, spokes=6):
    # Vertical wheel, with its axle perpendicular to the back wall.
    n = 22
    for j in range(n):
        a = 2*math.pi*j/n
        b = 2*math.pi*(j+1)/n
        beam(parent, name+'rim'+str(j),
             (x+radius*math.cos(a),y,z+radius*math.sin(a)),
             (x+radius*math.cos(b),y,z+radius*math.sin(b)), .026, color)
    for j in range(spokes):
        a = 2*math.pi*j/spokes+.15
        beam(parent,name+'spoke'+str(j),(x,y,z),
             (x+radius*.94*math.cos(a),y,z+radius*.94*math.sin(a)), .028,color)
    beam(parent,name+'hub',(x,y-.085,z),(x,y+.085,z),.075,color)

# Long floorboards with visible narrow joints.
floor = Asset('Worn plank floor')
for i in range(27):
    yy = -5.2+i*.245
    add(floor,'plank'+str(i),box((12,.236,.075),center=(-.3,yy,-.045),
        color=(.40+random.uniform(-.045,.045),.33+random.uniform(-.025,.025),.23+random.uniform(-.02,.02))))
for i in range(26):
    xx = random.uniform(-5,5)
    yy = -5.2+i*.245
    add(floor,'end_joint'+str(i),box((.012,.235,.002),center=(xx,yy,-.006),color=(.16,.14,.10)))
scene.include('floor',floor)

architecture = Asset('Plaster walls and tall windows')
add(architecture,'back_lower',box((12,.17,1.65),center=(-.6,1.27,.825),color=wall))
add(architecture,'back_upper',box((12,.17,.6),center=(-.6,1.27,3.65),color=wall))
for i,x in enumerate([-5.4,-3.2,-.9,1.4,3.7]):
    add(architecture,'pier'+str(i),box((.30,.19,2.1),center=(x,1.26,2.55),color=wall))
for i,x in enumerate([-4.3,-2.05,.25,2.55]):
    add(architecture,'daylight'+str(i),box((1.86,.045,1.76),center=(x,1.34,2.64),color=(.83,.90,.91)))
    add(architecture,'sill'+str(i),box((2.10,.40,.09),center=(x,1.09,1.74),color=(.31,.34,.31)))
    for j,xx in enumerate([x-.94,x,x+.94]):
        add(architecture,f'frame{i}_{j}',box((.047,.10,1.9),center=(xx,1.23,2.65),color=(.34,.38,.36)))
    add(architecture,'crossbar'+str(i),box((1.9,.1,.045),center=(x,1.23,2.63),color=(.43,.46,.42)))
# Rough exposed masonry at the distant left.
add(architecture,'left_wall',box((.18,3.3,3.8),center=(-5.6,-.3,1.9),color=(.46,.45,.39)))
for i in range(14):
    x = random.uniform(-5.1,4.6)
    z = random.uniform(.25,1.55)
    add(architecture,'plaster_patch'+str(i),box((random.uniform(.12,.40),.012,random.uniform(.10,.33)),
        center=(x,1.174,z),color=(.47,.51,.45)))
scene.include('architecture',architecture)

# Heavy joined workbench, mostly hidden beneath old machine tools.
bench = Asset('Continuous oak workbench')
add(bench,'slab',box((9.4,1.06,.17),center=(-.55,.36,1.03),color=edgewood))
add(bench,'front_apron',box((9.3,.11,.27),center=(-.55,-.15,.83),color=wood))
for i,x in enumerate([-4.9,-3.3,-1.6,.1,1.8,3.7]):
    for j,y in enumerate([-.04,.76]):
        add(bench,f'leg{i}_{j}',box((.16,.17,.94),center=(x,y,.48),color=wood))
    add(bench,'crossfoot'+str(i),box((.22,1.1,.13),center=(x,.34,.15),color=wood))
    add(bench,'stretcher'+str(i),box((1.3,.09,.12),center=(x-.55,.67,.32),color=wood))
scene.include('bench',bench)

def lathe(name,x,length,scale=1.0):
    a=Asset(name)
    z=1.16
    for j,y in enumerate([.14,.49]):
        beam(a,'bedrail'+str(j),(x-length/2,y,z),(x+length/2,y,z),.043,steel)
    for j,xx in enumerate([x-length*.34,x+length*.34]):
        add(a,'foot'+str(j),box((.19,.66,.12),center=(xx,.32,1.13),color=iron))
        add(a,'pedestal'+str(j),box((.17,.26,.30*scale),center=(xx,.32,1.28),color=iron))
    beam(a,'spindle',(x-length*.47,.32,1.48),(x+length*.56,.32,1.48),.055,steel)
    beam(a,'headstock',(x-length*.32,.32,1.48),(x-length*.06,.32,1.48),.13*scale,iron)
    beam(a,'chuck',(x-length*.03,.32,1.48),(x+length*.07,.32,1.48),.10*scale,steel)
    beam(a,'tailstock',(x+length*.29,.32,1.48),(x+length*.43,.32,1.48),.11*scale,iron)
    add(a,'toolrest',box((.38,.08,.055),center=(x+.10,.09,1.40),color=steel))
    beam(a,'restpost',(x+.1,.09,1.18),(x+.1,.09,1.40),.027)
    beam(a,'crank',(x+length*.56,.32,1.48),(x+length*.56,.32,1.32),.025)
    beam(a,'handle',(x+length*.56,.23,1.32),(x+length*.56,.43,1.32),.032,wood)
    scene.include(name,a)

lathe('Foreground screw cutting lathe',2.20,1.85,1)
lathe('Middle small lathe',-2.35,1.35,.8)
lathe('Far small lathe',-4.20,1.2,.7)

drive=Asset('Tall cast iron belt drive')
for i,x in enumerate([.75,1.22]):
    add(drive,'column'+str(i),box((.075,.13,.95),center=(x,.81,1.63),color=iron))
add(drive,'bearing',box((.66,.22,.12),center=(.99,.80,2.03),color=iron))
wheel(drive,'large',1.03,.67,2.13,.53,(.16,.18,.17),6)
# A second narrow rim gives the flywheel substantial depth.
for j in range(18):
    a=2*math.pi*j/18
    b=2*math.pi*(j+1)/18
    beam(drive,'rear_rim'+str(j),(1.03+.48*math.cos(a),.79,2.13+.48*math.sin(a)),
         (1.03+.48*math.cos(b),.79,2.13+.48*math.sin(b)),.018,rust)
beam(drive,'axle',(1.03,.52,2.13),(1.03,1.02,2.13),.05)
beam(drive,'crank_arm',(1.03,.48,2.13),(1.28,.48,1.92),.03)
beam(drive,'crank_grip',(1.28,.32,1.92),(1.28,.53,1.92),.035,wood)
scene.include('drive',drive)

smallwheel=Asset('Blue gray middle wheel')
wheel(smallwheel,'wheel',-2.10,.66,1.89,.34,(.23,.34,.37),6)
beam(smallwheel,'stand',(-2.10,.70,1.11),(-2.10,.70,1.91),.055)
scene.include('middlewheel',smallwheel)

# Anvil with a broad striking surface, waisted body and tapering horn.
anvil=Asset('Large iron anvil')
add(anvil,'base',box((.64,.44,.10),center=(-.60,.29,1.17),color=rust))
add(anvil,'waist',box((.31,.28,.35),center=(-.60,.29,1.36),color=rust))
add(anvil,'shoulder',box((.53,.37,.18),center=(-.60,.29,1.55),color=(.29,.23,.15)))
add(anvil,'face',box((.72,.40,.09),center=(-.56,.29,1.68),color=(.40,.35,.25)))
for i in range(5):
    beam(anvil,'horn'+str(i),(-.19+i*.10,.29,1.61),(-.08+i*.10,.29,1.61),
         .14-i*.027,(.33,.28,.19))
scene.include('anvil',anvil)

vise=Asset('Heavy projecting front vise')
add(vise,'fixed_jaw',box((.47,.17,.19),center=(.82,-.19,1.10),color=iron))
add(vise,'moving_jaw',box((.47,.15,.19),center=(.82,-.59,1.10),color=steel))
for j,y in enumerate([-.20,-.60]):
    add(vise,'jawface'+str(j),box((.48,.06,.055),center=(.82,y,1.21),color=steel))
beam(vise,'slide',(.82,-.73,.91),(.82,.16,.91),.09,iron)
beam(vise,'screw',(.82,-.88,.94),(.82,-.15,.94),.038,steel)
beam(vise,'crossbar',(.57,-.86,.94),(1.07,-.86,.94),.024,steel)
for j,x in enumerate([.56,1.08]):
    add(vise,'knob'+str(j),ball(.043,center=(x,-.86,.94),color=iron))
beam(vise,'support',(.82,-.27,.18),(.82,-.27,.98),.055)
scene.include('vise',vise)

# Wooden open tray along the front of the bench.
tray=Asset('Open tool drawer')
add(tray,'bottom',box((1.04,.56,.06),center=(2.02,-.44,.64),color=wood))
for j,y in enumerate([-.72,-.17]):
    add(tray,'longwall'+str(j),box((1.1,.065,.27),center=(2.02,y,.76),color=iron))
for j,x in enumerate([1.48,2.56]):
    add(tray,'end'+str(j),box((.06,.56,.27),center=(x,-.44,.76),color=wood))
beam(tray,'pull',(1.89,-.77,.76),(2.13,-.77,.76),.025,rust)
scene.include('drawer',tray)

tools=Asset('Loose metalworking tools')
for i in range(13):
    x=random.uniform(-4.7,3.7)
    y=random.uniform(-.04,.65)
    beam(tools,'file'+str(i),(x,y,1.14),(x+.27,y+.05,1.16),.018,steel)
    beam(tools,'handle'+str(i),(x-.12,y-.02,1.14),(x,y,1.14),.026,wood)
for i,x in enumerate([1.22,1.46,2.95,-1.42]):
    add(tools,'plate'+str(i),box((.30,.25,.026),center=(x,.02,1.15),color=(.47,.47,.41)))
for i,x in enumerate([-3.75,-2.9,-1.15,.1,2.95]):
    add(tools,'block'+str(i),box((.16,.20,.15),center=(x,.80,1.21),color=rust))
scene.include('tools',tools)

# Bins, stock and buckets under the bench.
storage=Asset('Under bench storage')
for i,(x,y,r,h) in enumerate([(2.75,-.15,.29,.53),(3.85,.26,.34,.61),(-2.8,.22,.25,.52)]):
    beam(storage,'binbody'+str(i),(x,y,.08),(x,y,h),r,(.37,.36,.27))
    beam(storage,'darkopening'+str(i),(x,y,h+.002),(x,y,h+.018),r*.85,(.15,.15,.10))
    beam(storage,'scrap'+str(i),(x-.08,y,h-.05),(x+.08,y,h+.15),.055,wood)
for i in range(6):
    x=-.05+i*.11
    beam(storage,'long_stock'+str(i),(x,-.22,.08),(x-.18,-.10,1.08),.018,rust)
for i,x in enumerate([-4.3,-3.4,-1.5]):
    add(storage,'box'+str(i),box((.57,.54,.45),center=(x,.34,.27),color=(.27,.27,.20)))
scene.include('storage',storage)

walltools=Asset('Wall mounted rods and window objects')
for i,x in enumerate([-4.8,-3.0,-1.1,.05,3.3,4.2]):
    beam(walltools,'hanging'+str(i),(x,1.10,1.34),(x+.12,1.10,2.42),.022,rust)
for i in range(14):
    x=-5.0+i*.61
    h=random.uniform(.12,.28)
    beam(walltools,'bottle'+str(i),(x,1.03,1.80),(x,1.03,1.80+h),.046,
         random.choice([steel,rust,(.42,.44,.39)]))
    beam(walltools,'neck'+str(i),(x,1.03,1.80+h),(x,1.03,1.87+h),.022,iron)
scene.include('walltools',walltools)

realize(scene)

# Modest procedural variation gives timber, plaster and iron worn surfaces.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    if not bs:
        continue
    col=bs.inputs['Base Color'].default_value
    bs.inputs['Roughness'].default_value=.83
    if max(col[:3])-min(col[:3])<.08 and max(col[:3])<.48:
        bs.inputs['Metallic'].default_value=.5
        bs.inputs['Roughness'].default_value=.67
    tex=nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=37
    tex.inputs['Detail'].default_value=3
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.24
    bump.inputs['Distance'].default_value=.025
    mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if max(col[:3])>.80:
        bs.inputs['Emission Color'].default_value=(.72,.82,.86,1)
        bs.inputs['Emission Strength'].default_value=.65

CAMERA_POSITION=(6.3,-7.4,4.3)
CAMERA_TARGET=(-.45,.18,1.30)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=43,sensor=36)
area_emitter((-.5,.6,4.8),power=1300,size=5,target=(-.4,-.2,.7),color=(.84,.91,1))
area_emitter((3,-3,3.8),power=450,size=4,target=(0,.3,1),color=(1,.88,.71))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.49,.55,.59,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
