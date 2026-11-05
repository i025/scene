from sceneact import *
import bpy, math, random
random.seed(12)

scene = Scene('Colorful cafe')
def add(name, node):
    scene.include(name, node)
    return node

pink = (.62,.035,.29)
pinklight = (.72,.055,.36)
charcoal = (.075,.11,.12)
wood = (.43,.22,.075)

add('floor', box((12,12,.12), center=(0,0,-.06), color=(.52,.46,.37)))
for i in range(-8,9):
    add('floor_joint_'+str(i), box((.008,12,.002), center=(i*.52,0,.003), color=(.33,.30,.25)))
add('rear_room', box((10,.15,4.1), center=(0,3.45,2), color=(.78,.77,.64)))
add('rear_window', box((5,.04,2.9), center=(0,3.32,1.8), color=(.86,.96,.92)))
for x in [-2.3,-1.3,-.3,.7,1.7,2.7]:
    add('rear_mullion_'+str(x), box((.055,.10,3.0), center=(x,3.23,1.8), color=(.38,.43,.41)))
add('rear_gold_panel', box((.5,.13,3.3), center=(1.45,3.15,1.9), color=(.56,.36,.08)))

# Open shelving partition.
for k,z in enumerate([1.65,2.23,2.82,3.36]):
    add('shelf_horizontal_'+str(k), box((5.8,.36,.13), center=(0,2.35,z), color=charcoal))
for k,x in enumerate([-2.45,-1.37,-.39,.63,1.65,2.6]):
    add('shelf_upright_'+str(k), box((.16,.33,1.82), center=(x,2.36,2.49), color=(.13,.17,.17)))
for k,x in enumerate([-1.38,.63,2.6]):
    add('gold_edge_'+str(k), box((.045,.345,1.78), center=(x-.10,2.34,2.48), color=(.61,.43,.12)))

def plant(name,x,y,z,scale=1):
    a=Asset(name)
    potheight=.18*scale
    a.include('pot', rod(.095*scale, length=potheight,
                        center=(x,y,z+potheight/2), color=(.09,.14,.13)))
    a.include('rim', rod(.106*scale,length=.025*scale,
                        center=(x,y,z+potheight),color=(.16,.22,.20)))
    for j in range(11):
        angle=random.uniform(0,math.tau)
        length=random.uniform(.17,.34)*scale
        dx=math.cos(angle)*random.uniform(.06,.15)*scale
        dy=math.sin(angle)*random.uniform(.06,.15)*scale
        start=(x,y,z+potheight*.8)
        end=(x+dx,y+dy,z+potheight+length*.78)
        a.include('stem'+str(j),rod(.008*scale,start=start,end=end,color=(.10,.28,.07)))
        leaf=ball(1,center=(0,0,0),color=random.choice([(.10,.35,.10),(.16,.43,.12),(.025,.26,.12),(.25,.46,.13)]))
        leaf.resize((.035*scale,.023*scale,length*.57))
        leaf.turn(euler=(random.uniform(-35,35),random.uniform(-35,35),math.degrees(angle)))
        leaf.move((x+dx,y+dy,z+potheight+length*.68))
        a.include('leaf'+str(j),leaf)
    add(name,a)

for row,z in enumerate([1.72,2.30,2.89]):
    xs=[-2.05,-1.65,-.88,.05,1.18,1.90,2.25] if row!=1 else [-2.0,-1.15,-.65,.15,.82,1.55,2.1]
    for j,x in enumerate(xs):
        plant('plant_%s_%s'%(row,j),x,2.24,z,random.uniform(.75,1.12))

# Upholstered bench.
couch=Asset('magenta velvet banquette')
couch.include('base',fillet_box((4.45,1.13,.52),.10,center=(-.18,1.07,.39),color=pink))
couch.include('front_apron',fillet_box((4.45,.18,.40),.07,center=(-.18,.53,.39),color=(.59,.027,.26)))
couch.include('back',fillet_box((4.45,.30,.97),.12,center=(-.18,1.65,1.13),color=pinklight))
for i in range(4):
    couch.include('seat_'+str(i),fillet_box((1.10,1.03,.22),.095,center=(-1.83+i*1.1,1.02,.70),color=(.69,.043,.32)))
# Small pinched upholstery buttons and diagonal stitched diamonds.
for row in range(3):
    z=.86+row*.30
    for col in range(13):
        x=-2.19+col*.36+(row%2)*.18
        if x>2.0: continue
        couch.include('tuft_%s_%s'%(row,col),ball(.026,center=(x,1.483,z),color=(.37,.012,.15)))
        for sign in [-1,1]:
            if z+.28 <1.64:
                couch.include('crease_%s_%s_%s'%(row,col,sign),
                    sweep_tube(points=[(x,1.489,z),(x+sign*.085,1.484,z+.07),(x+sign*.17,1.49,z+.15)],radius=.005,color=(.50,.025,.23)))
for x in [-2.05,1.66]:
    for y in [.73,1.4]:
        couch.include('foot'+str(x)+str(y),rod(.045,length=.19,center=(x,y,.12),color=(.11,.075,.055)))
add('sofa',couch)

def pillow(name,x,y,z,color,sx=.36,sz=.40):
    p=ball(1,color=color)
    p.resize((sx,.13,sz))
    p.move((x,y,z))
    add(name,p)
    # A softly rounded fabric edge.
    pts=[]
    for j in range(65):
        t=j*math.tau/64
        pts.append((x+sx*.96*math.cos(t),y-.025,z+sz*.96*math.sin(t)))
    add(name+'_piping',sweep_tube(points=pts,radius=.009,color=tuple(v*.84 for v in color)))
pillow('ochre_round_cushion',-.99,1.21,1.03,(.64,.25,.065),.31,.36)
pillow('pink_round_cushion',1.28,1.20,.99,(.64,.055,.31),.36,.40)
pillow('small_orange_cushion',.69,1.30,.86,(.57,.21,.055),.32,.22)

# Round cafe table with slender metal pedestal.
table=Asset('round cafe table')
table.include('top',rod(.65,length=.065,center=(.02,.05,1.03),color=(.53,.29,.10)))
table.include('edge',rod(.655,length=.023,center=(.02,.05,1.005),color=(.39,.20,.065)))
for j in range(5):
    a=j*math.tau/5
    x=.02+.13*math.cos(a); y=.05+.13*math.sin(a)
    table.include('upright_'+str(j),rod(.019,start=(x,y,.10),end=(x,y,.998),color=(.025,.035,.035)))
    table.include('foot_'+str(j),rod(.019,start=(x,y,.12),end=(.02+.40*math.cos(a),.05+.40*math.sin(a),.04),color=(.025,.035,.035)))
table.include('collar',rod(.22,length=.045,center=(.02,.05,.81),color=(.035,.045,.04)))
add('table',table)
add('napkin_holder',box((.18,.12,.13),center=(-.17,.03,1.13),color=(.13,.16,.16)))
add('white_napkins',box((.13,.025,.15),center=(-.17,.035,1.15),color=(.90,.89,.80)))
add('little_bottle',rod(.035,length=.19,center=(.01,.10,1.16),color=(.64,.69,.62)))
add('bottle_cap',rod(.022,length=.045,center=(.01,.10,1.28),color=(.65,.63,.56)))
add('ashtray',rod(.105,length=.038,center=(.26,-.01,1.085),color=(.64,.68,.65)))
add('ashtray_inner',rod(.075,length=.007,center=(.26,-.01,1.108),color=(.38,.43,.41)))

# Green tub chair, seen from behind.
green=(.025,.22,.13)
chair=Asset('green foreground chair')
seat=ball(1,color=green)
seat.resize((.57,.49,.105))
seat.move((-.44,-1.13,.55))
chair.include('seat',seat)
# Dense horizontal arcs form a continuous curved upholstered shell.
for layer in range(24):
    z=.57+layer*.023
    r=.50+.055*math.sin((layer/23)*math.pi)
    pts=[]
    for j in range(49):
        a=math.radians(178+184*j/48)
        pts.append((-.44+r*math.cos(a),-1.08+.43*math.sin(a),z))
    chair.include('back_layer_'+str(layer),sweep_tube(points=pts,radius=.037,color=green))
for x in [-.84,-.07]:
    for y in [-1.43,-.88]:
        chair.include('leg'+str(x)+str(y),rod(.026,start=(x,y,.55),end=(x+(x+.44)*.20,y-.05,.015),color=(.035,.045,.038)))
add('chair',chair)

# Cropped tan chair and table at the edges.
add('left_table',rod(.52,length=.065,center=(-2.0,-.30,.91),color=(.55,.33,.12)))
tan=(.60,.38,.18)
for layer in range(19):
    pts=[]
    for j in range(35):
        a=math.radians(175+155*j/34)
        pts.append((1.54+.54*math.cos(a),-1.92+.46*math.sin(a),.51+layer*.025))
    add('tan_chair_'+str(layer),sweep_tube(points=pts,radius=.036,color=tan))

# Dark counter at right, with foliage above.
add('right_counter',box((.66,2.20,1.53),center=(2.06,.27,.765),color=(.045,.033,.034)))
add('counter_top',box((.81,2.29,.065),center=(2.02,.26,1.56),color=(.035,.046,.037)))
plant('large_right_plant',2.03,1.3,1.60,2.0)
for k in range(5):
    leaf=ball(1,color=(.035,.22,.075))
    leaf.resize((.15,.045,.52))
    leaf.turn(euler=(15,(-1)**k*38,k*50))
    leaf.move((1.95+random.uniform(-.25,.3),1.60,2.13+random.uniform(-.1,.3)))
    add('broad_leaf_'+str(k),leaf)

# Bright tiled ceiling: each panel is individually colored and framed.
add('ceiling_dark_base',box((9,9,.09),center=(0,.4,3.62),color=(.015,.035,.033)))
palette=[(.02,.30,.55),(.06,.45,.54),(.16,.47,.18),(.64,.14,.38),
         (.79,.43,.045),(.26,.58,.51),(.16,.25,.60),(.69,.71,.39)]
for iy in range(12):
    for ix in range(11):
        x=(ix-5)*.61
        y=-3.45+iy*.65
        col=palette[(ix+iy*3+random.randrange(3))%len(palette)]
        add('ceiling_tile_%d_%d'%(ix,iy),box((.578,.618,.025),center=(x,y,3.562),color=col))
        # Irregular colored patches suggest mottled glass within each panel.
        for p in range(4):
            patch=ball(1,color=tuple(min(.95,c*1.35+.10) for c in col))
            patch.resize((random.uniform(.07,.19),random.uniform(.05,.16),.002))
            patch.turn('z',random.uniform(0,180))
            patch.move((x+random.uniform(-.16,.16),y+random.uniform(-.18,.18),3.546))
            add('glass_pattern_%d_%d_%d'%(ix,iy,p),patch)

# Warm light points in the room beyond the shelves.
for i in range(7):
    x=-2.0+i*.61
    add('background_bulb_'+str(i),ball(.037,center=(x,3.05,2.56+(.08 if i%2 else 0)),color=(1,.88,.55)))

realize(scene)

# Soft velvet, matte ceramics, and subtle tabletop sheen.
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth=True
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bs=mat.node_tree.nodes.get('Principled BSDF')
                if bs:
                    bs.inputs['Roughness'].default_value=.64
                    if 'Sheen Weight' in bs.inputs:
                        bs.inputs['Sheen Weight'].default_value=.16

set_view((.05,-4.65,2.08),(.04,1.35,1.92),lens=53)
camera=bpy.context.scene.camera
camera.data.sensor_fit='HORIZONTAL'
area_emitter((-.6,-1.5,3.35),power=650,size=4.0,target=(0,1,1.0),color=(1.0,.91,.78))
area_emitter((0,3.08,2.25),power=1000,size=3.6,target=(0,0,1.0),color=(.83,.95,1.0))
area_emitter((-3,-.4,2.5),power=350,size=3,target=(0,1,1),color=(1,.94,.86))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.31,.38,.40,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
sc=bpy.context.scene
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'
