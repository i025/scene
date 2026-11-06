from sceneact import *
import bpy, math, random
random.seed(8)
scene = Scene('Victorian bedroom')
wood = (.085,.043,.025)
ivory = (.78,.77,.66)

def add(n,o):
    scene.include(n,o)
    return o

def bx(n,s,c,col):
    return add(n,box(s,center=c,color=col))

def bar(n,a,b,r,col):
    return add(n,rod(r,start=a,end=b,color=col))

def orb(n,c,s,col):
    o=ball(1,center=c,color=col)
    o.resize(s)
    return add(n,o)

bx('limestone floor',(8,11,.14),(0,-.6,-.08),(.57,.55,.49))
bx('rear wallpaper',(7.5,.16,3.5),(-.35,3.5,1.75),(.43,.35,.26))
bx('right wallpaper',(.16,10.5,3.5),(3.35,-1.65,1.75),(.44,.36,.28))
for z,w,h in [(3.39,.15,.16),(3.28,.10,.07),(3.20,.055,.045)]:
    bx('rear cornice '+str(z),(7.6,w,h),(-.35,3.36,z),(.86,.87,.83))
    bx('side cornice '+str(z),(w,10.5,h),(3.21,-1.65,z),(.86,.87,.83))
bx('back skirting',(7.5,.075,.18),(-.35,3.36,.09),(.25,.19,.12))
bx('right skirting',(.08,10,.18),(3.24,-1.6,.09),(.25,.19,.12))

for i,(x,w) in enumerate([(-3.28,1.18),(-1.05,1.43)]):
    bx('window luminous glass '+str(i),(w,.035,2.60),(x,3.365,1.81),(.84,.95,.94))
    for dx in [-w/2,w/2]:
        bx('window outer upright '+str(i)+str(dx),(.105,.19,2.79),(x+dx,3.25,1.83),(.88,.9,.87))
        bx('window inner upright '+str(i)+str(dx),(.035,.07,2.57),(x+dx*.91,3.13,1.81),(.68,.73,.70))
    for z in [.46,3.19]:
        bx('window molding '+str(i)+str(z),(w+.19,.18,.09),(x,3.25,z),(.93,.94,.90))
    bx('window sill '+str(i),(w+.25,.34,.09),(x,3.17,.48),(.82,.84,.80))
    bx('green roller blind '+str(i),(w-.12,.035,1.18),(x,3.19,2.45),(.13,.31,.28))
    bar('blind bottom '+str(i),(x-w/2+.06,3.15,1.86),(x+w/2-.06,3.15,1.86),.018,(.34,.46,.39))
    bx('lower sash '+str(i),(.037,.055,1.25),(x,3.14,1.12),(.89,.91,.87))
    bx('window horizontal sash '+str(i),(w-.1,.07,.045),(x,3.14,1.15),(.87,.89,.86))

bx('door casing',(.74,.13,2.36),(1.12,3.30,1.18),(.89,.89,.82))
bx('white door',(.62,.045,2.22),(1.12,3.20,1.15),(.73,.77,.72))
for z,h in [(.70,.85),(1.73,.88)]:
    bx('door inset '+str(z),(.49,.025,h),(1.12,3.165,z),(.68,.73,.69))
orb('door handle',(1.34,3.10,1.15),(.035,.035,.035),(.42,.31,.10))

def oval_portrait(x,z,w,h):
    orb('gilded oval outer',(x,3.235,z),(w/2,.045,h/2),(.61,.43,.13))
    orb('gilded oval inner',(x,3.175,z),(w*.445,.025,h*.45),(.29,.19,.065))
    orb('portrait black field',(x,3.14,z),(w*.405,.018,h*.415),(.035,.029,.024))
    orb('portrait shoulders',(x,3.112,z-h*.16),(w*.26,.012,h*.15),(.075,.047,.033))
    orb('portrait face',(x+.015,3.085,z+h*.085),(w*.105,.012,h*.13),(.43,.28,.17))
    orb('portrait hair',(x-.013,3.065,z+h*.16),(w*.11,.012,h*.075),(.08,.048,.025))
    bar('portrait collar',(x-.06,3.06,z-.015),(x+.035,3.06,z-.06),.012,(.70,.62,.46))

oval_portrait(-2.28,2.24,.72,.91)

def picture(name,x,z,w,h,side=False,y=0):
    if not side:
        bx(name+' gold frame',(w,.065,h),(x,3.20,z),(.54,.41,.20))
        bx(name+' mat',(w-.05,.022,h-.05),(x,3.15,z),(.80,.79,.69))
        bx(name+' print',(w*.65,.018,h*.72),(x,3.13,z),(.48,.48,.42))
        orb(name+' bust',(x,3.108,z-.04),(w*.18,.013,h*.23),(.29,.29,.26))
        orb(name+' head',(x,3.087,z+.10),(w*.115,.012,h*.13),(.36,.35,.30))
    else:
        bx(name+' frame',(.065,w,h),(3.20,y,z),(.58,.44,.22))
        bx(name+' paper',(.02,w-.055,h-.055),(3.15,y,z),(.79,.77,.66))
        orb(name+' cameo',(3.12,y,z),(.015,w*.25,h*.34),(.42,.40,.34))

picture('small framed engraving',.32,2.54,.43,.59)
picture('side oval engraving',0,2.49,.36,.56,True,2.55)

bedx=2.03
for x in [1.06,3.0]:
    for y in [-1.36,1.85]:
        bx('bed turned post '+str((x,y)),(.105,.105,.79),(x,y,.48),wood)
        orb('bed post finial '+str((x,y)),(x,y,.93 if y<0 else 1.23),(.075,.075,.085),wood)
        if y>0:
            bx('head tall post '+str(x),(.09,.10,1.18),(x,y,.65),wood)
bar('headboard top rail',(1.06,1.85,1.23),(3,1.85,1.23),.055,wood)
bx('headboard panel',(1.85,.11,.68),(bedx,1.85,.84),(.115,.064,.039))
for x in [1.11,2.96]:
    bx('bed long side rail '+str(x),(.10,3.18,.28),(x,.24,.37),wood)
bx('bed mattress',(1.82,3.10,.24),(bedx,.22,.59),(.61,.61,.52))
add('soft ivory cover',fillet_box((1.86,2.98,.28),radius=.13,center=(bedx,.15,.75),color=ivory))
bx('footboard main',(1.88,.13,.68),(bedx,-1.37,.54),(.105,.054,.031))
bx('footboard recessed panel',(1.60,.035,.37),(bedx,-1.448,.54),(.12,.065,.038))
bar('footboard polished top',(1.04,-1.39,.91),(3.02,-1.39,.91),.055,wood)
for x in [1.57,2.43]:
    p=fillet_box((.81,.70,.23),radius=.105,center=(x,1.25,.96),color=(.82,.82,.72))
    p.turn('x',20)
    p.turn('z',-5 if x<2 else 6)
    add('large cream pillow '+str(x),p)
for j in range(10):
    x=1.24+j*.16
    bar('cover foot fold '+str(j),(x,-1.28,.71),(x+.05,-1.08,.84),.012,(.64,.64,.54))

cx=-.48
cy=-.67
for x in [cx-.48,cx+.48]:
    for y in [cy-.44,cy+.40]:
        bar('chair leg '+str((x,y)),(x,y,.07),(x-.025,y,.48),.037,(.15,.10,.045))
add('chair lower upholstery',fillet_box((1.12,.99,.31),radius=.14,center=(cx,cy,.43),color=(.29,.27,.055)))
orb('chair upholstered back',(cx,cy+.40,.96),(.57,.17,.66),(.34,.32,.075))
orb('chair back inset',(cx,cy+.235,.98),(.47,.065,.52),(.38,.35,.085))
add('chair seat cushion',fillet_box((.88,.79,.18),radius=.09,center=(cx,cy-.06,.60),color=(.38,.35,.075)))
for side in [-1,1]:
    x=cx+side*.52
    orb('chair arm side '+str(side),(x,cy-.06,.67),(.16,.55,.37),(.30,.28,.055))
    pts=[(x,cy-.52,.70),(x,cy-.39,.78),(x,cy+.02,.88),(x,cy+.35,1.10)]
    add('chair rolled arm '+str(side),sweep_tube(points=pts,radius=.075,color=(.40,.37,.085)))
for row in range(4):
    for col in range(3):
        x=cx+(col-1)*.22+(row%2)*.075
        z=.79+row*.18
        orb('velvet tuft '+str((row,col)),(x,cy+.162,z),(.026,.015,.025),(.21,.21,.035))
        for sign in [-1,1]:
            bar('tuft crease '+str((row,col,sign)),(x,cy+.165,z),(x+sign*.075,cy+.17,z+.08),.008,(.27,.26,.05))

for i in range(3):
    x=.04+i*.49
    y=2.38+(.05 if i==1 else 0)
    bx('screen ochre panel '+str(i),(.49,.055,1.50),(x,y,1.12),(.55,.40,.17))
    for dx in [-.245,.245]:
        bar('screen upright '+str((i,dx)),(x+dx,y-.045,.33),(x+dx,y-.045,1.90),.016,(.12,.085,.04))
    bx('screen blue lower area '+str(i),(.45,.013,.36),(x,y-.038,.56),(.045,.10,.34))
    for k in range(5):
        xx=x+random.uniform(-.19,.19)
        zz=random.uniform(.72,1.79)
        o=orb('screen blue painted shape '+str((i,k)),(xx,y-.045,zz),(random.uniform(.10,.19),.009,random.uniform(.08,.24)),(.035,.10,.37))
        o.turn('y',random.uniform(-35,35))
    for k in range(3):
        xx=x+random.uniform(-.17,.17)
        zz=random.uniform(.60,1.72)
        orb('screen ochre leaf '+str((i,k)),(xx,y-.063,zz),(.072,.008,.12),(.64,.43,.13))
        bar('screen green stem '+str((i,k)),(xx-.04,y-.074,zz-.10),(xx+.035,y-.074,zz+.1),.006,(.12,.29,.20))
    for k in range(7):
        orb('screen little motif '+str((i,k)),(x+random.uniform(-.21,.21),y-.075,random.uniform(1.35,1.85)),(.015,.007,.018),(.22,.20,.12))

tx=-2.17
ty=2.65
bx('small table top',(.79,.56,.075),(tx,ty,.70),wood)
for dx in [-.31,.31]:
    for dy in [-.20,.20]:
        bar('small table leg '+str((dx,dy)),(tx+dx,ty+dy,.04),(tx+dx,ty+dy,.69),.026,wood)
bx('table white linen',(.83,.59,.018),(tx,ty,.752),(.83,.82,.72))
add('hanging tablecloth',box((.69,.018,.25),center=(tx,ty-.295,.62),color=(.82,.81,.72)))
for x in [-2.41,-2.12,-1.94]:
    orb('table porcelain '+str(x),(x,2.62,.80),(.07,.065,.035),(.72,.73,.64))
    bar('table cup '+str(x),(x,2.62,.80),(x,2.62,.86),.026,(.78,.77,.65))
orb('small brass bowl',(-2.02,2.75,.80),(.09,.07,.035),(.46,.35,.10))
bx('left chest',(.88,.55,.58),(-3.48,2.53,.32),(.10,.061,.032))
bx('left chest top',(.98,.63,.07),(-3.48,2.53,.64),(.12,.072,.035))
for z in [.20,.40,.55]:
    bx('chest drawer '+str(z),(.76,.035,.12),(-3.48,2.235,z),(.13,.079,.041))
    for x in [-3.70,-3.27]:
        orb('drawer knob '+str((x,z)),(x,2.205,z),(.021,.018,.021),(.48,.34,.13))
bx('miniature table frame',(.30,.045,.36),(-3.48,2.50,.88),(.43,.31,.11))
bx('miniature table image',(.24,.018,.30),(-3.48,2.465,.88),(.10,.12,.08))
orb('miniature sitter',(-3.48,2.448,.90),(.05,.01,.085),(.43,.33,.19))

for x in [1.45,1.81]:
    for y in [2.37,2.72]:
        bar('black chair leg '+str((x,y)),(x,y,.04),(x,y,.52),.018,(.045,.034,.025))
bx('black chair seat',(.41,.43,.045),(1.63,2.52,.52),(.13,.12,.075))
for x in [1.45,1.81]:
    bar('black chair upright '+str(x),(x,2.73,.49),(x,2.73,1.04),.018,(.04,.032,.02))
bar('black chair crest',(1.44,2.73,1.04),(1.82,2.73,1.04),.024,wood)
for x in [1.53,1.64,1.74]:
    bar('chair spindle '+str(x),(x,2.73,.60),(x,2.73,1.03),.012,wood)
orb('round bedside cabinet',(3.35,-.33,.34),(.40,.40,.34),(.095,.058,.035))
orb('round bedside top',(3.35,-.33,.70),(.43,.43,.035),(.13,.08,.045))

def rug(name,x,y,w,h):
    colors=[(.34,.19,.13),(.57,.43,.30),(.24,.30,.30),(.62,.47,.32),(.44,.20,.13),(.61,.51,.36)]
    for i,c in enumerate(colors):
        bx(name+' border '+str(i),(w-i*.065,h-i*.065,.008),(x,y,.008+i*.002),c)
    for row in range(5):
        for col in range(7):
            xx=x+(col-3)*(w-.40)/7
            yy=y+(row-2)*(h-.36)/5
            o=box((.065,.065,.003),center=(xx,yy,.026),color=(.66,.55,.36))
            o.turn('z',45)
            add(name+' woven diamond '+str((row,col)),o)

rug('back carpet',-1.28,1.47,1.50,.97)
rug('foreground carpet',1.35,-2.05,1.95,.86)

realize(scene)

wallmat=bpy.data.materials.new('aged floral wallpaper')
wallmat.use_nodes=True
nt=wallmat.node_tree
n=nt.nodes
l=nt.links
bs=n.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.95
tex=n.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value=74
tex.inputs['Detail'].default_value=3.2
tex.inputs['Roughness'].default_value=.72
coord=n.new('ShaderNodeTexCoord')
l.new(coord.outputs['Generated'],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for pos,col in [
    (0,(.12,.16,.15,1)),
    (.35,(.22,.24,.20,1)),
    (.46,(.40,.31,.22,1)),
    (.55,(.52,.40,.27,1)),
    (.64,(.35,.27,.19,1)),
    (.77,(.60,.48,.33,1)),
    (1,(.30,.32,.27,1))
]:
    e=ramp.color_ramp.elements[0] if pos==0 else ramp.color_ramp.elements.new(pos)
    e.color=col
l.new(tex.outputs['Fac'],ramp.inputs[0])
l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
bump=n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.14
bump.inputs['Distance'].default_value=.035
l.new(tex.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs['Normal'],bs.inputs['Normal'])

for ob in bpy.data.objects:
    if ob.type=='MESH' and 'wallpaper' in ob.name:
        ob.data.materials.clear()
        ob.data.materials.append(wallmat)
    if ob.type=='MESH' and any(s in ob.name for s in ['pillow','soft ivory','upholstered','chair back inset']):
        for p in ob.data.polygons:
            p.use_smooth=True
        sub=ob.modifiers.new('soft textile surface','SUBSURF')
        sub.levels=2
        sub.render_levels=2
        dis=ob.modifiers.new('subtle fabric wrinkles','DISPLACE')
        t=bpy.data.textures.new(ob.name+' fabric',type='CLOUDS')
        t.noise_scale=.12
        t.noise_depth=2
        dis.texture=t
        dis.strength=.018
        dis.mid_level=.5

for ob in bpy.data.objects:
    if ob.type=='MESH' and 'luminous glass' in ob.name:
        mat=bpy.data.materials.new('window daylight '+ob.name)
        mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(.76,.91,.91,1)
        p.inputs['Emission Color'].default_value=(.76,.93,1,1)
        p.inputs['Emission Strength'].default_value=2.5
        ob.data.materials.clear()
        ob.data.materials.append(mat)

set_view((-4.35,-6.8,2.75),(-.02,1.05,1.43),lens=35,sensor=36)
area_emitter((-1.6,3.0,2.45),power=650,size=2.0,target=(.0,-.8,.4),color=(.80,.91,1))
area_emitter((-3.1,.0,3.0),power=180,size=3,target=(1,1,.7),color=(1,.88,.72))

sc=bpy.context.scene
world=sc.world
if world is None:
    world=bpy.data.worlds.new('Bedroom ambient world')
    sc.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.48,.51,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.23
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
