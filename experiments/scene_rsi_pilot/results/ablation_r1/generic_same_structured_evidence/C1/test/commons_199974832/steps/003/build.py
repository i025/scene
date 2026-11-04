from sceneact import *
import bpy, math, random
random.seed(18)

# Review: the feedback is much too pale, especially timber and iron.
# Assign shader colors explicitly from SceneAct material diffuse colors, lower
# light powers/exposure, and add restrained dark wood grain.
# The back wall stops inside the frame: increase wall height without moving shelves.
# Hanging squares form sideways chevrons: rotate their assemblies to roof silhouettes.
# Anchors: top shelf (.18,.34)-(.77,.33); bench tools around (.38,.78),(.66,.89).
CAMERA=(.05,-5.25,2.60)
TARGET=(0,1.65,2.02)
LENS=31
BACK_Y=2.65
SHELF_HEIGHTS=[1.05,1.64,2.23,2.88]
KEY_POWER=650

scene=Scene('Antique woodworking tool room')
ivory=(.67,.70,.65)
wood=(.29,.135,.042)
ochre=(.48,.265,.085)
darkwood=(.12,.055,.018)
iron=(.035,.043,.039)
steel=(.23,.26,.24)
woodcolors=[wood,darkwood,(.37,.19,.065),(.23,.12,.048)]

def B(p,key,size,center,color):
    return p.include(key,box(size=size,center=center,color=color))
def R(p,key,start,end,r,color):
    return p.include(key,rod(radius=r,start=start,end=end,color=color))

room=Asset('Plaster room')
B(room,'back_wall',(6.15,.14,6.5),(0,BACK_Y,3.2),ivory)
B(room,'right_wall',(.14,6.7,6.5),(3.08,-.55,3.2),(.64,.67,.62))
B(room,'left_wall',(.14,6.7,6.5),(-3.08,-.55,3.2),(.71,.73,.67))
B(room,'floor',(6.1,7,.12),(0,-.5,-.08),(.20,.16,.10))
scene.include('architecture',room)

window=Asset('Left daylight window')
B(window,'recess',(.035,2,2.95),(-2.995,.52,2.35),(.035,.085,.10))
for iy in range(3):
    for iz in range(3):
        B(window,f'pane_{iy}_{iz}',(.04,.58,.88),
          (-2.965,-.12+iy*.65,1.40+iz*.94),(.26,.48,.58))
for i,y in enumerate([-.47,.17,.82,1.47]):
    B(window,f'mullion_{i}',(.10,.055,2.98),(-2.91,y,2.34),(.50,.52,.45))
for i,z in enumerate([.88,1.85,2.8,3.83]):
    B(window,f'crossbar_{i}',(.10,2.05,.065),(-2.91,.5,z),(.57,.59,.50))
scene.include('window',window)

shelves=Asset('Timber shelving')
for i,z in enumerate(SHELF_HEIGHTS):
    B(shelves,f'back_board_{i}',(5.85,.50,.075),(0,2.29,z),ochre)
    B(shelves,f'back_edge_{i}',(5.85,.045,.055),(0,2.025,z-.025),(.58,.34,.12))
    B(shelves,f'right_board_{i}',(.58,3.65,.085),(2.75,.58,z),ochre)
    for j,x in enumerate([-2.35,-.75,.8,2.3]):
        R(shelves,f'bracket_{i}_{j}',(x,2.57,z-.30),(x,2.10,z-.04),.018,iron)
for i,z in enumerate([1.75,2.90,3.81]):
    B(shelves,f'left_rack_{i}',(.38,2.15,.065),(-2.82,.52,z),ochre)
scene.include('shelves',shelves)

def plane(name,pos,length=.48,width=.19,height=.16,yaw=0,metal=False,detailed=False):
    a=Asset(name)
    col=random.choice(woodcolors)
    B(a,'stock',(length,width,height),(0,0,height/2),iron if metal else col)
    B(a,'sole',(length+.015,width+.008,.015),(0,0,.012),steel if metal else darkwood)
    blade=B(a,'cutter',(.045,width*.72,height*.95),(.025,0,height*.98),steel)
    blade.turn('y',-29,pivot=(.025,0,height*.8))
    wedge=B(a,'wedge',(.09,width*.58,.065),(-.025,0,height*.84),darkwood)
    wedge.turn('y',-22,pivot=(-.025,0,height*.84))
    if length>.39:
        grip=B(a,'rear_tote',(.07,.055,height*.9),
               (length*.32,0,height*1.18),darkwood)
        grip.turn('y',24,pivot=(length*.32,0,height*1.18))
    if detailed:
        R(a,'front_knob',(-length*.32,0,height),(-length*.32,0,height*1.35),.038,col)
    a.turn('z',yaw,pivot=(0,0,0))
    a.move(pos)
    scene.include(name,a)

for row,z in enumerate(SHELF_HEIGHTS[:-1]):
    x=-2.67
    for j in range(10):
        length=random.uniform(.40,.54)
        plane(f'back_plane_{row}_{j}',(x+length/2,2.22,z+.045),
              length,.18,random.uniform(.14,.23),random.uniform(-6,6),
              metal=(row==1 and j%3==0))
        x+=.55

for i in range(39):
    a=Asset(f'Moulding plane {i}')
    x=-2.73+i*.142
    h=random.uniform(.19,.35)
    block=B(a,'stock',(.108,.25,h),(x,2.28,2.925+h/2),random.choice(woodcolors))
    block.turn('y',random.uniform(-9,11),pivot=(x,2.28,2.925))
    if i%3==0:
        B(a,'iron',(.018,.12,.12),(x,2.24,2.95+h),steel)
    scene.include(f'moulding_{i}',a)

for row,z in enumerate(SHELF_HEIGHTS):
    for j in range(7):
        if row==3 and j<2:
            continue
        plane(f'right_plane_{row}_{j}',(2.72,-1.02+j*.47,z+.046),
              random.uniform(.33,.47),.20,random.uniform(.17,.27),90,
              metal=(j%4==0 and row<3))
for j in range(4):
    a=Asset(f'High wooden tool {j}')
    y=.4+j*.43
    B(a,'block',(.30,.34,.40),(2.74,y,3.13),random.choice(woodcolors))
    B(a,'cutter',(.035,.17,.20),(2.73,y,3.40),steel)
    scene.include(f'high_tool_{j}',a)

def wall_square(name,x,z,length,angle):
    a=Asset(name)
    B(a,'long_arm',(.088,.035,length),(0,0,length/2),iron)
    B(a,'short_arm',(length*.70,.035,.088),(length*.35,0,.044),iron)
    B(a,'long_inlay',(.012,.012,length*.94),(.027,-.024,length*.5),(.38,.40,.35))
    B(a,'short_inlay',(length*.64,.012,.012),(length*.35,-.024,.066),(.38,.40,.35))
    a.turn('y',angle,pivot=(0,0,0))
    a.move((x,2.535,z))
    scene.include(name,a)

wall_square('Large framing square',-1.40,4.63,1.50,134)
wall_square('Middle framing square',-1.35,4.24,1.15,134)
wall_square('Small framing square',-1.30,3.87,.86,134)
wall_square('Upright square',-.02,3.75,.95,0)
wall_square('Narrow square',.29,3.75,.70,24)

for i,(x,z,h) in enumerate([(.75,3.47,.72),(.88,3.79,.94),(1.04,4.02,1.10),(.64,3.14,.30)]):
    a=Asset(f'Hanging dividers {i}')
    R(a,'left_leg',(x,2.51,z+h),(x-.17,2.51,z),.018,darkwood)
    R(a,'right_leg',(x,2.51,z+h),(x+.17,2.51,z),.018,darkwood)
    R(a,'crossbar',(x-.10,2.50,z+.22),(x+.10,2.50,z+.22),.009,steel)
    scene.include(f'dividers_{i}',a)

for j,(x,z) in enumerate([(1.57,3.88),(2.02,3.61)]):
    a=Asset(f'Wall mallet {j}')
    R(a,'shaft',(x,2.49,z-.35),(x,2.49,z+.32),.033,wood)
    B(a,'head',(.39,.12,.13),(x,2.49,z+.29),darkwood)
    scene.include(f'wall_mallet_{j}',a)

for row,z in enumerate([1.79,2.94,3.85]):
    for j in range(8):
        y=-.39+j*.25
        h=random.uniform(.25,.43)
        a=Asset(f'Window chisel {row} {j}')
        R(a,'blade',(-2.76,y,z-.24),(-2.76,y,z+.04),.013,steel)
        handle=B(a,'handle',(.067,.073,h),(-2.76,y,z+h/2+.025),
                 random.choice(woodcolors))
        handle.turn('x',random.uniform(-6,6),pivot=(-2.76,y,z+.025))
        scene.include(f'rack_chisel_{row}_{j}',a)

bench=Asset('Heavy workbench')
B(bench,'top',(5.1,2.48,.16),(-.18,-1.03,.79),(.25,.18,.095))
B(bench,'apron',(5.1,.12,.31),(-.18,-2.21,.60),wood)
for i,x in enumerate([-2.25,1.95]):
    for j,y in enumerate([-1.85,-.02]):
        B(bench,f'leg_{i}_{j}',(.17,.17,.76),(x,y,.35),darkwood)
for i in range(7):
    B(bench,f'plank_joint_{i}',(5,.008,.003),(-.18,-2.05+i*.32,.873),(.10,.065,.03))
for i in range(30):
    x=random.uniform(-2.5,2.1)
    y=random.uniform(-2.1,.1)
    scar=B(bench,f'scar_{i}',(random.uniform(.10,.35),.008,.003),
           (x,y,.875),(.43,.34,.19))
    scar.turn('z',random.uniform(-35,35),pivot=(x,y,.875))
scene.include('bench',bench)

for i,(x,y,l,ang) in enumerate([(-1.65,-.06,.83,4),(-.45,.03,.78,-6),
                                (.65,-.02,.92,4),(1.60,-.25,.70,-18),
                                (.35,-.58,.70,12)]):
    plane(f'Bench plane {i}',(x,y,.88),l,.26,.21,ang,i==4,True)
plane('Large foreground plane',(1.50,-1.02,.89),1.02,.34,.30,-23,False,True)

for i in range(6):
    a=Asset(f'Foreground saw {i}')
    x=-2.12+i*.24
    y=-1.13+i*.045
    blade=B(a,'blade',(.17,1.12,.018),(x,y,.902+i*.009),(.24,.27,.25))
    blade.turn('z',-13+i*5,pivot=(x,y,.902+i*.009))
    B(a,'wood_grip',(.14,.25,.065),(x,y+.62,.94+i*.009),(.30,.14,.045))
    B(a,'grip_slot',(.055,.12,.008),(x,y+.62,.977+i*.009),(.065,.055,.035))
    scene.include(f'saw_{i}',a)

for i in range(19):
    a=Asset(f'Loose chisel {i}')
    x=random.uniform(-2.13,.15)
    y=random.uniform(-2.13,-.7)
    R(a,'shaft',(0,-.26,0),(0,.23,0),.014,steel)
    R(a,'handle',(0,.21,.012),(0,.43,.012),.035,random.choice(woodcolors))
    R(a,'collar',(0,.195,.012),(0,.23,.012),.037,steel)
    a.turn('z',random.uniform(-75,75),pivot=(0,0,0))
    a.move((x,y,.96))
    scene.include(f'loose_chisel_{i}',a)

for i in range(4):
    a=Asset(f'Folding rule {i}')
    B(a,'rule',(.90,.038,.018),(0,0,0),(.59,.39,.12))
    for k in range(8):
        B(a,f'tick_{k}',(.004,.018,.002),(-.40+k*.11,.007,.011),(.10,.075,.025))
    a.turn('z',[-12,18,36,-27][i],pivot=(0,0,0))
    a.move((-.17+i*.33,-1.48+i*.12,.99+i*.023))
    scene.include(f'rule_{i}',a)

pot=Asset('Oil can')
R(pot,'body',(-.84,-.35,.89),(-.84,-.35,1.21),.155,iron)
R(pot,'lid',(-.84,-.35,1.205),(-.84,-.35,1.23),.166,steel)
R(pot,'cap',(-.84,-.35,1.23),(-.84,-.35,1.28),.060,iron)
pot.include('loop_handle',sweep_tube(
    points=[(-.98,-.35,1.15),(-1.09,-.35,1.31),(-1.03,-.35,1.48),
            (-.89,-.35,1.45),(-.86,-.35,1.28)],radius=.014,color=steel))
pot.include('spout',sweep_tube(
    points=[(-.72,-.35,1.20),(-.63,-.35,1.35),(-.64,-.35,1.51)],
    radius=.021,color=iron))
scene.include('oil_can',pot)

bottle=Asset('Cloudy bottle')
R(bottle,'body',(-.23,-.40,.89),(-.23,-.40,1.25),.094,(.36,.39,.29))
R(bottle,'shoulder',(-.23,-.40,1.25),(-.23,-.40,1.30),.068,(.40,.43,.32))
R(bottle,'neck',(-.23,-.40,1.30),(-.23,-.40,1.39),.042,(.46,.49,.37))
R(bottle,'stopper',(-.23,-.40,1.39),(-.23,-.40,1.42),.045,(.33,.26,.16))
B(bottle,'paper_label',(.13,.009,.16),(-.23,-.492,1.12),(.64,.62,.46))
scene.include('bottle',bottle)

for idx,(x,y,r) in enumerate([(.80,-1.27,.35),(.68,-.91,.27)]):
    a=Asset(f'Parts tray {idx}')
    R(a,'base',(x,y,.89),(x,y,.92),r,(.14,.17,.15))
    pts=[(x+r*math.cos(k*math.tau/24),
          y+r*math.sin(k*math.tau/24),.985) for k in range(25)]
    a.include('rim',sweep_tube(points=pts,radius=.022,color=(.30,.33,.29)))
    for k in range(18):
        px=x+random.uniform(-r*.65,r*.65)
        py=y+random.uniform(-r*.65,r*.65)
        R(a,f'fastener_{k}',(px,py,.94),
          (px+random.uniform(-.07,.07),py+.075,.96),.008,steel)
    for k in range(3):
        px=x+random.uniform(-r*.5,r*.5)
        py=y+random.uniform(-r*.5,r*.5)
        pts=[(px+.043*math.cos(t*.6),py+.043*math.sin(t*.6),.95+t*.001)
             for t in range(11)]
        a.include(f'curl_{k}',sweep_tube(points=pts,radius=.006,color=(.43,.45,.37)))
    scene.include(f'tray_{idx}',a)

mallet=Asset('Foreground mallet and stick')
R(mallet,'handle',(1.13,-2.08,.94),(1.92,-.86,1.02),.034,(.55,.34,.12))
head=B(mallet,'head',(.49,.16,.15),(1.25,-1.70,1.03),(.44,.26,.075))
head.turn('z',-34,pivot=(1.25,-1.70,1.03))
R(mallet,'crossing_stick',(1.23,-.93,1.04),(2.03,-1.97,.95),.023,(.62,.42,.16))
scene.include('foreground_mallet',mallet)

labels=Asset('Shelf tickets')
for i in range(9):
    z=SHELF_HEIGHTS[i%3]
    x=-2.4+(i//3)*2+(i%3)*.19
    B(labels,f'ticket_{i}',(.15,.008,.034),(x,1.996,z-.009),(.82,.79,.64))
    B(labels,f'writing_{i}',(.095,.003,.005),(x,1.989,z-.006),(.10,.10,.075))
scene.include('tickets',labels)

# Audit: no fillets; dimensions and radii positive; distinct rod endpoints;
# indexed sibling keys; sweep paths contain no consecutive duplicate points.
realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.60,.67,.73,1)
bg.inputs['Strength'].default_value=.22

# All finish changes are global and intentional. Semantic groups remain editable.
for mat in bpy.data.materials:
    color=tuple(mat.diffuse_color)
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=.78
    if max(color[:3])-min(color[:3])<.065 and color[0]<.5:
        bs.inputs['Metallic'].default_value=.5
        bs.inputs['Roughness'].default_value=.5
    elif color[0]>color[1]*1.22 and color[1]>color[2]*1.2:
        coord=nt.nodes.new('ShaderNodeTexCoord')
        scale=nt.nodes.new('ShaderNodeVectorMath')
        scale.operation='MULTIPLY'
        scale.inputs[1].default_value=(3,42,9)
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=5
        tex.inputs['Detail'].default_value=2
        nt.links.new(coord.outputs['Generated'],scale.inputs[0])
        nt.links.new(scale.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.22
        ramp.color_ramp.elements[0].color=tuple(v*.55 for v in color[:3])+(1,)
        ramp.color_ramp.elements[1].position=.8
        ramp.color_ramp.elements[1].color=tuple(min(1,v*1.15) for v in color[:3])+(1,)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16
        bump.inputs['Distance'].default_value=.014
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter((-2.6,-.7,3.4),power=KEY_POWER,size=2.6,
             target=(0,1.1,1.5),color=(.83,.93,1))
area_emitter((.1,-1,4.5),power=320,size=3.5,
             target=(0,1.3,1.4),color=(1,.91,.75))
area_emitter((2.1,1.4,4.4),power=170,size=2.5,target=(0,1,1.6))
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.45
if hasattr(sc,'cycles'):
    sc.cycles.use_denoising=True
