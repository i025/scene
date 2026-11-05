from sceneact import *
import bpy, math, random
random.seed(13)

scene=Scene('Historic workshop tool display')
cream=(.57,.53,.34)
pale=(.49,.52,.39)
iron=(.045,.043,.032)
edge=(.073,.067,.045)
rust=(.13,.105,.060)
black=(.022,.024,.018)

def add(name,node):
    scene.include(name,node)
    return node
def B(name,size,center,col):
    return add(name,box(size=size,center=center,color=col))
def R(name,a,b,r=.012,col=iron):
    return add(name,rod(radius=r,start=a,end=b,color=col))
def ring(name,x,y,z,r,t,col=iron,n=48):
    return add(name,assemble([
        rod(radius=t,
            start=(x+r*math.cos(i*2*math.pi/n),y,z+r*math.sin(i*2*math.pi/n)),
            end=(x+r*math.cos((i+1)*2*math.pi/n),y,z+r*math.sin((i+1)*2*math.pi/n)),
            color=col) for i in range(n)]))
def disc(name,x,y,z,r,depth,col):
    return R(name,(x,y-depth/2,z),(x,y+depth/2,z),r,col)
def radial_bar(name,x,y,z,inner,outer,a,width,depth,col):
    mid=(inner+outer)/2
    node=box((outer-inner,depth,width),
             center=(x+mid*math.cos(a),y,z+mid*math.sin(a)),color=col)
    node.turn('y',-math.degrees(a))
    return add(name,node)

B('floor',(8,8,.12),(0,1,-.065),(.36,.38,.31))
B('main plaster pier',(1.23,.37,2.93),(0,.17,1.465),cream)
B('upper plaster lintel',(1.63,.43,.15),(-.13,.18,2.89),(.60,.55,.36))
B('left plaster reveal',(.105,.08,2.72),(-.59,-.065,1.39),(.65,.59,.39))
B('right plaster reveal',(.085,.095,2.74),(.585,-.065,1.39),(.66,.61,.42))
B('display backing',(.98,.037,1.69),(0,-.035,1.995),pale)

for x in [-.522,.522]:
    B('outer vertical frame '+str(x),(.047,.083,1.83),(x,-.082,1.996),edge)
    B('inner vertical lip '+str(x),(.012,.025,1.74),(x*.92,-.133,1.996),(.14,.13,.085))
for z in [1.095,2.895]:
    B('outer horizontal frame '+str(z),(1.09,.08,.045),(0,-.08,z),edge)
for z in [1.13,2.858]:
    B('inner horizontal lip '+str(z),(1,.03,.012),(0,-.13,z),(.16,.15,.10))
for x in [-.523,.523]:
    for z in [1.14,1.99,2.84]:
        disc('frame screw',x,-.137,z,.009,.008,(.23,.20,.12))

wx,wz=-.292,2.635
ring('large top wheel',wx,-.165,wz,.151,.015,iron)
ring('wheel inner rim',wx,-.166,wz,.136,.005,rust)
for k in range(5):
    a=2*math.pi*k/5+.2
    radial_bar('five wheel spokes',wx,-.184,wz,.015,.142,a,.021,.026,iron)
disc('top wheel hub',wx,-.195,wz,.027,.040,edge)
disc('top wheel axle',wx,-.222,wz,.009,.012,(.25,.22,.13))

for i,(x,r) in enumerate([(-.045,.059),(.105,.049),(.246,.047),(.378,.044)]):
    disc('round machine die '+str(i),x,-.133,2.635,r,.035,iron)
    ring('die rim '+str(i),x,-.160,2.635,r*.76,.009,rust)
    disc('die central hole '+str(i),x,-.175,2.635,r*.27,.014,black)
    disc('die central pin '+str(i),x,-.186,2.635,r*.10,.012,(.29,.26,.15))
    for j in range(3):
        a=j*2*math.pi/3
        disc('die recess',x+r*.43*math.cos(a),-.175,
             2.635+r*.43*math.sin(a),.006,.006,black)

B('long saw blade',(.72,.020,.043),(-.087,-.126,2.343),(.12,.095,.052))
for i in range(31):
    x=-.427+i*.022
    B('saw tooth',(.009,.017,.009),(x,-.13,2.318),rust)
B('dark saw handle',(.285,.050,.062),(.226,-.158,2.336),(.055,.036,.018))
B('handle upper worn edge',(.25,.015,.009),(.22,-.188,2.365),(.14,.10,.045))
R('saw handle end',(.365,-.16,2.35),(.382,-.16,2.32),.014)
R('hanging saw strip',(.365,-.14,2.315),(.382,-.15,2.166),.006,rust)
for x in [-.38,-.20,-.06]:
    R('blade fastening clips',(x,-.16,2.32),(x,-.16,2.365),.005,(.29,.27,.16))

R('center crossbar',(-.255,-.172,1.996),(.169,-.172,2.025),.010,rust)
R('center vertical shank',(-.035,-.175,2.045),(-.035,-.175,1.900),.011,edge)
disc('crossbar hub',-.035,-.193,2.005,.018,.024,(.17,.15,.08))
for x in [-.40,-.32,.22,.31]:
    B('square mounting plate',(.066,.025,.07),(x,-.117,1.91),black)
B('left mounting bridge',(.035,.047,.078),(-.365,-.15,1.91),(.23,.24,.15))
for x in [-.08,-.035,.01]:
    R('small hooks',(x,-.115,1.795),(x+.005,-.14,1.818),.005,(.27,.28,.17))

R('ring peg',(-.385,-.107,1.602),(-.385,-.19,1.602),.009)
ring('hanging ring',-.385,-.19,1.55,.045,.010,rust)
R('pliers left handle',(-.075,-.185,1.46),(-.091,-.185,1.62),.014,iron)
R('pliers right handle',(-.018,-.185,1.47),(-.068,-.185,1.62),.013,iron)
disc('pliers pivot',-.067,-.205,1.62,.025,.026,rust)
R('pliers jaw left',(-.080,-.185,1.63),(-.063,-.185,1.665),.014)
R('pliers jaw right',(-.047,-.185,1.63),(-.040,-.185,1.665),.011)

B('vise mounting foot',(.30,.14,.041),(.273,-.175,1.245),edge)
B('vise foot front lip',(.32,.04,.024),(.273,-.265,1.247),iron)
R('vise left leg',(.166,-.20,1.28),(.215,-.21,1.46),.035,iron)
R('vise right leg',(.379,-.20,1.28),(.318,-.21,1.46),.039,iron)
ring('vise round casting',.268,-.22,1.436,.083,.025,iron,36)
B('vise central block',(.135,.116,.14),(.27,-.20,1.56),edge)
B('vise upright',(.063,.083,.185),(.279,-.175,1.745),iron)
B('vise fixed jaw',(.133,.12,.05),(.30,-.20,1.835),edge)
B('vise movable jaw',(.09,.145,.056),(.283,-.295,1.779),rust)
R('vise screw',(.27,-.16,1.606),(.27,-.365,1.606),.026,rust)
disc('vise screw collar',.27,-.37,1.606,.047,.033,edge)
R('vise cross handle',(.16,-.404,1.66),(.398,-.404,1.532),.012,iron)
for x,z in [(.16,1.66),(.398,1.532)]:
    add('handle knob',ball(.019,center=(x,-.404,z),color=edge))
R('upper jaw hook',(.34,-.18,1.86),(.347,-.18,1.94),.014)
ring('upper jaw eye',.346,-.18,1.927,.027,.010,iron)
B('loose sill tool',(.14,.047,.02),(-.26,-.16,1.174),iron)
R('small sill piece',(-.46,-.16,1.16),(-.429,-.16,1.18),.013,rust)

B('horizontal iron strap',(1.13,.032,.102),(0,-.049,.966),black)
B('yellow identification label',(.188,.022,.153),(.037,-.078,1.018),(.52,.36,.018))
for i in range(5):
    B('label engraving',(.0018,.003,.105),(-.026+i*.024,-.092,1.02),(.26,.19,.025))
R('strap left peg',(-.29,-.08,.95),(-.29,-.235,.95),.022,rust)
R('strap right peg',(.303,-.08,.981),(.366,-.28,.957),.026,edge)

B('lower wheel support strap',(1.05,.032,.070),(0,-.046,.514),iron)
disc('left large chuck',-.245,-.135,.529,.225,.075,(.12,.105,.060))
ring('left chuck rim',-.245,-.182,.529,.213,.008,(.16,.14,.08))
for j in range(8):
    a=j*math.pi/4+.14
    radial_bar('left chuck radial dark slot',-.245,-.187,.529,.105,.197,a,.011,.009,black)
B('left chuck square hub',(.064,.036,.063),(-.245,-.206,.529),(.25,.23,.13))
B('left chuck square socket',(.019,.008,.031),(-.245,-.229,.529),black)
disc('right chuck backing',.312,-.139,.527,.206,.087,(.085,.077,.042))
ring('right chuck rim',.312,-.19,.527,.189,.010,(.15,.13,.075))
disc('right chuck center',.312,-.214,.527,.063,.045,edge)
for j in range(4):
    a=j*math.pi/2+.18
    radial_bar('right chuck radial slot',.312,-.192,.527,.066,.187,a,.016,.01,black)
    radial_bar('right chuck heavy jaw',.312,-.265,.527,.063,.173,a,.071,.11,(.14,.13,.082))
    radial_bar('right chuck jaw step',.312,-.322,.527,.075,.126,a,.049,.045,(.11,.10,.06))
R('lower hanging shaft',(.267,-.105,.32),(.267,-.105,.095),.019,(.14,.14,.08))
R('bottom crank',(.12,-.12,.079),(.432,-.12,.109),.014,edge)
ring('small crank loop',.268,-.14,.185,.022,.007,rust)
B('bottom skirting',(1.20,.08,.038),(0,-.025,.025),(.19,.18,.11))

B('left surrounding wall',(1.14,.28,3.1),(-1.19,.18,1.55),(.56,.49,.29))
B('red wooden door',(.94,.095,2.84),(-1.13,-.025,1.42),(.31,.068,.028))
B('door right jamb',(.065,.14,2.92),(-.63,-.07,1.46),(.35,.27,.13))
for z,h in [(.66,.78),(1.87,1.01)]:
    B('door inset panel',(.64,.015,h),(-1.13,-.083,z),(.29,.066,.027))
    for x in [-1.47,-.79]:
        B('door vertical molding',(.028,.028,h+.07),(x,-.098,z),(.37,.105,.044))
    for zz in [z-h/2-.02,z+h/2+.02]:
        B('door horizontal molding',(.70,.028,.028),(-1.13,-.098,zz),(.37,.105,.044))
B('door central crosspiece',(.88,.04,.11),(-1.13,-.085,1.205),(.35,.084,.033))

B('right background wall',(3,.20,3.35),(2.02,.96,1.675),(.59,.57,.38))
B('window opening',(1.15,.06,1.39),(1.33,.832,2.315),(.035,.045,.037))
B('bright window glass',(1.025,.025,1.29),(1.33,.790,2.315),(.75,.84,.85))
for x in [.78,1.88]:
    B('window side frame',(.065,.12,1.39),(x,.75,2.315),(.055,.075,.065))
for z in [1.65,2.98]:
    B('window outer horizontal frame',(1.17,.12,.065),(1.33,.75,z),(.06,.08,.065))
for x in [1.055,1.34,1.62]:
    B('window vertical mullion',(.025,.062,1.32),(x,.71,2.315),(.055,.075,.065))
for z in [1.95,2.30,2.65]:
    B('window horizontal mullion',(1.06,.06,.024),(1.33,.70,z),(.065,.085,.065))
B('deep window sill',(1.38,.40,.09),(1.33,.69,1.615),(.27,.28,.19))
for i in range(24):
    a=math.pi*i/24
    b=math.pi*(i+1)/24
    R('arched window frame',
      (1.33+.57*math.cos(a),.73,2.85+.18*math.sin(a)),
      (1.33+.57*math.cos(b),.73,2.85+.18*math.sin(b)),.029,(.065,.085,.065))

B('bench worktop',(2.05,.64,.095),(1.65,.56,1.345),(.24,.17,.085))
B('bench front apron',(2.01,.065,.13),(1.65,.222,1.22),(.11,.075,.033))
B('bench lower shelf',(2,.62,.065),(1.65,.56,1.005),(.21,.16,.085))
for x in [.75,2.48]:
    B('bench legs',(.09,.11,1.31),(x,.48,.655),(.13,.10,.045))
B('dark slot beneath bench top',(.80,.04,.075),(1.13,.20,1.254),black)

pipepts=[(-.23,-.035,3.085),(.02,-.035,3.073),
         (.22,-.035,3.076),(.37,-.027,3.13),(1.06,.09,3.27)]
for a,b in zip(pipepts[:-1],pipepts[1:]):
    R('overhead blue pipe',a,b,.035,(.10,.19,.20))
for x in [-.20,.06]:
    R('pipe coupling',(x-.025,-.035,3.078),(x+.025,-.035,3.078),.044,(.13,.21,.21))

realize(scene)

# Add subtle surface variation without any image textures.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    if not bs:
        continue
    bs.inputs['Roughness'].default_value=.84
    base=tuple(bs.inputs['Base Color'].default_value)
    noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=95
    noise.inputs['Detail'].default_value=2
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=tuple(v*.79 for v in base[:3])+(1,)
    ramp.color_ramp.elements[1].position=.82
    ramp.color_ramp.elements[1].color=base
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.13
    bump.inputs['Distance'].default_value=.002
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if base[0]>.7 and base[2]>.7:
        bs.inputs['Emission Color'].default_value=(.75,.86,.90,1)
        bs.inputs['Emission Strength'].default_value=1.1

set_view((-1.38,-5.8,2.25),(-.015,0,1.54),lens=65,sensor=36)
sc=bpy.context.scene
sc.camera.data.sensor_fit='VERTICAL'
sc.camera.data.sensor_height=36

area_emitter((2.1,-.3,3.35),power=240,size=1.7,
             target=(0,0,1.3),color=(.91,.95,1))
area_emitter((-2.2,-3,3.5),power=95,size=3.4,
             target=(0,0,1.5),color=(1,.86,.62))
if sc.world is None:
    sc.world=bpy.data.worlds.new('Workshop ambient')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.28,.28,.20,1)
bg.inputs['Strength'].default_value=.25
sc.render.resolution_x=341
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=-.25
