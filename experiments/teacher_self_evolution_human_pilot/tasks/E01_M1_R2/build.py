from sceneact import *
import bpy, math, random
random.seed(8)
scene = Scene('Sage room')
wall=(0.43,0.49,0.40); trim=(0.50,0.44,0.36); dark=(0.17,0.065,0.025); wood=(0.28,0.12,0.045); edge=(0.095,0.038,0.018)
scene.include('floor',box((8,8,.12),center=(0,0,-.08),color=(.65,.64,.60)))
scene.include('back wall',box((8,.16,3.7),center=(0,3.15,1.85),color=wall))
scene.include('right wall',box((.16,8,3.7),center=(4,0,1.85),color=(.46,.51,.42)))
scene.include('left wall',box((.16,8,3.7),center=(-4,0,1.85),color=(.48,.53,.42)))
scene.include('ceiling',box((8,8,.12),center=(0,0,3.76),color=(.69,.69,.65)))
for i in range(25):
    x=i*.32-3.84
    scene.include('floorboard seam %02d'%i,box((.009,8,.004),center=(x,0,-.015),color=(.45,.45,.42)))
for y in (-2.5,-.2,2):
    for i in range(12):
        x=-3.7+i*.64
        scene.include('board joint %.1f %d'%(y,i),box((.32,.008,.003),center=(x,y+(i%3)*.65,-.012),color=(.52,.51,.48)))
scene.include('back skirting',box((8,.09,.17),center=(0,3.03,.09),color=trim))
scene.include('right skirting',box((.09,8,.17),center=(3.91,0,.09),color=trim))
scene.include('back cornice',box((8,.07,.045),center=(0,3.03,3.67),color=(.35,.36,.31)))
scene.include('right cornice',box((.07,8,.045),center=(3.91,0,3.67),color=(.35,.36,.31)))
arch_specs=[]
def window(name,x,width,top,bottom):
    spring=top-width*.60; y=3.045
    scene.include(name+' lower light',box((width-.09,.035,spring-bottom),center=(x,y-.025,(spring+bottom)/2),color=(.81,.86,.80)))
    arch_specs.append((name,x,width,top,spring,y-.05))
    c=(.53,.49,.42)
    scene.include(name+' left jamb',box((.075,.11,spring-bottom+.05),center=(x-width/2,y-.06,(spring+bottom)/2),color=c))
    scene.include(name+' right jamb',box((.075,.11,spring-bottom+.05),center=(x+width/2,y-.06,(spring+bottom)/2),color=c))
    pts=[]
    for i in range(13):
        t=i/12; pts.append((x-width/2+width*.5*t,y-.06,spring+(top-spring)*(1-(1-t)**1.6)))
    for i in range(1,13):
        t=i/12; pts.append((x+width*.5*t,y-.06,top-(top-spring)*t**1.6))
    scene.include(name+' pointed arch frame',sweep_tube(pts,radius=.038,color=c))
    scene.include(name+' sill',box((width+.19,.20,.075),center=(x,y-.10,bottom),color=(.60,.57,.50)))
    scene.include(name+' central mullion',box((.035,.06,spring-bottom),center=(x,y-.10,(spring+bottom)/2),color=(.45,.43,.38)))
    scene.include(name+' cross mullion',box((width,.06,.035),center=(x,y-.10,bottom+(spring-bottom)*.46),color=(.47,.45,.40)))
    scene.include(name+' blind',box((width-.035,.065,.48),center=(x,y-.13,spring-.19),color=(.52,.52,.48)))
    scene.include(name+' blind lower rail',box((width,.07,.025),center=(x,y-.17,spring-.43),color=(.70,.69,.63)))
    for side in (-1,1):
        scene.include(name+' upper branching mullion '+str(side),sweep_tube([(x,y-.11,spring+.02),(x+side*width*.10,y-.11,spring+(top-spring)*.45),(x+side*width*.30,y-.11,spring+(top-spring)*.76)],radius=.017,color=(.48,.46,.42)))
    scene.include(name+' radiator',box((width+.24,.13,.72),center=(x,2.90,bottom-.46),color=(.76,.76,.72)))
    scene.include(name+' radiator top',box((width+.26,.16,.035),center=(x,2.90,bottom-.09),color=(.85,.84,.78)))
window('left window',-1.15,1.10,3.03,1.13)
window('right window',.75,.91,2.90,1.13)
ward=Asset('antique wardrobe')
ward.include('main cabinet',box((1.40,1.05,3.03),center=(-3.02,1.15,1.53),color=wood))
ward.include('left side broad panel',box((1.43,.045,2.85),center=(-3.02,.61,1.57),color=(.30,.12,.035)))
for x in (-3.66,-2.39):
    ward.include('side upright '+str(x),box((.075,.07,2.96),center=(x,.57,1.57),color=dark))
for z in (.23,2.85):
    ward.include('side rail '+str(z),box((1.42,.07,.09),center=(-3.02,.57,z),color=dark))
for y in (.88,1.42):
    ward.include('door panel '+str(y),box((.045,.48,2.49),center=(-2.30,y,1.57),color=(.38,.19,.07)))
    for yy in (y-.21,y+.21):
        ward.include('door vertical molding %.2f'%yy,box((.07,.035,2.35),center=(-2.265,yy,1.58),color=(.16,.07,.025)))
    for z in (.43,2.73):
        ward.include('door horizontal molding %.2f %.2f'%(y,z),box((.07,.44,.04),center=(-2.265,y,z),color=(.18,.075,.025)))
    ward.include('brass handle '+str(y),ball(.025,center=(-2.22,y+.12,1.5),color=(.65,.48,.18)))
ward.include('heavy cornice',box((1.52,1.15,.14),center=(-3.02,1.15,3.08),color=edge))
ward.include('lower plinth',box((1.49,1.13,.16),center=(-3.02,1.15,.18),color=edge))
for x in (-3.56,-2.48):
    for y in (.76,1.55):
        ward.include('foot %.2f %.2f'%(x,y),box((.20,.20,.24),center=(x,y,.12),color=edge))
scene.include('wardrobe',ward)
backchair=Asset('straight chair')
backchair.include('seat',box((.66,.60,.10),center=(-1.98,1.62,.77),color=(.62,.55,.43)))
for x in (-2.26,-1.70):
    for y in (1.37,1.87):
        backchair.include('leg %.2f %.2f'%(x,y),box((.055,.055,.77),center=(x,y,.39),color=edge))
for x in (-2.26,-1.70):
    backchair.include('back post '+str(x),box((.055,.055,.90),center=(x,1.88,1.16),color=edge))
backchair.include('back top',box((.62,.06,.07),center=(-1.98,1.88,1.59),color=edge))
for x in (-2.12,-1.98,-1.84):
    backchair.include('back slat '+str(x),box((.045,.05,.65),center=(x,1.88,1.23),color=edge))
scene.include('straight chair behind cabinet',backchair)
table=Asset('oval pedestal table')
table.include('oval table edge',resized(ball(1,center=(1.40,.65,.91),color=edge),(1.13,.62,.105)))
table.include('polished oval top',resized(ball(1,center=(1.40,.65,.97),color=(.37,.20,.09)),(1.12,.61,.065)))
table.include('central pedestal',rod(.12,start=(1.4,.65,.23),end=(1.4,.65,.89),color=dark))
for z,r in ((.28,.18),(.40,.14),(.72,.16),(.84,.19)):
    table.include('turned pedestal %.2f'%z,resized(ball(r,center=(1.4,.65,z),color=wood),(1,1,.45)))
for i,a in enumerate((0,90,180,270)):
    a=math.radians(a); dx=math.cos(a); dy=math.sin(a)
    table.include('curved foot %d'%i,sweep_tube([(1.4,.65,.36),(1.4+dx*.20,.65+dy*.20,.23),(1.4+dx*.43,.65+dy*.43,.12),(1.4+dx*.58,.65+dy*.58,.09)],radius=.065,color=dark))
    table.include('foot tip %d'%i,ball(.075,center=(1.4+dx*.58,.65+dy*.58,.09),color=edge))
scene.include('table',table)
def chair(name,cx,cy,angle):
    a=Asset(name)
    a.include('seat wooden apron',box((.64,.58,.12),center=(cx,cy,.55),color=dark))
    a.include('pale upholstered cushion',fillet_box((.63,.57,.14),radius=.05,center=(cx,cy,.64),color=(.66,.65,.59)))
    for dx in (-.27,.27):
        for dy in (-.23,.23):
            a.include('curved leg %.2f %.2f'%(dx,dy),sweep_tube([(cx+dx,cy+dy,.53),(cx+dx*1.06,cy+dy,.30),(cx+dx*1.15,cy+dy-.035,.06)],radius=.035,color=dark))
    for dx in (-.29,.29):
        a.include('back upright '+str(dx),sweep_tube([(cx+dx,cy+.25,.57),(cx+dx*.93,cy+.27,1.05),(cx+dx*.84,cy+.27,1.45),(cx+dx*.72,cy+.27,1.58)],radius=.038,color=dark))
    a.include('carved top rail',sweep_tube([(cx-.21,cy+.27,1.56),(cx-.12,cy+.27,1.61),(cx,cy+.27,1.57),(cx+.12,cy+.27,1.61),(cx+.21,cy+.27,1.56)],radius=.045,color=dark))
    a.include('back splat',sweep_tube([(cx,cy+.27,.90),(cx-.08,cy+.27,1.12),(cx+.07,cy+.27,1.33),(cx,cy+.27,1.55)],radius=.035,color=wood))
    a.turn('+z',angle,pivot=(cx,cy,0))
    scene.include(name,a)
chair('left upholstered chair',.25,.48,-30)
chair('right upholstered chair',2.87,-.30,-30)
scene.include('picture frame',box((.055,.83,.58),center=(3.89,1.53,2.38),color=(.46,.30,.13)))
scene.include('picture mat',box((.02,.73,.48),center=(3.85,1.53,2.38),color=(.79,.77,.67)))
scene.include('picture image',box((.015,.53,.29),center=(3.835,1.53,2.38),color=(.56,.62,.51)))
scene.include('lamp stem',rod(.018,start=(1.47,2.58,.12),end=(1.47,2.58,1.91),color=(.42,.42,.38)))
scene.include('lamp angled arm',rod(.018,start=(1.47,2.58,1.65),end=(1.25,2.58,2.03),color=(.42,.42,.38)))
scene.include('lamp shade',resized(ball(.13,center=(1.24,2.58,2.04),color=(.66,.67,.63)),(1,1,.45)))
scene.include('paper on table',box((.56,.31,.008),center=(1.32,.65,1.043),color=(.83,.81,.72)))
scene.include('second paper',box((.38,.23,.009),center=(1.64,.62,1.048),color=(.76,.75,.67)))
scene.include('small dish',resized(ball(.10,center=(.93,.83,1.045),color=(.68,.67,.59)),(1,.75,.18)))
scene.include('vase body',resized(ball(.085,center=(1.31,.84,1.13),color=(.29,.40,.31)),(.78,.78,1.25)))
scene.include('vase neck',rod(.035,start=(1.31,.84,1.18),end=(1.31,.84,1.29),color=(.30,.42,.32)))
for i in range(4):
    x=1.31+(i-1.5)*.035; z=1.48+(i%2)*.07
    scene.include('flower stem '+str(i),rod(.008,start=(1.31,.84,1.24),end=(x,.84,z),color=(.16,.34,.12)))
    scene.include('red flower '+str(i),resized(ball(.038,center=(x,.84,z),color=(.63,.07,.09)),(.7,.7,1.5)))
    scene.include('leaf '+str(i),resized(ball(.06,center=(1.31+(i-1.5)*.045,.84,1.34+i*.025),color=(.20,.40,.13)),(.35,.3,1)))
realize(scene)
def mat(name,color,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    return m
glass=mat('soft daylight glass',(.83,.91,.86),.7)
for name,x,w,top,spring,y in arch_specs:
    coords=[(x-w/2,y,spring)]
    for i in range(1,13):
        t=i/12; coords.append((x-w/2+w*.5*t,y,spring+(top-spring)*(1-(1-t)**1.6)))
    for i in range(1,13):
        t=i/12; coords.append((x+w*.5*t,y,top-(top-spring)*t**1.6))
    mesh=bpy.data.meshes.new(name+' arch glass mesh'); mesh.from_pydata(coords,[],[list(range(len(coords)))]); mesh.materials.append(glass)
    obj=bpy.data.objects.new(name+' arch glass',mesh); bpy.context.collection.objects.link(obj)
if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new('Room world')
bpy.context.scene.world.use_nodes=True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.63,.69,.64,1)
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
set_view((0,-7.7,2.65),(0,2.2,1.60),lens=27,sensor=36)
area_emitter((0,-3.0,3.3),power=450,size=5,target=(0,1,1.1))
area_emitter((-1.2,2.6,2.5),power=350,size=2,target=(0,-1,1))
area_emitter((2,2.7,2.5),power=260,size=2,target=(1,-1,1))