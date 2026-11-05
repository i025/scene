from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(12)

# Reference inventory (normalized image bounds, approximate):
# Ceiling 0,0–1,.20: colored translucent rectangular panels in dark grid.
# Rear partition 0,.19–1,.56: three open shelf rows, dark horizontal
# beams, pale vertical piers, plants in separate openings; bright cafe behind.
# Magenta banquette 0,.55–.91,.90: tufted tall back, broad seat,
# orange round cushion left and plum round cushion right; ends cropped.
# Round wood table .33,.64–.71,.91: thin top, black pedestal and feet;
# small bottle, dark holder and clear dish on top.
# Green foreground chair .13,.75–.58,1: curved shell and slender dark legs.
# Tan chair .75,.84–1,1 and small tan seat at left .0,.69–.07,.82.
# Dark planter/cabinet .89,.56–1,1 with broad green leaves above.
# Floor visible below seating, pale tiles with dark joints.
# Uncertain: details behind shelf plants, couch ends, rear room geometry.
# Named assets below preserve these memberships and visible occlusions.
# Expanded primitive estimate: architecture/grid ~100, sofa ~95,
# 20 plants ~180, furniture and props ~55, foreground foliage ~16:
# approximately 450 meshes. No fillet_box, booleans or long tube paths.

scene = Scene('Colorful cafe interior')
dark = (.065,.09,.095)
cream = (.83,.81,.65)
pink = (.57,.035,.28)
wood = (.49,.25,.095)
green = (.035,.23,.135)

def add_asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def ell(parent, name, center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale)
    parent.include(name, n)
    return n

def cube(parent, name, size, center, color):
    n = box(size=size, center=center, color=color)
    parent.include(name,n)
    return n

def cyl(parent,name,radius,start,end,color):
    n=rod(radius=radius,start=start,end=end,color=color)
    parent.include(name,n)
    return n

floor=add_asset('pale tiled floor')
cube(floor,'floor',(12,13,.12),(0,1,-.08),(.63,.61,.52))
for x in [-3,-2,-1,0,1,2,3]:
    cube(floor,'vertical grout '+str(x),(.014,11,.004),(x,0,-.016),(.27,.28,.25))
for y in [-4,-3,-2,-1,0,1,2,3,4]:
    cube(floor,'horizontal grout '+str(y),(10,.014,.004),(0,y,-.015),(.28,.28,.25))

rear=add_asset('bright room behind open partition')
cube(rear,'back wall',(10,.12,3.8),(0,3.4,1.9),(.84,.79,.59))
# Broad bright window fields behind the open shelves.
for i,x in enumerate([-2.2,-1.1,0,1.1,2.2]):
    cube(rear,'window '+str(i),(.93,.035,2.4),(x,3.31,1.62),(.84,.94,.91))
    cube(rear,'window upright '+str(i),(.045,.09,2.6),(x-.51,3.24,1.7),(.27,.32,.29))
cube(rear,'warm rear fascia',(6,.12,.22),(0,3.17,2.63),(.68,.45,.16))
for i,x in enumerate([-1.65,-.75,.5,1.55]):
    cyl(rear,'hanging light cord '+str(i),.009,(x,2.8,2.74),(x,2.8,2.42),dark)
    ell(rear,'white pendant '+str(i),(x,2.8,2.40),(.048,.048,.07),(1,.94,.75))

shelf=add_asset('open architectural plant shelving')
# Dark bands, pale piers and openings remain explicitly parameterized.
shelf_y=1.85
for i,z in enumerate([1.68,2.22,2.78,3.28]):
    cube(shelf,'charcoal horizontal beam '+str(i),(5.7,.35,.13),(0,shelf_y,z),(.115,.145,.15))
for row,(z,h) in enumerate([(1.95,.42),(2.50,.43),(3.02,.38)]):
    xs=[-2.10,-1.20,-.24,.82,1.83] if row!=1 else [-2.10,-1.43,-.43,.65,1.63]
    for j,x in enumerate(xs):
        cube(shelf,'pale pier %d %d'%(row,j),(.19,.35,h),(x,shelf_y,z),cream)
cube(shelf,'top shadow',(6,.5,.13),(0,1.9,3.40),(.035,.065,.075))

def plant(name,x,y,z,scale=1):
    a=add_asset(name)
    # z is the support surface; five irregular spear leaves create visible gaps.
    cyl(a,'dark flowerpot',.065*scale,(x,y,z),(x,y,z+.14*scale),(.065,.15,.125))
    for k in range(6):
        ang=k*2.399
        spread=(.10 if k<4 else .065)*scale
        end=(x+math.cos(ang)*spread,y+math.sin(ang)*spread,z+(.29+random.random()*.12)*scale)
        cyl(a,'stem '+str(k),.007*scale,(x,y,z+.10*scale),end,(.10,.29,.10))
        leaf=ell(a,'leaf '+str(k),end,(.035*scale,.022*scale,.105*scale),
                 [(.08,.34,.12),(.14,.43,.18),(.035,.26,.11)][k%3])
        leaf.turn(axis='+y',degrees=math.sin(ang)*30)
    return a

for row,z in enumerate([1.755,2.295,2.855]):
    positions=[-1.88,-1.05,-.49,.28,1.05,1.65]
    if row==1: positions=[-2.1,-1.42,-.90,-.06,.52,1.30,1.91]
    for j,x in enumerate(positions):
        plant('shelf plant %d %d'%(row,j),x,1.63,z,.78+random.random()*.22)

sofa=add_asset('magenta tufted velvet banquette')
cube(sofa,'low plinth',(4.6,.81,.17),(0,.89,.20),(.25,.025,.12))
ell(sofa,'rounded front upholstered base',(0,.78,.43),(2.35,.54,.25),pink)
# Plush broad back, soft scalloped top.
cube(sofa,'back upholstered core',(4.65,.28,.93),(0,1.29,1.10),pink)
for i in range(15):
    x=-2.22+i*.32
    ell(sofa,'back top roll '+str(i),(x,1.245,1.55),(.205,.19,.17),(.61,.045,.31))
# Tuft cushions and dark indent buttons distributed across back.
for row,z in enumerate([.87,1.16,1.42]):
    for j in range(14):
        x=-2.1+j*.33+(row%2)*.12
        ell(sofa,'soft quilt field %d %d'%(row,j),(x,1.105,z),(.215,.075,.18),
            (.58+.015*(j%3),.038,.285))
        ell(sofa,'tuft button %d %d'%(row,j),(x+.14,1.019,z+.10),(.022,.013,.022),(.32,.018,.145))
for j,x in enumerate([-1.52,-.51,.51,1.52]):
    ell(sofa,'seat cushion '+str(j),(x,.76,.64),(.56,.48,.13),(.62,.045,.31))
# Round velvet throw cushions, flattened in depth.
ell(sofa,'left burnt orange round cushion',(-.99,.85,1.12),(.265,.13,.30),(.65,.23,.065))
ell(sofa,'right purple round cushion',(1.03,.78,1.04),(.28,.135,.30),(.53,.035,.27))
ell(sofa,'small ochre cushion behind tabletop',(.38,1.00,.96),(.27,.115,.24),(.58,.22,.055))

table=add_asset('round central cafe table')
tx,ty=.05,.01
cyl(table,'thin round oak top',.58,(tx,ty,1.005),(tx,ty,1.065),wood)
cyl(table,'top edge highlight',.582,(tx,ty,1.044),(tx,ty,1.064),(.61,.34,.14))
cyl(table,'black center pedestal',.046,(tx,ty,.10),(tx,ty,1.01),(.025,.035,.034))
for i,ang in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
    ex=tx+.34*math.cos(ang); ey=ty+.34*math.sin(ang)
    cyl(table,'foot '+str(i),.026,(tx,ty,.12),(ex,ey,.045),dark)
# Two narrow vertical support bars are visible beneath the tabletop.
for i,x in enumerate([-.09,.12]):
    cyl(table,'pedestal outer brace '+str(i),.018,(x,ty,.12),(x,ty,.94),dark)
props=add_asset('tabletop bottle holder and glass dish')
cube(props,'black napkin holder',(.16,.09,.085),(-.11,-.03,1.108),(.045,.06,.06))
cube(props,'paper napkins',(.115,.018,.07),(-.11,-.033,1.145),(.81,.80,.70))
cyl(props,'small clear bottle body',.032,(.025,.05,1.065),(.025,.05,1.22),(.60,.73,.69))
cyl(props,'bottle neck',.013,(.025,.05,1.20),(.025,.05,1.29),(.56,.67,.62))
cyl(props,'metal bottle cap',.016,(.025,.05,1.278),(.025,.05,1.30),(.25,.26,.22))
cyl(props,'glass ashtray',.092,(.18,-.035,1.065),(.18,-.035,1.095),(.65,.68,.61))
cyl(props,'ashtray inner shadow',.064,(.18,-.035,1.094),(.18,-.035,1.099),(.39,.42,.38))

chair=add_asset('foreground emerald curved chair')
cx,cy=-.53,-1.42
ell(chair,'green seat',(cx,cy,.52),(.49,.40,.095),(.035,.24,.14))
# Curved barrel back built with one continuous low-resolution custom surface
# from SceneAct rods and stretched balls, retaining the open space below.
# Back is nearest the viewer and rises at both sides.
ell(chair,'broad bowed back',(cx,cy-.24,.83),(.52,.12,.32),green)
for i,side in enumerate([-1,1]):
    ell(chair,'rounded wing '+str(i),(cx+side*.44,cy-.05,.85),(.10,.30,.26),(.035,.21,.115))
for i,(dx,dy) in enumerate([(-.34,-.22),(.34,-.22),(-.31,.22),(.31,.22)]):
    cyl(chair,'slender black leg '+str(i),.022,(cx+dx,cy+dy,.51),
        (cx+dx*1.15,cy+dy*1.16,-.02),(.035,.045,.035))

tan=add_asset('cropped foreground tan chair')
ell(tan,'tan shell',(1.40,-1.90,.66),(.49,.38,.15),(.63,.41,.20))
ell(tan,'tan curved back',(1.40,-2.12,.93),(.49,.085,.30),(.72,.48,.25))
for i,x in enumerate([1.10,1.70]):
    cyl(tan,'leg '+str(i),.025,(x,-1.9,.61),(x,-1.9,-.1),dark)
left=add_asset('cropped left tan chair')
ell(left,'left seat',(-1.85,-.18,.65),(.38,.36,.15),(.52,.33,.12))

cab=add_asset('right dark planter pedestal')
cube(cab,'tall dark cabinet',(.66,.64,1.49),(1.73,.41,.745),(.065,.052,.048))
cube(cab,'projecting cap',(.76,.72,.055),(1.73,.41,1.515),(.10,.11,.075))
for i in range(8):
    ang=i*2.4
    base=(1.77,.62,1.55)
    tip=(1.77+math.cos(ang)*.48,.62+math.sin(ang)*.30,1.93+random.random()*.50)
    cyl(cab,'large plant stem '+str(i),.014,base,tip,(.07,.25,.09))
    leaf=ell(cab,'broad lance leaf '+str(i),tip,(.115,.035,.29),(.035,.23,.085))
    leaf.turn(axis='+y',degrees=35*math.cos(ang))
    leaf.turn(axis='+z',degrees=ang*180/math.pi)

ceiling=add_asset('multicolored glass ceiling grid')
palette=[(.12,.41,.44),(.10,.25,.49),(.51,.67,.57),(.91,.56,.13),
         (.63,.05,.28),(.29,.52,.24),(.15,.44,.65),(.79,.75,.52)]
panel_w=.70
panel_d=.66
for ix in range(9):
    for iy in range(7):
        x=(ix-4)*panel_w
        y=-1.55+iy*panel_d
        col=palette[(ix*3+iy*5)%len(palette)]
        cube(ceiling,'colored panel %d %d'%(ix,iy),(panel_w-.035,panel_d-.035,.035),(x,y,3.53),col)
for ix in range(10):
    cube(ceiling,'long black grid rail '+str(ix),(.035,4.68,.055),((ix-4.5)*panel_w,.43,3.50),(.025,.045,.046))
for iy in range(8):
    cube(ceiling,'cross grid rail '+str(iy),(6.34,.035,.055),(0,-1.88+iy*panel_d,3.50),(.025,.045,.046))

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg is None:
    bg=sc.world.node_tree.nodes.new('ShaderNodeBackground')
out=sc.world.node_tree.nodes.get('World Output')
if out is None:
    out=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface'])
bg.inputs['Color'].default_value=(.69,.77,.79,1)
bg.inputs['Strength'].default_value=.35

# Subtle shared surface variation preserves large color fields while suggesting
# velvet, timber and irregular glass without extra repeated geometry.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    color=bs.inputs['Base Color'].default_value
    bs.inputs['Roughness'].default_value=.69
    if color[0]>.35 and color[2]>.15 and color[1]<.15:
        bs.inputs['Roughness'].default_value=.88
        if 'Sheen Weight' in bs.inputs:
            bs.inputs['Sheen Weight'].default_value=.24
    noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=35
    noise.inputs['Detail'].default_value=2
    bump=mat.node_tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.11
    bump.inputs['Distance'].default_value=.018
    mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view((0,-5.25,1.86),(0,1.0,1.84),lens=48)
camera=sc.camera
camera.data.sensor_fit='VERTICAL'
camera.data.sensor_height=32
area_emitter((0,-2.3,3.25),power=430,size=4,target=(0,.9,1.0),color=(1,.88,.73))
area_emitter((-.7,3.05,2.45),power=800,size=3.0,target=(0,.4,1.4),color=(.85,.97,1))
area_emitter((-3,-.8,2.4),power=240,size=2.7,target=(0,.8,1),color=(1,.92,.82))
sc.render.resolution_x=342
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
