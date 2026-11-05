from sceneact import *
import bpy, math, random
random.seed(13)

scene = Scene('Antique workshop display')
cream=(.66,.63,.43)
pale=(.66,.69,.55)
iron=(.105,.105,.078)
edge=(.16,.15,.11)
rust=(.23,.20,.13)
black=(.055,.060,.050)

def add(name,node):
    scene.include(name,node)
    return node

def B(name,size,center,col):
    return add(name,box(size=size,center=center,color=col))

def R(name,a,b,r=.012,col=iron):
    return add(name,rod(radius=r,start=a,end=b,color=col))

def ring(name,x,y,z,r,t,col=iron,n=48):
    nodes=[]
    for i in range(n):
        a=i*2*math.pi/n
        b=(i+1)*2*math.pi/n
        nodes.append(rod(radius=t,
            start=(x+r*math.cos(a),y,z+r*math.sin(a)),
            end=(x+r*math.cos(b),y,z+r*math.sin(b)),color=col))
    return add(name,assemble(nodes))

def disc(name,x,y,z,r,depth,col):
    return R(name,(x,y-depth/2,z),(x,y+depth/2,z),r,col)

B('floor',(8,8,.12),(0,1,-.065),(.43,.45,.38))
B('main plaster pier',(1.23,.37,2.93),(0,.17,1.465),cream)
B('upper plaster lintel',(1.63,.43,.15),(-.13,.18,2.89),(.67,.64,.45))
B('left narrow plaster reveal',(.105,.08,2.72),(-.59,-.065,1.39),(.73,.69,.49))
B('right plaster reveal',(.085,.095,2.74),(.585,-.065,1.39),(.76,.73,.54))
B('display backing',(.98,.037,1.69),(0,-.035,1.995),pale)

for x in [-.522,.522]:
    B('outer vertical frame '+str(x),(.047,.083,1.83),(x,-.082,1.996),edge)
    B('inner vertical lip '+str(x),(.012,.025,1.74),(x*.92,-.133,1.996),(.24,.23,.17))
for z in [1.095,2.895]:
    B('outer horizontal frame '+str(z),(1.09,.08,.045),(0,-.08,z),edge)
for z in [1.13,2.858]:
    B('inner horizontal lip '+str(z),(1.00,.03,.012),(0,-.13,z),(.25,.25,.18))
for x in [-.523,.523]:
    for z in [1.14,1.99,2.84]:
        disc('frame screw',x,-.132,z,.009,.008,(.37,.34,.24))

wx,wz=-.292,2.635
ring('large top wheel outer',wx,-.145,wz,.151,.014,iron)
ring('large top wheel inner',wx,-.148,wz,.136,.005,rust)
disc('top wheel hub',wx,-.163,wz,.027,.040,edge)
for k in range(5):
    a=2*math.pi*k/5+.2
    R('wheel spoke',(wx,-.153,wz),
      (wx+.139*math.cos(a),-.153,wz+.139*math.sin(a)),.013,iron)
disc('top wheel axle',wx,-.19,wz,.009,.01,(.43,.40,.27))

for i,(x,r) in enumerate([(-.045,.059),(.105,.049),(.246,.047),(.378,.044)]):
    disc('round die '+str(i),x,-.112,2.635,r,.035,edge)
    ring('die raised rim '+str(i),x,-.141,2.635,r*.76,.009,rust)
    disc('die center '+str(i),x,-.153,2.635,r*.24,.018,(.38,.36,.25))
    for j in range(3):
        a=j*2*math.pi/3
        disc('die recess',x+r*.43*math.cos(a),-.161,
             2.635+r*.43*math.sin(a),.006,.005,black)

B('saw upper blade',(.72,.017,.034),(-.087,-.113,2.343),(.24,.21,.14))
for i in range(31):
    x=-.427+i*.022
    R('saw tooth',(x,-.125,2.327),(x+.009,-.125,2.312),.004,rust)
B('saw dark wooden handle',(.285,.046,.062),(.226,-.149,2.336),(.10,.075,.045))
B('saw grip highlight',(.25,.015,.009),(.22,-.178,2.365),(.22,.17,.10))
R('saw handle end',(.365,-.147,2.35),(.382,-.147,2.32),.014)
R('thin hanging strip',(.365,-.114,2.315),(.382,-.13,2.166),.006,rust)
for x in [-.38,-.20,-.06]:
    R('blade clips',(x,-.14,2.32),(x,-.14,2.365),.005,(.43,.42,.29))

R('center crossbar',(-.255,-.156,1.996),(.169,-.156,2.025),.010,rust)
R('center vertical shank',(-.035,-.154,2.045),(-.035,-.154,1.900),.011,edge)
R('crossbar hub',(-.054,-.175,1.996),(-.016,-.175,2.009),.017,(.32,.30,.21))
for x in [-.40,-.32,.22,.31]:
    B('square tool mounting plate',(.066,.022,.07),(x,-.108,1.91),black)
B('small left mounting bridge',(.035,.047,.078),(-.365,-.135,1.91),(.39,.40,.28))
for x in [-.08,-.035,.01]:
    R('small pale hooks',(x,-.10,1.795),(x+.005,-.125,1.818),.005,(.42,.43,.31))

R('ring peg',(-.385,-.107,1.602),(-.385,-.177,1.602),.009)
ring('hanging iron ring',-.385,-.171,1.55,.045,.010,rust)
R('pliers left handle',(-.075,-.161,1.48),(-.091,-.162,1.64),.014,iron)
R('pliers right handle',(-.018,-.158,1.49),(-.068,-.158,1.63),.013,iron)
disc('pliers pivot',-.067,-.18,1.64,.025,.026,rust)
R('pliers jaw left',(-.080,-.164,1.65),(-.063,-.164,1.685),.014)
R('pliers jaw right',(-.047,-.164,1.65),(-.040,-.164,1.685),.011)

B('vise mounting foot',(.30,.14,.041),(.273,-.155,1.245),edge)
B('vise foot front lip',(.32,.04,.024),(.273,-.244,1.247),iron)
R('vise left sloping support',(.166,-.177,1.28),(.215,-.184,1.46),.035,iron)
R('vise right sloping support',(.379,-.176,1.28),(.318,-.184,1.46),.039,iron)
ring('vise round body',.268,-.19,1.436,.083,.025,iron,36)
B('vise central block',(.135,.116,.14),(.27,-.17,1.56),edge)
B('vise upper vertical casting',(.063,.083,.185),(.279,-.145,1.745),iron)
B('vise fixed jaw',(.133,.12,.050),(.30,-.17,1.835),edge)
B('vise movable jaw',(.09,.145,.056),(.283,-.265,1.779),rust)
R('vise long screw',(.27,-.13,1.606),(.27,-.335,1.606),.026,rust)
disc('vise screw collar',.27,-.34,1.606,.047,.033,edge)
R('vise cross handle',(.16,-.374,1.66),(.398,-.374,1.532),.012,iron)
for x,z in [(.16,1.66),(.398,1.532)]:
    add('vise handle knob',ball(.019,center=(x,-.374,z),color=edge))
R('upper jaw hook',(.34,-.149,1.86),(.347,-.149,1.94),.014)
ring('upper jaw eye',.346,-.15,1.927,.027,.010,iron)
B('small loose tool on sill',(.14,.047,.02),(-.26,-.14,1.174),iron)
R('small sill angled piece',(-.46,-.14,1.16),(-.429,-.14,1.18),.013,rust)

B('black horizontal strap',(1.13,.027,.102),(0,-.041,.966),black)
B('ochre label',(.188,.020,.153),(.037,-.067,1.018),(.68,.49,.045))
for i in range(5):
    B('label engraved line',(.0018,.003,.105),(-.026+i*.024,-.080,1.020),(.40,.32,.07))
R('strap left pin',(-.29,-.075,.95),(-.29,-.205,.95),.022,rust)
R('strap right pin',(.303,-.07,.981),(.366,-.26,.957),.026,edge)

B('lower wheel support strip',(1.05,.025,.070),(0,-.037,.514),iron)
disc('left large solid chuck',-.245,-.11,.529,.225,.075,(.22,.205,.145))
ring('left chuck rim',-.245,-.155,.529,.213,.010,(.25,.23,.16))
for j in range(8):
    a=j*math.pi/4+.14
    R('radial groove',
      (-.245+.105*math.cos(a),-.158,.529+.105*math.sin(a)),
      (-.245+.197*math.cos(a),-.158,.529+.197*math.sin(a)),.007,black)
B('left chuck square hub',(.064,.036,.063),(-.245,-.173,.529),(.39,.37,.25))
B('left chuck square socket',(.019,.006,.031),(-.245,-.195,.529),black)
disc('right large chuck',.312,-.111,.527,.206,.087,(.18,.175,.12))
ring('right chuck rim',.312,-.16,.527,.189,.014,(.26,.24,.17))
disc('right chuck center',.312,-.184,.527,.063,.045,edge)
for j in range(4):
    a=j*math.pi/2+.18
    dx,dz=math.cos(a),math.sin(a)
    jaw=box((.104,.091,.068),
            center=(.312+.12*dx,-.207,.527+.12*dz),color=(.27,.26,.19))
    jaw.turn('y',-math.degrees(a))
    add('right chuck projecting jaw',jaw)
    R('right chuck radial slot',
      (.312+.066*dx,-.166,.527+.066*dz),
      (.312+.187*dx,-.166,.527+.187*dz),.009,black)
R('lower hanging shaft',(.267,-.092,.32),(.267,-.092,.095),.019,(.26,.26,.18))
R('bottom horizontal crank',(.12,-.10,.079),(.432,-.10,.109),.014,edge)
ring('small crank loop',.268,-.12,.185,.022,.007,rust)
B('bottom skirting',(1.20,.08,.038),(0,-.025,.025),(.30,.29,.20))

B('left surrounding wall',(1.14,.28,3.1),(-1.19,.18,1.55),(.63,.58,.38))
B('red door',(.94,.095,2.84),(-1.13,-.025,1.42),(.38,.105,.050))
B('door right jamb',(.065,.14,2.92),(-.63,-.07,1.46),(.48,.39,.22))
for z,h in [(.66,.78),(1.87,1.01)]:
    B('door inset panel',(.64,.015,h),(-1.13,-.083,z),(.36,.105,.055))
    for x in [-1.47,-.79]:
        B('door raised vertical molding',(.028,.028,h+.07),(x,-.098,z),(.47,.16,.085))
    for zz in [z-h/2-.02,z+h/2+.02]:
        B('door raised horizontal molding',(.70,.028,.028),(-1.13,-.098,zz),(.47,.16,.085))
B('door center crosspiece',(.88,.04,.11),(-1.13,-.085,1.205),(.44,.13,.065))

B('right background wall',(3,.20,3.35),(2.02,.96,1.675),(.68,.67,.49))
B('window dark opening',(1.15,.06,1.98),(1.33,.832,2.04),(.065,.075,.065))
B('luminous window glass',(1.025,.025,1.82),(1.33,.790,2.04),(.77,.86,.84))
for x in [.78,1.88]:
    B('window outer side',(.065,.12,1.98),(x,.75,2.04),(.13,.16,.14))
for z in [1.075,2.98]:
    B('window horizontal outer rail',(1.17,.12,.065),(1.33,.75,z),(.14,.16,.14))
for x in [1.055,1.34,1.62]:
    B('window slender vertical mullion',(.025,.062,1.90),(x,.71,2.03),(.13,.16,.14))
for z in [1.57,2.04,2.50]:
    B('window horizontal mullion',(1.06,.060,.024),(1.33,.70,z),(.16,.18,.15))
B('deep window sill',(1.38,.40,.09),(1.33,.69,1.045),(.37,.38,.29))
for i in range(24):
    a=math.pi*i/24
    b=math.pi*(i+1)/24
    R('arched window surround',
      (1.33+.57*math.cos(a),.73,2.85+.18*math.sin(a)),
      (1.33+.57*math.cos(b),.73,2.85+.18*math.sin(b)),.029,(.16,.18,.15))
B('bench worktop',(2.05,.64,.095),(1.65,.56,.824),(.32,.25,.15))
B('bench front apron',(2.01,.065,.13),(1.65,.222,.70),(.20,.16,.10))
B('bench lower shelf',(2.00,.62,.065),(1.65,.56,.435),(.27,.23,.15))
for x in [.75,2.48]:
    B('bench legs',(.09,.11,.79),(x,.48,.40),(.22,.19,.12))
B('dark slot under worktop',(.80,.04,.075),(1.13,.20,.733),black)

add('overhead pipe',sweep_tube(
    points=[(-.23,-.035,3.085),(.02,-.035,3.073),
            (.22,-.035,3.076),(.37,-.027,3.13),(1.06,.09,3.27)],
    radius=.035,color=(.22,.32,.32)))
for x in [-.20,.06]:
    R('pipe coupling',(x-.025,-.035,3.078),(x+.025,-.035,3.078),.044,(.26,.34,.32))

realize(scene)

for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        for mat in obj.data.materials:
            mat.use_nodes=True
            bs=mat.node_tree.nodes.get('Principled BSDF')
            if bs:
                bs.inputs['Roughness'].default_value=.81
        if any(k in obj.name.lower() for k in ['chuck','vise','frame','jaw','door']):
            bevel=obj.modifiers.new('Small worn edges','BEVEL')
            bevel.width=.003
            bevel.segments=1
            obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')

for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and 'luminous window glass' in obj.name:
        for mat in obj.data.materials:
            bs=mat.node_tree.nodes.get('Principled BSDF')
            if bs:
                bs.inputs['Emission Color'].default_value=(.78,.88,.92,1)
                bs.inputs['Emission Strength'].default_value=.8

set_view((1.15,-5.8,2.25),(-.04,0,1.54),lens=69,sensor=36)
bpy.context.scene.camera.data.sensor_fit='VERTICAL'
bpy.context.scene.camera.data.sensor_height=36

area_emitter((2.1,-.6,3.35),power=450,size=2.0,
             target=(0,0,1.3),color=(.89,.94,1))
area_emitter((-2.2,-3,3.5),power=210,size=3.4,
             target=(0,0,1.5),color=(1,.87,.64))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Workshop ambient world')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(.30,.30,.23,1)
background.inputs['Strength'].default_value=.35

sc.render.resolution_x=341
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
