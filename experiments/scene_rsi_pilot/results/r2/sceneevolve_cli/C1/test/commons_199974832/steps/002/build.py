from sceneact import *
import bpy, math, random
random.seed(23)

# Render is too pale: deepen wood and iron, reduce light and ambient fill.
# Hanging squares are too small and low: enlarge them above the top shelf.
# Foreground is too sparse and low: raise the bench and crowd it with tools.

scene=Scene('Antique woodworking tool room')
WOOD=(.19,.072,.021)
HONEY=(.39,.18,.045)
DARKWOOD=(.085,.032,.009)
IRON=(.018,.024,.022)
STEEL=(.16,.18,.16)
WALL=(.52,.55,.51)

def add(parent,name,node):
    parent.include(name,node)
    return node

def beam(parent,name,a,b,width,depth,color):
    dx,dy,dz=(b[i]-a[i] for i in range(3))
    length=math.sqrt(dx*dx+dy*dy+dz*dz)
    q=box((width,depth,length),center=tuple((a[i]+b[i])/2 for i in range(3)),color=color)
    q.turn('y',math.degrees(math.acos(dz/length)))
    q.turn('z',math.degrees(math.atan2(dy,dx)))
    return add(parent,name,q)

room=Asset('Plaster walls and window')
add(room,'back plaster',box((6.6,.13,7),center=(0,1.72,3.45),color=WALL))
add(room,'right plaster',box((.13,5.7,7),center=(2.83,-1.05,3.45),color=(.59,.60,.55)))
add(room,'left plaster',box((.12,4.7,7),center=(-3.23,-.7,3.45),color=(.49,.53,.49)))
add(room,'floor',box((6.5,6,.12),center=(0,-.8,-.08),color=(.16,.14,.10)))
add(room,'window recess',box((.025,2.25,2.85),center=(-3.15,-.08,2.20),color=(.075,.15,.18)))
for k in range(3):
    add(room,'glass%d'%k,box((.03,.66,2.63),center=(-3.12,-.82+k*.73,2.22),color=(.25,.52,.67)))
for k in range(4):
    add(room,'mullion%d'%k,box((.12,.055,2.93),center=(-3.06,-1.18+k*.73,2.22),color=(.49,.56,.53)))
for j,z in enumerate((.79,2.04,3.66)):
    add(room,'crossbar%d'%j,box((.14,2.4,.07),center=(-3.04,-.10,z),color=(.50,.56,.53)))
scene.include('architecture',room)

shelves=Asset('Wooden shelves and iron brackets')
levels=(.98,1.58,2.22,2.94)
for j,z in enumerate(levels):
    add(shelves,'back shelf%d'%j,box((5.75,.48,.075),center=(-.20,1.36,z),color=HONEY))
    add(shelves,'right shelf%d'%j,box((.48,4.2,.075),center=(2.56,-.55,z),color=HONEY))
    for k,x in enumerate((-2.6,-1.1,.6,2.2)):
        add(shelves,'bracket%d_%d'%(j,k),box((.035,.32,.22),center=(x,1.48,z-.12),color=IRON))
    for k in range(7):
        add(shelves,'label%d_%d'%(j,k),box((.19,.008,.037),center=(-2.7+k*.78,1.114,z-.006),color=(.76,.73,.57)))
    for k in range(4):
        add(shelves,'side label%d_%d'%(j,k),box((.008,.20,.035),center=(2.316,-2.1+k*.92,z),color=(.76,.73,.57)))
scene.include('shelves',shelves)

def plane(name,pos,scale=1,angle=0,wooden=True):
    a=Asset(name)
    x,y,z=pos
    c=random.choice([WOOD,HONEY,DARKWOOD,(.25,.12,.037)])
    if wooden:
        add(a,'body',box((.43*scale,.17*scale,.145*scale),center=(x,y,z+.078*scale),color=c))
        add(a,'sole',box((.45*scale,.18*scale,.025*scale),center=(x,y,z+.012*scale),color=DARKWOOD))
        add(a,'mouth',box((.08*scale,.174*scale,.018*scale),center=(x+.035*scale,y,z+.153*scale),color=IRON))
    else:
        add(a,'metal sole',box((.47*scale,.18*scale,.035*scale),center=(x,y,z+.02*scale),color=IRON))
        add(a,'frog',box((.18*scale,.13*scale,.085*scale),center=(x,y,z+.07*scale),color=IRON))
        sweep=[(x+.17*scale,y,z+.05*scale),(x+.20*scale,y,z+.21*scale),
               (x+.12*scale,y,z+.25*scale),(x+.08*scale,y,z+.12*scale)]
        add(a,'rear handle',sweep_tube(points=sweep,radius=.026*scale,color=DARKWOOD))
        add(a,'front knob',rod(.035*scale,length=.085*scale,center=(x-.16*scale,y,z+.075*scale),color=WOOD))
        add(a,'knob cap',ball(.039*scale,center=(x-.16*scale,y,z+.12*scale),color=WOOD))
    blade=box((.065*scale,.13*scale,.24*scale),center=(x+.025*scale,y,z+.16*scale),color=STEEL)
    blade.turn('y',-27)
    add(a,'blade',blade)
    wedge=box((.07*scale,.115*scale,.15*scale),center=(x-.035*scale,y-.005,z+.14*scale),color=c)
    wedge.turn('y',-27)
    add(a,'wedge',wedge)
    a.turn('z',angle,pivot=(x,y,z))
    return a

for k in range(42):
    x=-2.91+k*.132
    h=random.uniform(.19,.35)
    q=Asset('Upper molding plane %02d'%k)
    add(q,'stock',box((.105,.29,h),center=(x,1.38,3.00+h/2),color=random.choice([WOOD,HONEY,DARKWOOD])))
    iron=box((.034,.12,h*.75),center=(x,1.33,3.04+h*.65),color=STEEL)
    iron.turn('y',random.uniform(-20,10))
    add(q,'cutting iron',iron)
    q.turn('y',random.uniform(-9,9))
    scene.include('upper tool%d'%k,q)
for row,z in enumerate(levels[:3]):
    count=(13,14,13)[row]
    for k in range(count):
        x=-2.78+k*5.12/(count-1)
        scene.include('back tool%d_%d'%(row,k),
                      plane('Shelf plane',(x,1.28,z+.045),random.uniform(.82,1.12),
                            random.uniform(-9,9),random.random()>.30))
for row,z in enumerate(levels):
    for k in range(7):
        scene.include('return tool%d_%d'%(row,k),
                      plane('Return plane',(2.54,-2.34+k*.60,z+.045),
                            random.uniform(1.05,1.40),90,wooden=(row!=0 or k%2==0)))

walltools=Asset('Hanging squares saws and measuring tools')
for k,(cx,top,span) in enumerate(((-1.38,4.46,1.25),(-1.38,4.15,1.05),(-1.38,3.83,.79))):
    beam(walltools,'square left%d'%k,(cx-span*.55,1.615,top-span*.59),(cx,1.615,top),.12,.035,IRON)
    beam(walltools,'square right%d'%k,(cx,1.615,top),(cx+span*.60,1.615,top-span*.58),.12,.035,IRON)
    beam(walltools,'steel edge%d'%k,(cx-span*.52,1.586,top-span*.57),(cx,1.586,top-.025),.014,.012,STEEL)
for k in range(3):
    x=-.20+k*.46
    beam(walltools,'rule a%d'%k,(x-.18,1.60,3.48),(x+.07,1.60,4.30-k*.12),.045,.025,IRON)
    beam(walltools,'rule b%d'%k,(x+.07,1.60,4.30-k*.12),(x+.21,1.60,3.48),.035,.025,IRON)
for k in range(3):
    x=.83+k*.17
    beam(walltools,'divider left%d'%k,(x-.12,1.60,3.52+k*.20),(x,1.60,3.95+k*.20),.026,.025,DARKWOOD)
    beam(walltools,'divider right%d'%k,(x,1.60,3.95+k*.20),(x+.13,1.60,3.52+k*.20),.026,.025,DARKWOOD)
add(walltools,'mallet shaft',box((.085,.08,.66),center=(1.63,1.57,3.88),color=WOOD))
add(walltools,'mallet head',box((.36,.14,.15),center=(1.63,1.56,4.23),color=DARKWOOD))
add(walltools,'hammer handle',box((.065,.065,.51),center=(2.03,1.56,3.59),color=WOOD))
add(walltools,'hammer head',box((.42,.11,.10),center=(2.03,1.54,3.86),color=IRON))
beam(walltools,'left saw',(-2.92,1.59,4.24),(-2.25,1.59,3.94),.18,.04,STEEL)
add(walltools,'saw handle',box((.25,.08,.22),center=(-2.91,1.55,4.26),color=DARKWOOD))
walltools.resize((1,1,1.48),pivot=(0,1.6,3.32))
scene.include('hanging tools',walltools)

racks=Asset('Window chisel racks')
for row,z in enumerate((1.20,2.35,3.34)):
    add(racks,'rack%d'%row,box((.18,2.35,.065),center=(-2.98,-.16,z),color=HONEY))
    for k in range(8):
        y=-1.15+k*.29
        h=random.uniform(.28,.46)
        add(racks,'handle%d_%d'%(row,k),rod(.042,start=(-2.96,y,z+.03),end=(-2.96,y,z+h),color=random.choice([WOOD,HONEY,DARKWOOD])))
        add(racks,'blade%d_%d'%(row,k),box((.025,.045,.23),center=(-2.96,y,z-.10),color=STEEL))
scene.include('left chisels',racks)

bench=Asset('Foreground workbench')
add(bench,'heavy top',box((5.65,2.55,.16),center=(-.10,-1.87,.91),color=(.17,.12,.060)))
for x in (-2.55,2.25):
    for y in (-2.65,-.93):
        add(bench,'leg%s%s'%(x,y),box((.16,.16,.90),center=(x,y,.45),color=WOOD))
add(bench,'back apron',box((5.4,.11,.25),center=(-.1,-.68,.72),color=DARKWOOD))
scene.include('workbench',bench)
for k,(x,y,s,ang) in enumerate(((-1.4,-1.1,1.8,5),(.25,-1.04,2.0,3),
                               (1.68,-1.32,1.6,88),(-.35,-1.68,1.6,-14),
                               (.83,-2.02,1.65,12),(-2.10,-2.03,1.5,74),
                               (1.95,-.77,1.4,14),(-1.45,-2.62,1.5,83))):
    scene.include('bench plane%d'%k,plane('Large bench plane',(x,y,1.00),s,ang,k%3!=1))

loose=Asset('Loose bench tools')
for k in range(11):
    x=-2.5+k*.17
    y=-2.55+random.uniform(-.17,.16)
    beam(loose,'chisel blade%d'%k,(x,y,1.035),(x+.24,y+.72,1.07),.068,.026,STEEL)
    beam(loose,'chisel handle%d'%k,(x+.24,y+.72,1.08),(x+.35,y+1.01,1.15),.08,.065,random.choice([WOOD,HONEY,DARKWOOD]))
for k in range(7):
    x=-1.0+k*.36
    beam(loose,'loose ruler%d'%k,(x,-2.89,1.03),(x+.83,-2.18,1.06),.065,.025,HONEY)
for k,(x,y) in enumerate(((.82,-2.63),(1.15,-2.17))):
    add(loose,'tray bottom%d'%k,box((.71,.46,.035),center=(x,y,1.03),color=IRON))
    for j in (-1,1):
        add(loose,'tray side%d_%d'%(k,j),box((.72,.025,.15),center=(x,y+j*.23,1.09),color=STEEL))
        add(loose,'tray end%d_%d'%(k,j),box((.025,.46,.15),center=(x+j*.35,y,1.09),color=STEEL))
    for j in range(22):
        a=(x+random.uniform(-.28,.28),y+random.uniform(-.17,.17),1.08)
        b=(a[0]+random.uniform(-.09,.09),a[1]+.09,1.10)
        add(loose,'nail%d_%d'%(k,j),rod(.008,start=a,end=b,color=(.42,.45,.42)))
add(loose,'oil can',rod(.18,length=.31,center=(-.83,-1.45,1.18),color=IRON))
add(loose,'can lid',rod(.19,length=.035,center=(-.83,-1.45,1.35),color=STEEL))
beam(loose,'oil spout',(-.83,-1.45,1.36),(-.77,-1.43,1.65),.025,.025,STEEL)
add(loose,'can handle',sweep_tube(points=[(-.97,-1.45,1.25),(-1.10,-1.45,1.40),(-.96,-1.45,1.47)],radius=.018,color=STEEL))
add(loose,'bottle',rod(.095,length=.40,center=(-.13,-1.47,1.22),color=(.23,.28,.20)))
add(loose,'shoulder',ball(.096,center=(-.13,-1.47,1.41),color=(.23,.28,.20)))
add(loose,'neck',rod(.040,length=.15,center=(-.13,-1.47,1.49),color=(.38,.39,.28)))
add(loose,'label',box((.14,.012,.18),center=(-.13,-1.569,1.22),color=(.66,.62,.46)))
add(loose,'mallet head',box((.48,.25,.25),center=(2.02,-2.36,1.20),color=HONEY))
beam(loose,'mallet handle',(1.91,-2.39,1.20),(1.48,-3.13,1.02),.075,.075,WOOD)
for k in range(5):
    x=-2.15+k*.21
    beam(loose,'file%d'%k,(x,-2.81,1.05),(x-.18,-1.91,1.13),.07,.025,IRON)
scene.include('bench contents',loose)

realize(scene)
CAMERA_POSITION=(-.38,-6.45,2.80)
CAMERA_TARGET=(0,.65,2.05)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=33,sensor=36)
area_emitter((-3,-1.1,3.25),power=480,size=2.3,target=(0,.5,1.4),color=(.82,.93,1))
area_emitter((.5,-3.4,4.7),power=280,size=3.5,target=(0,.6,1.5),color=(1,.93,.82))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.63,.69,.72,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
for mat in bpy.data.materials:
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    if not p:
        continue
    col=tuple(p.inputs['Base Color'].default_value)
    p.inputs['Roughness'].default_value=.76
    if col[0]>col[2]*1.7 and col[0]<.7:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=5
        tex.inputs['Detail'].default_value=3
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(3,38,5)
        coord=nodes.new('ShaderNodeTexCoord')
        links.new(coord.outputs['Generated'],mapping.inputs[0])
        links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(col[0]*.40,col[1]*.36,col[2]*.30,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(col[0]*1.15,col[1]*1.10,col[2],1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],p.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.22
        bump.inputs['Distance'].default_value=.025
        links.new(tex.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],p.inputs['Normal'])
    elif abs(col[0]-col[1])<.055 and col[0]<.40:
        p.inputs['Metallic'].default_value=.65
        p.inputs['Roughness'].default_value=.48
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.30
